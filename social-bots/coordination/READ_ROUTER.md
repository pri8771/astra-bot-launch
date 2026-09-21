# Social Bots — read router

Purpose: minimize context use. **Do not read every file below. Read only the route matching the active work.**

## Always read

- `coordination/SESSION_START.md`
- `state/CURRENT.md`
- your assignment file
- active artifact packet(s)

## V0.4–V0.7 recovery implementation

Read:
- `RECOVERY_TO_V07.md`
- exact `artifact-packets/recovery-v07/<ARTIFACT>.md`
- relevant source/tests only

Read `AUTHORIZATION_MANIFEST_SCHEMA.md` only for authorization/live-provider work.
Read `INVOCATION_RECEIPT_SCHEMA.md` only for worker/scheduler receipt work.

## V0.8–V1.7

Read:
- `V07_TO_V17_EXECUTION.md`
- exact `artifact-packets/v07-v17/<ARTIFACT>.md`

Load account/public-effect schemas only when working those surfaces.

## V1.8–V3.0

Read:
- `DETAILED_EXECUTION_V18_TO_V30.md`
- exact `artifact-packets/v18-v30/<ARTIFACT>.md`

For V2.3 specialist work, also read:
- `SPECIALIST_WORKER_CONTRACT_SCHEMA.md`

For V2.4+/V3 memory, also read:
- `ORGANIZATIONAL_MEMORY_SCHEMA.md`

For V2.8+/V3 allocation, also read:
- `PORTFOLIO_RESOURCE_BUDGET_SCHEMA.md`

For V3 architecture, read:
- `V3_TARGET_ARCHITECTURE.md`

## Roadmap/planning audit only

Only when explicitly assigned architecture/planning, read:
- `VERSION_ROADMAP.md`
- `MILESTONE_MANIFEST.md`
- `MASTER_PLAN_V04_TO_V30.md`
- `V07_TO_V17_EXECUTION.md`
- `DETAILED_EXECUTION_V18_TO_V30.md`

Do not load all 298 artifact packets. Query/filter `ARTIFACT_INDEX.json` and open only the required cards.

## Status / lead review

Use targeted reads:
- `STATE.json` for machine-readable truth
- `WORK_QUEUE.md` for immediate queue
- latest `lead-reviews/LEAD-*.md` only when acceptance/status matters
- `AGENT_MESSAGES.md` tail only when a recent handoff is relevant

## Historical context

Past conversations/memory and legacy branches are useful for intent/why. They never outrank current canonical Git state.
