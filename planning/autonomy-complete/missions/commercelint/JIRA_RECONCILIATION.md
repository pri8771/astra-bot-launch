# CommerceLint Jira reconciliation proposal

This is an outbox-ready planning proposal. Actual `jira.key` is null for every task. The designated Windows release parent is the sole writer; no issue was created or edited by this lane.

Current root read-only snapshots: `../../evidence/JIRA_READBACK.json` and `../../evidence/JIRA_MISSION_SEARCH.json`. Their metadata proves candidates exist, not exact source/spec admission. Compare current descriptions, dependencies, field contexts, acceptance artifacts and worker scope before choosing reuse/extend/new. Do not overwrite original estimates, remaining estimates, actuals, labels or history from these new planning ranges; observation waiting is not work time.

| Planning ID | Candidate keys, not bindings | Scope matching action |
|---|---|---|
| CL-01 | BOTS-114, BOTS-5, BOTS-6, BOTS-7, PCH-139 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-02 | BOTS-115 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-03 | BOTS-115, BOTS-116 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-04 | BOTS-115, BOTS-116 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-05 | BOTS-116, BOTS-118 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-06 | BOTS-113, BOTS-115, BOTS-118 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-07 | BOTS-116 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-08 | BOTS-5, BOTS-6, BOTS-7 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-09 | BOTS-5, BOTS-7 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-10 | BOTS-118, BOTS-5 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-11 | BOTS-5, BOTS-6 | Reuse accepted overlap; extend only missing criteria; native readback required |
| CL-12 | BOTS-118, BOTS-5 | Reuse accepted overlap; extend only missing criteria; native readback required |

BOTS-114 baseline was present in root current readback with original estimate 5,400 seconds and link to PCH-139. Preserve that value and accepted baseline evidence. BOTS-113/115/116/118 are broader product/experiment matching candidates; BOTS-5/6/7 carry existing operating-scope candidates and must be checked before proposing duplicate autonomy work. Historical source account/CRM facts do not justify resetting issue state or changing current workers.

Before dispatch: sole writer returns actual native key, owner, complete scope/acceptance, dates/dependencies/required planning fields, original estimate and preserved actuals, task/source/spec hash and matching readback. Changed task/source invalidates that admission. Unavailable writer queues the proposal; it does not create a competing writer or stop unrelated already-admitted releases.