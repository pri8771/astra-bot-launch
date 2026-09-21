## TODAY-ONLY HEARTBEAT SOAK — 2026-09-21

For this fresh session, start the heartbeat soak immediately and keep useful lane work running in parallel.

Stage 1:
- produce heartbeat records at T0, ~T0+5m, ~T0+10m, ~T0+15m;
- this is 3 consecutive real 5-minute intervals;
- use cadence_mode `FAST_5M`;
- append every timed record to the lane's HEARTBEAT_LOG.jsonl and push it;
- no fabricated/backfilled timestamps and no burst updates counted as timed success.

Stage 2:
- after the third successful 5-minute interval, switch immediately to `SOAK_15M_24H`;
- continue every 15 minutes for 24 hours (target 96 intervals);
- do not wait for lead acknowledgement to start Stage 2;
- keep engineering/review work running between heartbeat intervals;
- if an interval is missed or the heartbeat process dies, record it truthfully and continue prospectively.

Read canonical `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md` before starting.

# SESSION_INSTRUCTIONS — Intelligence / Evidence Integrity

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-intelligence-repair-v2`
Lead review: LEAD-033

Heartbeat is observability only. Do NOT pause implementation for heartbeat testing. Record genuine timestamps only; no backfill. Hourly cadence remains unauthorized because seq6 -> seq7 was ~30m28s.

## Accepted and frozen
- `SB-V13-001` — ACCEPTED.
- `SB-V14-001` — ACCEPTED.

## Priority 1 — SB-V05-001 — IMPLEMENT NOW

The lane remains stale: no worker source/heartbeat after seq7 at `2026-09-21T04:10:36Z`. LEAD-033 found no later worker progress; continue this assignment now rather than waiting for another heartbeat or lead prompt.

Repair the actual HTTPS production path:
- connect to the already validated/pinned public IP;
- preserve original hostname for TLS SNI and certificate verification;
- no hostname re-resolution after validation;
- correct Host header semantics;
- redirects fail closed unless each hop is independently validated/pinned;
- add a regression through the real production connection-construction path that would catch invalid stdlib HTTPSConnection usage/signature;
- preserve SSRF protections, collector-owned trust, extraction honesty, fixture-vs-operational distinction and operational signal gating.

Return exact SHA/tests/limitations; do not claim fixture/stub evidence is live external evidence.

## Priority 2 — SB-V15-001

After V05 submission, implement authoritative bot+persona experiment persistence/read/list APIs. Normal persona flows must not enumerate another persona's experiments; whole-runtime access, if retained, must be explicit admin/internal. Add mixed-persona production-path regressions and preserve normalized-observation provenance + INCONCLUSIVE-on-missing behavior.

## Hold for later audit

Preserve V16/V17/V20-002. Do not expand higher-version work until V05/V15 are submitted and independently reviewed.

## Safety / ownership

Do not edit Core state/decision/reasoning/leasing/worker. No public effects, paid APIs/new spend, secrets, fake metrics/evidence, engagement manipulation or SwarmAI dependency.
