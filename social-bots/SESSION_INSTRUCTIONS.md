# FAST TRACK NOTICE

Heartbeat is observability only and does NOT block implementation. Continue the explicit V05-001 and V15-001 repairs immediately while timed heartbeat proof continues in the background. After each parent artifact, push/report and pull this file again.

# SESSION_INSTRUCTIONS — Intelligence / Evidence Integrity

Lead review: LEAD-020
Branch: `claude/social-bots-intelligence-repair-v2`

## Coordination loop

At session start and after every parent artifact checkpoint:

1. `git pull --ff-only`
2. `git fetch origin`
3. Read this file.
4. Read:
   `git show origin/chatgpt/social-bots-plan-20260920:social-bots/SESSION_ROUTER.md`
5. Read latest canonical CHATGPT -> CLAUDE lead entry.
6. Inspect `social-bots/worker-reports/intelligence-repair/LEAD_ACK.json`.
7. Update/push the heartbeat only when a real heartbeat is due or a material state transition occurs.
8. Continue the next dependency-ready repair below.

Do not rewrite this file.

## Current lead disposition

Accepted in LEAD-020:
- `SB-V13-001` — ACCEPTED engineering artifact.
- `SB-V14-001` — ACCEPTED engineering artifact.

Still requires repair:
- `SB-V05-001` — CHANGES_REQUIRED.
- `SB-V05-002` — CHANGES_REQUIRED / fail-closed pending accepted semantic-provider integration.
- `SB-V15-001` — CHANGES_REQUIRED.
- `SB-V16-001`, `SB-V17-001`, `SB-V20-002` — remain CHANGES_REQUIRED pending deeper independent lead source audit of the latest repair batch.

Do not restart accepted V13/V14 work. Do not add more higher-version expansion until the two explicit repairs below are submitted unless the lead changes this file.

## Next 1 — SB-V05-001 real HTTPS path repair

Preserve the good LEAD-018 trust-boundary work:
- static/internal trusted transport policy;
- no caller-grantable operational trust;
- evidence classes;
- operational bridge rejects fixtures/untrusted receipts;
- public-address validation/pinning;
- redirect fail-closed posture;
- extraction-status honesty.

LEAD-020 independent defect:

`UrllibFetcher._perform()` calls stdlib `http.client.HTTPSConnection` with a `server_hostname=` constructor keyword. Stdlib `HTTPSConnection` does not accept that keyword, so the actual trusted HTTPS live path fails before a successful retrieval.

Required repair:
1. implement a valid pinned-IP HTTPS connection that still performs TLS SNI and certificate verification for the original hostname;
2. the actual socket must connect to the already validated/pinned public IP — do not re-resolve the hostname after validation;
3. keep Host header semantics correct;
4. keep redirects fail-closed unless you implement/revalidate/re-pin every hop end to end;
5. add a regression that exercises the production HTTPS connection-construction path sufficiently to catch an invalid constructor/API signature;
6. retain HTTP path safety and all existing trust/evidence regressions;
7. do not claim fixture/stub transport evidence proves real live HTTPS.

Submit `SB-V05-001` with exact commit/tests and a truthful limitation statement. No real external network proof is required for this repair unless the environment already permits a safe public read at zero additional spend; fixture/unit tests remain engineering evidence only.

## Next 2 — SB-V15-001 persona-scoped production experiment boundary

Preserve the measurement-provenance repair already submitted:
- baseline/treatment bind to normalized observation IDs;
- metric semantic/kind/window compatibility checks;
- exact observation refs in learning trace;
- missing/incompatible data => INCONCLUSIVE rather than fabricated measurement.

LEAD-020 remaining defect:
- `Experiment` carries persona, but persistence/read helpers are still bot-wide (`_dir(bot)`, `load(bot, id)`, `load_all(bot)`). A normal production reader can enumerate/read another persona's private experiment state.

Required repair:
1. add authoritative bot+persona production save/load/list/read APIs;
2. normal persona-facing reads must never return a different persona's experiment;
3. raw bot-wide access may remain only if explicitly named/documented admin/internal and not used by normal production persona flows;
4. add mixed-persona regressions through the actual production read/list API;
5. preserve existing overlap/measurement/closeout behavior.

Submit `SB-V15-001` for lead audit.

## SB-V05-002

Keep the current fail-closed design stable unless V05-001 repair forces a narrow interface change:
- operational assessor policy stays static and empty until an accepted semantic provider is integrated;
- `KeywordSupportAssessor` / heuristic claim extraction remain diagnostic/test-only;
- operational stance requires trusted-operational evidence;
- do not build a second model gateway.

A future accepted Core adaptive provider may supply the operational semantic assessor/extractor integration.

## Pending lead audits — hold expansion

The latest repairs for:
- `SB-V16-001`
- `SB-V17-001`
- `SB-V20-002`

are submitted and may be useful, but are not accepted merely because the local suite is green. Preserve them while lead review catches up. Do not start V2.1/V2.2/V2.3 implementation from this lane.

## Heartbeat correction

Read `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`.

This lane remains in `BOOTSTRAP_15M` mode.

LEAD-020 found:
- `HEARTBEAT.json` reports sequence 4;
- `worker-reports/intelligence-repair/HEARTBEAT_LOG.jsonl` contains only the lead-seeded sequence 0 record.

Therefore no real bootstrap interval is currently accepted.

Rules now:
- **do not backfill** missing seq1-4 records;
- do not reset sequence merely to make the log look contiguous;
- continue prospectively from the current heartbeat snapshot sequence;
- every future real heartbeat must append the full record to `HEARTBEAT_LOG.jsonl` and be pushed;
- heartbeat entries intended to prove cadence must be approximately 15 minutes apart, not burst commits;
- artifact submission/blocker heartbeats may occur immediately, but burst state-transition updates do not replace the elapsed-time cadence proof;
- after at least 3 consecutive real approximately-15-minute future worker heartbeats are durably logged, remain on bootstrap cadence until `LEAD_ACK.json` explicitly sets `steady_hourly_authorized=true`.

Use `social-bots/bin/worker_heartbeat.py` if it preserves the truth rules above.

The heartbeat is GitHub coordination evidence, not proof of runtime correctness or V0.7 Social Bots liveness.

## Safety / ownership

Do not edit Core state/decision/reasoning/leasing/worker.
No public effects, account login unless separately authorized, network scanning, paid APIs/new spend, secrets, fake metrics/evidence, engagement manipulation or SwarmAI dependency.
