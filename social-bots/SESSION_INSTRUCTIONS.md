# SESSION_INSTRUCTIONS — Windows Core / V0.3 preserve + V0.4 acceptance repair

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-windows-core-host`
Lead review: LEAD-031

Heartbeat is observability only. Do not wait on heartbeat acceptance before coding.

At start/checkpoint:
1. `git pull --ff-only`
2. `git fetch origin`
3. read canonical `FAST_TRACK_EXECUTION.md`, `SESSION_ROUTER.md`, and `artifact-packets/SB-V04-004.md` with `git show`
4. inspect `worker-reports/windows-core/LEAD_ACK.json`
5. continue dependency-ready work without routine permission prompts.

## Preserve final V0.3 source/evidence

- `SB-V03-005` remains ACCEPTED at implementation `796d4e390bd135167e5de2ff8f586bc07ac7f370`.
- `SB-V03-004` source remains positive; Mac QA owns the independent lifecycle execution required for final acceptance.
- `SB-V03-006` remains final/prepared at evidence `436787b0a63fdae0e89c224a54054607e32b5187` with exact 130-test OK output.

Do not churn V03 unless independent QA supplies a concrete defect.

## Lead review of `76e96dde...` V04-004 attempt

Useful work, but **not acceptance-ready**.

Two tests do not isolate the variable named in the acceptance claim:
- `test_same_evidence_different_personas_diverge` changes persona AND evidence (`shared` -> `shared2`).
- `test_same_persona_different_evidence_diverges` does not hold persona/runtime context constant.

Also, all six tests force `SBOTS_REASONING=contextual`, which resolves to `contextual-deterministic-v1` with `adaptive=false`. Keep this suite as supplemental deterministic/context-sensitive engineering coverage, but it cannot prove the adaptive V0.4 divergence required by `SB-V04-002`.

Positive re-audit: preserve the production `bin/run_worker.py` adaptive-required default and fail-closed provider resolution. Do not regress it.

LEAD-031 still sees no new Claude worker-generated commit after `76e96dde...`. Continue the existing bounded repair now; do not wait for another lead message.

## Current assignment — SB-V04-004 repair only

Read canonical `artifact-packets/SB-V04-004.md` and implement the bounded repair:

1. Persona-only case: same exact evidence snapshot, objective, runtime state/history, duplication state and policy; vary only persona/workspace.
2. Evidence-only case: same exact bot/runtime, persona/workspace, objective, state/history, duplication state and policy; vary only evidence.
3. Keep at least three persona/workspace divergence comparisons including a cultural/Primandir workspace.
4. Keep deterministic contextual tests as diagnostics if useful.
5. Add a clean acceptance seam capable of consuming the sanitized real adaptive provider/proposal receipt from `SB-V04-005` without fabricating it.
6. Do **not** invoke another live model/provider call, API/PAYG, or any new-spend route. The one owner-authorized existing-subscription call belongs to the dedicated canary lane.
7. Preserve deterministic policy/authority/no-public-effect invariants.
8. Commit/push exact tests and report which portions are diagnostic vs still waiting on the real adaptive receipt.

Do NOT execute `SB-V04-005` here. Dedicated branch `claude/social-bots-v04-live-canary` exclusively owns the real subscription-authenticated canary.

## Reporting

Reports stay under `social-bots/worker-reports/windows-core/`.
Commit/push after the bounded repair; do not self-accept the artifact.

## Safety

No public effects, Anthropic API/PAYG or other new spend, destructive actions, secrets, fake evidence, or SwarmAI dependency.
