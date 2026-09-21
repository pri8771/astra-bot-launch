# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current operating mode: FAST TRACK.
Current lead review: LEAD-034.

Read:
- `FAST_TRACK_EXECUTION.md`
- `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `lead-reviews/LEAD-034_2026-09-21T1055.md`

Heartbeat is observability only. It does not block implementation or the real V0.4 canary.

## Today's heartbeat soak — all four Claude lanes

Fresh sessions must run:
1. `FAST_5M`: T0, +~5m, +~10m, +~15m — three real consecutive intervals.
2. `SOAK_15M_24H`: immediately afterward, every 15 minutes for 24 hours (target 96 intervals).

No synthetic/backfilled timestamps. Engineering/review/canary work continues in parallel.

**LEAD-034 truth:** no active lane has yet pushed a durable `FAST_5M` T0. Historical heartbeat entries do not count toward today's soak.

## Lane A — Windows Core
Branch: `claude/social-bots-windows-core-host`
Status: ACTIVE / V0.3 SOURCE STABLE / SB-V04-004 REPAIR / TODAY SOAK NOT STARTED.

Verified final V0.3 source/evidence:
- `796d4e390bd135167e5de2ff8f586bc07ac7f370` — final V03 implementation;
- `436787b0a63fdae0e89c224a54054607e32b5187` — final prepared V03 evidence; exact 130-test OK output;
- `SB-V03-005` ACCEPTED.

Latest worker-generated Core implementation evidence remains `76e96dde4677346fd5b40c8cba4988f6e4c64fee`. Newer branch commits are lead-only soak/instruction updates.

Next: complete only `SB-V04-004` repair: true persona-only/evidence-only isolation, keep contextual `adaptive=false` tests as diagnostics, and add a clean seam for the real adaptive canary receipt. Do not execute `SB-V04-005` from Core.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE ASSIGNMENT / WORKER STALLED / TODAY SOAK NOT STARTED.

Durable history still ends at seq7 `04:10:36Z`. Seq5→6 is ~16m37s; seq6→7 is ~30m28s, so historical hourly authorization remains false. No `FAST_5M` entry exists yet.

Next:
1. `SB-V05-001` real pinned-IP HTTPS/TLS/SNI/certificate path + production-constructor regression.
2. `SB-V15-001` persona-scoped production experiment persistence/read/list boundary.
3. Preserve V16/V17/V20-002 for later audit.

Heartbeat remains background-only.

## Lane C — Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`
Status: ACTIVE / HISTORICAL HOURLY AUTHORIZATION / WORKER STALE / V0.3 GATING EXECUTOR / TODAY SOAK NOT STARTED.

Historical bootstrap seq7→8→9 remains accepted coordination evidence, but today's temporary soak is a separate measurement and has no `FAST_5M` T0 yet.

Immediate assignment:
1. independently execute current Core `796d4e3...` V03-004 lifecycle regressions: post-cycle takeover success-receipt rejection, active-cycle lease-loss old-owner commit rejection, staged migration fencing;
2. report exact commands/results and ACCEPT-READY or a concrete defect; no Core source edits;
3. continue CI/control, artifact validation and V2 acceptance/integration harness;
4. run today's heartbeat soak in parallel.

## Lane D — local real V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: PRIORITY ZERO / READY / NO WORKER EXECUTION / NO DURABLE HEARTBEAT LOG.

Execute `SB-V04-005` now on an actual local Claude Code subscription-authenticated host. Heartbeat is not a prerequisite.

Required: real current public source, live retrieval/hash/timestamp/status/byte length, actual existing-subscription Claude CLI invocation, no fixture/injected runner/prewritten proposal/API PAYG, proposal schema validation, deterministic policy, persisted local decision, zero public effect. If subscription auth is unavailable, submit a truthful BLOCKED report.

## Lane E — worker-pc independent verification
Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1.

LEAD-034 retried the independent V03 lifecycle audit after unrelated capacity cleared. Actions run `35615370153` reached the real Windows worker but failed again before Claude/tests with `Repository clone failed.` Result: `socialbots-v03-audit-retry-20260921-1052`.

This contributes zero Social Bots acceptance evidence. Do not dispatch another Social Bots task until private-repo clone/auth access to `pri8771/astra-bot-launch` is demonstrably repaired. Never weaken the private-repository safety boundary.

## Lead

ChatGPT audits artifacts/evidence, owns canonical reconciliation/acceptance, and keeps dependency-safe work stocked.

## Version truth

Official version remains **V0.3.x**. V0.3 still requires independent acceptance of `SB-V03-004` plus final V03-001/V03-006/SB-EVD-001 reconciliation. V0.4 additionally requires corrected adaptive divergence evidence, real `SB-V04-005`, and independent `SB-EVD-002`.

## Safety

No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake operational evidence, engagement manipulation, or SwarmAI dependency.
