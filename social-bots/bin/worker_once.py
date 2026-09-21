#!/usr/bin/env python3
"""SB-V07-001 — ONE bounded worker session. This is what an OS scheduler runs.

A single invocation does exactly this, then exits:

    1. consume current ChatGPT lead direction from GitHub (plain ``git``, no ``gh``);
    2. emit exactly ONE durable SESSION_ONCE heartbeat;
    3. acknowledge the direction it consumed;
    4. claim AT MOST ONE task (first candidate whose lease is free);
    5. run that one bounded unit;
    6. write an invocation receipt;
    7. exit with a code the scheduler can act on.

It is never a daemon, never loops, never keeps a model conversation alive and
never makes a live model call: the reasoning posture is unchanged from
``bin/run_worker.py``, so with no adaptive provider configured the cycle fails
closed to BLOCKED_REASONING_UNAVAILABLE rather than spending anything.

Ordering matters. Direction is consumed BEFORE the heartbeat so the heartbeat
can truthfully record which canonical SHA this session read — that is exactly
what the heartbeat is supposed to attest.

Usage:
    python3 bin/worker_once.py --lane windows-core \
        --branch claude/social-bots-windows-core-host \
        [--bots social-a,social-b,social-c] [--repo-root /path/to/clone] \
        [--session-id s-...] [--skip-fetch] [--allow-deterministic] \
        [--post-issue] [--home /runtime/data/root]

Exit codes (the scheduler contract):
    0  a bounded unit completed (any decision, including NO_ACTION or a block)
    3  no-overlap: every candidate task is held by a live worker. BENIGN.
    5  lead direction halted this lane. BENIGN.
    1  unexpected failure (an invocation receipt records it)
    2  bad usage
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import direction as direction_mod  # noqa: E402
from runtime import invocation as invocation_mod  # noqa: E402
from runtime import leasing, worker  # noqa: E402
from runtime import session_heartbeat as sh  # noqa: E402

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2
EXIT_NO_OVERLAP = 3
EXIT_HALTED = 5

DEFAULT_BOTS = ("social-a", "social-b", "social-c")


def _allow_deterministic(flag: bool) -> bool:
    return flag or os.environ.get("SBOTS_WORKER_ALLOW_DETERMINISTIC", "0") \
        .strip().lower() in {"1", "true", "yes", "on"}


def claim_one(bots: list[str], *, require_adaptive: bool | None) -> tuple[dict | None, list]:
    """Run the FIRST claimable bot's bounded unit. At most one unit ever runs.

    Claiming is not a separate probe-then-acquire step: each candidate's unit is
    attempted directly, and a ``LeaseHeld`` simply moves to the next candidate.
    That removes the probe/acquire race entirely — there is no window in which a
    task looks free but is taken before the real acquire.
    """
    tried: list[dict] = []
    for bot in bots:
        task_id = worker.runtime_task_id(bot)
        try:
            result = worker.run_one_unit(task_id, bot, bot,
                                         require_adaptive=require_adaptive)
        except leasing.LeaseHeld as held:
            tried.append({"bot": bot, "task_id": task_id, "result": "lease_held",
                          "holder": (held.holder or {}).get("worker_id")})
            continue
        tried.append({"bot": bot, "task_id": task_id, "result": "claimed"})
        return result, tried
    return None, tried


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lane", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--bots", default=",".join(DEFAULT_BOTS),
                        help="comma-separated candidate runtimes, tried in order")
    parser.add_argument("--repo-root", default=None,
                        help="git clone to read lead direction from (default: this checkout)")
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--skip-fetch", action="store_true",
                        help="do not contact the remote; read the last known canonical ref")
    parser.add_argument("--allow-deterministic", action="store_true",
                        help="diagnostics only: permit a non-adaptive provider")
    parser.add_argument("--post-issue", action="store_true",
                        help="best-effort Issue #3 visibility via gh, never required")
    parser.add_argument("--home", default=None, help="runtime data root (else SBOTS_HOME)")
    parser.add_argument("--report-root", default=None,
                        help="override the social-bots root for worker-reports")
    args = parser.parse_args(argv)

    bots = [b.strip() for b in args.bots.split(",") if b.strip()]
    session_id = args.session_id or sh.new_session_id()
    repo_root = Path(args.repo_root) if args.repo_root else \
        Path(__file__).resolve().parent.parent.parent

    inv = invocation_mod.start(session_id=session_id, lane=args.lane,
                               branch=args.branch, home=args.home)

    # (1) Direction first, so the heartbeat can attest the SHA this session read.
    try:
        lead = direction_mod.consume(args.lane, repo_root, fetch=not args.skip_fetch)
    except direction_mod.DirectionError as exc:
        inv.update(claim_outcome=invocation_mod.CLAIM_ERROR,
                   work_outcome="direction_unavailable")
        inv.close(exit_code=EXIT_FAILURE, error=f"DirectionError: {exc}")
        print(f"DIRECTION ERROR: {exc}", file=sys.stderr)
        return EXIT_FAILURE

    inv.update(direction_id=lead.direction_id, direction_source=lead.source,
               canonical_sha=lead.canonical_sha)

    # (2) Exactly one durable SESSION_ONCE heartbeat for this invocation.
    heartbeat = sh.SessionHeartbeat(
        session_id=session_id, lane=args.lane, branch=args.branch,
        current_artifact=lead.assignment or "scheduled bounded worker session",
        canonical_seen_sha=lead.canonical_sha, lead_review_seen=lead.direction_id,
        blocker=("lane halted by lead direction" if lead.halt else None),
        notes=(f"invocation={inv.receipt.invocation_id} scheduler="
               f"{inv.receipt.scheduler} direction_source={lead.source} "
               f"fetch_ok={lead.fetch_ok}"))
    if args.post_issue:
        posted, reason = sh.post_issue_comment(heartbeat.to_record())
        heartbeat.issue_comment_posted = posted
        heartbeat.issue_comment_skipped_reason = reason
    else:
        heartbeat.issue_comment_skipped_reason = "not requested"
    try:
        sh.emit(heartbeat, root=args.report_root)
        inv.update(heartbeat_emitted=True)
    except sh.DuplicateSessionHeartbeat as exc:
        # A session id must be unique per invocation; reusing one would forge a
        # second heartbeat for one session. Refuse rather than write it.
        inv.update(claim_outcome=invocation_mod.CLAIM_ERROR,
                   work_outcome="duplicate_session_heartbeat")
        inv.close(exit_code=EXIT_FAILURE, error=str(exc))
        print(f"DUPLICATE HEARTBEAT: {exc}", file=sys.stderr)
        return EXIT_FAILURE

    # (3) Acknowledge what was consumed, so the lead can see it from the repo.
    direction_mod.acknowledge(lead, session_id=session_id,
                              invocation_id=inv.receipt.invocation_id,
                              root=args.report_root)

    # (4) Halt is a legitimate, non-failure outcome: the session ran and was told
    # to stand down. It still leaves a heartbeat and a receipt.
    if lead.halt:
        inv.update(claim_outcome=invocation_mod.CLAIM_HALTED,
                   work_outcome="halted_by_direction")
        record = inv.close(exit_code=EXIT_HALTED)
        print(json.dumps({"session_id": session_id,
                          "invocation_id": record["invocation_id"],
                          "claim_outcome": record["claim_outcome"],
                          "direction_id": lead.direction_id,
                          "exit_code": EXIT_HALTED}, indent=2))
        return EXIT_HALTED

    if not bots:
        inv.update(claim_outcome=invocation_mod.CLAIM_NONE_AVAILABLE,
                   work_outcome="no_candidate_tasks")
        inv.close(exit_code=EXIT_NO_OVERLAP)
        print("NO CANDIDATE TASKS configured", file=sys.stderr)
        return EXIT_NO_OVERLAP

    # (5) Claim at most one task and run its bounded unit.
    require_adaptive = None if _allow_deterministic(args.allow_deterministic) else True
    try:
        result, tried = claim_one(bots, require_adaptive=require_adaptive)
    except Exception as exc:                       # noqa: BLE001 - record, then fail
        inv.update(claim_outcome=invocation_mod.CLAIM_ERROR, work_outcome="unit_failed",
                   candidates_tried=[])
        inv.close(exit_code=EXIT_FAILURE, error=f"{type(exc).__name__}: {exc}"[:300])
        print(f"FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_FAILURE

    inv.update(candidates_tried=tried)

    if result is None:
        inv.update(claim_outcome=invocation_mod.CLAIM_NO_OVERLAP,
                   work_outcome="no_overlap_all_tasks_held")
        record = inv.close(exit_code=EXIT_NO_OVERLAP)
        print(json.dumps({"session_id": session_id,
                          "invocation_id": record["invocation_id"],
                          "claim_outcome": record["claim_outcome"],
                          "candidates_tried": tried,
                          "exit_code": EXIT_NO_OVERLAP}, indent=2))
        return EXIT_NO_OVERLAP

    summary = {k: result.get(k) for k in (
        "worker_id", "task_id", "bot", "persona", "lease_id", "chosen_action",
        "outcome", "withheld", "verified", "lease_released", "start_receipt",
        "finish_receipt")}
    inv.update(claim_outcome=invocation_mod.CLAIM_CLAIMED,
               claimed_task=result.get("task_id"), claimed_bot=result.get("bot"),
               work_outcome=result.get("outcome"), work_summary=summary)
    record = inv.close(exit_code=EXIT_OK)
    print(json.dumps({"session_id": session_id,
                      "invocation_id": record["invocation_id"],
                      "claim_outcome": record["claim_outcome"],
                      "claimed_task": record["claimed_task"],
                      "work_outcome": record["work_outcome"],
                      "heartbeat_emitted": record["heartbeat_emitted"],
                      "live_model_call": record["live_model_call"],
                      "exit_code": EXIT_OK}, indent=2))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
