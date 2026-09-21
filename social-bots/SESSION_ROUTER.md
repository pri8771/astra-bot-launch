# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current operating mode: FAST TRACK.
Current lead review: LEAD-026.

Read:
- `FAST_TRACK_EXECUTION.md`
- `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `lead-reviews/LEAD-026_2026-09-21T0252.md`

Heartbeat is observability only. It does not block implementation or the real V0.4 canary.

## Lane A — Windows Core / V0.3 closure
Branch: `claude/social-bots-windows-core-host`
Status: ACTIVE / FINAL NARROW REPAIR REQUIRED.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Latest worker source/evidence:
- `f73c337...` — V03-005 queue/analytics whole-runtime readers renamed to explicit admin surfaces; 129 worker-reported tests;
- `65c720b...` — V03-006 regenerated from `f73c337...` with exact committed full-suite output: 129 tests, OK;
- `b4c2e73...` — signed quiet-hold heartbeat awaiting lead audit.

LEAD-026 independent findings:
1. `SB-V03-004`: source repair remains positive; keep it unchanged unless independent QA finds a concrete defect. Final acceptance is pending independent execution required by the artifact packet.
2. `SB-V03-005`: queue/analytics raw-reader repair is good, but `RuntimeState.content_history()` remains an ordinary publicly named whole-runtime reader. A docstring saying ADMIN is not a structural boundary. The new bypass regression only asserts the removed `publish_queue` / `events_for` names.
3. Narrow repair: make `RuntimeState.content_history()` explicitly admin/internal or remove it in favor of `isolation.admin_all_records`; expand the structural bypass test across all persona-private raw-reader surfaces.
4. Regenerate `SB-V03-006` one final time from the final implementation SHA, preserving exact test output/count evidence.
5. Then reconcile V03-001/EVD-001 and V04 dependency readiness.

Do not defer source work for heartbeat testing.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE / IMPLEMENTATION STALLED.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Heartbeat seq7 does not complete bootstrap: seq5→6 is ~16m37s but seq6→7 is ~30m28s. `steady_hourly_authorized=false` remains authoritative. Do not backfill.

Next:
1. `SB-V05-001` real HTTPS pinned-IP/SNI/cert path + production-constructor regression **now**;
2. `SB-V15-001` persona-scoped production experiment read/write boundary;
3. preserve V16/V17/V20-002 for later lead audit.

Heartbeat runs in the background and does not block work.

## Lane C — Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`
Status: ACTIVE / HOURLY AUTHORIZED / WORKER STALE.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

No independent Core verification report has landed since the last review.

Immediate assignment:
1. resume hourly coordination heartbeat;
2. independently execute/probe current Core `f73c337...`, especially the V03-004 post-cycle finish-receipt takeover scenario;
3. independently inspect/probe the complete V03-005 raw-reader boundary, including `RuntimeState.content_history()` and any equivalent ordinary whole-runtime surface;
4. report exact commands/results/files/symbols without editing Core runtime source;
5. then continue CI/control, artifact validation and V2 acceptance/integration harness.

Heartbeat proves coordination only, not V0.7 runtime liveness.

## Lane D — Mac LOCAL real V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: PRIORITY ZERO / READY / NO WORKER EXECUTION VISIBLE.

Execute `SB-V04-005` immediately on an actual local host with working Claude Code subscription authentication:
- heartbeat validation is not a prerequisite;
- real current public source + actual existing-subscription Claude Code invocation;
- no fixture/injected runner/prewritten proposal/API PAYG;
- validate schema + deterministic policy;
- persist decision;
- zero public effect;
- push evidence and stop for lead audit.

Owner authorization already exists for one bounded existing-subscription call at zero additional spend.

## Lane E — worker-pc / optional independent remote worker
Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1 protocol task.
Project authority remains in this repository.

Current status:
- Social Bots retry `socialbots-v03-repair-audit-20260921-01` reached the worker but failed before source/tests with `Repository clone failed`;
- failed result counts as zero Social Bots acceptance evidence;
- private-repo controls must remain intact.

Do not re-dispatch Social Bots until clone/auth access to `pri8771/astra-bot-launch` is actually fixed. Repeating the known-failing clone is not useful work. Mac QA owns current independent V0.3 execution so project progress does not wait on this resource.

## Lead
ChatGPT audits checkpoints, updates canonical artifact/state evidence, assigns next work, and prepares integration/V2 runway.

## Version truth
Official version remains `V0.3.x` and artifact/evidence-gated.
Heartbeat success is not a product-version gate.
V0.4 cannot complete without all V0.4 manifest artifacts, including real `SB-V04-005` + independent `SB-EVD-002`.

## Safety
No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake evidence, engagement manipulation or SwarmAI dependency.
