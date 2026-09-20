# Social Bots work-management contract

Established 2026-09-20 by ChatGPT lead.

## Artifact-first rule

`ARTIFACT_MANAGEMENT.md` is authoritative for how work is represented.

Tasks and story points describe worker packets; durable progress is represented by artifact IDs in `ARTIFACT_INDEX.json`. A task is not complete merely because its implementation steps were performed. The produced/repaired artifact must reach the required status and acceptance evidence.

Where possible, queue entries should reference an artifact ID and a packet under `artifact-packets/`.

## Lead / worker operating rule

Claude Code is the implementation workhorse.

The lead should keep Claude's queue stocked with the bulk of implementation work, especially routine and easy work. ChatGPT may research, review, debug, reproduce failures, inspect external/current source, define product behavior, write acceptance criteria, groom backlog, decompose difficult tasks and maintain truthful project state.

The lead should not absorb the implementation backlog merely because it can solve a problem. If a task is primarily source-code implementation, repetitive repair, test writing, host setup or routine integration, assign it to Claude unless:
- independent verification requires the lead to reproduce or inspect it;
- the worker is blocked and a small lead-side investigation can unblock it;
- debugging requires an independent second perspective;
- the task is a product/architecture decision rather than implementation.

When current implementation work is waiting on Claude, the lead should move forward on useful non-overlapping work:
- research future platform/API constraints;
- inspect reusable repositories/components;
- review open PRs and tests;
- identify hidden defects;
- predefine acceptance tests;
- groom future-version backlog;
- split oversized work into 1–5 point tasks;
- resolve product ambiguity;
- verify account-safe metadata;
- prepare independent test/evidence plans.

Do not manufacture work merely to stay busy. Do not duplicate Claude's active implementation paths.

## Story-point scale

Story points measure complexity, uncertainty, blast radius and verification burden. They are not hours.

### SP1 — trivial / sharply bounded
Characteristics:
- one obvious isolated change;
- low ambiguity;
- very small blast radius;
- simple deterministic acceptance;
- usually one file or a tiny documentation/config/test change.

Worker expectation:
- should normally complete cleanly in one attempt;
- review should find little or no substantive repair.

Examples:
- add one missing validation;
- update one safe metadata record;
- add one narrow regression test after behavior already exists;
- rename/fix one broken path with clear evidence.

### SP2 — small
Characteristics:
- a couple of related changes;
- low ambiguity;
- limited multi-file impact;
- straightforward tests.

Worker expectation:
- high first-pass success rate;
- minimal lead intervention.

Examples:
- repair one guard plus its tests;
- add one receipt field end-to-end;
- implement one account-map parser/validator;
- add one platform-limit validation path.

### SP3 — medium
Characteristics:
- several files or one meaningful logic change;
- moderate state/edge-case reasoning;
- multiple acceptance checks;
- clear solution space but non-trivial integration.

Worker expectation:
- should be independently executable from a good task packet;
- one repair cycle is acceptable; repeated misunderstanding indicates task or worker-quality issues.

Examples:
- signal-delta consumption + persistence + regressions;
- live-source collector with receipts;
- factual-review pipeline for one content path;
- isolated adapter integration with fault handling.

### SP4 — substantial
Characteristics:
- cross-cutting integration;
- concurrency, lifecycle, external system or durable-state concerns;
- significant verification burden;
- some architectural choice.

Worker expectation:
- require a checkpoint/design readback before or during implementation when risk warrants;
- may be split into SP2/SP3 subtasks while retaining one SP4 integration acceptance.

Examples:
- recurring host worker installation + restart/recovery evidence;
- end-to-end account adapter with safe auth boundary;
- experiment closeout/learning integration across state and analytics.

### SP5 — difficult / high-risk
Characteristics:
- concurrency/fencing;
- new reasoning architecture;
- broad state migration;
- multi-system integration;
- high uncertainty or failure blast radius;
- adversarial verification required.

Worker expectation:
- usually decompose into smaller owned subtasks plus a final SP5 integration/acceptance task;
- lead should not hand Claude a vague monolith;
- failure should produce a narrower next packet rather than repeated whole-task retries.

Examples:
- race-safe lease takeover + shared-runtime concurrency model;
- adaptive reasoning interface with deterministic policy boundary and fail-closed model behavior;
- live multi-platform autonomous cycle spanning accounts, publishing, analytics and recovery.

## Worker performance tracking

For every completed Claude task, record:

- task ID;
- story points (1–5);
- source/base ref;
- first-attempt result: pass / partial / fail;
- tests claimed;
- tests independently evidenced;
- review findings count by severity when applicable;
- number of repair cycles;
- whether acceptance was ultimately reached;
- defects escaping into a later checkpoint;
- notes on ambiguity/task-packet quality.

Do not turn story points into speed estimates.

### Capability questions we want to answer

Over multiple tasks:
- What is Claude's clean first-pass rate at SP1, SP2, SP3, SP4 and SP5?
- At what point does decomposition materially improve results?
- Which task types produce the most lead-review defects?
- Does Claude handle isolated correctness work better than cross-cutting concurrency work?
- How many repair loops are typical by story-point level?
- Are failures caused by worker execution, insufficient task definition, missing evidence/access or integration complexity?

Maintain results in `WORKER_PERFORMANCE.md`.

## Queue policy

1. Keep at least several ready tasks when safe, but one task may be explicitly exclusive if it touches shared state.
2. Give Claude the bulk of SP1–SP3 work.
3. SP4 work stays with Claude but should have stronger acceptance/checkpoints.
4. SP5 remains Claude-owned implementation unless there is a compelling reason otherwise; ChatGPT decomposes, reviews and independently tests it.
5. If a task is too difficult or returns repeated defects, split it into smaller independent tasks with a final integration acceptance.
6. External MFA/account/permission gates should not stall unrelated ready work.
7. When the current version has no ready implementation task, groom the next version from `VERSION_ROADMAP.md` rather than waiting idle.
8. Do not begin external/public effects early merely to create work.

## Current decomposition

### V0.3 correctness
- SB-R0A1 — fix signal delta consumption and persistence — **SP3**
- SB-R0A2 — enforce failed-review stop semantics + regressions — **SP2**
- SB-R0B1 — race-safe stale lease takeover — **SP5**
- SB-R0B2 — shared-runtime persona state/lease isolation — **SP4**
- SB-R0B3 — adversarial concurrency integration acceptance — **SP3**

### V0.4 autonomous thinking
- SB-R1A — finish exact-source reuse reconciliation from lead-supplied evidence — **SP1**
- SB-R1B — define reasoning-provider interface + fail-closed contract — **SP3**
- SB-R1C — adaptive alternative generation/scoring implementation — **SP5**
- SB-R1D — deterministic policy boundary around model proposals — **SP4**
- SB-R1E — persona/evidence-divergence acceptance suite — **SP3**

### V0.5 real research/review
- SB-R2A — machine-captured source receipt schema/collector — **SP3**
- SB-R2B — claim-to-source factual support review — **SP4**
- SB-R2C — platform-native formatter/repair loop — **SP3**
- SB-R2D — cultural review evidence binding — **SP2**

### V0.6 dry-run proof
- SB-R3A — three real general-persona dry runs — **SP3**
- SB-R3B — independent reviewer receipt pipeline — **SP2**
- SB-R3C — dry-run evidence validator: all required checks must pass — **SP2**

### V0.7 always-on loop
- SB-R4A — authorized-host worker packaging/config — **SP3**
- SB-R4B — recurring host execution + heartbeat/receipt proof — **SP4**
- SB-R4C — ChatGPT-direction consumption / acknowledgement loop — **SP3**
- SB-R4D — crash/restart/no-overlap host acceptance — **SP4**

These are planning points and may be revised when implementation evidence changes.
