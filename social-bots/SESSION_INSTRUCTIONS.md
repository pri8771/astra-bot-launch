# SESSION_INSTRUCTIONS — Lane 1 / Core Builder

Mode: LEAD-037 — V0.4 EMPIRICAL GATE PREP -> V0.7 HOST WORK
Branch: `claude/social-bots-windows-core-host`

Read canonical first:
- `social-bots/lead-reviews/LEAD-037_2026-09-21T1717.md`
- `social-bots/V04_DIVERGENCE_ACCEPTANCE_PLAN.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`

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

Submit exact SHA/tests/report and stop for lead/QA audit of Priority A.

## Priority B — SB-V07-001

After Priority A is pushed, SB-V07-001 is dependency-ready.

Build the authorized-host worker/runbook package with:
- OS-level scheduling/event invocation rather than chat-session liveness;
- safe one-task claim;
- invocation/heartbeat receipts;
- crash/restart/no-overlap primitives;
- heartbeat durability independent of Issue-comment transport;
- durable heartbeat logging even when `gh` is missing;
- optional human-readable GitHub comment transport;
- no live model invocation in tests.

Do not self-accept any artifact.

No public effects, PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
