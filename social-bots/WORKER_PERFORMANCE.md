# Social Bots worker performance

Purpose: track implementation reliability by artifact and task type. Worker submissions never self-accept.

Current lead review: **LEAD-042** (`lead-reviews/LEAD-042_2026-09-21T1556.md`).  
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

## Current verified activity

### Cursor Recovery — ACTIVE / materially productive

- Fresh recovery session `s-20260921T191500Z-a23cc77e` emitted one durable `SESSION_ONCE` heartbeat at `2026-09-21T19:15:00Z` after reading LEAD-041.
- Current verified branch head is `d7ecb256d430f437f4ad9249480b6430af52ecf9`; commits are signed by Cursor Agent.
- `SB-R07-071` source `0c74336b793189b4ba32d1f1229de0fb4d3e5ebb` fixes the cross-process duplicate-session race with `fcntl.flock` around the find+append critical section. The regression uses 8 OS processes x 20 rounds; worker evidence reports 314 passed / 1 skipped. **Disposition: SUBMITTED pending independent Acceptance execution.**
- `SB-R07-041` source `21cc2e7a65750d20dc609b9e9517f920157389a2` materially improves the real Claude CLI spawn guard by using an import-time captured real runner, but lead source audit found a separate direct-library bypass: `ModelReasoningProvider` invokes a process-registered `_MODEL_CALLABLE` without checking the canonical live manifest. **Disposition: CHANGES_REQUIRED.**
- `SB-R07-044` source `5179217ea222e94caa5580104fbc6aaacd4b2192` is an honestly engineering-only divergence verifier that refuses to self-accept fixtures. **Disposition: SUBMITTED / pending audit.**
- `SB-R07-072` source `7f59f915b9f5bb60691d06215a463518fd4519c7` truthfully classifies the current Cursor environment as `UNSUITABLE_NOT_PERSISTENT_OWNER_HOST`. **Do not run/install R07-073 there.**
- Cursor also reports later no-live engineering submissions R07-042/051/052/053/061 and a cumulative 416 passed / 2 skipped suite. Those submissions are not accepted from self-report and remain queued for lead/independent audit.

### Legacy Core

- Final V03 implementation/evidence remains accepted with the committed 130-test final bundle and independent lifecycle execution.
- V04 deterministic/fixture work remains useful engineering evidence, but controlled causal adaptive divergence is still authorization-blocked.
- Legacy Core remains **PARKED / evidence-only** to prevent overlapping implementation ownership.

### Intelligence

- `SB-V05-001` is **ACCEPTED**: pinned-IP HTTPS retains original-host SNI/certificate verification and Host semantics, avoids implicit DNS reconnect, and fails redirects closed.
- `SB-V15-001` remains **CHANGES_REQUIRED** because ordinary whole-runtime `load` / `load_all` aliases remain structurally ambiguous despite improved persona-scoped APIs.
- Intelligence remains **PARKED / evidence-only** during consolidated recovery. No overlapping source edits are assigned.
- `SB-V13-001` and `SB-V14-001` remain accepted. `SB-V16-001`, `SB-V17-001`, and `SB-V20-002` remain changes-required pending dependency repair and independent audit.

### Acceptance / QA — STALE / ACTION REQUIRED

- `SB-V03-004` independent lifecycle acceptance is **ACCEPTED**, scoped to a single POSIX host/filesystem.
- `SB-V04-005` is **ACCEPTED** from the first chronological authorized real canary. The second historical real call exceeded the exactly-one authorization and remains permanently excluded from acceptance evidence.
- No post-LEAD-041 worker QA commit is visible; the branch head is still the lead review-only acknowledgement.
- Immediate independent target is `SB-R07-071`: execute the actual cross-process duplicate-session race against the submitted source and verify exactly one durable heartbeat record wins. Then audit repaired `SB-R07-041` through the direct-library `model` path with worker entrypoints bypassed.
- Acceptance owns no runtime source and must execute no model call.
- `SB-EVD-002` remains WITHHELD because `SB-V04-002` / `SB-V04-004` remain blocked on fresh controlled causal evidence.

### Live canary

- Dedicated canary branch remains **FROZEN / evidence preservation only**.
- No additional Claude/adaptive/model call is authorized.
- Any future five-call controlled divergence batch requires fresh explicit owner authorization plus a matching canonical lead authorization manifest before provider spawn/callable execution.

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
| SB-R07-041 | — | CHANGES_REQUIRED | direct registered model callable can bypass manifest when worker entrypoints are bypassed |
| SB-R07-044 | — | SUBMITTED | engineering verifier; live causal evidence still owner-gated |
| SB-R07-072 | 1 | SUBMITTED | current Cursor host honestly unsuitable for LIVE scheduler acceptance |

## Heartbeat quality

Canonical policy is **ONE SESSION = ONE HEARTBEAT**. The earlier FAST_5M / SOAK_15M_24H experiment is superseded.

The Cursor recovery session has one real durable heartbeat. This establishes session liveness only; it does not establish artifact correctness. `SB-R07-071` now appears structurally correct in lead source inspection, but independent execution remains required before acceptance.

V0.7 recurring liveness still requires repeated real **OS-scheduled bounded worker sessions** on an owner-controlled persistent host, each producing a session heartbeat plus invocation receipt. Chat liveness, Issue comments, temporary-host fixtures, and a kept-open session do not count. The current Cursor host has explicitly failed the persistent-host preflight, which is a truthful useful result, not V0.7 evidence.

## Current lessons

- **Guard every live-capable provider boundary, not just the CLI subprocess.** R07-041 exposed a second route: a registered `ModelReasoningProvider` callable can be live-capable even when the Claude CLI spawn point is guarded.
- **Independent adversarial execution matters.** R07-071 stays submitted until Acceptance reruns the actual OS-process race.
- **A truthful UNSUITABLE preflight is valuable.** It prevents false V0.7 scheduler claims on an ephemeral cloud agent.
- **Green tests are not enough.** Synthetic/replayed adaptive receipts do not prove causal model divergence.
- **Authorization must be machine-visible and fail closed.** Future live-call execution needs an explicit canonical manifest and exact budget, not permissive prose.
- **Isolation boundaries must be structural.** V15 remains open because ordinary public aliases still cross persona scope.

## Current concurrency implication

- **Cursor Recovery:** ACTIVE primary implementation; fix R07-041 direct model-callable authorization boundary next.
- **Legacy Core:** PARKED / evidence-only.
- **Intelligence:** PARKED / evidence-only.
- **Acceptance:** REVIEW-ONLY but stale; independent R07-071 then repaired R07-041 audit now.
- **Canary:** FROZEN / evidence-only.
- **worker-pc:** excluded until private-repo clone/auth is demonstrably fixed.
