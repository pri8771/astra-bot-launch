# SESSION_INSTRUCTIONS — Lane 1 / Windows Core Builder

Mode: FAST TRACK — LEAD-036
Branch: `claude/social-bots-windows-core-host`
Lead check: 2026-09-21T17:10:00Z

Official phase is **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

Read canonical:
- `social-bots/lead-reviews/LEAD-036_2026-09-21T1710.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/artifact-packets/SB-V04-002.md`
- `social-bots/artifact-packets/SB-V04-004.md`

## Accepted / frozen

- SB-V03-001/002/003/004/005/006 and SB-EVD-001 are accepted. Do not churn V03.
- SB-V04-001 is accepted.
- SB-V04-003 is accepted.
- SB-V04-005 is accepted from the first authorized real canary.

## Hard authorization boundary

The owner's **exactly one** existing-subscription live model call has been consumed. A later duplicate call occurred and is excluded from acceptance evidence.

**DO NOT execute any further `claude` CLI / adaptive provider / live model call.**
No PAYG/API-key path, no new spend, no public effects.

## Current mission

SB-V04-002 and SB-V04-004 remain CHANGES_REQUIRED because the accepted single canary does not establish the required real adaptive causal-divergence cases.

Work only on non-live engineering that improves acceptance readiness without pretending to fill that evidence gap:
1. preserve the corrected single-variable deterministic persona/evidence test design;
2. keep the sanitized real-canary receipt seam deterministic and read-only;
3. make the suite clearly distinguish `fixture/replay engineering check` from `real adaptive causal-divergence evidence`;
4. do not label replay of one canary receipt as persona/evidence divergence proof;
5. document exactly which V04-002/V04-004 acceptance cases remain impossible without additional owner-authorized live model calls;
6. run focused/full tests and push a bounded report if you make a useful non-live improvement;
7. otherwise move to dependency-safe non-overlapping Core QA/research only after pulling current canonical instructions.

Heartbeat runs in parallel. The reset soak is **not yet durable-verified** because the branch HEARTBEAT_LOG lacks reset-epoch FAST_5M entries. Commit real prospective entries only; no backfill.

No public effects, PAYG/new spend, secrets, fake evidence, destructive actions or SwarmAI dependency.
