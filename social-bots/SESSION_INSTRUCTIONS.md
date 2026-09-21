# SESSION_INSTRUCTIONS — Lane 3 / Acceptance + QA

Mode: FAST TRACK — LEAD-036
Primary branch: `claude/social-bots-mac-qa-control`
Lead check: 2026-09-21T17:10:00Z

Official phase is **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

Read canonical:
- `social-bots/lead-reviews/LEAD-036_2026-09-21T1710.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`

## Mission A result

Your independent SB-V03-004 execution at `72e380bda71561429154e67bc07636b89143a488` is **ACCEPTED**:
- 37/37 invariant checks passed;
- focused 36 tests passed;
- full 130-test suite passed;
- V0.3 is now closed.

Scope remains single POSIX host/filesystem. The execution actually ran on Linux CCR rather than the reset-plan physical Mac; do not generalize this to native Windows/cross-host behavior.

## Mission B / live canary state

SB-V04-005 is **ACCEPTED from the first chronological real canary at ~16:15Z**. That call consumed the owner's exactly-one existing-subscription authorization.

A second real call later occurred at ~16:53Z. It exceeded the exactly-one authorization and is excluded from acceptance evidence.

### HARD STOP

**DO NOT execute any more Claude CLI / adaptive reasoning / live model calls.**
No API/PAYG, no new spend, no public effects.

## Current assignment

1. Continue non-overlapping QA/CI/artifact-validator/V2 acceptance-harness work only.
2. Do not edit Core or Intelligence runtime source.
3. Preserve canary evidence and the authorization-incident record; do not rerun or “improve” the canary.
4. Help validate future submitted Core/Intelligence artifacts only by read-only execution/review when explicitly dependency-ready.
5. Repair heartbeat durability prospectively: the current committed `HEARTBEAT_LOG.jsonl` contains no reset-epoch FAST_5M entries. Commit real future heartbeat records only; no synthetic timestamps/backfill.
6. Keep Issue #3 comments concise and truthful, but remember they do not substitute for the durable heartbeat log.

No public social effects, paid API/PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
