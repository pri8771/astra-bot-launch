#!/usr/bin/env python3
"""Branch-local Social Bots heartbeat helper.

This helper performs one heartbeat update. A worker/session or local scheduler
invokes it at the due cadence. It does not daemonize, modify source, or call any
external service directly; git commit/push remains the caller's responsibility.

Cadence:
- BOOTSTRAP_15M until LEAD_ACK authorizes steady hourly.
- HOURLY afterward.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--heartbeat", required=True)
    p.add_argument("--ack", required=True)
    p.add_argument("--lane", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--artifact", default=None)
    p.add_argument("--next-artifact", default=None)
    p.add_argument("--commit-sha", default=None)
    p.add_argument("--canonical-sha", default=None)
    p.add_argument("--instructions-sha", default=None)
    p.add_argument("--lead-message", default=None)
    p.add_argument("--blocker", default=None)
    p.add_argument("--notify", default=None)
    p.add_argument("--notes", default="")
    args = p.parse_args()

    hb_path = Path(args.heartbeat)
    ack_path = Path(args.ack)
    old = read_json(hb_path, {})
    ack = read_json(ack_path, {})

    steady = bool(ack.get("steady_hourly_authorized"))
    cadence = "HOURLY" if steady else "BOOTSTRAP_15M"
    interval = timedelta(hours=1) if steady else timedelta(minutes=15)

    t = now()
    seq = int(old.get("sequence", 0)) + 1
    started = old.get("started_at") or iso(t)
    notify_reason = args.notify
    data = {
        "schema_version": 2,
        "lane": args.lane,
        "branch": args.branch,
        "sequence": seq,
        "cadence_mode": cadence,
        "session_status": args.status,
        "current_artifact": args.artifact,
        "started_at": started,
        "last_updated_at": iso(t),
        "next_due_at": iso(t + interval),
        "last_commit_sha": args.commit_sha,
        "canonical_seen_sha": args.canonical_sha,
        "instructions_seen_sha": args.instructions_sha,
        "lead_message_seen": args.lead_message,
        "next_artifact": args.next_artifact,
        "blocker": args.blocker,
        "notification_pending": bool(notify_reason),
        "notification_reason": notify_reason,
        "notes": args.notes,
    }
    hb_path.parent.mkdir(parents=True, exist_ok=True)
    hb_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "sequence": seq,
        "cadence_mode": cadence,
        "next_due_at": data["next_due_at"],
        "notification_pending": data["notification_pending"],
    }))


if __name__ == "__main__":
    main()
