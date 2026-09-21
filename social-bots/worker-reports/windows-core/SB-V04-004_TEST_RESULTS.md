# SB-V04-004 — exact test commands and results

- Lane: Lane 1 / Windows Core Builder
- Branch: `claude/social-bots-windows-core-host`
- Base commit before this work: `798385573ced0c76f7c6773cf852825ecced7550`
- Python: 3.11.15
- Runner: `python3 -m unittest` (repo has no pytest dependency)
- Working dir for all commands: `social-bots/`
- Environment: single POSIX host, offline. No live model/provider call, no network,
  no spend, no public effect. (Executed on Linux; the suite is OS-independent
  stdlib `unittest`.)

## 1. Seam unit tests (new)

```
$ python3 -m unittest tests.test_reasoning_receipt
Ran 18 tests in 0.004s
OK
```

Covers: receipt schema validation, `adaptive=false` rejection, authority-key
smuggling rejection (recursive), fabricated-evidence-ref rejection, out-of-range
estimate rejection, recommended-not-among-alternatives rejection, context_digest
tamper detection, single-variable isolation helper (persona-only / evidence-only /
confounded detection), material-divergence detection, replay callable
match/fail-closed, and disk load + real-canary kind filtering.

## 2. Divergence acceptance suite (repaired + extended)

```
$ python3 -m unittest tests.test_v04_divergence_acceptance
Ran 12 tests in 0.041s
OK (skipped=1)
```

- 11 passed; 1 skipped.
- The single skip is `RealCanaryReceiptAcceptanceTest.test_real_canary_receipts_replay_through_adaptive_path`,
  which skips with: "awaiting SB-V04-005 real canary receipt in
  `social-bots/acceptance/sb-v04-005-receipts`". This is intentional and truthful:
  the real sanitized receipt does not exist yet (canary unexecuted), and Core does
  not fabricate it. The seam + isolation are fully verified by
  `AdaptiveReceiptDivergenceTest`.

Acceptance-layer provider identity: proposals resolve through
`ModelReasoningProvider` (`provider_id="model-adaptive-v0"`, `adaptive=True`);
replayed receipts carry inner `provider_id="claude-code-subscription-v1"`.

## 3. Reasoning + policy + decision regression

```
$ python3 -m unittest tests.test_reasoning tests.test_reasoning_cli \
    tests.test_reasoning_contextual tests.test_reasoning_contract \
    tests.test_policy_boundary tests.test_decision
Ran 63 tests in 0.180s
OK
```

## 4. Full Social Bots suite

```
$ python3 -m unittest discover -s tests -p 'test_*.py'
Ran 160 tests in 1.222s
OK (skipped=1)
```

Baseline before this work was 136 tests. This change adds 24 tests
(18 seam + net 6 in the acceptance suite) with no regressions. The single skip is
the real-canary gate described above.

## Invariants explicitly re-verified

- Adaptive-required production default: unchanged; `resolve_provider(require_adaptive=True)`
  returns an adaptive provider or an unavailable one. Diagnostic contextual provider
  still fails closed under adaptive-required (both in the acceptance suite and
  `test_reasoning_contextual`).
- Fail-closed provider behavior: `AdaptiveReceiptDivergenceTest.test_replay_fails_closed_when_no_receipt_matches`
  → `blocked_reasoning_unavailable`, signal NOT consumed.
- REASONING_PROPOSAL schema validation: every reconstructed proposal passes
  `reasoning.validate_proposal`; malformed/authority-bearing receipts are rejected.
- Deterministic authority/policy boundary: `test_recommended_action_is_advisory_policy_selects_by_ranking`
  (policy overrides a NO_ACTION recommendation) and
  `test_authority_smuggling_receipt_is_refused`.
- No-public-effect boundary: `test_replayed_create_is_queued_unpublished_with_no_public_effect`
  (`publish_authorized=False`, `published=False`, queued only).
