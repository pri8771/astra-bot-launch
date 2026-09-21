# Forward execution plan — V0.6 through V3.0

This file is **planning / backlog decomposition**, not current execution authority.

Claude should use it to build dependency-safe future scaffolding only when current canonical assignments permit.
ChatGPT lead should keep refining these downstream contracts, acceptance criteria and artifact packets while Claude owns implementation.

Version promotion remains governed by `MILESTONE_MANIFEST.md`.

---

## V0.6 — honest end-to-end dry runs

### Goal
Prove all three general bots can complete the full internal operating loop on real current evidence with zero public publication.

### Required existing artifacts
- SB-V06-001 Social-A real dry-run packet
- SB-V06-002 Social-B real dry-run packet
- SB-V06-003 Social-C real dry-run packet
- SB-V06-004 independent final-candidate review bundle
- SB-V06-005 dry-run evidence validator

### Engineering tasks
- one reusable bounded dry-run runner;
- run manifest with source/provider/code/config hashes;
- exact call-budget manifest integration;
- no-retry model invocation accounting;
- zero-public-effect authority profile;
- factual/voice/platform/cultural review composition;
- experiment registration + learning delta + next-check persistence;
- mechanical evidence validator;
- independent reviewer surface separate from generator.

### Acceptance evidence
Each bot must use newly captured current evidence and produce a complete attributable run packet. No fixture can satisfy operational acceptance.

---

## V0.7 — always-on worker/lead loop

### Goal
Prove autonomous execution infrastructure without relying on an open chat.

### Required artifacts
- SB-V07-001 host worker/runbook
- SB-V07-002 recurring host invocation/session-heartbeat proof
- SB-V07-003 ChatGPT direction acknowledgement/consumption
- SB-V07-004 crash/restart/no-overlap acceptance
- SB-V07-005 two-cycle autonomous lead/worker proof

### Engineering tasks
- worker-once command;
- scheduler adapters;
- local durable one-session heartbeat;
- invocation receipts;
- assignment claiming;
- lease/fencing integration;
- crash injection;
- canonical lead-direction fetch/ack;
- Git conflict-safe commit/push behavior;
- host runbook;
- observability/dashboard derived from receipts, not chat presence.

---

## V0.8 — real account connectivity

### Goal
Map each persona to verified real platform destinations while keeping credentials outside Git.

### Existing preparation
The registry already includes zero-spend route research and several Buffer/direct-route artifacts.

### Tasks
- canonical account registry schema: platform/account/profile/persona/verification time/status;
- exact X route;
- Instagram route;
- TikTok route;
- Reddit route;
- Facebook route;
- analytics read route;
- Buffer workspace/channel readback if used;
- destination validator;
- draft-only adapter before any public authority;
- MFA/passkey/CAPTCHA owner-gate runbook;
- secret-store integration;
- read-only health checks;
- destination/persona mismatch hard stop.

### Acceptance
Fresh readback of the real destination mappings. No credentials in repo. Public posting still disabled.

---

## V0.9 — controlled public canaries

### Goal
One bounded real public canary for each general persona after explicit owner authorization.

### Tasks
- canary authorization manifest;
- destination lock;
- content hash lock;
- exactly-once submission;
- external permalink/readback;
- duplicate detection;
- correction/delete escalation rules;
- analytics observation window;
- measurement receipts;
- post-window learning update;
- next-decision proof.

### Acceptance
Real public evidence per persona plus measured post-window learning. Never infer publication from an API request alone; require readback/permalink.

---

## V1.0 — three autonomous real-world bots

### Goal
All three bots continuously operate the full loop on real social presences.

### Required manifest artifacts
- SB-V10-001 continuous three-bot operation acceptance run
- SB-V10-002 real measurement -> learning -> next-decision proof for each bot
- SB-V10-003 failure/recovery/duplicate-prevention acceptance
- SB-V10-004 owner-intervention boundary proof
- SB-V10-005 no-SwarmAI-dependency proof

### Tasks
- sustained multi-bot run window;
- account outage handling;
- scheduler/resource isolation;
- exact-once effects;
- uncertain-effect reconciliation;
- measurement ingestion;
- learning/strategy feedback;
- owner-gate instrumentation;
- full dependency audit proving standalone operation.

---

# V1.x — reliability and intelligence

## V1.1 Reliability hardening
Existing:
- SB-V11-001 reliability/fault injection
- SB-V11-002 acceptance

Tasks:
- process kill at every state transition;
- network/Git/provider/account outage matrix;
- corrupted receipt/state recovery;
- idempotent restart;
- stale worker;
- clock skew;
- disk full/read-only;
- duplicate submission protection;
- correction rollback runbooks;
- long unattended acceptance run.

## V1.2 Multi-platform intelligence
Existing:
- SB-V12-001 platform selection intelligence
- SB-V12-002 acceptance

Tasks:
- expected-value + learning-value platform selector;
- audience/platform fit;
- format capability matrix;
- cost/rate-limit awareness;
- no-platform/NO_ACTION option;
- avoid blind cross-posting;
- evidence that the same idea can choose different platforms under different state.

## V1.3 Analytics brain
Existing:
- SB-V13-001 accepted
- SB-V13-002 acceptance pending

Tasks:
- metric semantic registry;
- provenance and observation windows;
- normalized but non-conflated metrics;
- missing/partial data;
- confidence;
- analytics route freshness;
- cross-platform comparison rules.

## V1.4 Audience memory
Existing:
- SB-V14-001 accepted
- SB-V14-002 pending

Tasks:
- evidence-linked audience hypotheses;
- confidence updates;
- decay;
- contradictions;
- segment boundaries;
- provenance;
- avoid sensitive-person profiling;
- merge/supersede logic.

## V1.5 Autonomous experiment engine
Existing:
- SB-V15-001 repair in progress
- SB-V15-002 pending

Tasks:
- persona-private experiment storage;
- hypothesis/baseline/intervention/window/metric/stop criteria;
- measurement compatibility;
- closeout;
- inconclusive outcome;
- confidence update only from compatible evidence;
- experiment overlap/dedup;
- explicit admin-only cross-persona surfaces.

## V1.6 Content intelligence
Existing:
- SB-V16-001 changes required
- SB-V16-002 pending

Tasks:
- platform-native hooks/forms;
- series memory;
- semantic duplicate detection;
- novelty score;
- reuse/repurpose lineage;
- creative quality signals;
- evidence-locked claims through transformations;
- image/video concept interfaces;
- avoid template-like repetitive style.

## V1.7 Community operation
Existing:
- SB-V17-001 changes required
- SB-V17-002/003 pending

Tasks:
- read-only comment/reply observation;
- conversation memory;
- authority classification;
- candidate reply generation;
- harassment/spam/manipulation filters;
- no engagement bait;
- exact destination/thread binding;
- public reply separately authority-gated;
- community learning without identity contamination.

## V1.8 Cultural personas operational — proposed detailed artifacts
The roadmap names this milestone but registry decomposition should be expanded.

Proposed:
- SB-V18-001 cultural source/reviewer policy
- SB-V18-002 cultural persona community workflow
- SB-V18-003 Primandir-adjacent independence/ad-disclosure acceptance
- SB-V18-004 cultural operational acceptance bundle

Tasks:
- source hierarchy;
- reviewer attribution;
- sensitive-topic escalation;
- religious/cultural accuracy;
- no disguised advertising;
- brand/persona separation;
- correction workflow.

## V1.9 V1 stabilization — proposed detailed artifacts
Proposed:
- SB-V19-001 unattended soak suite
- SB-V19-002 observability/account-health SLOs
- SB-V19-003 cost/resource budgets
- SB-V19-004 runbooks and operator recovery
- SB-V19-005 V1 stabilization acceptance

Tasks:
- long sustained runs;
- account/provider health;
- queue age;
- error budgets;
- resource caps;
- logs/metrics;
- operator playbooks;
- no known supported-path P1/P0 defects.

---

# V2.x — autonomous growth system

## V2.0 Autonomous Growth Engine
Existing:
- SB-V20-001 strategy state/revision engine
- SB-V20-002 growth evaluator/allocation
- SB-V20-003 measured-evidence strategy-change acceptance
- SB-V20-004 operational acceptance
- SB-V20-099 engineering readiness

Tasks:
- versioned strategy state;
- strategy hypotheses;
- measurable objectives;
- evidence-triggered revision;
- reversible changes;
- growth vs learning allocation;
- opportunity-cost model;
- real measured evidence required for operational promotion.

## V2.1 Dynamic strategy
Existing SB-V21-001.

Tasks:
- strategy lifecycle;
- expiration/decay;
- rollback;
- contradiction handling;
- guard against chasing short-term noise;
- explicit rationale/evidence refs.

## V2.2 Goal decomposition
Existing SB-V22-001.

Tasks:
- high-level goal -> bounded subgoals;
- dependency graph;
- budget/authority constraints;
- completion criteria;
- stop conditions;
- no recursive runaway planning;
- artifacts addressable to workers.

## V2.3 Temporary specialist workers
Existing:
- SB-V23-001 worker contract
- SB-V23-002 lifecycle/sandbox/evidence
- SB-V23-003 checkpoint

Tasks:
- researcher/analyst/writer/reviewer/media roles;
- bounded context;
- least authority;
- time/call budgets;
- isolated scratch state;
- attributable output;
- parent integration/rejection;
- cleanup/retirement;
- no SwarmAI dependency.

## V2.4 Long-term learning — proposed decomposition
Proposed:
- SB-V24-001 institutional memory schema
- SB-V24-002 contradiction/decay/seasonality engine
- SB-V24-003 failed-hypothesis archive
- SB-V24-004 long-term learning acceptance

## V2.5 Audience segmentation — proposed decomposition
Proposed:
- SB-V25-001 evidence-backed non-sensitive segment model
- SB-V25-002 segment strategy differentiation
- SB-V25-003 privacy/safety acceptance

Do not create deceptive or sensitive personal profiling.

## V2.6 Trend intelligence — proposed decomposition
Proposed:
- SB-V26-001 trend collector/normalizer
- SB-V26-002 persona relevance/novelty evaluator
- SB-V26-003 trend timing experiment planner
- SB-V26-004 irrelevant-virality rejection acceptance

## V2.7 Cross-platform strategy — proposed decomposition
Proposed:
- SB-V27-001 idea lineage/canonical concept
- SB-V27-002 platform-native transformation
- SB-V27-003 cross-platform sequencing
- SB-V27-004 duplication/cannibalization acceptance

## V2.8 Growth allocation — proposed decomposition
Proposed:
- SB-V28-001 portfolio of experiments allocator
- SB-V28-002 time/resource opportunity-cost model
- SB-V28-003 exploration/exploitation policy
- SB-V28-004 allocation acceptance

## V2.9 Self-evaluation — proposed decomposition
Proposed:
- SB-V29-001 strategy drift detector
- SB-V29-002 repetition/quality regression detector
- SB-V29-003 reliability self-audit
- SB-V29-004 bounded improvement proposal workflow
- SB-V29-005 self-evaluation acceptance

Self-evaluation may propose code/config changes; it does not get unrestricted self-modification authority.

---

# V3.0 — autonomous multi-brand media organization

Existing:
- SB-V30-001 portfolio-level planning
- SB-V30-002 shared-knowledge/brand-isolation boundary
- SB-V30-003 portfolio growth/resource allocation
- SB-V30-004 organizational memory/self-evaluation
- SB-V30-005 V3.0 acceptance

## Target architecture

### Brand plane
Each persistent brand/persona has:
- strategy;
- voice/persona memory;
- account mappings;
- content/experiment history;
- community memory;
- objectives and constraints.

### Shared knowledge plane
May contain:
- public factual knowledge;
- source receipts;
- reusable platform knowledge;
- generalized learnings proven safe to share.

Must not leak:
- private persona identity state;
- account secrets;
- brand-specific confidential state;
- unreviewed strategy assumptions.

### Specialist worker plane
Temporary bounded workers can be created for:
- research;
- analysis;
- writing;
- review;
- media concepts;
- QA.

### Portfolio plane
Optimizes:
- attention;
- compute/model call budgets;
- platform coverage;
- experiment diversity;
- cross-brand opportunity cost;
- learning value.

### Organizational memory
Stores:
- accepted strategies;
- failed hypotheses;
- incidents;
- source trust history;
- platform changes;
- operational lessons;
- versioned policies.

## V3.0 acceptance themes
- multi-brand isolation under concurrency;
- safe shared facts without identity contamination;
- portfolio planning from real evidence;
- specialist-worker lifecycle;
- bounded autonomous execution;
- organizational self-evaluation;
- owner intervention focused on authority/identity/legal/policy/strategy;
- explicit proof of zero SwarmAI runtime/service dependency.

---

# Cross-version planning rules

1. Reuse > rebuild.
2. Every operational effect has an attributable receipt.
3. Every model call has a bounded authorization/budget where required.
4. Every public effect is exactly-once or reconciled as uncertain.
5. Every persona-private surface is structurally isolated.
6. Every future autonomous planner has bounded authority and stop conditions.
7. Engineering readiness must never be mislabeled as operational promotion.
8. ChatGPT lead works ahead on contracts, risks and acceptance; Claude primarily implements.
