#!/usr/bin/env python3
"""Emit the ONE durable SESSION_ONCE heartbeat for this worker session.

Owner policy (LEAD-038): one fresh worker session = one heartbeat. Run this once,
after syncing and reading current coordination, then work normally. There is no
loop, no soak and no daemon.

Usage:
    python3 bin/session_heartbeat.py \
        --lane windows-core \
        --branch claude/social-bots-windows-core-host \
        --artifact "SB-V07-001 host worker packaging" \
        --canonical-sha 671abbc --lead-review LEAD-038 \
        [--session-id s-...] [--head-sha <sha>] [--blocker "..."] \
        [--notes "..."] [--post-issue] [--issue 3] [--repo owner/name]

Durable evidence is written FIRST and needs no network:
    social-bots/worker-reports/<lane>/HEARTBEAT_LOG.jsonl   (append-only history)
    social-bots/worker-reports/<lane>/HEARTBEAT.json        (latest record)

``--post-issue`` adds best-effort Issue visibility through ``gh``, attempted only
AFTER the durable write succeeds, with its outcome logged to
``HEARTBEAT_ISSUE_POSTS.jsonl`` beside the ledger. A missing or unauthenticated
``gh`` is recorded as a skip reason and never fails this command: GitHub
transport must not gate durable evidence or useful work, and a comment is never
posted for a heartbeat that was not written.

Exit codes:
    0  heartbeat emitted
    4  this session_id already emitted a heartbeat (duplicate refused)
    2  bad usage (including an unsafe lane name)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import session_heartbeat as sh  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lane", required=True,
                   help="worker lane, e.g. windows-core / intelligence / mac-qa")
    p.add_argument("--branch", required=True, help="branch this session works on")
    p.add_argument("--artifact", required=True,
                   help="current artifact or assignment this session begins")
    p.add_argument("--session-id", default=None,
                   help="session id (default: freshly generated)")
    p.add_argument("--canonical-sha", default=None,
                   help="canonical coordination-branch SHA this session read")
    p.add_argument("--lead-review", default=None,
                   help="latest lead review this session read, e.g. LEAD-038")
    p.add_argument("--head-sha", default=None, help="worker branch HEAD at session start")
    p.add_argument("--blocker", default=None, help="current hard blocker, if any")
    p.add_argument("--notes", default="", help="concise session note")
    p.add_argument("--root", default=None,
                   help="override the social-bots root (tests/alt checkouts)")
    p.add_argument("--post-issue", action="store_true",
                   help="also attempt one best-effort Issue visibility comment")
    p.add_argument("--issue", type=int, default=3, help="issue number (default 3)")
    p.add_argument("--repo", default=None, help="owner/name for gh (default: gh's repo)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    hb = sh.SessionHeartbeat(
        session_id=args.session_id or sh.new_session_id(),
        lane=args.lane,
        branch=args.branch,
        current_artifact=args.artifact,
        canonical_seen_sha=args.canonical_sha,
        lead_review_seen=args.lead_review,
        head_sha=args.head_sha,
        blocker=args.blocker,
        notes=args.notes,
    )
    # Durable evidence FIRST, visibility second. Posting first would announce a
    # heartbeat that a refused duplicate then never wrote.
    hb.issue_comment_skipped_reason = (
        "pending: posted after the durable write" if args.post_issue else "not requested")
    try:
        record = sh.emit(hb, root=args.root)
    except sh.DuplicateSessionHeartbeat as exc:
        print(f"DUPLICATE: {exc}", file=sys.stderr)
        return 4
    except sh.UnsafeLane as exc:
        print(f"UNSAFE LANE: {exc}", file=sys.stderr)
        return 2

    post = {"posted": False, "skipped_reason": "not requested"}
    if args.post_issue:
        post = sh.record_issue_post(record, issue=args.issue, repo=args.repo,
                                    root=args.root)

    print(json.dumps({
        "session_id": record["session_id"],
        "lane": record["lane"],
        "cadence_mode": record["cadence_mode"],
        "session_status": record["session_status"],
        "started_at": record["started_at"],
        "issue_comment_posted": post["posted"],
        "issue_comment_skipped_reason": post["skipped_reason"],
        "log": str(sh.lane_dir(record["lane"], args.root) / sh.LOG_FILENAME),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
