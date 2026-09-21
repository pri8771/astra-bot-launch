# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current operating mode: FAST TRACK.
Current lead review: LEAD-024.

Read:
- `FAST_TRACK_EXECUTION.md`
- `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `lead-reviews/LEAD-024_2026-09-21T0052.md`

Heartbeat is observability only. It does not block implementation or the real V0.4 canary.

## Lane A — Windows Core / V0.3 closure
Branch: `claude/social-bots-windows-core-host`
Status: ACTIVE / REPAIR REQUIRED.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Latest worker source/evidence:
- `d1e4bee...` — `SB-V03-005` persona-read facade submission;
- `0433fc85...` — `SB-V03-006` regenerated PREPARED evidence, 122 worker-reported tests.

LEAD-024 independent findings:
1. `SB-V03-004`: migration staging is repaired, but `worker.run_one_unit()` emits its success/finish receipt after the fenced decision cycle returns. Repair the post-cycle ownership gap and add a forced takeover regression proving a stale owner cannot emit success-implying finish evidence.
2. `SB-V03-005`: preserve the new `persona_records()` facade/tests, but enforce the boundary in real production readers. Whole-runtime APIs such as `pipeline.publish_queue(bot)` / `analytics.events_for(bot)` must not remain accidental persona-facing bypasses; raw access must be explicit admin/internal or equivalent.
3. Regenerate `SB-V03-006` only after the two repairs above.
4. Then reconcile the V0.4 Core dependency chain.

Do not defer source work for heartbeat testing.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE / IMPLEMENTATION STALLED.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Heartbeat seq7 does not complete bootstrap: seq5→6 is ~16m37s but seq6→7 is ~30m28s. `steady_hourly_authorized=false` remains authoritative. Do not backfill.

Next:
1. `SB-V05-001` actual HTTPS pinned-IP TLS/SNI/certificate repair + production-constructor regression **now**;
2. `SB-V15-001` persona-scoped production experiment save/load/list/read boundary;
3. preserve V16/V17/V20-002 for later lead audit.

Heartbeat runs in the background and must not replace implementation.

## Lane C — Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`
Status: ACTIVE / hourly coordination heartbeat authorized.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

No independent Core verification report has landed since LEAD-023.

Immediate assignment:
1. independently reproduce/disprove the V03-004 post-cycle success-receipt takeover scenario without editing Core source;
2. independently probe V03-005 real production-reader bypass paths, not only the safe isolation facade;
3. report exact commands/results/files/symbols;
4. then continue CI/control, artifact validation and V2 acceptance/integration harness.

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
- prior Social Bots task `socialbots-v03-audit-20260920-01` failed before clone because worker-local GitHub credentials could not establish private-repo visibility/access;
- private-repo guard must remain intact;
- the failed result counts as zero Social Bots acceptance evidence;
- the unrelated shared-worker run that occupied the slot earlier completed with failure at 04:55:35Z, so the slot is no longer known busy.

Do not re-dispatch Social Bots until the repo credential visibility problem is actually fixed and the slot is confirmed idle at dispatch time. Repeating the same known-failing clone is not useful work. Mac QA owns current independent V0.3 verification so project progress does not wait on this resource.

## Lead
ChatGPT audits checkpoints, updates canonical artifact/state evidence, assigns next work, and prepares integration/V2 runway.

## Version truth
Official version remains `V0.3.x` and artifact/evidence-gated.
Heartbeat success is not a product-version gate.
V0.4 cannot complete without all V0.4 manifest artifacts, including real `SB-V04-005` + independent `SB-EVD-002`.

## Safety
No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake evidence, engagement manipulation or SwarmAI dependency.
