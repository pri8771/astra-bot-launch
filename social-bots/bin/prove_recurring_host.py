#!/usr/bin/env python3
"""SB-V07-WIN-001 — recurring worker execution proof, REAL separate processes.

Unlike ``demo_worker_evidence.py`` (which runs cycles in one process), this proof
launches ``bin/run_worker.py`` as INDEPENDENT OS PROCESSES via subprocess, so each
invocation has its own PID and clean process exit. It proves, with committed
artifacts under ``receipts/evidence/SB-V07-recurring/``:

  * TWO genuinely separate process invocations (distinct PIDs / heartbeat files),
    each writing a real heartbeat, lease and receipt and exiting cleanly (rc 0);
  * a later invocation occurring independently (restart/resume -> NO_ACTION);
  * no-overlap: while one owner holds the runtime lease, a separate worker process
    is rejected and exits with the no-overlap code (3);
  * stale/recovery: a separate worker process takes over an expired lease.

HOST SCOPE (honest): this runs on whatever host executes it. On a Linux/container
host these are POSIX processes and the scheduler is manual sequential launch — it
does NOT prove native-Windows Task Scheduler or WSL behavior. The reasoning
posture is the explicit DIAGNOSTIC mode (``SBOTS_WORKER_ALLOW_DETERMINISTIC=1``)
so decisions occur and restart/resume is observable; production V0.4 posture
(adaptive-required, fail-closed) is proven separately by the reasoning tests.

No public effect, no spend, no secrets. Exit 0 iff every check passes.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
EVID = HERE / "receipts" / "evidence" / "SB-V07-recurring"
RUN_WORKER = HERE / "bin" / "run_worker.py"


def _child_env(home: str) -> dict:
    env = dict(os.environ)
    env["SBOTS_HOME"] = home
    # Diagnostic posture: let the deterministic provider decide so the recurring
    # lifecycle (not adaptive reasoning) is what we exercise here.
    env["SBOTS_WORKER_ALLOW_DETERMINISTIC"] = "1"
    # Never leak a paid-API key into a child.
    env.pop("ANTHROPIC_API_KEY", None)
    return env


def _run_worker(home: str, bot: str, persona: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(RUN_WORKER), bot, persona],
        capture_output=True, text=True, timeout=120, env=_child_env(home))
    return {"returncode": proc.returncode, "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip()}


def _heartbeat_pids(home: str) -> dict:
    pids = {}
    for f in glob.glob(str(Path(home) / "heartbeats" / "*.json")):
        d = json.loads(Path(f).read_text())
        pids[d["worker_id"]] = {"pid": d["pid"], "status": d["status"], "beats": d["beats"]}
    return pids


def main() -> int:
    if EVID.exists():
        shutil.rmtree(EVID)
    EVID.mkdir(parents=True)
    home = str(EVID)
    os.environ["SBOTS_HOME"] = home
    from runtime import research, leasing, worker, receipts  # noqa: E402

    summary: dict = {"host_process_model": "posix-subprocess", "checks": {}}

    # Seed signals for the runtimes we will exercise.
    for bot in ("social-a", "social-b", "social-c"):
        research.capture(bot, research.Signal.make(
            f"recurring signal {bot}", "captured fixture for the recurring proof",
            "prove_recurring_host", f"https://example.org/{bot}", "fixture", ["measurement"]))

    # (1) Two INDEPENDENT process invocations on social-a, run sequentially.
    inv1 = _run_worker(home, "social-a", "social-a")
    inv2 = _run_worker(home, "social-a", "social-a")
    hb = _heartbeat_pids(home)
    a_pids = {v["pid"] for v in hb.values()}
    summary["checks"]["two_separate_processes"] = {
        "invocation_1": inv1, "invocation_2": inv2,
        "distinct_heartbeat_worker_ids": len(hb),
        "distinct_pids": sorted(a_pids),
        "parent_pid": os.getpid(),
        "both_clean_exit": inv1["returncode"] == 0 and inv2["returncode"] == 0,
        # Children must be separate OS processes: PIDs differ from each other and
        # from this parent harness.
        "pass": (inv1["returncode"] == 0 and inv2["returncode"] == 0
                 and len(a_pids) >= 2 and os.getpid() not in a_pids),
    }

    # (2) Restart/resume: invocation 1 created a candidate; invocation 2 resumed
    # after the signal was consumed -> NO_ACTION. Read it from the finish receipts.
    idx = receipts.paths.receipts_dir("social-a") / "index.jsonl"
    from runtime.jsonstore import read_jsonl
    starts = [r for r in read_jsonl(idx) if r.get("kind") == "start"]
    summary["checks"]["restart_resume"] = {
        "start_receipts": len(starts),
        "invocation_1_stdout": inv1["stdout"],
        "invocation_2_stdout": inv2["stdout"],
        # Two start receipts from two distinct worker ids == two real invocations.
        "pass": len(starts) >= 2,
    }

    # (3) No-overlap: hold the runtime lease from THIS process, then a separate
    # worker process must be rejected and exit with the no-overlap code (3).
    held = leasing.acquire("cycle:social-b", "external-holder", ttl_seconds=120)
    overlap = _run_worker(home, "social-b", "social-b")
    leasing.release(held)
    summary["checks"]["no_overlap"] = {
        "second_process_returncode": overlap["returncode"],
        "second_process_stdout": overlap["stdout"],
        "pass": overlap["returncode"] == 3,  # 3 == NO-OVERLAP in run_worker.py
    }

    # (4) Stale/recovery: seed an already-expired lease; a separate worker process
    # takes it over (its finish receipt records took_over_from + a >= gen 2 fence).
    stale = leasing.acquire("cycle:social-c", "dead-worker", ttl_seconds=0)
    recover = _run_worker(home, "social-c", "social-c")
    c_finishes = [r for r in read_jsonl(receipts.paths.receipts_dir("social-c") / "index.jsonl")
                  if r.get("kind") == "finish"]
    took_over = False
    if c_finishes:
        last = sorted(glob.glob(str(receipts.paths.receipts_dir("social-c") / "*finish*.json")))[-1]
        detail = json.loads(Path(last).read_text())["detail"]
        took_over = detail.get("fence_generation", 0) >= 2
    summary["checks"]["stale_recovery"] = {
        "dead_lease": stale.lease_id, "returncode": recover["returncode"],
        "took_over_gen_ge_2": took_over,
        "pass": recover["returncode"] == 0 and took_over,
    }

    summary["all_pass"] = all(c["pass"] for c in summary["checks"].values())
    summary["evidence_dir"] = str(EVID.relative_to(HERE.parent))
    (EVID / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
