# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current operating mode: FAST TRACK.

Read:
- `FAST_TRACK_EXECUTION.md`
- `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`

Heartbeat is observability only. It does not block implementation or the real V0.4 canary.

## Lane A — Windows Core / V0.3 closure
Branch: `claude/social-bots-windows-core-host`
Status: ACTIVE / REACTIVATED.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Next:
1. close SB-V03-004 migration-side-effect fencing;
2. close SB-V03-005 persona-scoped production reads;
3. regenerate SB-V03-006;
4. reconcile V04 dependency chain.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Next:
1. SB-V05-001 real HTTPS pinned-IP/SNI/cert path;
2. SB-V15-001 persona-scoped production experiment read/write boundary;
3. submit/preserve V16/V17/V20-002 for lead audit.

Heartbeat runs in background and does not block work.

## Lane C — Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`
Status: ACTIVE.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Continue:
- heartbeat proof in background;
- CI/control;
- artifact validation;
- V2 acceptance/integration harness.
No runtime-source ownership.

## Lane D — Mac LOCAL real V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: READY TO START NOW on an actual local authenticated Claude Code host.

Priority Zero:
- execute SB-V04-005 immediately;
- do not wait for heartbeat validation;
- real public source + actual existing-subscription Claude Code invocation;
- no fixture/injected runner/API PAYG;
- persist decision;
- zero public effect;
- push evidence and stop for lead audit.

Owner authorization already exists for one bounded existing-subscription call at zero additional spend.

## Lead
ChatGPT audits checkpoints, updates canonical artifact statuses, assigns next work, and prepares integration/V2 runway.

## Concurrency
Fast-track maximum: 4 workers + ChatGPT lead.
After canary completes, reassign that worker to the largest dependency-ready backlog.

## Version truth
Official version remains artifact/evidence-gated.
Heartbeat success is not a product-version gate.
V0.4 cannot complete without SB-V04-005 + SB-EVD-002.

## Safety
No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake evidence, engagement manipulation or SwarmAI dependency.
