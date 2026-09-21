# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current heartbeat review: `LEAD-017` (`lead-reviews/LEAD-017_2026-09-20T2152.md`). Foundational deep audit remains `LEAD-015` (`LEAD_AUDIT_TWO_LANE_BATCH.md`).

At LEAD-017, the Intelligence repair lane has fresh signed repository activity through `cbd781cab4d751b2a0626c3ce060c5a217d771e9`. The expected Windows Core/Host and Mac QA branches were not yet visible remotely. No GitHub status checks exist at the latest Intelligence repair head, so test counts remain worker-local unless source/acceptance behavior is independently inspected.

## Current observations

The SP2–SP5 sample continues to support worker-first implementation with stronger lead review at trust/isolation boundaries:
- SP2 bounded test/evidence repair (`SB-V03-003`) closed cleanly after one lead-found coverage gap.
- SP3 can be strong on bounded state changes (`SB-V03-002`), but `SB-V05-001` now shows repeated trust-boundary misses: first `mode="live"` was caller-forgeable; the repair moved trust into a registry, but the public registry still lets arbitrary runtime code self-register a custom class and obtain operational-live evidence.
- SP4 repair `SB-V05-002` fixed the original caller-stance/material-claim omissions, but independently repeated the same public self-registration authority pattern for assessors and still overclaims full support from token co-occurrence. Cross-interface/persona/trust work remains the main SP4 risk cluster.
- SP5 fencing improved substantially but still requires the Windows repair wave for complete durable-write fencing and supported host proof.

This is not a reason to take implementation away from Claude. It is a reason to specify closed trust boundaries, dependency provenance and adversarial semantic tests explicitly in SP3+ evidence artifacts.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> worker added forced FACT + VOICE failures | ACCEPTED | good bounded repair behavior |
| SB-V03-004 | 5 | PARTIAL | first repair added generation fence; deep audit found decision log/latest-decision writes outside fence and transactionality overclaim | CHANGES_REQUIRED | Windows repair branch expected; no remote checkpoint visible at LEAD-017 |
| SB-V03-005 | 4 | PARTIAL | logical filters added; deep audit found hypotheses + consumed_signal_ids still runtime-shared and contextual reasoning reads cross-persona hypothesis count | CHANGES_REQUIRED | state model repair required, not just read-filter repair |
| SB-V03-006 | 3 | BLOCKED | depends on accepted V03-004/V03-005 | BLOCKED | regenerate only after repair |
| SB-V04-001 | 3 | PARTIAL | schema validation fixed; production default still baseline/non-adaptive unless env opt-in | CHANGES_REQUIRED | repair default posture; preserve validation |
| SB-V04-002 | 5 | PARTIAL | contextual provider materially varies by context but truthfully reports adaptive=false | CHANGES_REQUIRED | useful component, not real V0.4 adaptive provider |
| SB-V04-003 | 4 | PASS-LIKE source review | dependency V04-001 unresolved | BLOCKED | policy boundary looks sound; avoid churn unless upstream repair affects it |

## Intelligence lane task results

| Artifact | SP | First submission | Independent review finding / repair cycles | Current lead disposition |
|---|---:|---|---|---|
| SB-V05-001 | 3 | PARTIAL | Repair cycle closed direct `mode=live`, obvious SSRF classes and extraction validity, but LEAD-017 found public mutable `register_trusted_transport` self-certification; `to_signal()` accepts verified-but-untrusted live receipts; real urllib redirect/DNS TOCTOU proof incomplete | CHANGES_REQUIRED |
| SB-V05-002 | 4 | PARTIAL | Repair added attributable assessor + material-claim identification, but `register_operational_assessor` is publicly self-registerable; operational evidence refs accept verified fixture/untrusted captures; keyword co-occurrence can overclaim full SUPPORTS | CHANGES_REQUIRED |
| SB-V13-001 | 4 | FAIL acceptance invariant | no snapshot/delta/gauge/rate kind; aggregate sums cumulative snapshots | CHANGES_REQUIRED |
| SB-V14-001 | 4 | FAIL isolation/privacy invariant | bot-scoped persistence; sensitive-attribute blacklist bypassable; fork converts contradiction into unsupported positive evidence | CHANGES_REQUIRED |
| SB-V15-001 | 4 | PARTIAL | honest lifecycle behavior, but baseline/treatment lack required normalized-observation/evidence provenance | CHANGES_REQUIRED |
| SB-V16-001 | 4 | PARTIAL | bot-wide history/novelty plus factual binding is presence-only rather than accepted support-status validation | CHANGES_REQUIRED |
| SB-V12-001 | 3 | PASS-LIKE source review | good no-fabricated-history/availability behavior; depends on V13 | BLOCKED |
| SB-V17-001 | 4 | PARTIAL | no-public-effect boundary good; read-only source is caller-asserted and community memory/themes are bot-wide | CHANGES_REQUIRED |
| SB-V20-002 | 4 | PARTIAL | good missing/no-spend math, but arbitrary numeric performance/audience inputs can drive recommendations without typed accepted evidence | CHANGES_REQUIRED |

## LEAD-017 focused lessons

### Trust registries

A registry is not automatically a trust boundary. If arbitrary runtime code can call the registration function, the caller still controls trust.

For future evidence/security packets, acceptance tests should distinguish:
- declaring a property;
- registering oneself;
- using a module/configuration-owned closed allowlist/capability;
- test-only dependency injection.

The operational path must use the third model. The fourth is acceptable only when it is structurally prevented from becoming operational evidence.

### Semantic verification

An attributable assessor is necessary but not sufficient. A weak assessor should not be promoted to an operational factual oracle simply because it has a name/version. If it cannot establish proposition/negation/value relations, it should return uncertainty/partial/unsupported rather than full support.

### Dependency provenance

A downstream artifact must not silently upgrade fixture/untrusted upstream evidence merely because the object is structurally valid or hash-verified. Operational provenance must survive every interface boundary.

## Independent defect themes

### Persona/workspace isolation
Repeated across SP4 Intelligence/Core work:
- V03-005 private state remains runtime-shared;
- V14 audience memory bot-wide;
- V16 novelty/history bot-wide;
- V17 community themes bot-wide;
- V20-002 needs validated persona scope.

Action: every SP4+ packet touching memory/history/analytics must state whether data is runtime-shared, persona-private or organization-shared and include mixed-persona tests.

### Metric semantics
V13 preserved missing-vs-zero but missed the stronger semantic-kind contract despite it being groomed before implementation. Future analytics/experiment work must carry cumulative/delta/gauge/rate semantics through interfaces and acceptance examples.

### Dependency discipline
Workers can build useful additive scaffolding ahead of acceptance, but dependent artifact status remains blocked until prerequisites are accepted. Consume the newest canonical repair packet before each artifact.

### Worker-local tests vs independent CI
Core historical batch reports 85 tests. Intelligence repair reports 145 at `cbd781ca...`; GitHub independent status checks remain absent. Implement `SB-CTL-006` once ownership is resolved to improve independent acceptance evidence.

## Metrics to continue accumulating

For each SP level:
- attempts;
- first-pass accepted;
- first-pass partial/failed;
- repair cycles;
- independent findings;
- dependency violations/early-start incidents;
- escaped defects;
- acceptance after repair;
- CI vs worker-local evidence.

Do not infer worker quality from one artifact. Current evidence supports high Claude throughput with adversarial lead review at cross-cutting trust, isolation and host-boundary artifacts.

## Current concurrency implication

Keep the planned three-session ceiling:
- Windows Core/Host implementation;
- Intelligence repair implementation;
- Mac QA/control only.

Do not add another runtime coding lane until the shared Core state and Intelligence evidence contracts stabilize.
