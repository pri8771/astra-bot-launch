# Social Bots worker performance

Purpose: track implementation reliability by artifact and task type. Worker submissions never self-accept.

Current lead review: **LEAD-045** (`lead-reviews/LEAD-045_2026-09-21T1758.md`).  
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

## Current verified activity

### Fable Fast-track — MATERIAL SUBMISSIONS / PAUSED FOR REVIEW

- Fresh session `s-20260921T211438Z-d5589881` emitted one durable `SESSION_ONCE` heartbeat and produced signed work on `fable/social-bots-v23-fasttrack-20260921` through reviewed head `a204ad0827748a4e9661f1945b8e025d53d0ae09`.
- Fable submitted **SB-S20-001** and **SB-S23-001..SB-S23-008** as engineering evidence. Lead inspected actual `SB-S23-001` contract source and `SB-S23-008` lifecycle source/report rather than relying only on self-report.
- Worker baseline reports **523 tests discovered, 521 passed, 0 failed, 0 errors, 2 skipped**, plus a valid 32-task next-round plan and 18 validator self-tests.
- Diff/ownership evidence says no Cursor-owned existing runtime source was edited; the lane used new specialist/strategy modules, tests, proof code, fixture evidence, and append-only handoff records.
- `SB-S23-008` is explicitly fixture-class evidence. It demonstrates useful engineering behavior but does not prove a live specialist process boundary or operational V2.3. Independent Acceptance rerun is required.
- Known limits remain explicit: specialist execution is in-process/thread-based on one POSIX host; strategy version publication is detectable but not transactionally crash-consistent; live-provider trust/call-budget closure remains a next-round concern.
- **Disposition:** nine artifacts are reviewable engineering submissions, not operational acceptance. Fable is now paused from new source until explicit lead release.

### Cursor Recovery — STALE / ACTION REQUIRED

- The previously verified recovery session `s-20260921T191500Z-a23cc77e` produced useful submissions, but the current branch head remains lead acknowledgement `488ce0c720d857473ab9f2ce448d9197a955df14`; no requested `SB-R07-041` repair has landed since the lead finding.
- `SB-R07-071` source `0c74336b793189b4ba32d1f1229de0fb4d3e5ebb` fixes the cross-process duplicate-session race with `fcntl.flock` around the find+append critical section. The regression uses 8 OS processes x 20 rounds; worker evidence reports 314 passed / 1 skipped. **Disposition: SUBMITTED pending independent Acceptance execution.**
- `SB-R07-041` source `21cc2e7a65750d20dc609b9e9517f920157389a2` materially improves the Claude CLI spawn guard, but lead audit found a separate direct-library bypass: `ModelReasoningProvider` can invoke a process-registered `_MODEL_CALLABLE` without checking the canonical live manifest when worker entrypoints are bypassed. **Disposition: CHANGES_REQUIRED.**
- `SB-R07-044` is an engineering-only divergence verifier that refuses to self-accept fixtures. **Disposition: SUBMITTED / pending audit.**
- `SB-R07-072` truthfully classifies the current Cursor environment as `UNSUITABLE_NOT_PERSISTENT_OWNER_HOST`. Do not run/install the LIVE scheduler there.
- Immediate worker action remains a bounded zero-live `SB-R07-041` repair plus a direct-library sentinel regression.

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
- No fresh independent R07 execution is visible at current branch head `a508c06bc87a9f36b7d6347eeb86cde62f4d9907`.
- Immediate independent order: execute `SB-R07-071`; audit repaired `SB-R07-041` direct-library route with a harmless sentinel; then independently rerun/audit Fable `SB-S23-008` fixture lifecycle evidence.
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
| SB-S20-001 | 2 | SUBMITTED ENGINEERING | Fable versioned strategy store; independent audit/integration pending |
| SB-S23-001 | 2 | SUBMITTED ENGINEERING | least-authority specialist contract; independently inspect before acceptance |
| SB-S23-002..007 | — | SUBMITTED ENGINEERING | new-files-only specialist components; independent audit pending |
| SB-S23-008 | 3 | SUBMITTED ENGINEERING | fixture lifecycle bundle; independent Acceptance rerun required |

## Heartbeat quality

Canonical policy is **ONE SESSION = ONE HEARTBEAT**. The earlier FAST_5M / SOAK_15M_24H experiment is superseded.

Fable's fresh durable session heartbeat establishes session liveness only. Cursor's historical recovery heartbeat likewise establishes that one session existed, not that the current assignment is progressing. Artifact correctness requires source/test/evidence review.

V0.7 recurring liveness still requires repeated real **OS-scheduled bounded worker sessions** on an owner-controlled persistent host, each producing a session heartbeat plus invocation receipt. Chat liveness, Issue comments, temporary-host fixtures, and a kept-open session do not count. The current Cursor host has explicitly failed the persistent-host preflight, which is a truthful useful result, not V0.7 evidence.

## Current lessons

- **New-files-only parallelism works when ownership is explicit.** Fable completed a large specialist engineering batch without editing Cursor-owned existing runtime files.
- **Guard every live-capable provider boundary, not just the CLI subprocess.** R07-041 exposed a second route through a registered model callable.
- **Independent adversarial execution matters.** R07-071 and S23-008 stay submitted until Acceptance reruns the required cases.
- **Fixture evidence stays fixture evidence.** A green specialist lifecycle bundle does not establish hard process isolation or operational V2.3.
- **A truthful UNSUITABLE preflight is valuable.** It prevents false V0.7 scheduler claims on an ephemeral cloud agent.
- **Authorization must be machine-visible and fail closed.** Future live-call execution needs an explicit canonical manifest and exact budget, not permissive prose.
- **Isolation boundaries must be structural.** V15 remains open because ordinary public aliases still cross persona scope.

## Current concurrency implication

- **Cursor Recovery:** primary implementation but STALE / ACTION REQUIRED; repair R07-041 now.
- **Fable Fast-track:** PAUSED after material engineering submissions; preserve evidence, await explicit next release.
- **Legacy Core:** PARKED / evidence-only.
- **Intelligence:** PARKED / evidence-only.
- **Acceptance:** REVIEW-ONLY and STALE; independent R07-071 -> repaired R07-041 -> S23-008.
- **Canary:** FROZEN / evidence-only.
- **worker-pc:** excluded until private-repo clone/auth is demonstrably fixed.
