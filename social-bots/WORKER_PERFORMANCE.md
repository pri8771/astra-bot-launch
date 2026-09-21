# Social Bots worker performance

Purpose: track implementation reliability by artifact and task type. Worker submissions never self-accept.

Current lead review: **LEAD-041** (`lead-reviews/LEAD-041_2026-09-21T1852.md`).
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

## Current verified activity

### Recovery / inherited Core descendant

- LEAD-040 created `cursor/social-bots-recovery-v07-20260921` at `918c42e...`, but the verified Core descendant continued immediately afterward.
- Material source commit `a73b7b58de8f3669795b81637bff55247d67943c` moved the no-live authorization-manifest refusal to the actual `ClaudeCodeReasoningProvider` spawn point. That closes alternate entrypoint bypasses while retaining injected-runner fixture seams.
- Worker evidence for that source reports **312 passed, 1 skipped**, with no live model call.
- Corrected Core reports/progress continue through `2f14a5cb08c9019fd174c1f54ecda130fa9308d4`.
- LEAD-041 fast-forwarded the recovery branch to this verified descendant history before assigning new work. This avoids rebuilding from or auditing a stale safety baseline.
- Immediate implementation gate: **SB-R07-071** atomic cross-process `SESSION_ONCE` uniqueness. The inherited duplicate-session check remains check-then-append and is not yet safe against concurrent processes.
- At the LEAD-041 cutoff, the recovery lane is **ASSIGNED but not yet evidenced running**; there is no fresh recovery worker heartbeat/source submission after the lead assignment.

### Legacy Core

- Final V03 implementation/evidence remains accepted with the committed 130-test final bundle and independent lifecycle execution.
- V04 deterministic/fixture work remains useful engineering evidence, but controlled causal adaptive divergence is still authorization-blocked.
- The post-LEAD-040 safety work above has been transferred into the recovery branch.
- Legacy Core is now **PARKED / evidence-only** to prevent overlapping implementation ownership.

### Intelligence

- `SB-V05-001` is **ACCEPTED**: pinned-IP HTTPS retains original-host SNI/certificate verification and Host semantics, avoids implicit DNS reconnect, and fails redirects closed.
- `SB-V15-001` remains **CHANGES_REQUIRED** because ordinary whole-runtime `load` / `load_all` aliases remain structurally ambiguous despite improved persona-scoped APIs.
- Intelligence is now **PARKED / evidence-only** during consolidated recovery. Its prior evidence remains available to the recovery lane; no overlapping source edits are assigned.
- `SB-V13-001` and `SB-V14-001` remain accepted. `SB-V16-001`, `SB-V17-001`, and `SB-V20-002` remain changes-required pending dependency repair and independent audit.

### Acceptance / QA

- `SB-V03-004` independent lifecycle acceptance is **ACCEPTED**, scoped to a single POSIX host/filesystem.
- `SB-V04-005` is **ACCEPTED** from the first chronological authorized real canary. The second historical real call exceeded the exactly-one authorization and remains permanently excluded from acceptance evidence.
- Acceptance is now **REVIEW-ONLY STANDBY**. It owns no runtime source.
- First new independent target is `SB-R07-071`: execute an actual cross-process duplicate-session race and verify exactly one durable heartbeat record wins. Then audit `SB-R07-041` when explicitly assigned.
- `SB-EVD-002` remains WITHHELD because `SB-V04-002` / `SB-V04-004` remain blocked on fresh controlled causal evidence.

### Live canary

- Dedicated canary branch remains **FROZEN / evidence preservation only**.
- No additional Claude/adaptive/model call is authorized.
- Any future five-call controlled divergence batch requires fresh explicit owner authorization plus a matching canonical lead authorization manifest before provider spawn.

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
| SB-R07-071 | — | READY | atomic cross-process session heartbeat uniqueness |
| SB-R07-041 | — | READY_AFTER_071 | audit inherited spawn-point live authorization hardening |

## Heartbeat quality

Canonical policy is **ONE SESSION = ONE HEARTBEAT**. The earlier FAST_5M / SOAK_15M_24H experiment is superseded.

A session heartbeat establishes fresh worker-session liveness only; it does not establish artifact correctness. The inherited implementation currently has a concurrency defect: duplicate-session detection and durable append are separate operations. `SB-R07-071` must make that uniqueness claim atomic and prove it with an adversarial cross-process race.

V0.7 recurring liveness still requires repeated real **OS-scheduled bounded worker sessions** on an owner-controlled persistent host, each producing a session heartbeat plus invocation receipt. Chat liveness, Issue comments, temporary-host fixtures, and a kept-open session do not count.

## Current lessons

- **Do not let recovery branches lag verified safety work.** LEAD-041 had to fast-forward recovery from `918c42e...` to the verified descendant history through `2f14a5c...` before assigning new work.
- **Gate at the actual side-effect/spawn point.** `a73b7b5...` is materially stronger because authorization refusal occurs where the real Claude CLI process would spawn, not only in one caller.
- **Independent adversarial execution matters.** V03 only closed after takeover/migration tests were executed independently; the same standard applies to SB-R07-071.
- **Green tests are not enough.** Synthetic/replayed adaptive receipts do not prove causal model divergence.
- **Authorization must be machine-visible and fail closed.** Future live-call execution needs an explicit canonical manifest and exact budget, not permissive prose.
- **Isolation boundaries must be structural.** V15 remains open because ordinary public aliases still cross persona scope.

## Current concurrency implication

- **Cursor Recovery:** primary implementation; SB-R07-071 first.
- **Legacy Core:** PARKED / evidence-only.
- **Intelligence:** PARKED / evidence-only.
- **Acceptance:** REVIEW-ONLY standby; independent SB-R07-071/SB-R07-041 audits when submissions land.
- **Canary:** FROZEN / evidence-only.
- **worker-pc:** excluded until private-repo clone/auth is demonstrably fixed.
