# Mac QA / Integration Control Wave 1

Worker instance: Mac Claude
Suggested branch: `claude/social-bots-mac-qa-control`

This lane exists to help the lead stay ahead without colliding with the two Windows implementation sessions.

## Branch/base

Start from the latest canonical coordination branch:
`chatgpt/social-bots-plan-20260920`

Do NOT branch from Core or Intelligence implementation.

This lane should not edit runtime implementation modules.

## Wave order

### 1. SB-CTL-012 — artifact graph validator/readiness reporter
Read `artifact-packets/SB-CTL-012.md`.

Build and test the validator.

### 2. SB-CTL-006 — CI control, if not already claimed by a Windows worker
Implement only the CI/control part:
- run artifact validator;
- validate JSON;
- run unit tests when a branch contains the runtime test suite;
- no secrets/network/model calls/deployment.

Before implementing SB-CTL-006, check whether `claude/social-bots-windows-core-host` has already submitted or claimed it in a worker report/message. If yes, do not duplicate it.

### 3. Integration acceptance harness preparation
Without editing runtime source, add test fixtures/contracts/helpers for `V2_ENGINEERING_ACCEPTANCE.md` that can later be pointed at the merged Core + Intelligence implementation.

Focus on:
- fixture labeling;
- traceability assertions;
- persona-scope assertions;
- missing/stale evidence scenarios;
- authority-block scenario;
- no public effect.

If runtime imports are not yet available on this branch, keep this as harness/schema fixtures rather than fake passing integration tests.

## Hard ownership boundary

Do not edit:
- runtime/state.py
- runtime/decision.py
- runtime/reasoning.py
- runtime/leasing.py
- runtime/worker.py
- runtime/collector.py
- runtime/factcheck.py
- runtime/metrics.py
- runtime/audience.py
- runtime/experiment_engine.py
- runtime/content_intelligence.py
- runtime/community.py
- runtime/growth_evaluator.py

Do not change canonical artifact statuses.

Submit worker reports under:
`social-bots/worker-reports/mac-qa/`

## Purpose

This lane should reduce lead review/integration cost, not create a third competing implementation architecture.
