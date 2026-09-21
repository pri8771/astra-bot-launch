# SESSION_INSTRUCTIONS — Windows Core / V0.3 closure

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-windows-core-host`
Lead review: LEAD-026

Heartbeat is observability only. Do not wait on heartbeat acceptance before coding.

At start/checkpoint:
1. `git pull --ff-only`
2. `git fetch origin`
3. read canonical `FAST_TRACK_EXECUTION.md` and `SESSION_ROUTER.md` with `git show`
4. inspect `worker-reports/windows-core/LEAD_ACK.json`
5. continue dependency-ready work without routine permission prompts.

## Preserve — SB-V03-004 source repair

Lead source review continues to support `7e4345b041b59b9d1b1036dfea388cedf79b4d3d`:
- finish/success receipt is written through `fence.fenced_commit`;
- post-cycle fence loss emits truthful `fence_lost_post_commit` failure evidence with `candidate_succeeded=false`;
- adversarial test forces takeover between cycle commit and finish receipt and expects no finish receipt;
- migration remains staged/side-effect free until fenced commit.

Do **not** rework this path unless independent QA finds a concrete defect. SB-V03-004 remains lead-CHANGES_REQUIRED only because its packet explicitly requires independent execution and Mac QA/worker-pc have not supplied it yet.

## Priority 1 — SB-V03-005 final all-surface raw-reader/admin boundary repair

Your `f73c337...` repair correctly removed ordinary `pipeline.publish_queue` and `analytics.events_for` names and replaced them with explicit admin surfaces. Preserve that work and the real production-path tests.

LEAD-026 found one concrete remaining packet violation:

- `RuntimeState.content_history()` is still an ordinary publicly named whole-runtime reader returning every persona's content history. Its docstring says ADMIN, but the packet requires a **structural** admin/internal boundary, not comments/convention.

The current bypass test is also too narrow: it asserts only that the old `publish_queue` and `events_for` names are absent. It therefore missed `RuntimeState.content_history()`.

Required narrow repair:
1. make `RuntimeState.content_history()` explicitly admin/internal, e.g. rename to `admin_content_history`, make private/internal, remove it and use `isolation.admin_all_records`, or equivalent enforceable design;
2. audit all six persona-private store surfaces: content history, publish queue, experiments, analytics/history, action history, decision history;
3. prove every normal persona-facing read/list goes through persona-scoped APIs;
4. prove every whole-runtime reader that remains is explicitly admin/internal/private and has a justified admin/reconciliation call site;
5. expand `test_production_read_paths.py` or equivalent structural test to cover the **complete** prohibited raw-reader surface, not a two-name regex/list;
6. include a regression that would fail if an ordinary `RuntimeState.content_history()`-style whole-runtime reader were reintroduced;
7. do not redesign storage or touch Intelligence semantics beyond agreed interfaces.

## Priority 2 — final SB-V03-006 regeneration

After the final V03-005 repair:
- regenerate V03-006 from the new final implementation SHA;
- keep all focused V0.3 suites;
- keep post-cycle finish-receipt takeover regression;
- keep production persona read-boundary regressions and add the all-surface structural guard;
- commit exact full-suite command/output/count as evidence, preserving the good `FULL_SUITE_OUTPUT.txt` pattern from `65c720b...`;
- refresh hashes/manifest/dry-run/recurring evidence;
- remain honest about single-POSIX-host/local-filesystem scope;
- request SUBMITTED/PREPARED; do not self-accept.

## Then — V0.3/V0.4 dependency reconciliation

After final evidence is pushed, stop changing V0.3 source and report for lead audit. Lead will reconcile V03-001/EVD-001 and acceptance.

After V0.3 acceptance, reconcile SB-V04-001/002/003/004 dependency readiness. Do not run the real canary from this lane; dedicated branch `claude/social-bots-v04-live-canary` owns `SB-V04-005`.

## Independent review

Mac QA is assigned independent execution/probing of current Core. `worker-pc` remains unusable for Social Bots because repository clone failed. Do not duplicate QA ownership or lower the independent-execution bar.

## Reporting

Reports stay under `social-bots/worker-reports/windows-core/`.
Commit/push after each parent artifact and continue to the next dependency-ready item.

## Safety

No public effects, paid API/new spend, destructive actions, secrets, fake evidence, or SwarmAI dependency.
