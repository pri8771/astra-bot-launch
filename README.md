# Astra bot launch task library

> **2026-09-25 owner direction:** replace the old bot execution structure with n8n mission crews on the R730. See [the n8n crew transition](N8N_CREW_TRANSITION.md). The older launch instructions below are migration references, not the selected future runtime. No live cutover is claimed.

Private, portable instructions for One Person Ops, Wait How Big and CommerceLint first, then BidetFit and Guru. **Current owner priority: kick off these five before further Kai/Pri/Lipi discussion.** Start with `FIVE_BOT_KICKOFF.md`, `WAVE_STATUS.md`, `BOT_ROADMAPS.md` and `tasks/README.md`. This is the task/control repository, not all product source or proof of an operating dispatcher.

Target host roles are R730 central hub for Kai/local bots, Windows fallback/available development worker, and Intel i9 Mac low-priority staging/secondary fallback. Existing runtime ownership has not migrated. `focus/kai-pri-lipi/` preserves the three-project evidence and reusable owner-direction contract; those discussions are parked. `setup/i9/` holds optional tested setup scripts, not an i9 installation or running worker. Do not start redundant hardware/framework work instead of a useful launch.

## Product source homes

- OPO: https://github.com/pri8771/one-person-ops — preserved source snapshot, not the finished agent-facing product.
- CommerceLint: https://github.com/pri8771/autonomous_apps — use a fresh isolated checkout; the old Mac clone was stale.
- WHB: https://github.com/pri8771/orchestrator/tree/main/wait-how-big-social — source/operator bundle; execution not qualified.
- BidetFit: https://github.com/pri8771/priyanshchordia.com/tree/main/ventures/bidetfit — deferred.
- Guru: preserved editorial candidate under `reference/guru-sadhana-candidate/`; no runnable cloud bot established.

Each cloud or desktop worker needs its own authenticated local clone/worktree. `*_MAC.md` and `*_WINDOWS.md` are host-specific packets: their absolute paths do not exist automatically in a cloud job. Cloud workers should use the portable `tasks/<mission>/TASKS.md` and `queue.json`, resolve source repository and local checkout, set source_root_override in their own run receipt, and ask for a missing resource rather than invent it. Reference copies are under `reference/`; historical links back into the full Astra repository may be unavailable here. Do not start tasks requiring absent evidence.

## Current execution authorization

The owner resumed Windows release execution and requested a separate Windows Astra Ultra task to finish comprehensive autonomy plans for all five bots plus Lipi. Use `WINDOWS_RELEASE_EXECUTION.md` and `WINDOWS_ASTRA_ULTRA_HANDOVER.md`. The historical 22-task scope gap remains explicit, not a pause on specified release work. Windows/Jira setup is accepted. Actual worker/chat submissions require receiving-host receipts.

## Current gates

22 task definitions are proposed, not Jira issues or admitted jobs. Root/Cursor readiness artifacts already exist locally; do not repeat them simply because they are not copied here. Mac Cursor's existing sole Jira writer could not resume and its connector reported needsAuth. The owner now reports Windows Cursor is authenticated with Atlassian; verify that route and reconcile or explicitly rebind one writer before issue mutations. No credentials are included.

The owner requests native Jira analytics only: use `DASHBOARD_MASTER_PROMPT.md` and `DASHBOARD_METRIC_CONTRACT.md` for matching overall/project/product status, daily flow, completion and hour views. Retain waterfall and report unsupported native charts honestly. Do not install marketplace/BI tools or report invented token/cost totals. Preserve estimates, unknowns and independent reviewer attribution. `NEXT_PROJECT_DISCUSSIONS.md` inventories the five bot folders and proposes the following one-at-a-time discussions; it is not a new execution batch.

Publish source/receipts only to intended private repositories. No auto deployment, public posting, purchases, cloud-agent permissions, schedules or model polling were activated by this repository. Keep original local sources and unrelated work intact.
