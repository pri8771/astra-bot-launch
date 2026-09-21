# SESSION_INSTRUCTIONS — Intelligence / Evidence Integrity

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-intelligence-repair-v2`
Lead review: LEAD-032

Heartbeat is observability only. Do NOT pause implementation for heartbeat testing. Record genuine timestamps only; no backfill. Hourly cadence remains unauthorized because seq6 -> seq7 was ~30m28s.

## Accepted and frozen
- `SB-V13-001` — ACCEPTED.
- `SB-V14-001` — ACCEPTED.

## Priority 1 — SB-V05-001 — IMPLEMENT NOW

The lane remains stale: no worker source/heartbeat after seq7 at `2026-09-21T04:10:36Z`. LEAD-032 found no later worker progress; continue this assignment now rather than waiting for another heartbeat or lead prompt.

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
