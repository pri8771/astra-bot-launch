# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-mac-qa-control`
Lead review: LEAD-027

## Heartbeat

Mac-QA bootstrap is accepted and HOURLY coordination cadence is authorized. Resume the hourly worker heartbeat; lead-only instruction commits do not count as worker liveness. Heartbeat is observability only and must not pause QA.

## Existing accepted controls
- `SB-CTL-012` artifact validator — ACCEPTED.
- `SB-CTL-006` GitHub CI/control — ACCEPTED.

## PRIORITY 1 — final independent SB-V03-004 execution gate

Core has completed the V03-005 reader-boundary repair at implementation `796d4e390bd135167e5de2ff8f586bc07ac7f370`, and final prepared V03-006 evidence is at `436787b0a63fdae0e89c224a54054607e32b5187` with exact `Ran 130 tests ... OK` output.

LEAD-027 independently ACCEPTED SB-V03-005. Do not spend time re-auditing superseded `f73c337...` reader defects unless the current final source exposes a new concrete problem.

The remaining high-risk V0.3 technical acceptance gate is SB-V03-004 independent lifecycle execution. Do not edit Core runtime source.

Fetch/checkout current Core implementation and independently run/probe at minimum:
1. `test_stale_owner_cannot_write_success_finish_receipt_after_takeover` (or its exact current test path/name);
2. active-cycle lease-expiry/takeover old-owner commit rejection;
3. migration/load side-effect-free-until-fenced-commit regression;
4. focused fencing/concurrency suite sufficient to show no stale owner writes successful state/effect/completion evidence after takeover.

Report:
- exact Core implementation SHA tested (must include the current 796d4e3 implementation or a later source-equivalent head);
- exact commands and output/result counts;
- PASS/FAIL per lifecycle scenario;
- host/filesystem scope;
- whether any concrete source defect was found;
- no-public-effect/no-spend confirmation.

If PASS, explicitly recommend SB-V03-004 ACCEPT-READY to the lead. If FAIL, provide the minimal reproducible defect and do not edit Core source.

## PRIORITY 2 — integration/CI harness

After the V03-004 report, continue non-runtime integration work:
- merge/test checklist;
- artifact validator / CI maintenance;
- V2 traceability acceptance harness;
- persona isolation and missing/stale/authority/no-public-effect assertions;
- fixture-vs-operational distinction.

## V0.4 canary

Dedicated branch `claude/social-bots-v04-live-canary` exclusively owns SB-V04-005. Do not fabricate or substitute a QA/injected run for the real subscription-authenticated canary.

## Safety

No runtime implementation edits, public/account effects, paid API/new spend, secrets, fake evidence, or SwarmAI dependency.
