# Detailed execution plan — V1.8 through V3.0

This extends the already-cemented `RECOVERY_TO_V07.md` and `V07_TO_V17_EXECUTION.md`. It does not change current version status.

## North-star architecture

Social Bots evolves into six planes:

1. **Evidence plane** — real sources, analytics, community observations, provenance, factual support.
2. **Memory plane** — persona/audience/experiment/strategy/institutional memory with confidence, decay and contradictions.
3. **Decision plane** — adaptive reasoning, strategy revision, goal decomposition and deterministic policy.
4. **Action plane** — verified accounts, exact destinations, public-effect receipts, readback and reconciliation.
5. **Worker plane** — persistent scheduler sessions plus bounded temporary specialists.
6. **Portfolio plane** — multiple isolated brands, shared-safe knowledge, resource allocation and organizational self-evaluation.

The control plane cuts across all six: artifact registry, owner authorization manifests, budgets, receipts, independent acceptance and version promotion.

## Version completion philosophy

Every version has two distinct levels:
- **engineering-ready** — source/contracts/tests exist;
- **operationally accepted** — the milestone's required real evidence exists.

No later engineering may be used to pretend an earlier operational gate is complete.

---

## V1.8 — cultural personas operational

### Objective
Make the two cultural/Primandir-adjacent personas first-class autonomous editorial entities without sacrificing cultural accuracy or turning them into disguised advertising.

### Build
- SB-S18-001 source hierarchy registry.
- SB-S18-002 attributable reviewer registry.
- SB-S18-003 uncertainty/correction workflow.
- SB-S18-004 Primandir independence/disclosure boundary.
- SB-S18-005 cultural community integration.
- SB-S18-006 operational evidence bundle.

### Architecture
Cultural content uses the same evidence/fact/content/community pipeline as general personas plus an additional cultural-review policy layer. Do not fork a separate runtime.

### LIVE acceptance
Both cultural personas execute real-current-source, zero-public-effect workflows. Evidence must show source hierarchy, reviewer binding, uncertainty handling and no disguised Primandir promotion.

---

## V1.9 — V1 stabilization

### Objective
Turn a working bot system into something that can run unattended and be operated when it fails.

### Build
- structured observability;
- SLO/health evaluator;
- account/provider monitors;
- hard resource budgets;
- executable recovery runbooks;
- release-blocking defect gate;
- long unattended acceptance.

### Infrastructure
Stay single-host where it works. Do not introduce distributed infrastructure merely for scale theater.

Keep append-only receipts as truth. If file-store contention/volume becomes a measured issue, add a storage adapter and move high-churn indexes to SQLite WAL while retaining immutable evidence files. Do not perform a speculative wholesale database rewrite.

### LIVE acceptance
Real scheduler-driven unattended operation over a fixed acceptance window with SLOs, incidents, budgets and recovery receipts.

---

## V2.0 — autonomous growth engine

### Objective
Bots stop following a mostly static strategy and begin changing strategy from measured evidence.

### Inputs
- NormalizedMetricObservation
- AudienceHypothesis
- ExperimentRecord
- GrowthOpportunity
- current StrategyState

### Outputs
- StrategyRevisionProposal
- deterministic policy verdict
- immutable new StrategyState version or NO_CHANGE/REQUEST_MORE_EVIDENCE

### Build
SB-S20-001 through SB-S20-007.

### Guardrails
One anomalous post can never swing the strategy arbitrarily. Use confidence/evidence floors, max deltas, cooldown and rollback.

### LIVE acceptance
Real measured social evidence must cause a bounded strategy revision, and later evidence must validate, hold or roll it back. Engineering simulation cannot promote operational V2.0.

---

## V2.1 — dynamic strategy lifecycle

### Objective
Treat strategy as a durable, changing object rather than a prompt fragment.

### Build
Lifecycle state machine, expiry/decay, contradiction handling, cooldown and rollback.

### Acceptance
Show revise/hold/expire/rollback decisions from controlled evidence histories while preserving every prior strategy version.

---

## V2.2 — autonomous goal decomposition

### Objective
Allow a bot to take a bounded high-level goal such as “improve saves among audience segment X” and produce its own artifact-addressable execution DAG.

### Planner contract
A goal contains:
- objective;
- success metric;
- evidence baseline;
- time horizon;
- allowed authority;
- resource/model/effect budgets;
- stop conditions.

The planner creates:
- research artifacts;
- experiment artifacts;
- content artifacts;
- measurement tasks;
- review tasks;
- dependency edges.

### Hard limits
No recursive runaway planning. Cap task count, recursion depth, worker count, model calls and external effects.

### Acceptance
Generate a valid bounded DAG, execute a safe subset, introduce a blocker/evidence change, and prove the planner reuses completed artifacts rather than restarting everything.

---

## V2.3 — temporary specialist workers

### Objective
A persistent bot can create short-lived specialist workers when specialization is useful.

### Roles
- researcher;
- analyst;
- writer;
- reviewer;
- media-brief worker;
- QA.

### Design
Specialists receive:
- bounded context refs;
- least-authority toolset;
- explicit output schema;
- time/model/effect budgets;
- isolated scratch state.

They do not inherit account credentials or public authority merely because the parent has them.

### Parent integration
Parent validates the result and explicitly accepts/rejects it. Temporary workers cannot directly mutate durable parent state.

### Acceptance
Run concurrent specialists, prove isolation/budgeting/cleanup, and prove the parent can reject a malformed or unsupported result.

This is a Social Bots subsystem, not a SwarmAI dependency.

---

## V2.4 — long-term institutional learning

### Objective
Convert months of history into durable lessons that remain useful without freezing outdated beliefs forever.

### Memory
Use `ORGANIZATIONAL_MEMORY_SCHEMA.md`.

Track:
- facts;
- hypotheses;
- experiment lessons;
- failed hypotheses;
- strategy lessons;
- incidents;
- platform changes;
- source trust;
- runbook lessons.

### Required behavior
- decay;
- contradictions;
- supersession;
- seasonality/context;
- failed-hypothesis retest rules;
- scope-safe retrieval.

### Acceptance
Use time-shift/frozen-history testing plus available accumulated real history to prove old, contradicted and seasonal lessons are treated differently.

---

## V2.5 — audience segmentation

### Objective
Move from one global audience hypothesis per persona to evidence-backed aggregate segments.

### Privacy rule
Segments describe aggregate behavior, not sensitive personal traits or individual dossiers.

Useful features:
- topic engagement;
- format engagement;
- timing;
- save/share/reply patterns;
- content-series affinity.

Avoid:
- protected/sensitive attributes;
- inferred religion/health/politics for targeting;
- person-level behavioral dossiers.

### Build
Feature builder, segment discovery, confidence/provenance, drift/merge/split, strategy binding and privacy gate.

### LIVE acceptance
Real aggregate evidence produces at least two useful differentiated segment strategies without crossing privacy boundaries.

---

## V2.6 — trend intelligence

### Objective
Detect what is changing now, determine whether it matters to each persona, and reject irrelevant virality.

### Pipeline
source capture
→ canonical trend entity
→ velocity/saturation
→ persona relevance
→ audience relevance
→ novelty
→ timing experiment or NO_ACTION.

### Sources
Use public/current source routes already accepted by the evidence layer. Source count is less important than provenance and trust.

### Acceptance
Use newly captured trends. Demonstrate at least one relevant trend path and one high-volume-but-irrelevant rejection.

---

## V2.7 — cross-platform strategy

### Objective
Treat an idea as a canonical editorial object and each platform post as a platform-native execution.

### Flow
CanonicalIdea
→ platform fit
→ transformation
→ factual-lineage check
→ sequencing
→ publication/experiment
→ platform-specific analytics
→ idea-level learning.

### Rules
No copy/paste cross-posting as the default.
No metric conflation.
No factual drift during transformation.
Track cannibalization/duplicate spam.

### Acceptance
One idea must generate materially different, native executions with preserved factual lineage and rational sequencing.

---

## V2.8 — growth allocation

### Objective
Choose what the organization should spend its limited attention on.

### Candidates
- platform opportunities;
- experiments;
- trends;
- content series;
- audience segments;
- reliability work.

### Scoring
- expected growth;
- expected learning;
- confidence;
- opportunity cost;
- reversibility;
- risk;
- resource cost.

### Policy
Use deterministic final allocation. Model reasoning can estimate/propose but cannot grant spend/public authority.

Reserve explicit capacity for:
- exploration;
- reliability;
- existing commitments.

### Acceptance
Evidence/budget changes should produce understandable allocation changes without starving exploration or system health.

---

## V2.9 — bounded self-evaluation

### Objective
The system notices when its own strategy, content, experiments or reliability are deteriorating and proposes improvements.

### Detectors
- strategy drift;
- repetitive/template content;
- declining quality;
- SLO/reliability degradation;
- resource pressure;
- weak/repetitive experiments.

### Output
An improvement proposal includes:
- evidence;
- diagnosis;
- bounded change;
- expected outcome;
- tests;
- rollback.

### Critical boundary
Self-evaluation is NOT unrestricted self-modification.

The system proposes normal artifacts/config/code changes. Those changes still go through the same test/review/authority path as any other work.

### Acceptance
Seed known faults and use real operating evidence. System must find meaningful problems and propose bounded repairs, but must not self-approve or self-deploy them.

---

# V3.0 — autonomous multi-brand media organization

## Objective

Operate multiple persistent brands/personas as an autonomous media organization while preserving brand isolation, shared-safe knowledge and bounded human authority.

## Brand plane

Each brand gets isolated:
- strategy;
- personas/voice;
- objectives;
- account mappings;
- content/idea history;
- experiment history;
- audience/community memory;
- authority constraints.

## Shared knowledge plane

Only allowlisted, safely reusable information crosses brands:
- public factual knowledge;
- source trust;
- platform capability knowledge;
- generalized operational lessons;
- selected organizational incidents/runbook lessons.

Never share by default:
- account credentials;
- private identity state;
- raw community personal data;
- confidential brand strategy;
- unreviewed assumptions;
- another brand's audience hypotheses.

## Portfolio plane

The portfolio planner answers:
- Which brands need attention?
- Which opportunities have highest growth or learning value?
- Which platform/brand combinations are saturated?
- Where should specialist workers be deployed?
- How should fixed model/compute/time budgets be allocated?
- What systemic risk/reliability work outranks growth?

## Worker plane

Persistent brand runtimes may use the shared specialist-worker framework, but every temporary worker receives brand-scoped context and explicit authority.

## Organizational memory

Organization-wide memory includes only accepted reusable lessons and incidents with evidence, scope and confidence.

## Governance

Owner intervention should increasingly be limited to:
- account identity/login/MFA;
- new spend;
- public-action policy changes;
- legal/compliance decisions;
- destructive external actions;
- major brand/strategy decisions the owner explicitly reserves.

Routine planning, research, drafting, experimentation, measurement, recovery and bounded strategy adjustment should not require manual prompt relay.

## Build

SB-S30-001 through SB-S30-010.

## V3.0 acceptance scenario

Run at least two persistent brands concurrently with multiple personas and temporary specialists.

The acceptance run must demonstrate:

1. independent brand strategies and private state;
2. concurrency without cross-brand contamination;
3. safe reuse of an allowlisted shared public fact;
4. rejection of a forbidden cross-brand private-memory access;
5. portfolio-level goal decomposition;
6. resource allocation across brands;
7. at least one temporary specialist per brand with clean lifecycle;
8. organization-wide incident/lesson capture;
9. portfolio self-evaluation producing a bounded improvement proposal;
10. no SwarmAI runtime/service dependency;
11. owner gates remain enforced;
12. exact receipts/evidence for every material decision/effect.

V3.0 is not “AI can post for multiple accounts.” It is accepted when the system behaves as a bounded, auditable autonomous media organization.
