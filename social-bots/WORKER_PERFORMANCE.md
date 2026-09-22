# Social Bots worker performance

Purpose: track implementation reliability by artifact and task type. Worker submissions never self-accept.

Current lead review: **LEAD-055** (`lead-reviews/LEAD-055_2026-09-22T0501.md`).  
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.  
Current execution target/ceiling: **LIVE V1.3, genuine tests, then hard stop**. Prior V1.7 ceiling is superseded.

## Current verified activity

### Fable Integrator — EXISTING OWNERSHIP PRESERVED / NO NEW HANDOFF

- Verified worker session: `s-20260921T211438Z-d5589881`. It ingested LEAD-048/050 V1.7-only scope after a container restore and correctly did not emit a second heartbeat for the same session.
- Signed material worker history is verified through `af3fded92eaba5e68c8088737b68c6f043e40a5e`.
- `12c807e...` submitted shared pre-dispatch authorization/budget gate; worker reports **559 discovered / 557 passed / 2 skipped** on that SHA.
- `b5fd038...` submitted due-work rotation / first-bot-starvation repair; worker reports **569 discovered / 567 passed / 2 skipped**.
- `c4d31fee...` submitted C05/C06/C07 final-content review binding + prospective experiment semantics; commit reports **678 passed / 2 skipped**.
- `3da19a9c...` selectively consolidated V1.7 Intelligence producers (metrics, audience, experiment engine, community, platform selection) while excluding future V2.0 growth modules.
- `af3fded...` submitted a read-only V1.7 host/provider/account gate dossier. It truthfully records an ephemeral Linux VM, no native scheduler, social-platform CONNECT-403 restrictions, no canonical live authorization manifest, no account registry entries and no named cultural reviewer.

**Lead disposition of R07-041:** **ACCEPTED narrowly at LEAD-052.** Repair `0bca4e...` makes no-scope fail closed for EngineeringStub/injected-runner seams, permits them only inside the policy-owned ENGINEERING scope, and keeps production scope fail-closed. Independent Mac focused evidence passed 118/118 at production-equivalent `f0f1307...`. This does not promote V0.4 or authorize live effects.

**Disposition:** Existing Fable ownership and evidence are preserved, but owner now explicitly prohibits any new routing/message/assignment/handoff to Fable. Concrete new fixes are Codex-direct in isolated repair branches; ChatGPT remains formal acceptor.

### Mac Acceptance — STALE / ACTION REQUIRED

- Branch remains independent review-only; no runtime source edits and no real model calls.
- No fresh post-LEAD-050 independent reviewer result was verified at the LEAD-051 cutoff.
- Ordered work: audit repaired R07-041 with harmless sentinels; execute R07-071 multiprocess/session race; independently exercise due-work anti-starvation and C05/C06/C07 edit/replacement/symlink/late-write/wrong-scope/prospective-experiment controls; verify future modules are unreachable from enabled V1.7 dispatcher routes.
- Preflight host/account facts are reviewed as blockers only, never as operational acceptance.

### Cursor Recovery — PARKED / evidence-only

- Latest material recovery source remains `d7ecb256d430f437f4ad9249480b6430af52ecf9`; historical recovery session `s-20260921T191500Z-a23cc77e` remains evidence of one prior session only.
- `SB-R07-071` remains SUBMITTED pending independent Acceptance execution.
- Current Cursor host was already found unsuitable for LIVE native-scheduler proof.
- No new overlapping implementation is authorized; Fable owns shared enabled runtime through V1.7.

### Legacy Core

- V0.3 final implementation/evidence remains accepted, including the 130-test final bundle and independent lifecycle execution.
- V0.4 deterministic/fixture work remains useful engineering evidence, but controlled causal adaptive divergence remains owner-authorization blocked.
- Legacy Core remains **PARKED / evidence-only**.

### Intelligence

- `SB-V05-001`, `SB-V13-001`, and `SB-V14-001` remain accepted.
- Historical `SB-V15-001`, `SB-V16-001`, and `SB-V17-001` findings remain unresolved at registry level until the integrated candidate is independently reconciled. Selective producer consolidation by Fable is engineering integration, not automatic acceptance of those artifacts.
- Intelligence remains **PARKED / evidence-only**.

### Live canary

- Dedicated canary branch remains **FROZEN / evidence preservation only**.
- The first authorized V0.4 canary remains accepted evidence; the later duplicate call exceeded the exactly-one authorization and remains permanently excluded.
- No additional Claude/adaptive/product-model call is authorized. Any future controlled divergence batch requires fresh explicit owner authorization plus a matching canonical scoped lead manifest.

## Artifact reliability table

| Artifact | Current lead disposition | Current note |
|---|---|---|
| SB-V03-001..006 / SB-EVD-001 | ACCEPTED | V0.3 closed; independent lifecycle gate satisfied |
| SB-V04-001 | ACCEPTED | adaptive-required/fail-closed contract |
| SB-V04-002 | BLOCKED | controlled live causal divergence needs fresh owner authorization |
| SB-V04-003 | ACCEPTED | deterministic authority wall |
| SB-V04-004 | BLOCKED | replay/fixtures cannot prove causal adaptive divergence |
| SB-V04-005 | ACCEPTED | first authorized real canary accepted; duplicate excluded |
| SB-EVD-002 | WITHHELD | waits controlled divergence acceptance |
| SB-V05-001 | ACCEPTED | pinned-IP TLS/SNI/cert path |
| SB-V05-002 | CHANGES_REQUIRED | operational semantic evidence path remains open |
| SB-V13-001 | ACCEPTED | metric semantics/provenance |
| SB-V14-001 | ACCEPTED | bot+persona audience memory |
| SB-V15-001 | CHANGES_REQUIRED | historical registry status; integrated candidate needs independent reconciliation |
| SB-V16-001 | CHANGES_REQUIRED | integrated candidate needs independent audit |
| SB-V17-001 | CHANGES_REQUIRED | integrated candidate needs independent audit |
| SB-R07-041 | ACCEPTED | narrow authority-boundary repair accepted at `0bca4e...`; no version/live promotion |
| SB-R07-071 | SUBMITTED | atomic session uniqueness source; independent QA required |
| SB-R07-072 | ACCEPTED | exact `7acc1695...`; portable host-test isolation only; production predicates unchanged; not host qualification |
| `b5fd038` V1.7 due rotation | SUBMITTED ENGINEERING | worker tests green; independent review required |
| `c4d31fee` C05/C06/C07 | SUBMITTED ENGINEERING | final-review/prospective semantics; independent negative controls required |
| `3da19a9c` producer consolidation | SUBMITTED ENGINEERING | selective <=V1.7 integration only |
| `af3fded` gate dossier | SUBMITTED BLOCKER EVIDENCE | truthful host/account/route blockers; not operational acceptance |
| SB-S20/S23 prior work | PARKED ENGINEERING | preserved; outside current V1.7 execution ceiling unless narrowly reused |

## Heartbeat quality

Canonical policy is **ONE SESSION = ONE HEARTBEAT**. The earlier FAST_5M / SOAK_15M_24H experiment is superseded.

Fable's session heartbeat establishes that its worker session started; its later commits establish substantive progress. A restored/resumed continuation of the same session correctly emits no second heartbeat. Mac Acceptance remains stale because there is no fresh independent review result, not because a periodic timer failed.

V0.7 recurring liveness still requires repeated real **OS-scheduled bounded worker sessions** on a verified owner-controlled persistent host, each producing a session heartbeat plus invocation receipt. Fable's ephemeral VM and a kept-open chat cannot satisfy that requirement.

## Current lessons

- A guard must protect capability-bearing test seams as well as nominal live providers. "Engineering" is not safe merely because a caller labels or wraps an arbitrary callable that way.
- Omission of dispatch scope cannot itself be permission. No-scope should be the strictest fail-closed posture.
- Worker-local green tests are valuable but do not self-accept an artifact; independent negative controls remain necessary at high-risk authority and retained-content boundaries.
- Honest host/account/provider preflight is useful precisely because it makes operational blockers explicit instead of manufacturing compatibility.
- Consolidated source ownership plus independent review remains the preferred topology for this campaign.

## Current concurrency implication

- **Fable:** existing ownership/evidence preserved; no new handoff without fresh owner approval.
- **Acceptance:** independent review-only.
- **Cursor/Core/Intelligence:** PARKED / evidence-only.
- **Canary:** FROZEN / evidence-only.
- **worker-pc:** excluded until private-repo clone/auth is demonstrably fixed.

## LEAD-053 exact candidate review

- Codex isolated repair PR #6 exact source: `7acc1695d2961267580a156f31df6a5991476654`, base `e9678f8bead4f872c199bdf09dbf709a8f649159`.
- GitHub compare: one commit ahead, one changed file only: `social-bots/tests/test_host_preflight.py`; no production runtime predicate changed.
- Author-run submission evidence: 711 run / 709 passed / 0 failed / 0 errors / 2 genuine-evidence skips; host module 11 passed. No independent CI/workflow exists for this exact SHA, so those counts are not labeled independent acceptance.
- ChatGPT formal verdict: **SB-R07-072 ACCEPTED at exact SHA** strictly as the portable test-isolation repair. V0.7 host/model/reviewer/time prerequisites remain open.
- No Fable handoff, scheduler/model/public/account/spend/merge/release action was authorized.

## LEAD-054 due-rotation exact candidate review

- Exact candidate: `84f8f05b22d33dcfc1edd0d2fc8d98ddcc3e1b6d`, one commit over accepted `7acc1695...`.
- Original defect reproduced: the fairness cursor was persisted only after unit completion/release, leaving a crash/write-failure window that could reselect the just-completed bot.
- Repair accepted at engineering scope: claim cursor is persisted inside the current lease generation fence before reconciliation/useful work; persistence failure aborts before the cycle; later cycle failure retains rotation; held candidates do not advance it.
- Author evidence: 2 red regressions before edit; 39 focused pass; full 713 run / 711 pass / 0 fail / 0 error / 2 unchanged genuine-evidence skips; no exact-SHA CI/workflow run.
- User reports a separate 49-test bounded mechanical review with no defect, but that transcript was not present in published `f4e8d56` evidence and is not used as independent execution evidence here.
- Verdict: **ACCEPTED ENGINEERING**, not V0.7 operational acceptance and not version promotion.
- No Fable handoff. Codex remains direct isolated implementer under owner direction.

## LEAD-055 PR8 + V1.3 direct-repair review

- PR #8 exact `9d497b4567e022a8e7f93a3ee890af206272b5be` over accepted `84f8f05...` is **ACCEPTED ENGINEERING** for the bounded C05/C06 review-anchor and C07 measured-baseline validation repair.
- Review receipts are intentionally local audit anchors, not signatures/immutable stores. Baseline shape validation is not proof of a genuine source measurement.
- Author full evidence reports 723 run / 721 pass / 2 existing genuine-evidence skips; separate bounded agent reports 89 focused pass; no exact-SHA GitHub CI/workflow exists.
- New V1.3 diagnostic reproduces bool/NaN/±inf accepted as PRESENT by `runtime/metrics.py` and potentially persisted/aggregated to nonfinite outputs. Existing 21 metric tests miss these cases.
- Root cause: Python bool is an int subclass and current normalize/aggregate use broad `isinstance(...,(int,float))` checks without finite validation.
- **Codex SP1 released:** finite, non-bool PRESENT predicate + legacy-invalid aggregation defense + provenance/MISSING preservation + red/green/full evidence.
- Owner target is V1.3 genuine-live; no new external/live grant and no Fable handoff.
