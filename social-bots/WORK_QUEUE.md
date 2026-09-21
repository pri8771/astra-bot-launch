# Work queue — FAST TRACK

Canonical execution plan: `FAST_TRACK_EXECUTION.md`.

## Priority Zero
`SB-V04-005` real adaptive canary on `claude/social-bots-v04-live-canary`.

Run immediately from an actually authenticated local Claude Code host. Heartbeat validation is not a prerequisite.

## Lane A — Windows Core
Branch: `claude/social-bots-windows-core-host`
ACTIVE.

1. SB-V03-004 migration-side-effect fencing.
2. SB-V03-005 persona-scoped production readers.
3. SB-V03-006 fresh V0.3 acceptance bundle.
4. Reconcile V04 dependency chain.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
ACTIVE.

1. SB-V05-001 real HTTPS pinned-IP TLS/SNI/cert repair.
2. SB-V15-001 persona-scoped experiment persistence/readers.
3. Fresh lead audit of submitted V16/V17/V20-002.
4. Continue only dependency-safe work.

## Lane C — Mac QA / Integration
Branch: `claude/social-bots-mac-qa-control`
ACTIVE.

- heartbeat proof in background;
- CI/control;
- artifact graph;
- V2 acceptance/integration harness;
- prepare merge/test checklist.

## Lane D — Mac local canary
Branch: `claude/social-bots-v04-live-canary`
ACTIVE WHEN OWNER STARTS LOCAL CLAUDE CODE SESSION.

- one real source;
- one real Claude subscription call;
- persist decision;
- zero public effect;
- submit SB-V04-005.

## Heartbeat
Continue collecting real timed heartbeats, but do not pause engineering work for heartbeat validation.

## Current official version
V0.3.x until V03 required artifacts are accepted.
V0.4 additionally requires the real canary + independent lead acceptance.

## Fast-track concurrency
Use up to 4 workers now. Do not overlap source ownership.

## Authority
No public effects, paid API/new spend, destructive actions, secrets, fake evidence or SwarmAI dependency.


## worker-pc external verification

Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1.

First Social Bots task:
- `socialbots-v03-audit-20260920-01`
- intended: independent read-only V03-004/V03-005 audit
- result: **FAILED before repository clone**
- dispatch run: `35559393292`
- sanitized error: `Repository tasks must target a private repository.`

Independent GitHub metadata confirms `pri8771/astra-bot-launch` is private. Therefore this is a worker-local GitHub credential/repository-access visibility problem, not a project visibility problem.

Required infrastructure action:
- grant/refresh the worker-pc `gh` credential so it can access `pri8771/astra-bot-launch`;
- keep the private-repository guard intact;
- after access is repaired, re-dispatch the independent V0.3 audit before assigning source-changing work.

Do not move Social Bots project governance into `remote-workers`.
