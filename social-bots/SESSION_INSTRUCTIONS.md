# SESSION_INSTRUCTIONS — Windows Core / V0.3 closure

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-windows-core-host`

Heartbeat is observability only. Do not wait on heartbeat acceptance before coding.

At start:
1. `git pull --ff-only`
2. `git fetch origin`
3. read canonical `FAST_TRACK_EXECUTION.md` and `SESSION_ROUTER.md` with `git show`
4. resume from current branch state; do not discard submitted work.

## Priority 1 — SB-V03-004 migration fencing repair

LEAD-019/020 remaining issue:
legacy migration performs durable writes from load/migration paths before the cycle ownership fence.

Required:
- RuntimeState/PersonaState load must be side-effect free;
- stage migration in memory;
- persist persona migration + runtime migration marker only under the valid fenced commit;
- stale owner must not migrate/write anything after takeover;
- migration remains crash-safe/idempotent;
- add real regressions for stale-owner migration and run_cycle ordering.

Submit SB-V03-004.

## Priority 2 — SB-V03-005 production persona read boundary

Keep physical PersonaState split.

Add authoritative persona-scoped production APIs for persona-private/personalized stores:
- content history;
- experiment reads/listing;
- action history;
- decision history;
- analytics/history where persona-private;
- publish queue reads where applicable.

Raw whole-runtime reads may remain only as explicitly named admin/internal APIs.

Add mixed-persona production-path regressions proving one persona cannot enumerate another's records.

Submit SB-V03-005.

## Priority 3 — SB-V03-006

Once 004/005 pass your full suite:
- regenerate fresh V0.3 evidence;
- no reuse of superseded proof;
- submit SB-V03-006.

## Priority 4 — V04 dependency reconciliation

After V03 closure:
- reconcile SB-V04-001/003 against current code;
- preserve real-provider implementation;
- do NOT attempt the live canary here unless this environment is actually authenticated subscription host.
Dedicated branch `claude/social-bots-v04-live-canary` owns the real canary.

## CI

Mac QA owns CI/control. Do not duplicate.

## Reporting

Reports under `social-bots/worker-reports/windows-core/`.
Commit/push after each parent artifact.
Pull instructions after every checkpoint and continue to next dependency-ready artifact without generic permission prompts.

## Heartbeat

Continue heartbeat if the session supports it, but heartbeat proof does not block implementation.

## Safety

No public effects, paid API/new spend, destructive actions, secrets, fake evidence, or SwarmAI dependency.
