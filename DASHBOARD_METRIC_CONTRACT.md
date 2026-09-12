# Jira metrics — overall and per project

Requested 2026-09-12. Implement through `DASHBOARD_MASTER_PROMPT.md`. This is a specification, not live Jira configuration or verified issue totals. Use native Jira only and retain waterfall; do not introduce sprints to manufacture a chart.

## One definition, several scopes

Use the same definitions and layout with different validated saved filters:

1. **All accessible Jira:** inventory of all issues the viewing account can access. Label permission limits; it is not proof of all issues on the site. Separate raw inventory from deliverable-task analytics.
2. **Managed portfolio:** the agreed project/product cohort, with explicit exclusions. Reuse dashboard 10002 for delivery and 10003 for AI execution where suitable after inspecting them live.
3. **Each managed Jira project:** the same delivery and execution panels, using that project's filter.
4. **Each product sharing a Jira project:** the same panels with a verified product label/component filter. G7 contains DocPilot and Conduit; a G7 total alone cannot answer both products' progress. Shared PT scopes also need separate product filters.

Maintain a dashboard/filter directory linking each scope, Jira project, product, board and dashboard. Reuse existing objects before creating missing ones. A board is a filtered view, not an additive accounting unit: overlapping board/product counts must never be summed as portfolio totals. Digital Temple receives no configuration or issue changes; if it appears in read-only all-accessible inventory, distinguish it from managed work.

## Metrics and native delivery

| Metric, in overall and per-project views | Definition | Native delivery / verification needed |
|---|---|---|
| Total issues and total deliverable tasks | Two separate unique-key counts; document issue types and inclusion rules | Filter Results and supported count gadgets; show both denominators |
| Every current status | Exact workflow statuses, including review, blocked and waiting where they are statuses; also show To Do / In Progress / Done categories for comparison | Status Pie/Issue Statistics and project × status Two-Dimensional Statistics; separate flagged/blocked filters if those are not statuses |
| Newly opened per day | Issues created in the selected day, not every transition into an open state | Created vs Resolved, daily interval where available |
| Closed/resolved per day | State whether this means resolution events or accepted Done transitions | Native Created vs Resolved uses resolution semantics; verify workflow behavior before naming it “completed” |
| Reopened per day | Distinct issues meeting the documented reopen rule in that date window | Validated history JQL and Filter Results where supported; this is not a count of every repeated transition |
| Current open backlog and historical flow | Unfinished tasks now; historical count across mapped board columns separately | Saved filters now; Kanban Cumulative Flow Diagram for board history, not original-estimate hours |
| Count completion percentage | Accepted completed deliverables / eligible deliverables in the declared cohort | Status chart percentages only if statuses/denominator match; otherwise native counts plus an explicit capability gap for the custom ratio |
| Every status by execution identity | Current delivery tasks by verified executor route, actual model/provider/effort and machine; author/reviewer attempts separately | Supported Two-Dimensional Statistics axes, or filtered native tables when a field is not chartable. Include unknown/missing categories |
| Planned total, completed and unfinished hours | Sums of the original baseline estimates for eligible tasks, partitioned by accepted completion | Native time reports where the exact scope is supported; issue tables elsewhere. Verify whether the tenant's workload report/gadget supports the desired estimate and filtered cohort |
| Logged actual time and current remaining hours | Worklogged hours and current remaining estimates, each split accepted-completed / unfinished / other dispositions | Native Time Tracking report within its project/version limits; tables for wider unsupported scope. Keep nonzero remaining on completed tasks visible as anomalies |
| Completion weighted by planned hours | Original baseline hours attached to accepted completed tasks / total baseline hours | Custom arithmetic is not established in native gadgets. Preserve numerator/denominator and estimation coverage; do not promise a calculated native tile without verification |
| Remaining-hours history / burndown | Historical remaining estimates at each day boundary, with scope additions/removals visible | **Native gap for daily waterfall history at project, product and cross-project scopes unless a specific configuration is verified.** Today's estimate cannot recreate past daily values |

“Open” means all unfinished tasks unless a gadget explicitly means the exact workflow status named Open. Do not drop In Review, Waiting, Blocked or unusual project statuses. Every selected interval uses a stated timezone, initially America/New_York, and actual refresh time. Offer useful 7/30/90-day and all-time views only where the native control supports them; do not imply a global interactive dashboard selector exists.

## Honest completion and hour accounting

- Establish an explicit eligible delivery cohort. Epics, execution-attempt issues and administrative records are not automatically deliverable tasks. Choose task versus subtask accounting once: count the owned leaf estimate or parent estimate, never both its rollup and its children.
- Preserve original estimates. Jira Original Estimate is mutable: use an evidenced frozen baseline where available; otherwise label sums as current Original Estimate totals, with no historical-baseline claim. Show baseline scope and current scope separately when tasks are added, removed or re-estimated. Record baseline membership/time from available evidence; do not invent an old baseline.
- Canceled, duplicate, rejected and descoped work is a separate disposition, not accepted delivery. Excluding it from a revised denominator must be visible alongside the original baseline. A Done-category total is not automatically the accepted-completion numerator.
- Show an hours matrix with **planned original / logged actual / current remaining** rows and **accepted-completed / unfinished / canceled or other dispositions / total** columns. Original estimate minus worklogs is not a trustworthy remaining estimate. Baseline planned total reconciles across all baseline dispositions; a revised eligible cohort needs its own denominator. A task estimated at 1h and completed in 30m contributes 1h to completed planned effort and 30m to logged actual work; do not rewrite the baseline to 30m. Nonzero remaining on a completed task is an anomaly to inspect, not permission to force zero.
- Unknown estimates are missing, not zero. Show estimated-task and worklog coverage plus evidenced explicit-zero counts. Absent worklogs do not prove no work occurred. A weighted completion percentage covers estimated scope only unless every eligible estimate is known. Zero eligible tasks or zero total estimated hours produces N/A for the corresponding ratio. Jira's configured working hours/day and days/week govern display conversion; use native seconds for comparisons.
- A task finished by two models counts once as delivered. Preserve all actual attempts, host changes and reviewers separately. Parallel one-hour attempts may represent two aggregate execution hours but one elapsed hour. IDE names and planned assignments cannot prove actual model identity.
- Resolution date, status category, rightmost board column and accepted delivery can disagree. Test real issues before equating them. Created vs Resolved is a flow chart; it is not the daily unfinished backlog or a complete repeated-close event ledger. Never reconstruct historical events from current fields alone.

## Standard dashboard layout

Apply this template to the portfolio and then each agreed project/product:

1. **Scope and health:** eligible total, all-status distribution, accepted completion counts, unknown estimate/model coverage, last verification time.
2. **Daily flow:** created/resolved trend, valid reopen list, board CFD/report link, aging unfinished work and blocked/review-ready lists.
3. **Effort:** original estimate, measured spent and current remaining columns; supported native time-report links and clearly labeled gaps for cross-project totals/ratios/history.
4. **AI delivery and review:** route/model/provider × status where supported, author and reviewer cohorts, evidence missing/repair-needed lists, machine breakdown. No attribution inferred from a task's latest assignee.

For site-wide inventory add project × status and project issue counts. For individual products replace the portfolio grouping with their components/workstreams. Keep the same metric dictionary so comparisons mean the same thing. Reuse the template sequentially; do not create dozens of empty dashboards before validating the first portfolio and one project view.

## Native capability boundary, checked against official Cloud documentation

- [Report catalogue](https://support.atlassian.com/jira-software-cloud/docs/generate-a-report/): Time Tracking totals original/remaining/spent for a project version, requires Fix Version and enabled time tracking, and documents a limit of 1,000 issues plus 1,000 subtasks. This does not prove arbitrary whole-portfolio sums. Workload Pie Chart documents assignee workload for a project or saved filter; verify exact units, field selectors and gadget availability in this tenant before treating it as an hours summary. Do not create fake versions solely to force a metric.
- [Cumulative Flow Diagram](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-cumulative-flow-diagram/): native Kanban issue flow by board column. Multiple statuses in one column are combined; it is not an hours chart.
- [Burndown](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-burndown-chart/) and [Release Burndown](https://support.atlassian.com/jira-software-cloud/docs/what-is-the-release-burndown-report/): sprint-based. Preserve the user's waterfall decision.
- [Version Report](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-version-report/): Scrum-board-only, excludes subtasks, follows the board filter and rightmost-column completion. It is not an equivalent site-wide remaining-hours chart.

Deliver a metric-by-scope capability matrix: working native gadget, native report link, native issue list, or unavailable. Reconcile each working count/total to its issue scope, estimate completeness and representative source rows. Unsupported does not mean zero. No marketplace tools, external BI, synthetic worklogs, fabricated daily snapshot issues or hidden sprint conversion.
