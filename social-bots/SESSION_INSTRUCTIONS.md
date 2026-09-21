# SESSION_INSTRUCTIONS — Windows Core / V0.4 acceptance repair

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-windows-core-host`
Lead review: LEAD-034

Heartbeat is observability only and MUST NOT block source work.

## Today's heartbeat soak — not started yet in durable evidence

Start prospectively now if this session is active:
- `FAST_5M`: T0, +~5m, +~10m, +~15m;
- then immediately `SOAK_15M_24H`: every 15 minutes for 24 hours;
- append every timed record to `worker-reports/windows-core/HEARTBEAT_LOG.jsonl` and push;
- no synthetic/backfilled timestamps;
- stage heartbeat files only for heartbeat commits where practical;
- keep engineering work running in parallel.

LEAD-034 verified the durable Core log still ends at seq14 `2026-09-21T08:37:18Z` in the old `BOOTSTRAP_15M` mode. No `FAST_5M` T0 exists yet.

## Preserve V0.3

- Final V03 implementation: `796d4e390bd135167e5de2ff8f586bc07ac7f370`.
- Final V03 evidence: `436787b0a63fdae0e89c224a54054607e32b5187`, exact 130 tests OK.
- `SB-V03-005` remains ACCEPTED.
- `SB-V03-004` awaits independent lifecycle execution; do not churn V03 absent a concrete QA defect.

## Current assignment — SB-V04-004 repair only

Read canonical `artifact-packets/SB-V04-004.md` and implement the bounded repair:
1. Persona-only comparison: hold evidence/objective/runtime/history/dedup/policy constant; vary only persona/workspace.
2. Evidence-only comparison: hold bot/runtime/persona/workspace/objective/history/dedup/policy constant; vary only evidence.
3. Keep at least three persona/workspace comparisons including a cultural/Primandir workspace.
4. Keep deterministic contextual tests only as diagnostics; `contextual-deterministic-v1` is `adaptive=false` and cannot prove V0.4.
5. Add a clean acceptance seam that can consume sanitized real adaptive proposal/provider evidence from `SB-V04-005` without fabricating it.
6. Do NOT invoke another live model/provider call from Core. The authorized live subscription call belongs to the dedicated canary lane.
7. Preserve deterministic policy/authority/no-public-effect invariants.
8. Commit/push source/tests/report and distinguish diagnostic evidence from acceptance evidence.

## Safety

No public effects, Anthropic API/PAYG/new spend, destructive actions, secrets, fake evidence, or SwarmAI dependency.
