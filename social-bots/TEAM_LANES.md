# Social Bots — two-Claude team lane contract

## Lane A — Core Runtime / Autonomy

Suggested branch:
`claude/social-bots-core-to-v2`

Owned code areas by default:
- runtime/leasing.py
- runtime/worker.py
- runtime/state.py
- runtime/decision.py
- runtime/reasoning.py
- host worker/runner code
- recovery/fencing modules
- new strategy/orchestration modules owned by Core
- matching tests

Immediate chain:
1. SB-V03-003 repair if not already resolved in base.
2. SB-V03-004.
3. SB-V03-005 integration ownership / reconciliation.
4. SB-V03-006 evidence generation support.
5. SB-V04-001..005.
6. SB-V07 worker/recovery implementation artifacts.
7. SB-V11 reliability artifacts.
8. SB-V20-001 strategy state/revision engine.
9. Final V2 integration fixes assigned by lead.

Do not edit Lane B-owned source unless lead explicitly reassigns it.

## Lane B — Intelligence / Growth

Suggested branch:
`claude/social-bots-intelligence-to-v2`

Owned code areas by default:
- runtime/research.py after V03 signal code is stable; avoid modifying signal-consumption semantics.
- runtime/pipeline.py
- runtime/analytics.py
- new platform-intelligence modules
- new audience-memory modules
- new experiment-engine modules
- new content-intelligence modules
- new community modules
- growth evaluator/allocation modules owned by Intelligence
- matching tests

Immediate chain:
1. SB-V05-001 machine-captured source collector.
2. SB-V05-002 claim-to-source factual support.
3. SB-V05-003 platform-native repair/generation.
4. SB-V05-004 cultural-review evidence binding.
5. SB-V13-001 normalized analytics brain.
6. SB-V14-001 audience memory.
7. SB-V15-001 experiment engine.
8. SB-V16-001 content intelligence.
9. SB-V17-001 community intelligence.
10. SB-V20-002 growth evaluator/allocation inputs.

Lane B may prebuild isolated modules before earlier milestone promotion, but must not claim those milestones accepted.

## Shared-file rule

The following are lead-owned on canonical and should not be casually edited by either worker:
- ARTIFACT_INDEX.json
- STATE.json
- MILESTONE_MANIFEST.md
- VERSION_ROADMAP.md
- WORK_QUEUE.md
- WORKER_PERFORMANCE.md

Worker reporting should go under:
- social-bots/worker-reports/core/
- social-bots/worker-reports/intelligence/

Each report names:
- artifact IDs;
- base SHA;
- resulting SHA;
- paths changed;
- tests;
- known limits;
- requested status.

## Collision protocol

If both lanes need the same file:
1. Stop editing that shared file.
2. Implement the lane-specific interface/module first.
3. Record required integration hook.
4. Let ChatGPT lead assign one lane as integration owner.
5. The other lane rebases/merges only after the integration checkpoint.

No silent dual edits to decision.py, state.py, pipeline.py or analytics.py.

## Performance measurement

Story points remain complexity buckets, not time estimates.

The lead will track:
- first-pass acceptance;
- review defects;
- repair cycles;
- integration defects;
- performance by lane and SP size.
