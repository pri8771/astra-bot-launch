# SESSION_INSTRUCTIONS — Lane 3 / Acceptance + QA

Mode: LEAD-037 — INDEPENDENT REVIEW + V0.7 PREP
Branch: `claude/social-bots-mac-qa-control`

Read canonical:
- `social-bots/lead-reviews/LEAD-037_2026-09-21T1717.md`
- `social-bots/V04_DIVERGENCE_ACCEPTANCE_PLAN.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`

V0.3 is accepted/closed. SB-V04-005 is accepted from the first authorized call.

## Hard rule

**NO further Claude CLI/adaptive/model calls.**
The dedicated canary lane is frozen.

## Assignment

1. Independently review new Core/Intelligence submissions when they land.
2. Do not edit Core/Intelligence runtime source.
3. Prepare V0.7 host/heartbeat acceptance checks:
   - durable heartbeat logging must work without `gh`;
   - comment posting is optional transport, not the source of cadence truth;
   - prospective real timestamps only;
   - missed intervals are reported, never backfilled;
   - crash/restart/no-overlap and one-task-claim acceptance cases.
4. When Core submits the prepare-only V0.4 matrix, audit:
   - no live provider execution occurred;
   - all five contexts are exactly isolated as specified;
   - context/prompt hashes are stable;
   - authorization gate fails closed with no manifest.
5. When Intelligence submits SB-V15-001, independently check normal production APIs cannot cross persona boundaries.

Do not self-accept artifacts.

No public effects, PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
