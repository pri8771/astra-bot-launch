# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-mac-qa-control`
Lead review: LEAD-024

## Heartbeat

Lead has accepted the durable Mac-QA bootstrap heartbeat evidence and authorized HOURLY cadence in `LEAD_ACK.json`.
Routine heartbeat stays hourly. Artifact submissions and blockers push immediately.
Heartbeat is coordination observability only and must not pause useful QA/integration work.

## Existing accepted controls
- `SB-CTL-012` artifact validator — ACCEPTED.
- `SB-CTL-006` GitHub CI/control — ACCEPTED.

Preserve these.

## Priority 1 — independent Core verification of LEAD-024 findings

Do not edit Core runtime source. Independently inspect/execute the current Windows Core branch and return an evidence-based QA report.

### SB-V03-004 — post-cycle success-receipt fence

The migration repair in `175f741...` is still positive, but LEAD-024 found a separate scenario in current `runtime/worker.py`:
- `decision.run_cycle(..., fence=fence)` can finish its fenced durable commit;
- `worker.run_one_unit()` then writes the success/finish receipt outside the fence;
- if the old worker stalls after cycle commit, expires, another worker takes over, and the old worker resumes, it may emit a finish receipt implying success despite no longer owning the fence.

Independently reproduce or disprove this with a targeted adversarial test/harness. Verify the SB-V03-004 contract that an old owner cannot emit durable success-implying evidence after takeover. Do not accept a TTL increase as a fix.

Also retain checks that PersonaState migration staging is side-effect free and the main decision/state/content writes remain fenced.

### SB-V03-005 — actual production persona read boundary

Current Core commit `d1e4bee...` adds `persona_records()` and generic mixed-persona tests. Independently verify whether real production persona-facing readers are forced through that boundary.

Specifically inspect raw whole-runtime APIs such as `pipeline.publish_queue(bot)`, `analytics.events_for(bot)`, experiment list/load and direct append-only readers. Determine whether a normal production persona-specific caller can bypass `persona_records()` and enumerate another persona's records. Test actual production call paths, not only `isolation.audit()` / the facade itself.

Report exact files/symbols/scenarios and PASS/FAIL for each acceptance property. Do not self-accept Core artifacts.

## Priority 2 — V2 integration acceptance preparation

After the Core verification report, continue the non-runtime integration harness/checklist:
- merge-order checklist for Core + Intelligence;
- CI commands;
- full traceability assertions;
- persona isolation assertions;
- missing/stale/authority/no-public-effect scenarios;
- fixture-vs-operational distinction.

Do not edit Core/Intelligence runtime implementation.

## V0.4 canary

Dedicated local lane `claude/social-bots-v04-live-canary` owns `SB-V04-005`.
Do not switch this QA branch to the canary branch. Current canary branch still lacks a worker execution commit; QA must not fabricate it.

## Safety

No runtime feature implementation, public/account effects, paid API/new spend, secrets, fake evidence, or SwarmAI dependency.
