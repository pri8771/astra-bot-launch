# Work queue — FAST TRACK

Canonical execution plan: `FAST_TRACK_EXECUTION.md`.
Current lead review: `lead-reviews/LEAD-025_2026-09-21T0158.md`.

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
Status: ACTIVE / NARROW REPAIR REQUIRED.

New worker progress:
- `7e4345b...` repaired post-cycle finish-receipt fencing and added production-path isolation tests; signed Claude commit.
- `b2083b8...` regenerated `SB-V03-006` from `7e4345b...`; worker reports 127 passing tests.

LEAD-025 disposition:

1. **SB-V03-004 — CHANGES_REQUIRED / source repair verified:** the finish/success receipt is now written through `fence.fenced_commit`, and the committed adversarial regression forces takeover before that write and proves no finish receipt is emitted. Do not churn this repair. Independent execution from Mac QA/worker-pc has not succeeded yet, so final acceptance is held.
2. **SB-V03-005 — CHANGES_REQUIRED:** scoped dedup/analytics/facade behavior is improved, and `_reconcile` uses the explicit admin boundary. But ordinary whole-runtime APIs such as `pipeline.publish_queue(bot)`, `analytics.events_for(bot)` and `RuntimeState.content_history()` remain callable as normal functions. Documentation alone does not satisfy the packet's requirement that raw enumeration be structurally admin/internal. Narrowly repair this API boundary and add a regression against accidental persona-facing raw enumeration.
3. **SB-V03-006 — BLOCKED / PREPARED:** regenerated evidence is useful and bound to `7e4345b...`, but predecessors are not all accepted. The committed evidence records `full: OK` without a separate exact full-suite output/count artifact; final regeneration should include exact full-suite evidence.

Then reconcile V04 dependencies. Do not defer implementation for heartbeat work.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE ASSIGNMENT / WORKER STALLED.

No worker source or heartbeat commit has appeared after seq7 at `04:10:36Z`.
Heartbeat truth remains:
- seq5 `03:23:31Z` -> seq6 `03:40:08Z` is a valid ~16m37s interval;
- seq6 -> seq7 `04:10:36Z` is ~30m28s and does not complete bootstrap;
- hourly remains unauthorized.

Next:
1. **SB-V05-001 now** — implement valid pinned-IP HTTPS TLS/SNI/certificate execution plus production-constructor regression.
2. **SB-V15-001 next** — authoritative bot+persona experiment save/load/list/read boundary and mixed-persona regressions.
3. Preserve V16/V17/V20-002 for fresh lead audit after those repairs.

Heartbeat is background-only. Do not wait for cadence proof.

## Lane C — Mac QA / Integration
Branch: `claude/social-bots-mac-qa-control`
Status: HOURLY AUTHORIZED / WORKER STALE.

The last durable worker heartbeat is seq10 at `03:57:57Z`; no independent Core QA report has landed since. Lead-only branch commits do not count as worker liveness.

Immediate QA assignment:
1. resume the authorized hourly coordination heartbeat;
2. independently execute/probe Core implementation `7e4345b...`, specifically the post-cycle success-receipt takeover regression;
3. independently verify the remaining `SB-V03-005` structural raw-reader bypass risk in real persona-facing paths;
4. report exact commands/results/files/symbols;
5. then continue CI/control, artifact validation, V2 acceptance/integration harness and merge/test checklist.

No Core runtime source edits.

## Lane D — local authenticated V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: READY / NOT STARTED in repository evidence.

No worker-generated canary evidence exists. Execute `SB-V04-005` on an actual authenticated local Claude Code subscription host now, or submit a truthful authentication/host blocker. Heartbeat is not a prerequisite.

## Additional remote-worker capacity

Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1.

Second Social Bots task `socialbots-v03-repair-audit-20260921-01` reached `worker-pc` but **FAILED before audit** with `Repository clone failed`. No tests ran and it contributes no artifact evidence.

This progressed farther than the prior task's private-repository precheck failure, but clone/auth access to `pri8771/astra-bot-launch` is still not functional. Do not re-dispatch another Social Bots task until that exact access issue is repaired. Do not weaken private-repository controls and do not move project governance into `remote-workers`.

## Heartbeat truth

- Mac QA: real bootstrap cadence accepted; hourly coordination cadence authorized, but current worker is stale.
- Intelligence: bootstrap remains incomplete; hourly unauthorized and current worker is stale.
- Heartbeat never blocks source work or the live canary.
- Worker heartbeat proves GitHub coordination only, not Social Bots recurring runtime liveness.

## Current official version

**V0.3.x**.

V0.3 cannot close while V03-001/V03-004/V03-005/V03-006/EVD-001 remain unresolved in canonical artifact state.
V0.4 additionally requires all V0.4 manifest artifacts, including the real `SB-V04-005` canary and independent `SB-EVD-002` acceptance.
Later-version scaffolding does not advance the official product version.

## Authority

No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake operational evidence, engagement manipulation or SwarmAI dependency.
