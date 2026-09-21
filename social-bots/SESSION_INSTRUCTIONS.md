# SESSION_INSTRUCTIONS — Lane 2 / Mac Intelligence Builder

Mode: FAST TRACK — LEAD-036
Branch: `claude/social-bots-intelligence-repair-v2`
Lead check: 2026-09-21T17:10:00Z

Official phase is **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

Read canonical:
- `social-bots/lead-reviews/LEAD-036_2026-09-21T1710.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/artifact-packets/SB-V15-001.md`

## Accepted / frozen

- **SB-V05-001 ACCEPTED** from repair `a462bd6`.
- SB-V13-001 and SB-V14-001 remain accepted.
- Do not edit Core reasoning/runtime ownership areas.

## Current mission — SB-V15-001 narrow repair only

The persona-partitioned storage and explicit persona APIs in `2052955` are good, but the ordinary public aliases `load(bot, exp_id)` and `load_all(bot)` still expose whole-runtime cross-persona reads. A docstring calling them admin/internal is not a structural boundary.

Repair exactly this:
1. remove, private-prefix, or rename the ambiguous whole-runtime aliases so normal persona-facing callers cannot mistake them for production APIs;
2. keep explicit `admin_load_experiment` / `admin_load_all_experiments` (or equivalent clearly administrative names) if needed;
3. update any legitimate admin/test callers to the explicit admin names;
4. add a regression that inspects/uses the normal production API surface and proves another persona's experiments cannot be enumerated or loaded;
5. preserve bot+persona physical partitioning, ownership checks, normalized observation provenance and INCONCLUSIVE behavior;
6. run focused and full suites; commit/push source + report; then stop expansion for lead audit.

After lead accepts V15, V16/V17/V20-002 can be independently audited in sequence. Do not expand into those before this narrow fix lands.

No live model call is needed or authorized for this work. No public effects, PAYG/new spend, secrets, fake metrics/evidence, destructive actions or SwarmAI dependency.

Heartbeat is observability only. The reset soak is still 0 durable-verified intervals because the committed HEARTBEAT_LOG has no reset-epoch FAST_5M entries. Commit only real prospective records; no backfill.
