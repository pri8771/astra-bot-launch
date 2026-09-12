# OPO Jira reconciliation proposal

Writer: Dedicated owner-started OPO Cursor Windows writer. Root read-only native metadata was observed at 2026-09-12T21:13Z; this lane only consumed that sanitized evidence. No issue writes, comments, worklogs, links, estimates or statuses were changed. All proposed task jira.key fields remain null.

Current issue metadata is a matching lead, not source/spec admission or acceptance. The writer must read exact scope and returned accepted artifacts, distinguish superseded labels from current owner authority, preserve original estimates/actuals, and record native readback before effect admission. Unknown historical fields stay unknown. Planning estimate ranges are separate and never worklogs.

| Candidate | Current observed summary | Status | Original estimate | Actual | Proposed handling |

|---|---|---|---|---|---|

| BOTS-112 | [BM-001] Resolve mission charters and first-cycle authority | In Review | 1h 30m | unknown | Match only the relevant bounded existing scope; link genuinely missing autonomy integration after exact-source comparison. |

| BOTS-4 | One Person Ops | To Do | unknown | unknown | Match only the relevant bounded existing scope; link genuinely missing autonomy integration after exact-source comparison. |

| BOTS-60 | [BM-E04] One Person Ops first service experiment | To Do | unknown | unknown | Match only the relevant bounded existing scope; link genuinely missing autonomy integration after exact-source comparison. |

| BOTS-124 | [BM-OPO-02] Contract Check: freeze the exact validator, receipt and pilot contract | To Do | 1h 30m | unknown | Contract Check-specific historical scope; retain optional reuse, do not silently repurpose into whole agent business. |

| BOTS-125 | [BM-OPO-03] Contract Check: build the bounded static validator candidate | In Review | 2h | unknown | Contract Check-specific historical scope; retain optional reuse, do not silently repurpose into whole agent business. |

| BOTS-126 | [BM-OPO-04] Contract Check: qualify one approved static release | To Do | 1h 40m | unknown | Contract Check-specific historical scope; retain optional reuse, do not silently repurpose into whole agent business. |

| BOTS-127 | [BM-OPO-05] Contract Check: review the 14-day usefulness and revenue boundary | To Do | 1h 30m | unknown | Contract Check-specific historical scope; retain optional reuse, do not silently repurpose into whole agent business. |

## Outbox procedure

1. Match each TASKS.json candidate against current issue description/source/acceptance, then propose reuse, a dated scope amendment or a new linked missing-scope issue.
2. Keep changed mission goals visible and historical completion evidence intact. Do not bulk close or overwrite old original estimates.
3. Populate the real native task fields/ownership/dependencies and source binding through the designated writer, then save the exact native readback.
4. Register each experiment before its action and preserve a stable experiment/action ID through the outbox. Writer outage leaves durable proposals and blocks only affected unregistered effects.
5. No planner dispatch, worker interruption or new competing writer.
