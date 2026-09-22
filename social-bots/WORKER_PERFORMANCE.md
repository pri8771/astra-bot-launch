# Social Bots worker performance

Purpose: track implementation reliability by artifact and task type. Worker submissions never self-accept.

Current lead review: **LEAD-051** (`lead-reviews/LEAD-051_2026-09-21T2155.md`).  
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.  
Current execution ceiling: **LIVE V1.7 only, then hard stop**.

## Current verified activity

### Fable Integrator — ACTIVE

- Verified worker session: `s-20260921T211438Z-d5589881`. It ingested LEAD-048/050 V1.7-only scope after a container restore and correctly did not emit a second heartbeat for the same session.
- Signed material worker history is verified through `af3fded92eaba5e68c8088737b68c6f043e40a5e`.
- `12c807e...` submitted shared pre-dispatch authorization/budget gate; worker reports **559 discovered / 557 passed / 2 skipped** on that SHA.
- `b5fd038...` submitted due-work rotation / first-bot-starvation repair; worker reports **569 discovered / 567 passed / 2 skipped**.
- `c4d31fee...` submitted C05/C06/C07 final-content review binding + prospective experiment semantics; commit reports **678 passed / 2 skipped**.
- `3da19a9c...` selectively consolidated V1.7 Intelligence producers (metrics, audience, experiment engine, community, platform selection) while excluding future V2.0 growth modules.
- `af3fded...` submitted a read-only V1.7 host/provider/account gate dossier. It truthfully records an ephemeral Linux VM, no native scheduler, social-platform CONNECT-403 restrictions, no canonical live authorization manifest, no account registry entries and no named cultural reviewer.

**Lead disposition of R07-041:** **CHANGES_REQUIRED.** The raw live-callable and real CLI paths are materially improved, with canonical re-authorization and durable pre-dispatch call-budget reservation. However, exact policy-owned `EngineeringStub` and injected-runner seams are currently executable when **no dispatch scope exists**, while their constructors accept arbitrary caller-supplied callables/runners. That leaves a caller-controlled no-grant execution capability. No-scope must fail closed; engineering seams may run only under an explicit policy-owned engineering scope and must remain refused in production scopes. This repair is zero-live and requires harmless sentinel regressions.

The current tests themselves confirm the policy gap by explicitly asserting that a declared EngineeringStub runs outside production with no scope. This is evidence for the finding, not acceptance.

**Disposition:** Fable remains sole enabled implementation/integration owner through V1.7. Repair R07-041 first; then continue only non-overlapping zero-live/offline V1.7 work. No V1.8+/V2.3/V3.0 continuation.

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
| SB-R07-041 | CHANGES_REQUIRED | engineering/injected seam no-scope capability bypass remains |
| SB-R07-071 | SUBMITTED | atomic session uniqueness source; independent QA required |
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

- **Fable:** ACTIVE sole integrator; repair R07-041 seam, then continue <=V1.7 only.
- **Acceptance:** STALE / ACTION REQUIRED; review-only.
- **Cursor/Core/Intelligence:** PARKED / evidence-only.
- **Canary:** FROZEN / evidence-only.
- **worker-pc:** excluded until private-repo clone/auth is demonstrably fixed.
