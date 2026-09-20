#!/usr/bin/env python3
"""Produce SB-002 acceptance evidence by ACTUALLY RUNNING the worker.

This is not a claim that a worker runs — it runs one here, in-process, and emits
the real artifacts (receipts, heartbeat, lease files) plus a summary. Evidence is
written under receipts/evidence/SB-002-run/ so it can be committed and reviewed.

Demonstrates, with real files:
  * two actual invocations (two start receipts);
  * heartbeat updated by the running process;
  * successful atomic lease acquisition;
  * concurrent second-worker rejection (no-overlap);
  * stale-lock recovery (takeover + reconcile);
  * restart/resume (state advances; no duplicate candidate).
"""
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

EVID = HERE / "receipts" / "evidence" / "SB-002-run"


def main() -> int:
    # Fresh, deterministic evidence tree.
    if EVID.exists():
        shutil.rmtree(EVID)
    EVID.mkdir(parents=True)
    os.environ["SBOTS_HOME"] = str(EVID)

    # Import AFTER SBOTS_HOME is set so paths resolve into the evidence tree.
    from runtime import worker, leasing, research, receipts  # noqa: E402
    from runtime.heartbeat import read_heartbeat  # noqa: E402

    summary: dict = {"checks": {}}

    # Seed one real captured signal (fixture provenance, clearly labeled).
    sig = research.Signal.make(
        title="Evidence-run signal",
        summary="A captured fixture signal so the cycle has changed evidence.",
        source="demo_worker_evidence", url="https://example.org/evidence",
        provenance="fixture", tags=["demo", "measurement"])
    research.capture("social-a", sig)

    # (1) Invocation #1 — should create an unpublished candidate.
    r1 = worker.run_one_unit("cycle:social-a", "social-a", "social-a")
    # (2) Invocation #2 — restart/resume: evidence consumed -> NO_ACTION.
    r2 = worker.run_one_unit("cycle:social-a", "social-a", "social-a")

    summary["checks"]["two_invocations"] = {
        "start_receipts": receipts.count_invocations("social-a"),
        "invocation_1_action": r1["chosen_action"],
        "invocation_2_action": r2["chosen_action"],
        "pass": receipts.count_invocations("social-a") >= 2,
    }
    summary["checks"]["restart_resume"] = {
        "first": r1["chosen_action"], "second": r2["chosen_action"],
        "pass": r1["chosen_action"] == "CREATE_CANDIDATE" and r2["chosen_action"] == "NO_ACTION",
    }

    hb = read_heartbeat(r2["worker_id"])
    summary["checks"]["heartbeat"] = {
        "worker_id": hb["worker_id"], "pid": hb["pid"], "status": hb["status"],
        "beats": hb["beats"], "pass": hb["status"] == "done" and hb["beats"] >= 2,
    }

    # (3) No-overlap: hold the lease, a worker unit must be rejected.
    held = leasing.acquire("cycle:social-b", "external-holder", ttl_seconds=120)
    overlap_rejected = False
    try:
        worker.run_one_unit("cycle:social-b", "social-b", "social-b")
    except leasing.LeaseHeld:
        overlap_rejected = True
    leasing.release(held)
    summary["checks"]["no_overlap"] = {"second_worker_rejected": overlap_rejected,
                                       "pass": overlap_rejected}

    # (4) Stale-lock recovery: a 0-TTL (already stale) lease is taken over.
    stale = leasing.acquire("cycle:social-c", "dead-worker", ttl_seconds=0)
    r3 = worker.run_one_unit("cycle:social-c", "social-c", "social-c")
    summary["checks"]["stale_recovery"] = {
        "took_over_from": r3["took_over_from"], "dead_lease": stale.lease_id,
        "pass": r3["took_over_from"] == stale.lease_id,
    }

    summary["all_pass"] = all(c["pass"] for c in summary["checks"].values())
    summary["evidence_dir"] = str(EVID.relative_to(HERE.parent))
    summary["worker_ids"] = sorted({r1["worker_id"], r2["worker_id"], r3["worker_id"]})

    (EVID / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
