# V2.0 engineering-readiness integration acceptance plan

Lead-owned acceptance design for SB-V20-099.

## Purpose

Prove the software stack through V2.0 composes truthfully before real public/account evidence is available.

This is engineering readiness, NOT operational V2.0 promotion.

## Required integration path

1. Captured evidence receipt.
2. Normalized metric observations and/or experiment evidence.
3. Audience hypothesis update.
4. Experiment result or explicit INCONCLUSIVE state.
5. GrowthOpportunity generation.
6. StrategyRevisionProposal generation.
7. Deterministic policy validation.
8. Strategy update or NO_CHANGE.
9. Durable revision history + evidence links.

## Test scenarios

### A. Positive measured evidence
Fixture is clearly labeled fixture.
- Two experiments show consistent improvement on a format/platform.
- Growth evaluator recommends increased learning/allocation.
- Strategy engine proposes bounded increase.
- Policy accepts.
- Strategy version increments.
- Evidence chain is inspectable end to end.

### B. Contrary evidence
- Prior favored strategy receives consistent negative results.
- Audience hypothesis confidence drops.
- Growth recommendation changes.
- Strategy revision reduces/reverses prior allocation.

### C. Missing data
- Required metrics absent.
- Missing remains missing, not zero.
- Experiment becomes INCONCLUSIVE.
- Growth evaluator either requests more evidence or returns no recommendation.
- Strategy does not fabricate optimization.

### D. One anomalous result
- Single extreme observation conflicts with broader evidence.
- Engine does not swing allocation without configured confidence/evidence bar.

### E. Stale evidence
- Old evidence beyond freshness policy.
- Confidence decays or result is downweighted.
- Revision record identifies stale-source limitation.

### F. Authority block
- Growth opportunity recommends a platform/action not currently authorized/connected.
- Strategy may record opportunity but execution remains BLOCKED.
- No public effect occurs.

### G. Adversarial cross-lane payload
- malformed numeric fields, unsupported metric semantics, missing evidence refs, unknown action.
- validation rejects before strategy mutation.

## Traceability acceptance

Every final strategy revision must trace:
strategy_revision -> growth_opportunity -> audience/experiment/metric records -> raw evidence refs.

## Non-negotiable distinction

Engineering tests may use fixtures.
Fixtures must never be labeled live/operational evidence.
SB-V20-099 can be accepted on engineering evidence.
SB-V20-004 operational V2.0 cannot.
