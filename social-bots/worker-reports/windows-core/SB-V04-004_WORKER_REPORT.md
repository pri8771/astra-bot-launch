# SB-V04-004 — Worker report (Lane 1 / Windows Core Builder)

- Artifact: SB-V04-004 — Persona/evidence divergence acceptance suite (bounded repair)
- Lane: Lane 1 / Windows Core Builder
- Branch: `claude/social-bots-windows-core-host`
- Base commit: `798385573ced0c76f7c6773cf852825ecced7550`
- Status submitted for independent review: **NOT self-accepted.** Lead/QA owns acceptance.

## What the packet required (CHANGES REQUIRED) and what was done

The prior submission's two divergence tests were confounded and used the
non-adaptive contextual provider (`adaptive=false`), which cannot prove V0.4
adaptive behavior. This repair:

1. **Fixed persona-only isolation.** `ContextualDiagnosticTest.test_persona_only_divergence_diagnostic`
   now proposes the SAME signal/objective/state to multiple personas, varying ONLY
   persona. Isolation is enforced by `reasoning_receipt.assert_single_variable(...,
   "persona")`, so any difference is attributable to persona alone. (Previously it
   changed both persona and the evidence URL.)

2. **Fixed evidence-only isolation.** `ContextualDiagnosticTest.test_evidence_only_divergence_diagnostic`
   holds one persona/objective/state constant and varies ONLY the evidence,
   enforced by `assert_single_variable(..., "evidence")`. (Previously it changed
   persona and runtime as well.)

3. **Added the adaptive acceptance path** (`AdaptiveReceiptDivergenceTest`). This
   exercises the real adaptive provider path — `ModelReasoningProvider`,
   `adaptive=True`, via `reasoning.register_model_callable` — by REPLAYING sanitized
   adaptive receipts. It proves:
   - **Persona-only divergence across three workspaces including the cultural
     Primandir workspace** (`social-a`, `social-b`, `cultural-primandir-atman`) on
     identical evidence/objective/state, with every pair proved single-variable and
     materially divergent (>=3 comparisons).
   - **Evidence-only divergence** for a fixed persona/state, single-variable and
     materially divergent.
   No live model call is made; the one authorized live invocation stays reserved
   for SB-V04-005.

4. **Preserved the contextual deterministic tests as fast diagnostics only.**
   `ContextualDiagnosticTest` is explicitly labeled `adaptive=False` and includes a
   scope guard (`test_provider_is_diagnostic_only_not_the_live_canary`) plus a
   fail-closed-when-adaptive-required test. `contextual-deterministic-v1` does NOT
   satisfy final adaptive acceptance.

5. **Added a clean acceptance seam for the real SB-V04-005 receipt.** New module
   `runtime/reasoning_receipt.py`:
   - loads/validates a **sanitized** receipt (schema, `adaptive=true`, no authority
     keys anywhere, no fabricated evidence refs, `context_digest` integrity);
   - reconstructs a schema-clean `ReasoningProposal` and replays it through the
     adaptive provider path;
   - fails closed (returns `None` → `BLOCKED_REASONING_UNAVAILABLE`) when no receipt
     matches the context;
   - distinguishes `sanitized-real-canary` from `synthetic-seam-fixture` so a
     fixture can never be mistaken for the canary.
   Intake directory `social-bots/acceptance/sb-v04-005-receipts/` (with README) is
   where Lane 3 drops the sanitized receipt; `RealCanaryReceiptAcceptanceTest`
   auto-consumes it when present and skips truthfully until then.

6. **No additional live model invocation from Core.** Confirmed — this lane makes
   no network/provider/subprocess model call. Where a real adaptive proposal is
   needed for final acceptance, the harness consumes the SB-V04-005 receipt.

## Invariants preserved (see TEST_RESULTS for the exact tests)

- adaptive-required production default (unchanged `resolve_provider`);
- fail-closed provider behavior (replay + contextual both block when required);
- REASONING_PROPOSAL schema validation (every reconstructed proposal validated;
  malformed/authority-bearing receipts rejected);
- deterministic authority/policy boundary (recommendation is advisory; policy
  selects by its own ranking; authority-smuggling receipt refused);
- no-public-effect boundary (replayed CREATE is queued, `publish_authorized=False`,
  `published=False`).

## Files changed / added

- `runtime/reasoning_receipt.py` — NEW: sanitized adaptive-receipt seam.
- `tests/test_reasoning_receipt.py` — NEW: 18 seam unit tests.
- `tests/test_v04_divergence_acceptance.py` — REWRITTEN: repaired isolation +
  adaptive acceptance + real-canary gate.
- `acceptance/sb-v04-005-receipts/README.md` — NEW: real-receipt intake contract.
- `worker-reports/windows-core/CURRENT_PROGRESS.md`,
  `SB-V04-004_TEST_RESULTS.md`, `SB-V04-004_WORKER_REPORT.md` — reports.

## Product-state preservation

- Final V0.3 implementation/evidence untouched. No V0.3 source or test modified.
- No live canary executed; SB-V04-005 execution not touched; no provider receipt
  fabricated.

## Open items for independent review (not for Core to self-decide)

- **Final adaptive acceptance is gated on the real SB-V04-005 sanitized receipt.**
  Until Lane 3 drops it in `acceptance/sb-v04-005-receipts/`, the real-canary
  acceptance test skips. The seam and the persona-only/evidence-only isolation are
  fully verified now against clearly-labeled synthetic seam fixtures (never
  represented as the canary).
- The deterministic contextual provider treats two GENERAL personas alike (it keys
  on persona kind / source requirements, not voice). This is a documented
  limitation of the diagnostic layer and a reason the adaptive layer is required; it
  is not a divergence defect.

Do not treat this report as acceptance. Lead/independent QA owns the SB-V04-004
acceptance decision.
