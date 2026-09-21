#!/usr/bin/env python3
"""Social Bots human-readable heartbeat reporter.

Posts a concise progress comment to GitHub Issue #3 on a real clock:
- T0, +5m, +10m, +15m (3 successful 5-minute intervals)
- then every 15m for 24 hours.

It does not modify source, commit, merge, deploy, publish, or spend.
Requires an already-authenticated GitHub CLI (gh).
"""

from __future__ import annotations
import argparse, datetime as dt, pathlib, shutil, subprocess, sys, time

REPO = "pri8771/astra-bot-launch"
ISSUE = "3"

def utcnow():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)

def read_progress(path: pathlib.Path) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "working; progress file not updated yet"
    if not text:
        return "working; progress file empty"
    line = " ".join(text.split())
    return line[:700]

def git_value(args):
    p = subprocess.run(["git", *args], text=True, capture_output=True)
    return p.stdout.strip() if p.returncode == 0 else "unknown"

def post(lane, phase, n, progress_path, start, expected_interval):
    now = utcnow()
    branch = git_value(["branch", "--show-current"])
    head = git_value(["rev-parse", "--short", "HEAD"])
    progress = read_progress(progress_path)
    elapsed = int((now - start).total_seconds())
    body = (
        f"[{lane}] heartbeat | {phase} #{n} | {now.isoformat()} | "
        f"branch={branch} head={head} | elapsed={elapsed}s | "
        f"target_interval={expected_interval}s | {progress}"
    )
    p = subprocess.run(
        ["gh", "issue", "comment", ISSUE, "--repo", REPO, "--body", body],
        text=True, capture_output=True,
    )
    if p.returncode != 0:
        print(f"heartbeat post failed: {p.stderr.strip()}", file=sys.stderr, flush=True)
        return False
    print(body, flush=True)
    return True

def sleep_until(target):
    while True:
        remaining = (target - utcnow()).total_seconds()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 5))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--progress-file", required=True)
    ap.add_argument("--stage1-seconds", type=int, default=300)
    ap.add_argument("--stage2-seconds", type=int, default=900)
    ap.add_argument("--stage2-hours", type=float, default=24.0)
    args = ap.parse_args()

    if not shutil.which("gh"):
        raise SystemExit("gh CLI is required for live Issue #3 heartbeat updates")
    auth = subprocess.run(["gh", "auth", "status"], text=True, capture_output=True)
    if auth.returncode != 0:
        raise SystemExit("gh CLI is not authenticated; cannot post heartbeat updates")

    progress_path = pathlib.Path(args.progress_file)
    start = utcnow()

    # T0 plus three real five-minute intervals.
    post(args.lane, "FAST_5M", 0, progress_path, start, 0)
    target = start
    for i in range(1, 4):
        target += dt.timedelta(seconds=args.stage1_seconds)
        sleep_until(target)
        post(args.lane, "FAST_5M", i, progress_path, start, args.stage1_seconds)

    soak_start = utcnow()
    soak_end = soak_start + dt.timedelta(hours=args.stage2_hours)
    n = 0
    target = soak_start
    while True:
        target += dt.timedelta(seconds=args.stage2_seconds)
        if target > soak_end:
            break
        sleep_until(target)
        n += 1
        post(args.lane, "SOAK_15M_24H", n, progress_path, soak_start, args.stage2_seconds)

    post(args.lane, "SOAK_COMPLETE", n, progress_path, soak_start, args.stage2_seconds)

if __name__ == "__main__":
    main()
