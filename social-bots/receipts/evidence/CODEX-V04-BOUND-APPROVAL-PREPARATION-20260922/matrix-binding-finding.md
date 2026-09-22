# Confirmed execution-binding gap

Exact accepted source `8c86898d1c6641adbf5c9884e1aa7ab2923b1af3` does re-check internal context/prompt consistency immediately before dispatch: `_execute_one_case` rebuilds a `ReasoningContext` and refuses when its context digest or prompt-context digest differs from the selected `PreparedCase`. `verify_written` also detects hand edits that leave stale recorded digests. Those controls are real and should remain.

They are not equivalent to binding authorization to the owner-reviewed matrix. `execute_batch` accepts any caller-provided, internally consistent `PreparedMatrix`; `authorize` checks only artifact, lane, run scope, provider mode, call count, expiry, safety booleans, and process posture. It never checks Git identity or a matrix/freeze digest.

The offline reproducer rebuilt a different, internally consistent five-case matrix by changing the objective, while preserving `run_scope=v04-divergence-freeze`, `lane=cursor-recovery`, artifact and case count. P0 changed from reviewed context `sha256:500389...` / prompt `sha256:44e407...` to unreviewed context `sha256:a7cfa2...` / prompt `sha256:fa4759...`. A schema-valid temporary manifest for the existing artifact/run/lane passed the real authorization gate. The runner constructed and reached an in-process sentinel's `propose` method. The sentinel raised `KeyboardInterrupt` before any external provider/network action. One budget slot was created only inside the temporary directory and the directory was removed.

This confirms that a consistent matrix swap can execute under the same authorization scope. It is stronger than field-absence inference. The existing pre-dispatch consistency check protects against mismatched runtime inputs, but faithfully validates the swapped matrix rather than the matrix the owner reviewed.

The same causal path confirms source identity is not enforced: neither `authorize` nor `execute_batch` reads Git HEAD/tree, and the manifest has no required source identity. This reproduction ran accepted source; it did not modify source because proving an altered checkout would add no new causal information and would violate the bounded no-source-edit instruction.

## Smallest enforceable repair

Extend the canonical manifest and `ExecutionGrant` with required exact bindings:

- `source_sha`
- `source_tree`
- `prepared_matrix_sha256` (or `freeze_manifest_sha256` plus a defined closure over matrix, prompt and evidence files)

Before constructing `CallBudget` or the provider, `execute_batch` must:

1. verify current source SHA/tree using an injected/read-only trusted build identity or immutable packaged build identity;
2. hash the exact matrix bytes and prompt/evidence closure loaded for execution;
3. compare those values to the grant;
4. run existing `verify_written`/isolation checks;
5. refuse before budget/provider construction on any mismatch.

Bind each reserved slot/receipt to the source and matrix digest so later review can prove which reviewed bytes were invoked. Keep owner approval and lead manifest separate; adding fields must not activate authority.

Evidence: `matrix-binding-repro.py` and `matrix-binding-repro.log`. No model/provider/network/account/host/scheduler action or canonical/runtime grant file occurred.
