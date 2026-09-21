# Worker report — V2 engineering-acceptance harness prep (Mac QA lane)

- **Relates to:** SB-V20-099 (V2.0 engineering readiness) acceptance prep
- **Lane:** Mac QA / Integration Control (`claude/social-bots-mac-qa-control`)
- **Requested status:** SUBMITTED (preparation harness; not an acceptance claim)
- **Ownership:** QA/control only — NO runtime module imported or edited. The
  harness lives under `social-bots/qa/` and operates on record dicts (fixtures
  now; the real merged runtime's emitted records later).

## Deliverable

- `social-bots/qa/v2_acceptance_harness.py` — encodes the `V2_ENGINEERING_ACCEPTANCE.md`
  integration contract as record shapes + pure assertion helpers.
- `social-bots/tests/test_v2_acceptance_harness.py` — 20 tests over fixtures.

It does NOT fake an integrated runtime (the Core/Intelligence modules are not on
this branch); it is the assertion layer to point at those modules once merged.

## What it checks (maps to acceptance scenarios A–G + traceability)

- **Trace chain (Traceability acceptance):** `resolve_trace_chain` walks
  strategy_revision → growth_opportunity → audience/experiment/metric → raw
  evidence receipts; flags dangling refs, wrong-kind hops, and a chain that never
  reaches a provenance-labeled evidence receipt.
- **Persona/workspace isolation:** every persona-scoped record carries a known
  persona and may not reference another persona's record (cross-persona bleed).
- **Missing-vs-zero (C):** a distinct `MISSING` sentinel; a missing metric must be
  labeled absent, never carried as `0`; `experiment_should_be_inconclusive` when a
  required metric is missing.
- **Stale evidence (E):** evidence beyond the freshness window must be downweighted
  AND the revision must record a stale-source limitation.
- **Authority block (F):** an unauthorized opportunity may be recorded but its
  policy decision must be `BLOCKED`; global no-public-effect flag check.
- **Adversarial proposal (G):** `validate_proposal_shape` rejects unknown actions,
  out-of-[0,1] / NaN / inf / bool / string numerics, missing evidence/growth refs,
  and any proposal that illegally asserts authority/effect flags — BEFORE mutation.
- **Fixture-vs-operational:** engineering records must be fixture-labeled; an
  operational/live provenance in an engineering trace is rejected. This enforces
  the non-negotiable distinction (SB-V20-099 engineering vs SB-V20-004 operational).

## Test commands & results

```
cd social-bots && python3 -m unittest discover -s tests    # 38 passed
```

(18 SB-CTL-012 validator + 20 V2-harness tests.)

## How Core/Intelligence plug in later

Each runtime stage emits a record with `id`, `kind`, `persona`, and `*_refs`
back-links using the kinds this harness expects (`evidence_receipt`,
`metric_observation`, `experiment_result`, `audience_hypothesis`,
`growth_opportunity`, `strategy_revision_proposal`, `policy_decision`,
`strategy_revision`). Once merged, the integration acceptance test collects the
real records for a fixture-driven run and calls `check_global_invariants` +
`resolve_trace_chain` + the per-scenario helpers — no harness change needed.

## Requested status

**SUBMITTED** — harness/contract preparation for when Core + Intelligence merge.
