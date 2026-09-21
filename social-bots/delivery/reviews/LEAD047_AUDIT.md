# LEAD-047 source audit and required repairs

## Scope and evidence

Canonical read: 2cda05b4d0144687ca842ac4fe104aa3824e6039. Fable branch: 72a55319cf41f9910c5d3b9623129de3ac0eea31, latest material submission a204ad0827748a4e9661f1945b8e025d53d0ae09. Cursor: 74a515b7f3e30c94979e0f66dc6daae66daed571. QA: d57a10459dc441e94015168801254771d8e96b1a. Fresh branch recheck was unchanged at this audit cutoff; any subsequent unpushed code is outside this review.

Fable submitted nine ENGINEERING artifacts: strategy store and S23-001..008. Worker suite: 523 discovered, 521 passed, 2 skipped. The full runtime suite was not independently executed in this lead environment. The actual heartbeat log has one SESSION_ONCE for s-20260921T211438Z-d5589881 and reports a Linux vm/Python 3.11.15, not a verified owner Mac host. The latest branch acknowledgement is a pause instruction, not new implementation.

Six isolated source-excerpt probes used harmless local sentinels, fake grant support and temporary files. Their class/method bodies come from the inspected source, while dependencies are test doubles. They reproduce six failure scenarios, not six fresh full-repository acceptance tests. See LEAD047_PROBES.json and probes/. Exit zero for these historical probes means defects reproduced, not product passed.

## Required repairs before operational use

**P0 — R07-041 direct callable bypass persists.** `runtime/reasoning.py::ModelReasoningProvider.propose` invokes its callable with no canonical authorization check. The sentinel executed once with no grant. Close the deepest boundary and test direct-library calls, not only worker CLI entrypoints.

**P0 — Specialist label bypass.** `runtime/specialist_budget.py::BudgetedProvider` trusts the supplied adaptive flag. A false-labelled object executes despite a refused route and records authorization_required=false. Production must construct only policy-owned provider capabilities; no arbitrary callable exemption. Test real production factory refusal with a harmless sentinel.

**P0 — Accounting follows dispatch and is wrapper-private.** Despite its BEFORE comment, propose calls the provider before record_call. Two concurrent calls and one reentrant call exceed a one-slot budget; two wrappers each using the same mocked one-slot grant also execute. Reserve atomically and durably before dispatch across parent/child/wrappers/processes. Exceptions/crashes remain consumed or uncertain. Revocation/expiry must be checked at dispatch. Do not fix only the comment or add a per-object counter.

**P1 — Adopted evidence can change before consumption.** `_kept_doc` in specialist_integrator.py reads retained JSON and checks schema but not the receipt's hash. The probe changed ResearchResult bytes and the reader consumed the changed claim with the old digest. Verify canonical path, file type, actual hash and schema at consumption; avoid a check/read race by validating the bytes actually used. Add wrong-scope, replaced-file, symlink and late-write cases.

**P1 — Deadlines and cleanup need integration repair.** specialist_lifecycle.py uses ThreadPoolExecutor and cooperative Deadline. There is no outer finalizer covering every verify/receipt/I/O failure, and no hard termination of a non-cooperative adapter. This is source inspection, not a reproduced real-host hang in this review. Add supervised blocking execution, cancellation before cleanup, lease/result fencing and finally-based cleanup. Keep trusted helper scope distinct from arbitrary-code OS isolation.

**P1 — Strategy persistence is not a transaction.** strategy.py writes version, history, HEAD, activated history separately; fence=None is allowed; active() does not verify historical hashes. Source review identifies crash/tamper risk; not a full crash reproduction here. Use expected-version publication with a durable authoritative commit and recoverable projections. Test actual process interruption at each boundary and no late/stale commit.

**P1 — The product is not connected yet.** Strategy storage and fixture specialist lifecycle do not implement strategy revision/planner/execution integration. H1–H4 and DEVELOPMENT_ARTIFACT dispatch remain mandatory. A standalone fixture bundle and a bot NO_ACTION cannot substitute for real integrated/scheduled behavior.

## Review decision

Do not accept operational V2.3, S23 budget/lifecycle safety, or R07-041 from current evidence. Preserve all submissions. Release Fable to repair and integrate shared source on its branch rather than keep it paused waiting for stale lanes. Begin with the P0 negative regressions, then retained-output integrity/finalization and the remaining implementation. Independent review and all real-world gates still control acceptance.

No live model call, account setup, publication, new spend, scheduler installation or main merge was executed by this audit. No artifact is marked ACCEPTED by these observations.
