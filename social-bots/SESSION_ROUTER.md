# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current lead review: LEAD-018.

## Current heartbeat validation phase

Owner has chosen to validate **two Mac-hosted sessions first** before starting/resuming Windows.

Active heartbeat-test lanes:
1. Intelligence / Evidence — `claude/social-bots-intelligence-repair-v2`
2. Mac QA / Integration Control — `claude/social-bots-mac-qa-control`

Windows Core / Host is **STANDBY** for this validation phase. Do not assign new Windows work until the owner/lead explicitly reactivates it.

The goal is to observe three genuine ~15-minute worker heartbeat intervals on each active Mac lane. Do not authorize hourly cadence until the lane's durable heartbeat history proves that sequence and the lead acknowledges it.

## Session A — Intelligence / Evidence
Branch: `claude/social-bots-intelligence-repair-v2`
Instruction: `social-bots/SESSION_INSTRUCTIONS.md` on that branch.
Heartbeat test: ACTIVE.
Current implementation next remains V05 trust-boundary cleanup, then V13/V14/V15/V16/V17/V20-002.

## Session B — Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`
Instruction: `social-bots/SESSION_INSTRUCTIONS.md` on that branch.
Heartbeat test: ACTIVE.

**Priority Zero handoff after heartbeat validation:**
- once this lane has 3 verified ~15-minute heartbeat intervals and lead acknowledgement, pause ordinary QA work;
- switch to dedicated branch `claude/social-bots-v04-live-canary`;
- execute `SB-V04-005` real adaptive canary before resuming later QA/CI work.

SB-CTL-012 / SB-CTL-006 remain queued behind the real V0.4 canary unless the lead explicitly parallelizes them with another Mac session.

## Windows Core / Host — STANDBY
Branch: `claude/social-bots-windows-core-host`
Do not continue assigning work during the two-Mac heartbeat validation phase.
Preserve existing work/branch state. Reactivate only by explicit lead/owner instruction.

## Priority Zero — V0.4 real canary

Dedicated branch:
`claude/social-bots-v04-live-canary`

Artifact:
`SB-V04-005`

V0.4 cannot be marked complete until:
- one current public source is fetched live;
- the actual authenticated Claude Code subscription provider is invoked;
- no fixture/injected model runner is used;
- schema + deterministic policy run;
- a decision is persisted;
- no public effect occurs;
- ChatGPT independently accepts SB-EVD-002.

## Lead
ChatGPT verifies heartbeat history, audits submissions, acknowledges heartbeat sequences, updates assignments, and prepares V2/V2.3/V3 runway.

## Heartbeat acceptance
- Snapshot sequence numbers alone do not count.
- HEARTBEAT_LOG.jsonl must contain the actual timestamped sequence history.
- Need 3 consecutive approximately-15-minute worker intervals.
- Only after lead acknowledgement may a lane switch to hourly.

## Concurrency
Heartbeat validation phase: 2 active Claude workers + ChatGPT lead.
Windows remains standby.
