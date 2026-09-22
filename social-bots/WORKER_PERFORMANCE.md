# Social Bots worker performance

Purpose: track implementation reliability by artifact and task type. Worker submissions never self-accept.

Current lead review: **LEAD-047** (`lead-reviews/LEAD-047_DELIVERY_RELEASE_20260921.md`).  
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

## Current verified activity

### Fable Fast-track — RELEASED AS PRIMARY INTEGRATOR / AWAITING FRESH WORKER SESSION

- Latest verified material worker checkpoint remains `a204ad0827748a4e9661f1945b8e025d53d0ae09` from session `s-20260921T211438Z-d5589881`.
- Fable submitted **SB-S20-001** and **SB-S23-001..SB-S23-008** as engineering evidence. Worker baseline reports **523 discovered / 521 passed / 0 failed / 0 errors / 2 skipped**.
- `SB-S23-008` remains fixture-class evidence; it does not prove hard process isolation or operational V2.3.
- LEAD-047 source review reproduced six failure scenarios with isolated copied-source/test-double probes: direct no-grant callable execution; false fixture/capability dispatch; concurrent, reentrant and independent-wrapper budget overruns; and consumption of tampered retained output. Those probes are defect reproduction, not a full-checkout acceptance run.
- Additional source-review risks remain: hard timeout/finalization, crash-consistent strategy publication, final-content review binding, missing strategy/planner pieces, H1–H4 integration, and distinct DEVELOPMENT_ARTIFACT dispatch.
- Canonical delivery campaign now releases Fable as **sole primary implementation/integration owner**, including shared recovery/runtime repair. The old pause and new-files-only restriction are superseded.
- LEAD-047 branch handoff was delivered directly through Fable head `347de2b5c91c774670c3b884cc542c88fa6eabfa`. That head is lead-authored coordination, **not** a worker acknowledgement, heartbeat, test run or implementation result.
- **Disposition:** material engineering submissions preserved; no operational V2.3 acceptance; next worker evidence must come from a fresh session against `delivery/FINAL_RUN.md`.

### Cursor Recovery — PARKED_SAFE_HANDOFF

- Latest verified material recovery source remains `d7ecb256d430f437f4ad9249480b6430af52ecf9`; historical recovery session `s-20260921T191500Z-a23cc77e` remains evidence of one prior session only.
- `SB-R07-071` source `0c74336b793189b4ba32d1f1229de0fb4d3e5ebb` implements `fcntl.flock` around the duplicate-session find+append critical section. Worker regression uses 8 OS processes × 20 rounds; worker evidence reports 314 passed / 1 skipped. **Disposition: SUBMITTED pending independent QA execution.**
- `SB-R07-041` remains **CHANGES_REQUIRED**. LEAD-047 independently reproduced the direct `ModelReasoningProvider` callable bypass with a harmless sentinel and additionally found related provider capability/budget problems requiring shared repair.
- `SB-R07-044` and `SB-R07-072` remain submitted engineering evidence; the previously evaluated Cursor host remains unsuitable for LIVE scheduler acceptance.
- Cursor was explicitly parked at safe handoff; current branch head `bf18ac0083b15194c011b18dc791f4bd3d3e8019` is lead-authored park coordination, not worker progress. Fable owns new shared-runtime implementation.

### Legacy Core

- Final V03 implementation/evidence remains accepted with the committed 130-test final bundle and independent lifecycle execution.
- V04 deterministic/fixture work remains useful engineering evidence, but controlled causal adaptive divergence is still authorization-blocked.
- Legacy Core remains **PARKED / evidence-only**.

### Intelligence

- `SB-V05-001` is **ACCEPTED**: pinned-IP HTTPS preserves original-host SNI/certificate verification and Host semantics, avoids implicit DNS reconnect, and fails redirects closed.
- `SB-V15-001` remains **CHANGES_REQUIRED** because ordinary whole-runtime `load` / `load_all` aliases remain structurally ambiguous despite improved persona-scoped APIs.
- Intelligence remains **PARKED / evidence-only**. Fable may consolidate reviewed pieces on the integrated candidate without treating unresolved semantics as accepted.
- `SB-V13-001` and `SB-V14-001` remain accepted. `SB-V16-001`, `SB-V17-001`, and `SB-V20-002` remain changes-required pending dependency repair and independent audit.

### Acceptance / QA — REVIEW_ONLY / ASSIGNMENT DELIVERED

- `SB-V03-004` independent lifecycle acceptance remains **ACCEPTED**, scoped to a single POSIX host/filesystem.
- `SB-V04-005` remains **ACCEPTED** from the first chronological authorized real canary. The second historical real call exceeded the exactly-one authorization and remains permanently excluded from acceptance evidence.
- No fresh worker-generated post-LEAD-047 reviewer result exists yet. Branch head `bd6cbde805684efb2a4bbf06c3886cefdb842650` is lead-authored review assignment delivery.
- Ordered independent work: execute the real `SB-R07-071` process race; then audit Fable's repaired R07-041/provider-capability/budget/integrity paths on actual candidate modules using harmless sentinels and zero real inference; then rerun specialist lifecycle/integrated-candidate tests and report exact scope.
- Acceptance owns no runtime source and must execute no real model call.
- `SB-EVD-002` remains WITHHELD because `SB-V04-002` / `SB-V04-004` remain blocked on fresh controlled causal evidence.

### Live canary

- Dedicated canary branch remains **FROZEN / evidence preservation only**.
- No additional Claude/adaptive/product-model call is authorized.
- Any future five-call controlled divergence batch requires fresh explicit owner authorization plus a matching canonical scoped lead authorization manifest before provider spawn/callable execution.

## LEAD-047 source-audit findings that must be repaired

1. **P0 — R07-041 direct callable bypass:** direct `ModelReasoningProvider.propose` can invoke a registered callable without the canonical authorization check.
2. **P0 — false fixture/capability bypass:** caller-controlled capability/adaptive labeling can bypass refused routes; production must construct policy-owned capabilities.
3. **P0 — budget accounting after dispatch / wrapper-private:** reserve atomically and durably before dispatch across concurrency, reentry, wrappers/processes and restart; errors/crashes consume or remain uncertain.
4. **P1 — retained evidence integrity:** verify canonical path/type and the exact bytes/hash consumed; cover wrong scope, replacement, symlink and late-write cases.
5. **P1 — lifecycle finalization/deadline:** add reliable finalization and supervised hard-deadline behavior while keeping helper scope distinct from arbitrary-code OS isolation.
6. **P1 — strategy publication/integration:** make strategy publication crash-consistent/fenced and complete missing strategy/planner + H1–H4 + DEVELOPMENT_ARTIFACT production integration.

Lead probes used harmless sentinels/test doubles and made zero real provider/network/public calls. They reproduce defects but are not a substitute for actual-module candidate tests or the full suite.

## Artifact reliability table

| Artifact | SP | Current lead disposition | Current note |
|---|---:|---|---|
| SB-V03-002 | 3 | ACCEPTED | per-signal consumption correctness |
| SB-V03-003 | 2 | ACCEPTED | forced FACT/VOICE failures stop effects |
| SB-V03-004 | 5 | ACCEPTED | independently executed lifecycle fencing |
| SB-V03-005 | 4 | ACCEPTED | six-store persona/admin boundary hardened |
| SB-V03-006 | 3 | ACCEPTED | final 130-test bundle + independent lifecycle gate |
| SB-V04-001 | 3 | ACCEPTED | production adaptive-required/fail-closed contract |
| SB-V04-002 | 5 | BLOCKED | controlled live causal divergence needs fresh owner authorization |
| SB-V04-003 | 4 | ACCEPTED | deterministic authority wall |
| SB-V04-004 | 3 | BLOCKED | fixtures/replay insufficient for causal adaptive acceptance |
| SB-V04-005 | 3 | ACCEPTED | first authorized real canary accepted; duplicate excluded |
| SB-V05-001 | 3 | ACCEPTED | real pinned-IP TLS/SNI/cert path |
| SB-V05-002 | 4 | CHANGES_REQUIRED | operational semantic evidence path open |
| SB-V13-001 | 4 | ACCEPTED | metric semantics/provenance |
| SB-V14-001 | 4 | ACCEPTED | bot+persona audience memory |
| SB-V15-001 | 4 | CHANGES_REQUIRED | ambiguous whole-runtime load/load_all aliases remain |
| SB-V16-001 | 4 | CHANGES_REQUIRED | pending dependency repair + independent audit |
| SB-V17-001 | 4 | CHANGES_REQUIRED | pending dependency repair + independent audit |
| SB-V20-002 | 4 | CHANGES_REQUIRED | waits V15 + independent audit |
| SB-R07-071 | 1 | SUBMITTED | atomic flock source + multiprocess race; independent QA required |
| SB-R07-041 | — | CHANGES_REQUIRED | direct callable plus shared capability/budget boundaries still unsafe |
| SB-R07-044 | — | SUBMITTED | engineering verifier; live causal evidence still owner-gated |
| SB-R07-072 | 1 | SUBMITTED | current Cursor host honestly unsuitable for LIVE scheduler acceptance |
| SB-S20-001 | 2 | SUBMITTED ENGINEERING | strategy store useful; publication/integration hardening required |
| SB-S23-001 | 2 | SUBMITTED ENGINEERING | least-authority specialist contract; integrated enforcement pending |
| SB-S23-002..007 | — | SUBMITTED ENGINEERING | specialist components preserved; lead audit found shared guard/integrity gaps |
| SB-S23-008 | 3 | SUBMITTED ENGINEERING | fixture lifecycle bundle; independent actual-candidate rerun required |

## Heartbeat quality

Canonical policy is **ONE SESSION = ONE HEARTBEAT**. The earlier FAST_5M / SOAK_15M_24H experiment is superseded.

A lead-authored branch assignment is not a heartbeat or worker acknowledgement. Fable's historical `SESSION_ONCE` and Cursor's historical recovery heartbeat establish only that those prior sessions existed. The new LEAD-047 campaign is **awaiting a fresh worker session** at this review cutoff.

V0.7 recurring liveness still requires repeated real **OS-scheduled bounded worker sessions** on an owner-controlled persistent host, each producing a session heartbeat plus invocation receipt. Chat liveness, Issue comments, temporary-host fixtures and a kept-open session do not count.

## Current lessons

- Consolidated ownership is preferable to stale cross-lane dependency deadlock when shared-file repair is required; independence is preserved through review, not by freezing all implementation.
- Guard every live-capable provider boundary and capability source, not just the CLI subprocess.
- Reserve budgets before dispatch and share the durable accounting boundary across wrappers/processes/reentry.
- Verify the exact retained bytes consumed; receipt metadata without read-time integrity is insufficient.
- Fixture evidence stays fixture evidence; green worker-local tests do not establish operational V2.3.
- Authorization must remain machine-visible, scoped and fail-closed.

## Current concurrency implication

- **Fable Fast-track:** sole primary implementation/integration owner; released and assignment delivered; awaiting fresh worker-generated session/evidence.
- **Cursor Recovery:** PARKED_SAFE_HANDOFF; preserve/push only already-existing local material.
- **Legacy Core:** PARKED / evidence-only.
- **Intelligence:** PARKED / evidence-only.
- **Acceptance:** REVIEW-ONLY; assignment delivered; awaiting fresh independent reviewer evidence.
- **Canary:** FROZEN / evidence-only.
- **worker-pc:** excluded until private-repo clone/auth is demonstrably fixed.
