# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-mac-qa-control`
Lead review: LEAD-034

No Core runtime source edits.

## Heartbeat

Historical Mac-QA coordination bootstrap remains accepted and the historical hourly cadence authorization remains true. Today's temporary soak is a separate measurement and has not started in durable evidence.

Start prospectively now if this session is active:
- `FAST_5M`: T0, +~5m, +~10m, +~15m;
- then `SOAK_15M_24H`: every 15 minutes for 24 hours;
- append/push real timed records; no backfill;
- keep QA running in parallel.

LEAD-034 verified the durable log still ends at seq10 `2026-09-21T03:57:57Z`; no today's `FAST_5M` T0 exists yet.

## Existing accepted controls
- `SB-CTL-012` artifact validator — ACCEPTED.
- `SB-CTL-006` GitHub CI/control — ACCEPTED.

## PRIORITY 1 — final independent SB-V03-004 execution gate

Core final V03 implementation is `796d4e390bd135167e5de2ff8f586bc07ac7f370`; prepared evidence is `436787b0a63fdae0e89c224a54054607e32b5187` with exact 130-test OK output.

Independently run/probe at minimum:
1. post-cycle lease expiry/takeover where stale owner must not write a success finish receipt;
2. active-cycle lease-expiry/takeover where old owner must not commit state/effect evidence;
3. migration/load remains side-effect-free until fenced commit;
4. focused fencing/concurrency suite proving no stale owner writes successful state/effect/completion evidence after takeover.

Report exact SHA tested, exact commands/output/test counts, PASS/FAIL per scenario, host/filesystem scope, any concrete source defect, and no-public-effect/no-spend confirmation.

If PASS, explicitly recommend `SB-V03-004 ACCEPT-READY`. If FAIL, provide the minimal reproducible defect. Do not edit Core source.

## PRIORITY 2 — integration/CI harness

After the V03-004 report, continue merge/test checklist, artifact validator/CI maintenance, V2 traceability acceptance harness, persona isolation/missing/stale/authority/no-public-effect assertions, and fixture-vs-operational distinction.

## V0.4

Dedicated branch `claude/social-bots-v04-live-canary` owns `SB-V04-005`. Do not substitute QA/injected evidence for the real subscription-authenticated canary.

## Safety

No runtime implementation edits, public/account effects, paid API/new spend, secrets, fake evidence, or SwarmAI dependency.
