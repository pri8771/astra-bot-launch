# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current lead review: LEAD-020.

## Current heartbeat validation phase

Owner has chosen to validate **two Mac-target worker sessions first** before starting/resuming Windows. Do not infer actual Mac-host execution from the lane name alone; host evidence must prove it.

Active heartbeat-test lanes:
1. Intelligence / Evidence — `claude/social-bots-intelligence-repair-v2`
2. Mac QA / Integration Control — `claude/social-bots-mac-qa-control`

Windows Core / Host is **STANDBY** for this validation phase. Do not assign new Windows work until the owner/lead explicitly reactivates it.

The goal is to observe three genuine approximately-15-minute worker heartbeat intervals on each active target lane. Do not authorize hourly cadence until the lane's durable heartbeat history proves that sequence and the lead acknowledges it.

Current truth at LEAD-020:
- Intelligence: bootstrap **NOT PASSED**. `HEARTBEAT_LOG.jsonl` contains only lead-seeded seq0; the sequence-4 snapshot is not durable history.
- Mac QA: bootstrap **NOT PASSED**. Seq1-4 are burst updates minutes apart, not three consecutive ~15-minute intervals.
- `steady_hourly_authorized=false` for both lanes.
- No backfilled/synthetic heartbeat history is allowed.

## Session A — Intelligence / Evidence

Branch: `claude/social-bots-intelligence-repair-v2`
Instruction: `social-bots/SESSION_INSTRUCTIONS.md` on that branch.
Heartbeat test: ACTIVE / NOT YET PASSED.

Verified source head: `feb30f4c3fd00ae1fa0bb115a92bdb767ae9f67d`.

Current implementation next:
1. repair `SB-V05-001` pinned-IP HTTPS/SNI/certificate execution defect and exercise the production connection-construction path in a regression;
2. repair `SB-V15-001` authoritative persona-scoped experiment readers/writers;
3. continue real prospective heartbeat entries at bootstrap cadence;
4. hold additional higher-version expansion until pending V16/V17/V20-002 lead audits are reconciled.

Lead-accepted this review:
- `SB-V13-001`
- `SB-V14-001`

Do not edit Core-owned state/decision/reasoning/leasing/worker.

## Session B — Mac QA / Integration Control

Branch: `claude/social-bots-mac-qa-control`
Instruction: `social-bots/SESSION_INSTRUCTIONS.md` on that branch.
Heartbeat test: ACTIVE / NOT YET PASSED.

Verified source head: `ede387e256be19d6aaaf1e6c96151d7218221d33`.

Lead-accepted control artifacts:
- `SB-CTL-012` artifact graph validator/readiness reporter;
- `SB-CTL-006` GitHub CI/control; hosted run `35555060783` succeeded.

The V2 acceptance harness is prep only and does not promote `SB-V20-099`.

**Priority Zero handoff after heartbeat validation:**
- remain on this branch until 3 verified real ~15-minute worker heartbeat intervals exist;
- lead must explicitly acknowledge them and set hourly cadence authorization;
- then switch to dedicated branch `claude/social-bots-v04-live-canary`;
- execute `SB-V04-005` real adaptive canary before resuming ordinary QA/CI expansion.

Current Mac-QA worker evidence says its execution environment is a Linux container with no usable Claude subscription OAuth route. Therefore the eventual canary must run on an actually authenticated subscription host. Owner permission for one bounded existing-subscription call at zero additional spend is already granted; lack of owner authorization is **not** the blocker.

## Windows Core / Host — STANDBY

Branch: `claude/social-bots-windows-core-host`
Do not continue assigning work during the two-Mac-target heartbeat validation phase.
Preserve existing work/branch state. Reactivate only by explicit lead/owner instruction.

## Priority Zero — V0.4 real canary

Dedicated branch:
`claude/social-bots-v04-live-canary`

Artifact:
`SB-V04-005`

V0.4 cannot be marked complete until:
- one current public source is fetched live;
- URL/timestamp/status/byte length/SHA-256 are captured;
- the actual authenticated Claude Code subscription provider is invoked;
- no fixture/injected model runner/prewritten model output is used;
- schema + deterministic policy run;
- a decision is persisted;
- no public effect occurs;
- ChatGPT independently accepts `SB-EVD-002`.

Authorized:
- one bounded call through the owner's existing Claude Code subscription at zero additional spend.

Not authorized:
- Anthropic API/PAYG billing or key creation;
- public posting/replies/messages;
- purchases/destructive actions.

## Lead

ChatGPT verifies heartbeat history, audits submissions, acknowledges heartbeat sequences, updates assignments, and prepares V2/V2.3/V3 runway.

## Heartbeat acceptance

- Snapshot sequence numbers alone do not count.
- `HEARTBEAT_LOG.jsonl` must contain the actual timestamped worker sequence history.
- Need 3 consecutive approximately-15-minute worker intervals.
- Lead-seeded bootstrap records are not worker-liveness proof.
- Burst artifact-submission heartbeats do not satisfy elapsed-time cadence proof.
- Only after lead acknowledgement may a lane switch to hourly.

## Concurrency

Heartbeat validation phase: 2 active target Claude workers + ChatGPT lead.
Windows remains standby.
Do not start a fourth worker.
