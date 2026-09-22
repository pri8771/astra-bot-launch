# Social Bots — execution plan to V2.0

Established by ChatGPT lead on 2026-09-20.

## Owner goal

Long-term target: V3.0.

Strategic checkpoints:
1. V1.7
2. V2.3
3. V3.0

Today's engineering target:
- Reach **V2.0 engineering-ready** if implementation/review throughput allows.
- Do not falsify operational promotion. True V1.0+/V2.0 operational acceptance still requires real account/public/measurement evidence where the milestone contract requires it.

## Current verified position

Canonical accepted state remains **V0.3.x**.

Accepted:
- SB-V03-002 signal-delta correctness.

Changes required:
- SB-V03-003 review-stop regressions.
- SB-V03-004 active-cycle lease fencing / fence-loss prevention.
- SB-V03-005 persona workspace isolation contract/code reconciliation.

Blocked:
- SB-V03-006 acceptance bundle until 003/004/005 clear.
- Always-on host proof and public-account gates remain separate external blockers.

Worker branch has also submitted a partial V0.4 reasoning seam at PR #2 head 2a53046f. This is not yet V0.4 acceptance.

## Delivery model

Three-lane team:

### Lead lane — ChatGPT
Owns:
- artifact graph / acceptance;
- independent code and evidence review;
- decomposition;
- architecture/product decisions;
- hard-debugging support;
- future packet preparation;
- conflict resolution;
- integration sequencing;
- milestone promotion.

The lead should stay one step ahead and avoid absorbing routine implementation.

### Worker lane A — Claude Core
Owns:
- runtime correctness;
- leases/fencing;
- state isolation;
- reasoning seam/provider integration;
- deterministic policy boundary;
- worker packaging/recovery;
- reliability;
- V2.0 strategy-state/revision integration.

### Worker lane B — Claude Intelligence
Owns:
- live source capture;
- factual/review pipeline;
- platform-native content intelligence;
- analytics;
- audience memory;
- experiment engine;
- community intelligence;
- growth measurement/allocation inputs.

## Parallelism rule

The two Claude lanes MUST use separate branches and source ownership.

Suggested branches:
- claude/social-bots-core-to-v2
- claude/social-bots-intelligence-to-v2

Both should start from the newest implementation base after reconciling canonical control artifacts.

Neither worker lane should directly mutate canonical:
- ARTIFACT_INDEX.json
- STATE.json
- MILESTONE_MANIFEST.md
- WORK_QUEUE.md
- WORKER_PERFORMANCE.md

Workers submit branch-local source/tests/evidence plus an append-only worker report. ChatGPT lead reconciles canonical artifact state.

## Today critical path

### Gate 0 — clear V0.3
Lane A:
- SB-V03-003
- SB-V03-004
- SB-V03-005
- SB-V03-006

Lead:
- review immediately as each artifact is submitted.

### Parallel Track B starts immediately
Lane B does NOT need to wait for V0.3 to implement isolated modules that do not touch Lane A-owned files.

Start with:
- SB-V05-001 source-capture collector;
- SB-V13-001 normalized analytics/event model;
- then audience-memory / experiment modules behind stable interfaces.

These artifacts cannot promote V0.5/V1.3 early, but implementation can proceed.

### Gate 1 — V0.4 autonomy
Lane A:
- SB-V04-001 reasoning-provider/fail-closed contract repair;
- SB-V04-002 adaptive reasoning implementation;
- SB-V04-003 deterministic policy boundary;
- SB-V04-004 divergence/adversarial suite;
- SB-V04-005 evidence bundle.

### Gate 2 — V0.5/V0.6 intelligence proof
Lane B:
- real source capture;
- claim support review;
- platform-native generation/repair;
- cultural review binding;
- three end-to-end non-publishing dry-runs;
- independent candidate review evidence.

### Gate 3 — V0.7/V1.1 runtime reliability
Lane A:
- host package/runbook;
- worker command/ack protocol;
- crash/restart/no-overlap harness;
- reliability/fault-injection artifacts.

Host-side recurring-liveness evidence remains external until an authorized host actually runs it.

### Gate 4 — V1.2–V1.7 intelligence stack
Lane B:
- platform selection intelligence;
- normalized analytics brain;
- audience memory;
- autonomous experiment engine;
- content intelligence;
- community observation/decision/memory.

External posting/reply effects remain gated. Read-only/offline engineering can still be completed.

### Gate 5 — V2.0 growth engine
Lane A:
- strategy state + revision engine;
- integration into autonomous decision loop.

Lane B:
- growth objective evaluator + allocation recommendations from analytics/audience/experiments.

Lead:
- cross-lane integration/adversarial acceptance;
- ensure strategy changes are evidence-based, reversible, attributable and bounded.

## Definition: V2.0 engineering-ready

Engineering-ready means:
- code/test artifacts required through V2.0 are lead-accepted;
- interfaces compose;
- no operational mocks are presented as real evidence;
- real-world-only acceptance gaps are explicitly blocked;
- V2.0 strategy engine can consume real measurements when available;
- safety/authority gates still prevent unauthorized posting/spend/messages.

This does NOT equal operational V2.0 promotion.

## Operational V2.0 promotion

Still requires:
- verified real accounts / destinations;
- owner-authorized real canaries/public operations;
- real analytics windows;
- evidence that strategy actually changes from measured audience/content performance;
- successful unattended/recovery evidence where required.

If owner later authorizes those gates and the evidence is available today, operational promotion may also clear today.

## Stop conditions

Do not:
- fake live evidence;
- use operational mock data as acceptance;
- silently bypass account/public gates;
- couple to SwarmAI;
- weaken safety to make milestone numbers advance;
- merge conflicting worker branches without lead reconciliation.

## After V2.0

Next strategic checkpoint is V2.3:
- V2.1 persistent dynamic strategy;
- V2.2 autonomous goal decomposition;
- V2.3 temporary specialist worker lifecycle.

Then V3.0:
- portfolio/brand orchestration;
- shared knowledge boundaries;
- multi-brand resource allocation;
- organizational self-evaluation;
- human authority/legal/identity boundary.
