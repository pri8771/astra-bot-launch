# BidetFit Jira reconciliation proposal

This is an outbox-ready planning proposal. Actual `jira.key` is null for every task. The designated Windows release parent is the sole writer; no issue was created or edited by this lane.

Current root read-only snapshots: `../../evidence/JIRA_READBACK.json` and `../../evidence/JIRA_MISSION_SEARCH.json`. Their metadata proves candidates exist, not exact source/spec admission. Compare current descriptions, dependencies, field contexts, acceptance artifacts and worker scope before choosing reuse/extend/new. Do not overwrite original estimates, remaining estimates, actuals, labels or history from these new planning ranges; observation waiting is not work time.

| Planning ID | Candidate keys, not bindings | Scope matching action |
|---|---|---|
| BF-01 | BOTS-131, BOTS-134, PCH-90, PCH-127 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-02 | BOTS-135, PCH-106 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-03 | BOTS-135, PCH-107, PCH-121 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-04 | BOTS-135, PCH-106 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-05 | BOTS-135, PCH-105 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-06 | BOTS-136, PCH-104 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-07 | BOTS-138, PCH-120 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-08 | PCH-109, PCH-110, PCH-111, PCH-112, PCH-113, PCH-114, PCH-115, PCH-116, PCH-123, PCH-124 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-09 | BOTS-138, PCH-127, PCH-108 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-10 | PCH-108, PCH-122 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-11 | BOTS-138, PCH-120 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-12 | BOTS-136, PCH-98, PCH-121 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-13 | PCH-122, PCH-123, PCH-127 | Reuse accepted overlap; extend only missing criteria; native readback required |
| BF-14 | BOTS-138, PCH-120, PCH-124, PCH-127 | Reuse accepted overlap; extend only missing criteria; native readback required |

Retained canonical cross-project history:

- `docs/TRACKER_LINKS.csv` at the inspected portfolio ref maps historical BF-001..033 to PCH-92..124; BF-034 maps PCH-127, parent PCH-90. These are dated stored mappings, not a new live PCH audit.
- Existing BF-006/007/008 accepted beta/deployment/operator work must be reused and reverified, not rebuilt because broader autonomy is incomplete.
- BF-013/014/015/016 correspond to analytics/programs/model-data/measurement tools; BF-017 and BF-029/030/031/034 cover command/experiments/QA/alerts/runtime. Match both these and newer BOTS cards before new issues.
- BF-018..025 and BF-032/033 contain private draft-first support and conditional low-risk sends. Preserve those gates; BF-026..028 remain deferred seller/delegation work and are not required to operate the current affiliate business.
- Required Notion/documentation synchronization remains a designated-writer mirror/outbox operation. No Notion write is authorized to this planning lane.
- Planning IDs BF-01..BF-14 are distinct from historical zero-padded BF-001..BF-034. Do not truncate or mechanically equate them.

Before dispatch: sole writer returns actual native key, owner, complete scope/acceptance, dates/dependencies/required planning fields, original estimate and preserved actuals, task/source/spec hash and matching readback. Changed task/source invalidates that admission. Unavailable writer queues the proposal; it does not create a competing writer or stop unrelated already-admitted releases.