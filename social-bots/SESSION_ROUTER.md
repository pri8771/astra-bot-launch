# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current operating mode: FAST TRACK.
Current lead review: LEAD-023.

Read:
- `FAST_TRACK_EXECUTION.md`
- `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `lead-reviews/LEAD-023_2026-09-21T0006.md`

Heartbeat is observability only. It does not block implementation or the real V0.4 canary.

## Lane A — Windows Core / V0.3 closure
Branch: `claude/social-bots-windows-core-host`
Status: ACTIVE.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

`SB-V03-004` repair `175f741...` has positive lead source review and is assigned to Mac QA for independent execution/verification. Do not keep reworking it unless QA finds a concrete defect.

Next Core implementation:
1. close `SB-V03-005` authoritative persona-scoped production reads;
2. regenerate `SB-V03-006` fresh V0.3 acceptance evidence;
3. reconcile V0.4 Core dependency chain.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE / implementation resume required.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Durable seq5/seq6 timed checkpoints are real, but the lane has no new V05/V15 source repair since fast-track activation. Heartbeat remains background-only and hourly is not yet authorized.

Next:
1. `SB-V05-001` actual HTTPS pinned-IP TLS/SNI/certificate repair + production-constructor regression;
2. `SB-V15-001` persona-scoped production experiment save/load/list/read boundary;
3. preserve V16/V17/V20-002 for later lead audit.

## Lane C — Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`
Status: ACTIVE / hourly coordination heartbeat authorized.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Immediate assignment:
1. independently verify Windows Core `175f741...` for V03-004 migration/fence correctness without editing Core source;
2. report exact commands/results/defects;
3. then continue CI/control, artifact validation and V2 acceptance/integration harness.

Heartbeat proves coordination only, not V0.7 runtime liveness.

## Lane D — Mac LOCAL real V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: READY / NO WORKER EXECUTION VISIBLE.

Priority Zero:
- execute `SB-V04-005` immediately on an actual local host with working Claude Code subscription authentication;
- do not wait for heartbeat validation;
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
- attempted task `socialbots-v03-audit-20260920-01` failed before clone;
- worker-local GitHub credential could not establish private-repo visibility/access for `pri8771/astra-bot-launch`;
- private-repo guard must remain intact;
- no result from that task counts as Social Bots acceptance evidence.

Do not re-dispatch until credential visibility is repaired. Mac QA owns the current independent V03-004 verification so Core progress does not wait on worker-pc.

## Lead
ChatGPT audits checkpoints, updates canonical artifact/state evidence, assigns next work, and prepares integration/V2 runway.

## Concurrency
Primary fast-track lanes are Windows Core, Intelligence, Mac QA and local V0.4 canary. `worker-pc` is optional extra capacity only after its credential blocker is repaired. Do not overlap source ownership.

## Version truth
Official version remains `V0.3.x` and artifact/evidence-gated.
Heartbeat success is not a product-version gate.
V0.4 cannot complete without real `SB-V04-005` + independent `SB-EVD-002` and the rest of the V0.4 manifest.

## Safety
No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake evidence, engagement manipulation or SwarmAI dependency.
