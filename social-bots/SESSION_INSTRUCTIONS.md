# SESSION_INSTRUCTIONS — Lane 1 / Core Builder

Mode: LEAD-039 — ACTIVE SESSION / V0.4 PREP -> V0.7 HOST WORK
Branch: `claude/social-bots-windows-core-host`

Read canonical first:
- `social-bots/lead-reviews/LEAD-039_2026-09-21T1356.md`
- `social-bots/CLAUDE_EXECUTION_TO_V07.md`
- `social-bots/V04_DIVERGENCE_ACCEPTANCE_PLAN.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`

## Lead classification

ACTIVE. Issue #3 shows a fresh Core worker session started at 2026-09-21T17:48:17Z and emitted one `SESSION_ONCE` heartbeat. At lead review time, no new worker source/report commit from that session is yet visible on the authoritative Core branch, so this is liveness/assignment evidence only, not artifact acceptance.

## Hard rule

**DO NOT execute Claude CLI, adaptive reasoning, or any live model/provider call.**
No live authorization manifest exists.

Synthetic/replayed receipts are engineering fixtures/integration evidence only. Do not claim they prove live causal divergence.

## Priority A — prepare-only V0.4 divergence batch

Build/test without model calls:
1. Five planned contexts:
   - social-a / E1
   - social-b / same E1
   - social-c / same E1
   - one cultural Primandir workspace / same E1
   - social-a / E2
2. Emit full bounded context JSON + context SHA-256 + exact prompt SHA-256.
3. Enforce persona-only and evidence-only single-variable assertions.
4. Add proposal receipt validation/divergence reporting.
5. Add a fail-closed authorization-manifest gate and exact call-budget counter.
6. Because no authorization manifest exists, any live execution entry point must stop before spawning Claude.
7. No retry-until-pass logic.
8. Fixture tests must be labeled engineering-only.

Push the current session's durable heartbeat/report and exact source/test evidence to the authoritative Core branch before requesting artifact review.

## Priority B — SB-V07-001

After Priority A is pushed, continue dependency-ready SB-V07-001:
- bounded worker-once execution;
- OS-level scheduler adapters rather than chat-session liveness;
- safe one-task claim;
- one durable `SESSION_ONCE` heartbeat per fresh scheduled worker session;
- invocation receipts;
- crash/restart/no-overlap behavior;
- heartbeat durability independent of Issue-comment transport / `gh` availability;
- no live model invocation in tests.

Do not self-accept any artifact.

No public effects, PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
