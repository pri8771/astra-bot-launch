# Work queue — FAST TRACK

Canonical execution plan: `FAST_TRACK_EXECUTION.md`.
Current lead review: `lead-reviews/LEAD-024_2026-09-21T0052.md`.

## Priority Zero — real V0.4 canary

Artifact: `SB-V04-005`
Branch: `claude/social-bots-v04-live-canary`

**Status: READY but still no Claude worker execution is visible.**

Start immediately from an actually authenticated local Claude Code subscription host. Heartbeat validation is not a prerequisite.

Required proof remains:
- one real current public source;
- live retrieval timestamp/status/byte length/SHA-256;
- actual existing-subscription Claude Code provider invocation;
- no fixture/injected runner/prewritten proposal;
- no Anthropic API/PAYG/new spend;
- proposal schema validation;
- deterministic policy;
- persisted local decision;
- zero public effect.

After submission, ChatGPT lead audits `SB-V04-005` and, if accepted, performs `SB-EVD-002`.

## Lane A — Windows Core
Branch: `claude/social-bots-windows-core-host`
Status: ACTIVE / REPAIR REQUIRED.

Worker progress since LEAD-023:
- `d1e4bee...` submitted `SB-V03-005` read-boundary work;
- `0433fc85...` prepared a fresh `SB-V03-006` evidence bundle;
- worker reports 122 passing local tests.

Independent LEAD-024 findings keep V0.3 open:

1. **SB-V03-004 — CHANGES_REQUIRED:** migration staging is repaired, but `worker.run_one_unit()` writes its success/finish receipt after `decision.run_cycle()` returns and outside the fence. A worker can stall after cycle commit, expire, lose ownership to a new generation, then resume and emit success-implying finish evidence. Repair and add a forced post-cycle takeover regression.
2. **SB-V03-005 — CHANGES_REQUIRED:** `persona_records()` and generic no-bleed tests are useful, but raw whole-runtime APIs such as `pipeline.publish_queue(bot)` and `analytics.events_for(bot)` remain publicly callable. Enforce the persona boundary in actual production read/list paths or make raw access structurally admin/internal; test real production paths.
3. **SB-V03-006 — BLOCKED / PREPARED:** `0433fc85...` is useful current evidence but predates the required LEAD-024 repairs. Regenerate after V03-004/V03-005 are fixed.

Do not defer implementation for heartbeat work.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE but implementation progress remains stalled.

Heartbeat truth:
- seq5 `03:23:31Z` -> seq6 `03:40:08Z` is a valid ~16m37s interval;
- seq6 -> seq7 `04:10:36Z` is ~30m28s, so seq7 does **not** complete the required approximately-15-minute bootstrap;
- hourly remains unauthorized.

Next:
1. **SB-V05-001 now** — implement valid pinned-IP HTTPS TLS/SNI/certificate execution plus production-constructor regression.
2. **SB-V15-001 next** — authoritative bot+persona experiment save/load/list/read boundary and mixed-persona regressions.
3. Preserve V16/V17/V20-002 for fresh lead audit after those repairs.

Heartbeat remains background-only. Do not spend the session waiting for cadence proof.

## Lane C — Mac QA / Integration
Branch: `claude/social-bots-mac-qa-control`
Status: ACTIVE; hourly coordination heartbeat remains authorized.

No independent Core verification report has landed since LEAD-023.

Immediate QA assignment:
1. independently reproduce/disprove the `SB-V03-004` post-cycle success-receipt-after-takeover defect without editing Core source;
2. independently probe the `SB-V03-005` real production reader bypass risk (`publish_queue`, analytics/history, experiment/read paths, etc.) rather than only the isolation facade;
3. report exact commands/results/files/symbols;
4. then continue CI/control, artifact validation, V2 acceptance/integration harness and merge/test checklist.

Heartbeat is coordination observability only, not V0.7 runtime-liveness proof.

## Lane D — local authenticated V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: READY / NOT STARTED in repository evidence.

The branch still has no worker-generated canary evidence. Start/resume the actual local Claude Code subscription session and execute `SB-V04-005`.

## Additional remote-worker capacity

Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1.

Social Bots task `socialbots-v03-audit-20260920-01` remains **FAILED before repository clone** because the worker-local GitHub credential could not establish visibility/access to the private `pri8771/astra-bot-launch` repository. The failed task contributes no acceptance evidence.

A separate shared-worker run that occupied the slot earlier in this review completed with failure at `04:55:35Z`, so the worker is no longer known to be executing that task. Do **not** re-dispatch Social Bots yet: the Social Bots repository credential/visibility blocker has not been proven fixed, and repeating the same known-failing clone is not useful work.

Required before reuse:
- grant/refresh worker-pc GitHub credential access to `pri8771/astra-bot-launch` without weakening the private-repository guard;
- confirm the protocol slot is idle at dispatch time;
- then assign useful non-overlapping verification/implementation work.

Do not move Social Bots governance into `remote-workers`.

## Heartbeat truth

- Mac QA: real durable cadence accepted; hourly coordination cadence authorized.
- Intelligence: bootstrap claim rejected at seq7 due the ~30.5-minute interval; remain bootstrap.
- Heartbeat never blocks source work or the live canary.
- Worker heartbeat proves GitHub coordination only, not Social Bots recurring runtime liveness.

## Current official version

**V0.3.x**.

V0.3 cannot close while V03-001/V03-004/V03-005/V03-006/EVD-001 remain unresolved in canonical artifact state.
V0.4 additionally requires all V0.4 manifest artifacts, including the real `SB-V04-005` canary and independent `SB-EVD-002` acceptance.
Later-version scaffolding does not advance the official product version.

## Authority

No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake operational evidence, engagement manipulation or SwarmAI dependency.
