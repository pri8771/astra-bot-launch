# Work queue — FAST TRACK

Canonical execution plan: `FAST_TRACK_EXECUTION.md`.
Current lead review: `lead-reviews/LEAD-023_2026-09-21T0006.md`.

## Priority Zero — real V0.4 canary

Artifact: `SB-V04-005`
Branch: `claude/social-bots-v04-live-canary`

**Status: READY but no Claude worker execution is visible yet.**

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
Status: ACTIVE.

`SB-V03-004` repair commit `175f741fcedace3113191a847d6a7568d77b9cde` has positive lead source review. It appears to close the LEAD-019 side-effectful migration hole, but canonical status remains CHANGES_REQUIRED until Mac QA independently executes/reviews the repaired branch.

Next implementation:
1. **SB-V03-005 now** — finish authoritative persona-scoped production readers for private/personalized stores and mixed-persona production-path regressions.
2. **SB-V03-006 next** — regenerate a fresh V0.3 acceptance bundle from the current repaired code.
3. Then reconcile the V0.4 dependency chain.

Do not defer implementation for heartbeat testing. Do not keep modifying V03-004 unless independent QA finds a concrete defect.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE but source progress has stalled since FAST TRACK activation.

Durable heartbeat seq5/seq6 are real; hourly is not yet authorized. Heartbeat stays background-only.

Next:
1. **SB-V05-001 now** — valid pinned-IP HTTPS TLS/SNI/certificate execution plus production-constructor regression.
2. **SB-V15-001 next** — authoritative bot+persona experiment save/load/list/read boundary and mixed-persona regressions.
3. Preserve V16/V17/V20-002 for fresh lead audit after those repairs.

Do not spend the session waiting in a foreground heartbeat loop.

## Lane C — Mac QA / Integration
Branch: `claude/social-bots-mac-qa-control`
Status: ACTIVE; coordination heartbeat bootstrap accepted and routine hourly cadence authorized.

Immediate QA assignment:
1. independently verify Windows Core commit `175f741...` for SB-V03-004 migration/fencing correctness without editing Core source;
2. report exact commands/results/defects;
3. then continue CI/control, artifact validation, V2 acceptance/integration harness and merge/test checklist.

Heartbeat is coordination observability only, not V0.7 runtime-liveness proof.

## Lane D — local authenticated V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: READY / NOT STARTED in repository evidence.

The branch still contains only lead setup/authorization commits. Start/resume the actual local Claude Code session and execute `SB-V04-005`.

## Additional remote-worker capacity

Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1.

First Social Bots task:
- `socialbots-v03-audit-20260920-01`
- intended: independent read-only V03-004/V03-005 audit
- result: **FAILED before repository clone**
- dispatch run: `35559393292`
- sanitized error: `Repository tasks must target a private repository.`

Independent GitHub metadata confirms `pri8771/astra-bot-launch` is private. Therefore this is a worker-local GitHub credential/repository-access visibility problem, not a Social Bots repository visibility change.

Required infrastructure action:
- grant/refresh the worker-pc `gh` credential so it can access `pri8771/astra-bot-launch`;
- keep the private-repository guard intact;
- only then re-dispatch read-only verification work.

The failed attempt contributes no artifact acceptance evidence and does not replace the active Mac-QA verification assignment. Do not move Social Bots governance into `remote-workers`.

## Heartbeat truth

- Mac QA: real durable cadence observed; hourly coordination cadence authorized.
- Intelligence: timed seq5/seq6 observed; remain bootstrap until lead sees enough future durable cadence.
- Heartbeat never blocks source work or the live canary.
- Worker heartbeat proves GitHub coordination only, not Social Bots recurring runtime liveness.

## Current official version

**V0.3.x**.

V0.3 cannot close while V03-004/V03-005/V03-006 remain unresolved in canonical artifact state.
V0.4 additionally requires the real `SB-V04-005` canary and independent `SB-EVD-002` acceptance.
Later-version scaffolding does not advance the official product version.

## Authority

No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake operational evidence, engagement manipulation or SwarmAI dependency.
