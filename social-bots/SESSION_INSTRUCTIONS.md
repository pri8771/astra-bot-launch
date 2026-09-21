# SESSION_INSTRUCTIONS — Intelligence / Evidence Integrity

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-intelligence-repair-v2`
Lead review: LEAD-034

Heartbeat is observability only. Do not pause implementation for heartbeat timing.

## Today's heartbeat soak — not started yet in durable evidence

Start prospectively now if this session is active:
- `FAST_5M`: T0, +~5m, +~10m, +~15m;
- then `SOAK_15M_24H`: every 15 minutes for 24 hours;
- append/push real timed records; no backfill;
- continue source work in parallel.

Historical durable history still ends at seq7 `2026-09-21T04:10:36Z`; seq6→7 is ~30m28s, so historical hourly authorization remains false. No `FAST_5M` entry exists yet.

## Accepted and frozen
- `SB-V13-001` — ACCEPTED.
- `SB-V14-001` — ACCEPTED.

## Priority 1 — SB-V05-001 — IMPLEMENT NOW

Repair the actual HTTPS production path:
- connect to the already validated/pinned public IP;
- preserve original hostname for TLS SNI and certificate verification;
- no hostname re-resolution after validation;
- correct Host header semantics;
- redirects fail closed unless each hop is independently validated/pinned;
- add a regression through the real production connection-construction path that catches invalid stdlib HTTPSConnection use;
- preserve SSRF protections, collector-owned trust, extraction honesty, fixture-vs-operational distinction and operational signal gating.

Return exact SHA/tests/limits. Do not claim fixture/stub evidence as live external evidence.

## Priority 2 — SB-V15-001

After V05 submission:
- implement authoritative bot+persona experiment save/load/list/read APIs;
- normal persona flows must not enumerate another persona's experiments;
- whole-runtime access, if retained, must be explicit admin/internal;
- add mixed-persona production-path regressions;
- preserve normalized-observation provenance and INCONCLUSIVE-on-missing behavior.

Preserve V16/V17/V20-002 for later lead audit.

## Safety / ownership

Do not edit Core state/decision/reasoning/leasing/worker. No public effects, paid APIs/new spend, secrets, fake metrics/evidence, engagement manipulation, or SwarmAI dependency.
