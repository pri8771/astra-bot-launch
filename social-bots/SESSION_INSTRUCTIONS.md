# SESSION_INSTRUCTIONS — Lane 3 / Acceptance + QA

Mode: LEAD-039 — STALE WAKE-UP / INDEPENDENT REVIEW + V0.7 PREP
Branch: `claude/social-bots-mac-qa-control`

Read canonical:
- `social-bots/lead-reviews/LEAD-039_2026-09-21T1356.md`
- `social-bots/CLAUDE_EXECUTION_TO_V07.md`
- `social-bots/V04_DIVERGENCE_ACCEPTANCE_PLAN.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`

V0.3 is accepted/closed. SB-V04-005 is accepted from the first authorized call.

## Lead classification

STALE. No fresh Acceptance worker session, heartbeat, QA commit, or report is visible after LEAD-038. On the next fresh session, sync/read canonical coordination, emit exactly one real `SESSION_ONCE` heartbeat, then work normally. Do not run a timed heartbeat loop.

## Hard rule

**NO further Claude CLI/adaptive/model calls.**
The dedicated canary lane is frozen.

## Assignment

1. Independently review new Core/Intelligence submissions when they land.
2. Do not edit Core/Intelligence runtime source.
3. Prepare V0.7 acceptance checks for repeated OS-scheduled bounded worker sessions:
   - exactly one durable `SESSION_ONCE` heartbeat per fresh scheduled session;
   - heartbeat logging works without `gh` or Issue-comment transport;
   - scheduler invocation receipts bind session id, heartbeat ref, assignment/source refs, claim result and exit status;
   - crash/restart/no-overlap and one-task-claim cases;
   - no backfill/fabricated liveness.
4. When Core submits the prepare-only V0.4 matrix, audit:
   - no live provider execution occurred;
   - all five contexts are exactly isolated as specified;
   - context/prompt hashes are stable;
   - authorization gate fails closed with no manifest;
   - fixture/replay evidence is not misrepresented as causal adaptive acceptance.
5. When Intelligence submits SB-V15-001, independently check ordinary production APIs cannot cross persona boundaries and whole-runtime reads are explicitly admin/internal only.

Do not self-accept artifacts.

No public effects, PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
