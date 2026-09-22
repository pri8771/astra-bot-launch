# Whole-plan audit — lead revision for the next round

## Evidence boundary

Audited planning baseline: canonical `eeb4a39a9bcd813d8ca691db142851206129bf50`. Active Fable branch observed at `f7c1f007ebce6e8d4a915c4b5eeadb3c02196f81`; Cursor at `488ce0c720d857473ab9f2ce448d9197a955df14`; QA at `a508c06bc87a9f36b7d6347eeb86cde62f4d9907`. Refresh these at the next checkpoint. This is a plan/integration review, not a claim that runtime tests were independently rerun or that unseen local worker changes were audited.

Coverage: recovery V0.4–V0.7, execution V0.8–V1.7, V1.8–V3.0 architecture, milestone manifest, the V2.0–V2.3 implementation specification, specialist budget contract and current coordination. Deep review concentrated on interfaces, dependency semantics, evidence provenance, state/worker isolation and production integration. No active runtime code is changed by this package.

## Findings and resolutions

### F1 — Isolated modules can finish while the product remains unwired

`V20_TO_V23_IMPLEMENTATION_SPEC.md` section 7 leaves H1–H4 outside the implementation slices. The architecture can therefore accumulate green modules without strategy, planning or specialists affecting actual scheduled work.

Resolution: NR-14–NR-17 make all four production hooks explicit. NR-20 exercises the normal production entrypoints with isolated fixture dependencies; NR-21 then uses real inputs under grants. Neither direct helper-function tests nor the mere presence of classes closes operational V2.3.

### F2 — Build prerequisites and live acceptance prerequisites are mixed

The proposed readiness artifact SB-V23-099 depends on SB-S20-007, while that slice combines a fixture rehearsal with a LIVE strategy-change requirement. A flat accepted/not-accepted dependency cannot represent both honestly. Some detailed cards also retain pre-adoption dependency prose and PROPOSED headers while lead coordination says adopted.

Resolution: NR-01 produces explicit per-artifact predicates for build readiness, integrated engineering evidence and operational acceptance. SB-S20-007 rehearsal is a distinct evidence subrecord; it never flips the LIVE artifact to ACCEPTED. Parent milestone requirements remain intact. Resolve these semantics before selecting work, rather than silently deleting inconvenient dependency edges.

### F3 — Registry truth and summary truth can diverge

Historical recovery registry rows remained READY/PLANNED while later lead reviews described SUBMITTED/CHANGES_REQUIRED. Compact startup state, management pointers and old execution documents can lag the newest lead review.

Resolution: reconcile by exact lead decision and evidence SHA; generate compact summaries from one canonical status source. A worker may submit evidence but not overwrite lead status. Reject a stale instruction snapshot for operational effects. This package preserves historical records instead of rewriting them to look consistent retroactively.

### F4 — Specialist wire schema is inconsistent across documents

The canonical specialist schema was raised to version 2, but the adopted implementation spec says all dataclasses have schema_version=1. Some packets still claim field-for-field compatibility with the earlier free-form authority shape.

Resolution: NR-02 adds an explicit compatibility table and serialization tests. Specialist records use v2; strategy/planner types use their declared versions. Unknown fields and widening authority fail closed. Migration is explicit, never a silent dictionary merge.

### F5 — A provider's self-description is not a security boundary

SB-S23-007 allows a supplied provider to be treated as a fixture based on `adaptive == False`. Arbitrary callables can lie about that attribute; a configuration label also need not describe the actual object being called.

Resolution: NR-03/NR-18 require policy-owned provider construction and brokered capabilities. Tests may inject fixtures into an isolated test runner, but production must not accept a caller-supplied flag as proof of no network/model activity. Validate actual dispatch and durable call reservations at the deepest callable/spawn boundary.

### F6 — Timeouts and path wrappers need accurately scoped guarantees

The specialist plan uses ThreadPoolExecutor, cooperative Deadline checks and a Python Sandbox wrapper. Those can structure trusted helpers; they do not by themselves stop a running thread or deny arbitrary same-process filesystem access.

Resolution: NR-18 limits default specialists to trusted adapters and brokered data/tools; no generated Python or arbitrary shell. NR-19 adds a killable execution boundary for blocking provider/process work, process-tree cleanup and rejection of late results. Claim OS isolation only when an actual OS restriction has been installed and tested. A separate process alone is not a filesystem permission boundary.

Python's documented Future cancellation does not cancel already-running work. See https://docs.python.org/3/library/concurrent.futures.html . Claude's sandboxing documentation distinguishes filesystem/network isolation from approval prompts: https://code.claude.com/docs/en/sandboxing . These are design constraints, not claims that our current runtime implements them.

### F7 — Atomic replacement is not immutable, multi-file storage

The spec calls version files immutable while proposing a generic atomic write helper. Replacement may overwrite an existing destination; writing version, HEAD and HISTORY separately also leaves crash windows. Optional fence=None is appropriate only in an isolated engineering store, not as a production bypass.

Resolution: NR-13 defines no-overwrite version creation, compare-and-swap publication under the correct existing fence, one authoritative commit record, and index recovery. Crash tests stop after each durability boundary. Production persistence requires a validated fence/transaction; test stores are explicitly separate. Reference: https://docs.python.org/3/library/os.html#os.replace .

### F8 — Bot operation and code implementation are different workers

A scheduled bot cycle returning NO_ACTION does not prove that a Claude development worker read a code assignment, changed a file, tested and pushed it. A heartbeat is only a start receipt, not proof that work continues indefinitely.

Resolution: NR-07–NR-09 separately prove the bot scheduler, bounded engineering-worker adapter and two actual lead/worker cycles. Every stage has its own receipts and authority. An existing running ChatGPT/Claude chat is not a scheduler or a background-service guarantee.

### F9 — Dry-run learning must not become invented performance

V0.6 requires experiment registration and persisted learning before public publication. It cannot truthfully conclude an audience experiment succeeded or fabricate a measured baseline.

Resolution: NR-06 registers a prospective experiment as PLANNED/AWAITING_PUBLICATION and records observation/evidence/review lessons, not engagement outcomes. Missing analytics remain missing. Real performance learning begins when compatible measured outcomes exist.

### F10 — Current network retrieval is not necessarily useful current evidence

The existing input freeze used example.com and an RFC. Those are useful transport controls, but a retrieved timestamp alone does not make evidence editorially current or sufficiently discriminating for persona/evidence tests.

Resolution: select decision-relevant primary evidence, freeze exact bytes and prompts before a bounded authorized batch, and define semantic comparison criteria before observing outputs. Five calls demonstrate behavior on those cases; they are not a statistical guarantee of general causal reliability. No retries to cherry-pick a passing result.

### F11 — A real route may be unavailable or not free

The roadmap names five platforms, but support, scopes, quota, review requirements and subscription entitlements are external constraints. A fabricated route, undocumented browser fallback or newly purchased API cannot make the milestone green.

Resolution: NR-10 creates one verified capability dossier and a precise owner action list. Preserve all five V0.8 requirements unless the owner explicitly changes product scope. Unsupported/blocked is an honest result, not automatic route acceptance.

### F12 — Full V3.0 needs feedback integration, not another set of libraries

The later plan names memory, segments, trends, transformations, allocation, self-evaluation and brands. Their consumers and release evidence need to be explicit.

Resolution: NR-23–NR-32 wire each capability back into the same production cycle, add scoped migration/retention/recovery, and finish with a concurrent multi-brand run. The V2.4–V3.0 build spec defines input/output/consumer/failure/test contracts instead of demanding another roadmap essay.

## What is deliberately not promised

This revision can remove known ambiguity and make the next round resumable. It cannot honestly promise that model outputs, account approvals, real observation windows, host availability, or future defects will all cooperate in one chat session. A bounded failed live test remains failed. The expected end state is either accepted evidence or an exact bounded blocker dossier, never manufactured completion.
