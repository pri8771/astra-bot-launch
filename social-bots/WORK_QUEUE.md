# Work queue — FAST TRACK

Canonical execution plan: `FAST_TRACK_EXECUTION.md`.
Current lead review: `lead-reviews/LEAD-026_2026-09-21T0252.md`.

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
Status: ACTIVE / FINAL NARROW V0.3 REPAIR REQUIRED.

New worker progress after LEAD-025:
- `f73c337...` structurally renamed queue/analytics whole-runtime readers to explicit `admin_*` surfaces and added production-path bypass regressions; signed Claude commit.
- `65c720b...` regenerated `SB-V03-006` from `f73c337...` and committed exact full-suite output: **129 tests, OK**.
- current signed worker heartbeat head is `b4c2e73...`, awaiting lead audit.

LEAD-026 disposition:

1. **SB-V03-004 — CHANGES_REQUIRED / source repair remains positive:** no new source defect found in the finish-receipt/migration fencing repair. Final acceptance is still held because the packet explicitly requires independent execution and neither Mac QA nor worker-pc has executed the repaired branch.
2. **SB-V03-005 — CHANGES_REQUIRED:** the queue and analytics raw-reader repair is correct, but `RuntimeState.content_history()` is still an ordinary publicly named whole-runtime reader. A docstring saying ADMIN does not satisfy the packet's structural admin/internal boundary. The new bypass regression only guards the old `publish_queue` and `events_for` names, so it missed this surface.
3. Required narrow repair: make `RuntimeState.content_history()` explicitly admin/internal or remove it in favor of `isolation.admin_all_records`; expand the structural bypass test across all six persona-private store surfaces / sanctioned raw readers.
4. **SB-V03-006 — BLOCKED / PREPARED:** the prior exact-output evidence gap is fixed. `65c720b...` contains verbatim `FULL_SUITE_OUTPUT.txt` with `Ran 129 tests ... OK`, but the bundle must be regenerated from the final post-V03-005 SHA and cannot be accepted until predecessors are accepted.
5. Then reconcile `SB-V03-001`/`SB-EVD-001` and the V0.4 dependency chain.

Do not defer implementation for heartbeat work.

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
2. independently execute/probe current Core implementation `f73c337...`, especially the V03-004 post-cycle success-receipt takeover regression;
3. independently inspect/probe the full V03-005 raw-reader boundary, including `RuntimeState.content_history()`, and distinguish persona-facing vs explicit admin/runtime-wide access;
4. report exact commands/results/files/symbols without editing Core source;
5. then continue CI/control, artifact validation, V2 acceptance/integration harness and merge/test checklist.

## Lane D — local authenticated V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: READY / NOT STARTED in repository evidence.

No worker-generated canary evidence exists. Execute `SB-V04-005` on an actual authenticated local Claude Code subscription host now, or submit a truthful authentication/host blocker. Heartbeat is not a prerequisite.

## Additional remote-worker capacity

Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1.

Social Bots task `socialbots-v03-repair-audit-20260921-01` reached `worker-pc` but **FAILED before audit** with `Repository clone failed`. No tests ran and it contributes no artifact evidence.

Do not re-dispatch another Social Bots task until clone/auth access to `pri8771/astra-bot-launch` is demonstrably fixed. Do not weaken private-repository controls and do not move project governance into `remote-workers`.

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
