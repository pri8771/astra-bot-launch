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

``--post-issue`` adds best-effort Issue visibility through ``gh``. A missing or
unauthenticated ``gh`` is recorded as a skip reason and never fails this command:
GitHub transport must not gate durable evidence or useful work.

Exit codes:
    0  heartbeat emitted
    4  this session_id already emitted a heartbeat (duplicate refused)
    2  bad usage
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
    # Post BEFORE the durable write only in the sense of computing the flag: the
    # record must state truthfully whether a comment was actually posted, so the
    # best-effort attempt runs first and its real outcome is embedded.
    if args.post_issue:
        posted, reason = sh.post_issue_comment(hb.to_record(), issue=args.issue,
                                               repo=args.repo)
        hb.issue_comment_posted = posted
        hb.issue_comment_skipped_reason = reason
    else:
        hb.issue_comment_skipped_reason = "not requested"

    try:
        record = sh.emit(hb, root=args.root)
    except sh.DuplicateSessionHeartbeat as exc:
        print(f"DUPLICATE: {exc}", file=sys.stderr)
        return 4

    print(json.dumps({
        "session_id": record["session_id"],
        "lane": record["lane"],
        "cadence_mode": record["cadence_mode"],
        "session_status": record["session_status"],
        "started_at": record["started_at"],
        "issue_comment_posted": record["issue_comment_posted"],
        "issue_comment_skipped_reason": record["issue_comment_skipped_reason"],
        "log": str(sh.lane_dir(record["lane"], args.root) / sh.LOG_FILENAME),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
