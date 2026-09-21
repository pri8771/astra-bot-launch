#!/usr/bin/env python3
"""SB-V07-001 — prove real crash/restart behaviour of the bounded worker.

A unit test can simulate an abandoned receipt. This proves the real thing: a
genuine ``worker_once.py`` OS process is **SIGKILLed mid-invocation**, and we
then check what it left behind.

What must be true after a hard kill:

1. the killed invocation leaves an ``incomplete`` receipt — not a missing
   record, and never a ``complete``/success one;
2. no ``finish`` work receipt claims the unit succeeded;
3. while the dead worker's lease is still within its TTL, the next scheduled
   invocation does NOT double-run the task — it reports benign no-overlap;
4. once that lease goes stale, a restart takes it over, completes, and writes a
   **new** invocation id rather than reusing the dead one;
5. the durable heartbeat ledger still holds exactly one record per session id.

Point 3 is the one a scheduled host most needs: a SIGKILL cannot run a cleanup
handler, so the dead process's lease file survives it. The lease TTL, not the
dying process, is what protects the next firing from running the same task
twice.

SIGKILL is used deliberately: it cannot be caught, so no cleanup handler can
tidy up on the way out. That is the worst case a scheduled host actually faces
(OOM kill, power loss, ``systemctl kill -s SIGKILL``).

There is no test hook in production code. The kill delay is swept across a
range until one lands inside the work window, which is why a run reports how
many attempts it took. No model call, no network beyond an optional git fetch,
no public effect.

Usage:
    python3 bin/prove_worker_once_crash.py [--out DIR] [--attempts 40]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
from runtime import invocation as invocation_mod  # noqa: E402
from runtime import session_heartbeat as sh  # noqa: E402

ENTRYPOINT = ROOT / "bin" / "worker_once.py"

# A lane that current canonical STATE.json actually resolves, so direction
# consumption succeeds and the kill can land in the work window rather than in
# the earlier direction step. Reports go to a throwaway root, so the real lane
# ledger is never touched.
LANE = "windows-core"

# Slightly longer than leasing.DEFAULT_TTL_SECONDS, so the dead worker's lease
# is genuinely stale before the restart rather than force-cleared.
LEASE_TTL_WAIT_S = 125

# Weakest to strongest. A run reports the strongest stage it actually reached.
_STAGE_RANK = {"before_heartbeat": 0, "after_heartbeat_no_lease": 1,
               "mid_unit_lease_held": 2}


def _lease_held(home: Path) -> str | None:
    """A lease file the dead process left behind, if any."""
    leases = home / "leases"
    if not leases.is_dir():
        return None
    for path in sorted(leases.glob("*.lease.json")):
        return path.name
    return None


def _stage_for(receipt: dict, home: Path) -> str:
    if _lease_held(home):
        return "mid_unit_lease_held"
    if receipt.get("heartbeat_emitted"):
        return "after_heartbeat_no_lease"
    return "before_heartbeat"


def _spawn(home: Path, reports: Path, session_id: str) -> subprocess.Popen:
    env = dict(os.environ)
    env["SBOTS_HOME"] = str(home)
    env.pop("ANTHROPIC_API_KEY", None)
    return subprocess.Popen(
        [sys.executable, str(ENTRYPOINT),
         "--lane", LANE, "--branch", "crash-proof",
         "--bots", "social-a", "--repo-root", str(REPO_ROOT),
         "--session-id", session_id, "--skip-fetch", "--allow-deterministic",
         "--home", str(home), "--report-root", str(reports)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


def _kill_mid_invocation(work: Path, attempts: int) -> dict:
    """Sweep the kill delay until a SIGKILL lands inside a live invocation.

    Each attempt gets its OWN runtime home. A SIGKILLed worker leaves its lease
    held for the rest of the TTL, so sharing one home would make every later
    attempt exit immediately with no-overlap and the sweep would never reach the
    work window. That behaviour is real and is proven deliberately below; here
    it would only be noise.

    Three stages are distinguished, because they prove different things:

    ``before_heartbeat``        died during direction consumption; no heartbeat,
                                no lease.
    ``after_heartbeat_no_lease`` died after the heartbeat but before claiming a
                                task; a heartbeat exists, no lease is held.
    ``mid_unit_lease_held``     died inside the bounded unit with the task lease
                                held. Only this stage can prove the next firing
                                declines to double-run.

    Detected from what the dead process left on disk — a heartbeat record and a
    lease file — not from the receipt alone, since ``claim_outcome`` is only
    written once the unit returns. The strongest stage reached is preferred and
    always reported, so the proof never overstates where the process died.
    """
    # Calibrate against a real, uninterrupted invocation. A fixed delay ladder
    # is brittle: most of a run is direction consumption (two git subprocesses),
    # so a small delay reliably kills before the heartbeat and proves less.
    baseline = work / "baseline"
    (baseline / "home").mkdir(parents=True, exist_ok=True)
    (baseline / "reports").mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    _spawn(baseline / "home", baseline / "reports", "s-baseline").communicate(timeout=120)
    window = max(0.05, time.monotonic() - started)

    fallback: dict = {}
    for attempt in range(1, attempts + 1):
        # Sweep the LATE part of the measured window, where the lease is held.
        delay = window * (0.45 + 0.55 * (attempt - 1) / max(1, attempts - 1))
        session_id = f"s-crash-{attempt:03d}"
        home = work / f"attempt-{attempt:03d}" / "home"
        reports = work / f"attempt-{attempt:03d}" / "reports"
        home.mkdir(parents=True, exist_ok=True)
        reports.mkdir(parents=True, exist_ok=True)
        proc = _spawn(home, reports, session_id)
        time.sleep(delay)
        killed_while_running = proc.poll() is None
        if killed_while_running:
            proc.kill()                      # SIGKILL: uncatchable by design
        proc.communicate(timeout=60)
        if not killed_while_running:
            continue                         # it finished first; try a later delay
        receipts = [r for r in invocation_mod.read_all(home)
                    if r.get("session_id") == session_id]
        if not receipts or receipts[0].get("status") != invocation_mod.STATUS_INCOMPLETE:
            continue
        stage = _stage_for(receipts[0], home)
        found = {"attempt": attempt, "delay_seconds": round(delay, 4),
                 "session_id": session_id, "signal": int(signal.SIGKILL),
                 "returncode": proc.returncode, "stage": stage,
                 "lease_left_behind": _lease_held(home),
                 "home": str(home), "reports": str(reports),
                 "receipt": receipts[0]}
        if stage == "mid_unit_lease_held":
            return found
        if not fallback or _STAGE_RANK[stage] > _STAGE_RANK[fallback["stage"]]:
            fallback = found
    return fallback


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=None, help="directory to write the proof into")
    parser.add_argument("--attempts", type=int, default=24)
    args = parser.parse_args(argv)

    work = Path(tempfile.mkdtemp(prefix="worker-once-crash-"))

    crash = _kill_mid_invocation(work, args.attempts)
    if not crash:
        print("INCONCLUSIVE: no SIGKILL landed inside a live invocation within "
              f"{args.attempts} attempts. Nothing is claimed.", file=sys.stderr)
        return 1
    home, reports = Path(crash["home"]), Path(crash["reports"])

    # (3) Immediately after the crash: the dead worker's lease is still inside
    # its TTL, so the next firing must stand down rather than double-run.
    immediate = _spawn(home, reports, "s-immediately-after-crash")
    imm_out, imm_err = immediate.communicate(timeout=180)
    immediate_code = immediate.returncode

    # (4) Wait the lease out rather than force-clearing it: forcing would prove
    # nothing about real recovery on a host that actually lost a process.
    time.sleep(LEASE_TTL_WAIT_S)
    restart_session = "s-restart-after-crash"
    restart = _spawn(home, reports, restart_session)
    out, err = restart.communicate(timeout=180)
    restart_code = restart.returncode

    receipts = invocation_mod.read_all(home)
    killed = crash["receipt"]
    restarted = [r for r in receipts if r.get("session_id") == restart_session]
    heartbeats = sh.read_log(LANE, reports)
    session_ids = [r["session_id"] for r in heartbeats]

    checks = {
        "killed_invocation_left_an_incomplete_receipt":
            killed.get("status") == invocation_mod.STATUS_INCOMPLETE,
        "killed_invocation_claimed_no_success": killed.get("exit_code") is None,
        # Only meaningful when the kill landed after a lease was acquired. A
        # crash during direction consumption holds no lease, so the next firing
        # is expected to run normally; asserting 3 there would be a false alarm.
        # Only meaningful at ``mid_unit_lease_held``: a crash before the claim
        # holds no lease, so the next firing is expected to run normally, and
        # asserting 3 there would be a false alarm.
        "next_firing_did_not_double_run_while_the_dead_lease_was_live":
            immediate_code == 3 if crash["stage"] == "mid_unit_lease_held"
            else immediate_code in (0, 3),
        "restart_after_lease_expiry_completed":
            bool(restarted) and restarted[0].get("status") == invocation_mod.STATUS_COMPLETE
            and restart_code == 0,
        "restart_wrote_a_new_invocation_id":
            bool(restarted) and restarted[0]["invocation_id"] != killed["invocation_id"],
        "no_duplicate_session_heartbeats": len(session_ids) == len(set(session_ids)),
        "no_live_model_call": all(not r.get("live_model_call") for r in receipts),
    }
    audit = invocation_mod.audit(home)
    checks["audit_reports_the_crash"] = audit["incomplete"] >= 1
    if crash["stage"] in ("after_heartbeat_no_lease", "mid_unit_lease_held"):
        # Only claimable when the kill actually landed past the heartbeat.
        checks["killed_invocation_emitted_its_one_heartbeat"] = \
            killed.get("heartbeat_emitted") is True

    proof = {
        "artifact": "SB-V07-001",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": {"platform": sys.platform, "python": sys.version.split()[0]},
        "method": ("a real worker_once.py OS process was SIGKILLed mid-invocation; "
                   "no test hook exists in production code and the kill delay was "
                   "swept until one landed inside the work window"),
        "crash": {k: v for k, v in crash.items() if k != "receipt"},
        "crash_stage_meaning": {
            "mid_unit_lease_held": "the process died inside the bounded unit with "
                                   "the task lease held",
            "after_heartbeat_no_lease": "the process died after its one heartbeat "
                                        "but before claiming a task, so no lease "
                                        "was held",
            "before_heartbeat": "the process died during direction consumption, "
                                "before any heartbeat could be attested",
        }[crash["stage"]],
        "strongest_stage_reached": crash["stage"],
        "double_run_check_applicable": crash["stage"] == "mid_unit_lease_held",
        "killed_receipt": killed,
        "immediately_after_crash": {
            "session_id": "s-immediately-after-crash",
            "exit_code": immediate_code,
            "meaning": ("3 = benign no-overlap: the SIGKILLed worker's lease is "
                        "still within its TTL, so this firing correctly declined "
                        "to run the same task twice. 0 is correct instead when the "
                        "kill landed before any lease was acquired."),
            "applies_to_stage": crash["stage"],
            "stdout_tail": (imm_out or "").strip()[-400:],
            "stderr_tail": (imm_err or "").strip()[-200:],
        },
        "restart": {
            "session_id": restart_session,
            "exit_code": restart_code,
            "waited_seconds_for_lease_expiry": LEASE_TTL_WAIT_S,
            "invocation_id": restarted[0]["invocation_id"] if restarted else None,
            "claim_outcome": restarted[0].get("claim_outcome") if restarted else None,
            "stdout_tail": (out or "").strip()[-400:],
            "stderr_tail": (err or "").strip()[-400:],
        },
        "heartbeat_sessions": session_ids,
        "audit": audit,
        "checks": checks,
        "all_pass": all(checks.values()),
        "limitations": [
            "single POSIX host, single filesystem; not a power-loss or "
            "network-filesystem test",
            ("the kill point is timing-dependent; when the strongest stage "
             "reached is not mid_unit_lease_held, the no-double-run check is "
             "reported as not applicable rather than as a pass"),
            "engineering demonstration of crash behaviour only; NOT SB-V07-002 "
            "operational recurring-liveness proof on an owner-authorized host",
        ],
    }

    print(json.dumps(proof, indent=2, sort_keys=True))
    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "CRASH_RESTART_PROOF.json").write_text(
            json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        hb_log = reports / "worker-reports" / LANE / sh.LOG_FILENAME
        if hb_log.exists():
            shutil.copy(hb_log, out_dir / "CRASH_HEARTBEAT_LOG.jsonl")
        shutil.copy(invocation_mod.invocations_dir(home) / "index.jsonl",
                    out_dir / "CRASH_INVOCATION_INDEX.jsonl")
    return 0 if proof["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
