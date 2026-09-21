# SESSION_INSTRUCTIONS — Windows Core / V0.3 closure

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-windows-core-host`
Lead review: LEAD-025

Heartbeat is observability only. Do not wait on heartbeat acceptance before coding.

At start/checkpoint:
1. `git pull --ff-only`
2. `git fetch origin`
3. read canonical `FAST_TRACK_EXECUTION.md` and `SESSION_ROUTER.md` with `git show`
4. inspect `worker-reports/windows-core/LEAD_ACK.json`
5. continue dependency-ready work without routine permission prompts.

## Preserve — SB-V03-004 LEAD-024 repair

Lead source review of `7e4345b041b59b9d1b1036dfea388cedf79b4d3d` confirms the intended post-cycle repair is present:
- finish/success receipt is written through `fence.fenced_commit`;
- post-cycle fence loss emits truthful `fence_lost_post_commit` failure evidence with `candidate_succeeded=false`;
- the adversarial test forces takeover between cycle commit and finish receipt and expects no finish receipt.

Do **not** rework this path unless independent QA finds a concrete defect. SB-V03-004 remains lead-CHANGES_REQUIRED only because independent execution of the repaired branch has not yet succeeded.

## Priority 1 — SB-V03-005 final structural raw-reader/admin boundary repair

The new production-path tests and `_reconcile -> isolation.admin_all_records` change are useful. Keep them.

LEAD-025 still finds a packet-level structural gap: ordinary whole-runtime APIs remain directly callable with normal names, including examples such as:
- `pipeline.publish_queue(bot)`;
- `analytics.events_for(bot)`;
- `RuntimeState.content_history()`;
- direct experiment/index/action/decision store enumeration where applicable.

The packet explicitly requires raw whole-runtime access to be structurally admin/internal (or equivalent), not merely documented by comments/convention.

Required narrow repair:
1. keep logical persona isolation and the authoritative persona-scoped facade;
2. make remaining raw whole-runtime enumeration explicitly admin/internal at the API boundary (private/admin naming, wrapper/module separation, or equivalent enforceable design);
3. route normal persona-facing reads through scoped readers;
4. preserve deliberate runtime-wide reconciliation/admin reads and make those call sites explicit;
5. audit content history/dedup, publish queue, experiments list/load, analytics/history, action history and decision history;
6. add a regression proving a normal persona-facing code path cannot use the raw whole-runtime reader as the sanctioned interface to enumerate another persona's records;
7. do not edit Intelligence-owned semantics beyond agreed cross-lane interfaces.

## Priority 2 — final SB-V03-006 regeneration

After the V03-005 structural repair:
- regenerate V03-006 from the final implementation SHA;
- include all focused V0.3 suites;
- include the post-cycle finish-receipt takeover regression;
- include the production persona read-boundary regressions;
- include the exact full-suite command, output and test count as committed evidence (not only `full: OK` in a summary);
- update hashes/manifest;
- remain honest about single-POSIX-host/local-filesystem scope;
- request SUBMITTED/PREPARED; do not self-accept.

The current `b2083b8...` bundle is useful PREPARED evidence but not final because V03-005 still changes.

## Then — V0.4 Core dependency reconciliation

After final V0.3 repair evidence is pushed:
- reconcile SB-V04-001/002/003/004 dependency readiness;
- preserve deterministic authority/policy ownership;
- do not run the real canary from this lane.
Dedicated branch `claude/social-bots-v04-live-canary` owns `SB-V04-005`.

## Independent review

Mac QA is assigned independent execution/probing of `7e4345b...` and the remaining raw-reader boundary. `worker-pc` is currently unusable for Social Bots because repository clone failed. Do not duplicate QA ownership.

## Reporting

Reports stay under `social-bots/worker-reports/windows-core/`.
Commit/push after each parent artifact and continue to the next dependency-ready item.

## Safety

No public effects, paid API/new spend, destructive actions, secrets, fake evidence, or SwarmAI dependency.
