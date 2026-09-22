# V0.4 causal-divergence decision — 2026-09-21

## Decision

Do **not** weaken the V0.4 acceptance contract and do **not** treat receipt replay, fixtures, deterministic contextual reasoning, or injected outputs as proof that a live adaptive model causally changes behavior when persona/evidence changes.

The existing Core replay seam is useful engineering evidence for:
- context isolation;
- receipt integrity;
- adaptive-provider plumbing;
- schema validation;
- deterministic policy authority;
- fail-closed behavior;
- no-public-effect invariants.

It is **not** live causal-divergence evidence.

Therefore:
- `SB-V04-002` remains **CHANGES_REQUIRED**;
- `SB-V04-004` remains **CHANGES_REQUIRED**;
- `SB-EVD-002` remains **WITHHELD**;
- V0.4 remains **in progress**.

No further live Claude/model calls are authorized by this decision.

## Why one accepted live call cannot close the gate

The accepted first chronological canary proves one real adaptive path execution under one bounded context.

A causal-divergence claim requires observing model output under a controlled counterfactual:
- same evidence/state/objective, changed persona/workspace; or
- same persona/state/objective, changed evidence.

A single live observation has no counterfactual observation. Replaying its output under changed contexts tests plumbing and policy, not the model's response to those changed inputs.

## Cleanest legitimate closure path

If the owner later authorizes additional existing-subscription calls, preregister a minimal bounded counterfactual matrix before execution.

Use the accepted first canary as the baseline cell where its captured context is suitable.

Minimum likely additional calls: **3**.

1. Baseline accepted call: Persona A + Evidence X — already exists.
2. New authorized call: Persona B + exact same Evidence X.
3. New authorized call: Persona C (including a cultural/Primandir workspace) + exact same Evidence X.
4. New authorized call: Persona A + materially different Evidence Y.

This gives:
- three pairwise persona comparisons from A/B/C under identical Evidence X;
- one evidence-only comparison A+X vs A+Y;
- no redundant live calls.

All unrelated variables must be frozen and hashed before execution:
- objective;
- runtime state;
- prior history/hypotheses;
- duplication state;
- policy posture;
- evidence bytes for X;
- persona workspace identities;
- provider/version;
- prompt/schema/tool identity.

Every call must remain:
- existing-subscription only;
- no API/PAYG;
- zero public effect;
- no credentials in Git/logs;
- proposal-envelope capture only;
- deterministic policy authoritative.

The matrix must be owner-authorized explicitly before any call.

## Product sequencing while V0.4 is blocked

V0.4 acceptance blockage does **not** require stopping independent engineering.

Allowed in parallel:
- remaining V0.5 non-live/current-source and safety work;
- V0.6 dry-run orchestration scaffolding that does not claim adaptive causal proof;
- V0.7 scheduler/worker infrastructure engineering with no public effects;
- V0.8 connector contracts/stubs with no credential or real-account actions.

Not allowed:
- claim V0.4 complete;
- claim V0.6 complete if its adaptive step depends on unresolved V0.4 causal acceptance;
- public posting;
- new spend;
- additional live adaptive/model calls without explicit owner authorization.

## Status of the Core replay seam

Core `a19046d57ad7e90834d7a5d98b97da21c4491504` is retained as useful engineering support.

Its deterministic single-variable isolation checks and adaptive receipt replay seam should remain regression coverage, but they are not milestone acceptance evidence for causal model divergence.

## Future acceptance procedure

When/if owner authorization is granted:
1. lead preregisters exact four-cell matrix and hashes;
2. execute only the minimum authorized calls;
3. preserve raw bounded proposal receipts and provider identity;
4. independently verify variable isolation and material divergence;
5. accept/reject `SB-V04-002` and `SB-V04-004`;
6. then independently finalize `SB-EVD-002` and V0.4 promotion.

Until then, V0.4 is truthfully blocked on live counterfactual evidence, not on an implementation defect.
