# Claude worker performance

Purpose: track implementation reliability by artifact and task type. Worker submissions never self-accept.

Current lead review: **LEAD-036** (`lead-reviews/LEAD-036_2026-09-21T1710.md`).
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

## Current verified activity

### Core

- Final V03 implementation/evidence remains `796d4e390bd135167e5de2ff8f586bc07ac7f370` / `436787b0a63fdae0e89c224a54054607e32b5187`, with committed **130 tests — OK**.
- Independent Acceptance execution `72e380b` cleared the high-risk V03 lifecycle gate: 37/37 invariant checks, focused 36 tests, full 130-test suite.
- V03 artifacts SB-V03-001/002/003/004/005/006 and SB-EVD-001 are now accepted.
- Core V04 repair `a19046d` / `74a357d` fixed the previously confounded deterministic persona-only/evidence-only comparisons and reports **160 passed, 1 skipped**.
- SB-V04-001 and SB-V04-003 are accepted.
- SB-V04-002/SB-V04-004 remain CHANGES_REQUIRED because real adaptive causal-divergence evidence is still missing. Synthetic/replayed receipts are engineering fixtures, not that evidence.

### Intelligence

- SB-V05-001 repair `a462bd6` is **ACCEPTED**. The production HTTPS path connects once to the validated pinned IP, retains original-host SNI/certificate verification and Host header, prevents implicit hostname reconnect, fails redirects closed, and has a production-path regression.
- SB-V15-001 repair `2052955` is materially improved but remains **CHANGES_REQUIRED**: persona-facing storage/read APIs are partitioned, yet ordinary public aliases `load(bot,id)` / `load_all(bot)` still expose whole-runtime reads. A narrow structural admin-boundary repair is assigned.
- SB-V13-001 and SB-V14-001 remain accepted.
- V16/V17/V20-002 remain pending independent audit after V15 closure.

### Acceptance / QA

- SB-V03-004 independent lifecycle acceptance is **ACCEPTED**. Scope: single POSIX host/filesystem; execution actually ran on Linux CCR rather than the reset-plan physical Mac.
- SB-V04-005 real canary is **ACCEPTED** from the first chronological ~16:15Z call: real public source, actual Claude Code subscription CLI, no API key/PAYG, no injected runner, schema-valid proposal, deterministic policy, persisted local decision and no public effect.
- A second real ~16:53Z canary call occurred after the owner's exactly-one authorization was consumed. It is excluded from acceptance evidence and recorded as a process/authorization incident. **No further model calls are authorized.**
- SB-EVD-002 is WITHHELD because SB-V04-002 and SB-V04-004 remain open, not because the accepted canary chain itself failed.
- Existing engineering controls SB-CTL-006 CI and SB-CTL-012 artifact validator remain accepted.

## Artifact reliability table

| Artifact | SP | Current lead disposition | Current note |
|---|---:|---|---|
| SB-V03-002 | 3 | ACCEPTED | per-signal consumption correctness |
| SB-V03-003 | 2 | ACCEPTED | forced FACT/VOICE failures stop effects |
| SB-V03-004 | 5 | ACCEPTED | multiple repair cycles; independently executed at 72e380b |
| SB-V03-005 | 4 | ACCEPTED | six-store persona/admin boundary hardened |
| SB-V03-006 | 3 | ACCEPTED | final 130-test evidence bundle + independent lifecycle gate |
| SB-V04-001 | 3 | ACCEPTED | production adaptive-required/fail-closed contract |
| SB-V04-002 | 5 | CHANGES_REQUIRED | real adaptive causal divergence not proved |
| SB-V04-003 | 4 | ACCEPTED | deterministic authority wall proven in tests + live canary |
| SB-V04-004 | 3 | CHANGES_REQUIRED | deterministic design repaired; adaptive divergence still absent |
| SB-V04-005 | 3 | ACCEPTED | first authorized live canary accepted; duplicate later call excluded |
| SB-V05-001 | 3 | ACCEPTED | real pinned-IP TLS/SNI/cert path repaired |
| SB-V05-002 | 4 | CHANGES_REQUIRED | operational semantic evidence path still open |
| SB-V13-001 | 4 | ACCEPTED | metric semantics/provenance repaired |
| SB-V14-001 | 4 | ACCEPTED | bot+persona audience memory repaired |
| SB-V15-001 | 4 | CHANGES_REQUIRED | ambiguous whole-runtime load/load_all aliases remain |
| SB-V16-001 | 4 | CHANGES_REQUIRED | pending independent latest-repair audit |
| SB-V17-001 | 4 | CHANGES_REQUIRED | pending independent latest-repair audit |
| SB-V20-002 | 4 | CHANGES_REQUIRED | waits V15 + independent latest-repair audit |

## Heartbeat quality

Heartbeat quality is tracked separately from implementation quality. Issue #3 has current worker comments, but the reset protocol makes durable `HEARTBEAT_LOG.jsonl` authoritative. Core, Intelligence and Mac QA durable logs contain no reset-epoch FAST_5M entries at LEAD-036, so **0 reset intervals are verified on each lane**. Do not backfill. This does not block work.

## Current lessons

- **Independent adversarial execution matters.** V03 fencing only closed after the Acceptance lane ran takeover/migration scenarios against pinned final source.
- **Green tests are not enough.** V04 deterministic divergence tests had to be inspected for causal-variable isolation; synthetic adaptive receipts remain fixtures.
- **Authorization must be machine-visible.** The duplicate canary call shows that text instructions alone did not prevent a second live invocation. Any future live-call workflow should include a durable consumed-once authorization latch before execution.
- **Isolation boundaries must be structural.** V15 still fails because ordinary public alias names can cross persona boundaries even though explicit persona APIs are correct.
- **Heartbeat comments are not durable heartbeat proof.** Issue visibility and committed cadence evidence are separate concerns.

## Current concurrency implication

- **Core:** no live calls; non-live V04 acceptance/integration work only.
- **Intelligence:** close V15 structural admin aliases, then stop for lead audit.
- **Acceptance:** no live calls; QA/CI/V2 integration + durable heartbeat proof only.
- **Canary:** frozen, evidence preservation only.
- **worker-pc:** do not use for Social Bots until private-repo clone/auth is fixed.
