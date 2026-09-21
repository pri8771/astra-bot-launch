# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-mac-qa-control`
Lead review: LEAD-023

## Heartbeat

Lead has accepted the durable bootstrap heartbeat evidence and authorized HOURLY cadence in `LEAD_ACK.json`.
Switch future routine heartbeat checks to hourly. Artifact submissions and blockers still push immediately.
Heartbeat is coordination observability only and must not pause useful QA/integration work.

## Existing accepted controls
- `SB-CTL-012` artifact validator — ACCEPTED.
- `SB-CTL-006` GitHub CI/control — ACCEPTED.

Preserve these.

## Priority 1 — independent SB-V03-004 repair verification

Independently validate Windows Core repair commit:
`175f741fcedace3113191a847d6a7568d77b9cde`

Do not edit Core runtime source.

Review/run the relevant tests against that source and report whether the LEAD-019 migration-side-effect defect is actually closed:
- PersonaState load/migration staging is side-effect free;
- persona migration + runtime marker persist only under the ownership-fenced commit;
- forced takeover at commit leaves no stale-owner persona/runtime/decision writes;
- prior active-cycle fencing tests still pass;
- no false cross-host/native-Windows guarantee is introduced.

Return an independent QA report with exact commit, commands, results and any defect with file/symbol/scenario. Do not self-accept the Core artifact.

## Priority 2 — V2 integration acceptance preparation

Continue the non-runtime integration harness/checklist:
- merge-order checklist for Core + Intelligence;
- CI commands;
- full traceability assertions;
- persona isolation assertions;
- missing/stale/authority/no-public-effect scenarios;
- fixture-vs-operational distinction.

Do not edit Core/Intelligence runtime implementation.

## V0.4 canary

Dedicated local lane `claude/social-bots-v04-live-canary` owns `SB-V04-005`.
Do not switch this QA branch to the canary branch. Current canary branch still lacks a worker execution commit; QA should not fabricate it.

## Safety

No runtime feature implementation, public/account effects, paid API/new spend, secrets, fake evidence, or SwarmAI dependency.
