# Work queue — FAST TRACK

Canonical execution plan: `FAST_TRACK_EXECUTION.md`.
Current lead review: `lead-reviews/LEAD-034_2026-09-21T1055.md`.

## Priority Zero — real V0.4 canary

Artifact: `SB-V04-005`
Branch: `claude/social-bots-v04-live-canary`

**Status: READY but still no Claude worker execution is visible.**

Execute immediately from an actually authenticated local Claude Code subscription host. Heartbeat is not a prerequisite.

Required proof:
- one real current public source;
- live retrieval timestamp/status/byte length/SHA-256;
- actual existing-subscription Claude Code invocation;
- no fixture/injected runner/prewritten proposal;
- no Anthropic API/PAYG/new spend;
- proposal schema validation;
- deterministic policy;
- persisted local decision;
- zero public effect.

After submission, ChatGPT audits `SB-V04-005` and, if accepted, performs `SB-EVD-002`.

## Today's heartbeat soak

All four active Claude lanes must start prospectively with `FAST_5M` T0/+5/+10/+15, then switch to `SOAK_15M_24H` every 15 minutes for 24 hours. No backfill. Work continues in parallel.

**LEAD-034 evidence:** no lane has yet pushed a durable `FAST_5M` T0. Core/Intelligence/Mac-QA logs still end in their prior heartbeat modes; the canary lane has no `HEARTBEAT_LOG.jsonl` at all.

## Lane A — Windows Core
Branch: `claude/social-bots-windows-core-host`
Status: ACTIVE / V0.3 SOURCE STABLE / V04-004 REPAIR ASSIGNED / TODAY SOAK NOT STARTED.

Verified baseline remains:
- final V03 implementation `796d4e390bd135167e5de2ff8f586bc07ac7f370`;
- final prepared V03 evidence `436787b0a63fdae0e89c224a54054607e32b5187`, exact 130 tests OK;
- `SB-V03-005` accepted;
- latest worker-generated V04 attempt `76e96dde4677346fd5b40c8cba4988f6e4c64fee` remains `SB-V04-004` CHANGES_REQUIRED because the acceptance comparisons are confounded and use `adaptive=false` contextual reasoning.

Next:
- repair only `SB-V04-004` variable isolation and adaptive-receipt seam;
- preserve V03;
- do not execute the real live canary from Core.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE ASSIGNMENT / WORKER STALLED / TODAY SOAK NOT STARTED.

No worker source/heartbeat commit has appeared after seq7 at `04:10:36Z`. Seq5→6 is ~16m37s; seq6→7 is ~30m28s, so historical hourly authorization remains false.

Next:
1. **SB-V05-001 now** — valid pinned-IP HTTPS TLS/SNI/certificate execution plus production-constructor regression.
2. **SB-V15-001 next** — authoritative bot+persona experiment save/load/list/read boundary and mixed-persona regressions.
3. Preserve V16/V17/V20-002 for fresh lead audit after those repairs.

Heartbeat is background-only.

## Lane C — Mac QA / Integration
Branch: `claude/social-bots-mac-qa-control`
Status: HISTORICAL HOURLY AUTHORIZED / WORKER STALE / V0.3 GATING EXECUTOR / TODAY SOAK NOT STARTED.

Last durable worker heartbeat remains seq10 at `03:57:57Z`; no independent Core report has landed. Historical seq7→8→9 coordination proof remains valid, but today's temporary soak is separate and has not started.

Immediate assignment:
1. independently execute current final V03 implementation `796d4e3...`, especially post-cycle takeover/finish-receipt fencing, active-cycle lease-loss old-owner commit rejection, and staged migration fencing;
2. report exact commands/results, implementation SHA, host/filesystem scope and ACCEPT-READY or a reproducible defect;
3. do not edit Core runtime source;
4. continue CI/control, artifact validation, V2 acceptance/integration harness and merge/test checklist;
5. run today's soak in parallel.

## Lane D — local authenticated V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: READY / NOT STARTED in repository evidence / NO DURABLE HEARTBEAT LOG.

Execute `SB-V04-005` on an actual authenticated local Claude Code subscription host now, or submit a truthful authentication/host blocker. Heartbeat is not a prerequisite.

## External worker capacity

Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1.

After unrelated capacity cleared, LEAD-034 dispatched `socialbots-v03-audit-retry-20260921-1052` as a read-only independent lifecycle audit. Actions run `35615370153` reached `worker-pc` and failed before Claude/tests with **`Repository clone failed.`** No Social Bots evidence was produced.

This repeats the known private-repository clone/auth failure. Do not dispatch another Social Bots task until access to `pri8771/astra-bot-launch` is demonstrably repaired. Do not weaken private-repository controls or move project governance into `remote-workers`.

## Current official version

**V0.3.x**.

V0.3 cannot close until `SB-V03-004` receives packet-required independent execution/acceptance and the lead reconciles `SB-V03-001`, `SB-V03-006`, and `SB-EVD-001` against the final accepted chain.

V0.4 additionally requires all manifest artifacts including corrected adaptive divergence evidence, real `SB-V04-005`, and independent `SB-EVD-002`. Later-version scaffolding does not advance the official product version.

## Authority

No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake operational evidence, engagement manipulation, or SwarmAI dependency.
