# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-mac-qa-control`
Lead review: LEAD-026

## Heartbeat

Lead has accepted the durable Mac-QA bootstrap heartbeat evidence and authorized HOURLY cadence.
Routine heartbeat stays hourly. Artifact submissions and blockers push immediately.
Heartbeat is coordination observability only and must not pause useful QA/integration work.

Your last durable worker heartbeat remains seq10 at `2026-09-21T03:57:57Z`; no worker heartbeat/report has appeared since. Resume the authorized hourly heartbeat and continue QA work. Lead-only instruction commits do not count as worker liveness.

## Existing accepted controls
- `SB-CTL-012` artifact validator — ACCEPTED.
- `SB-CTL-006` GitHub CI/control — ACCEPTED.

Preserve these.

## Priority 1 — independently verify CURRENT Core V0.3 repair

Do not edit Core runtime source. Verify current Core behavior, not superseded defect states.

### SB-V03-004 — post-cycle success-receipt fence

Core `7e4345b041b59b9d1b1036dfea388cedf79b4d3d` writes the finish/success receipt through `fence.fenced_commit` and includes `test_stale_owner_cannot_write_success_finish_receipt_after_takeover`.

Independently execute/probe this scenario against current Core history:
1. cycle durable commit succeeds under owner A;
2. A stalls before completion receipt;
3. force lease expiry + generation takeover by B;
4. resume A;
5. prove A emits no finish/success receipt and cannot delete B's lease;
6. verify any A evidence is truthful fenced-out/failure evidence with `candidate_succeeded=false`.

Spot-check that side-effect-free migration and fenced cycle writes remain intact. Report PASS/FAIL with exact commands/results. Do not self-accept the artifact.

### SB-V03-005 — complete structural raw-reader/persona boundary

Core `f73c337e66ccdd5bd09313e37f4c87b4f00df07e` correctly renamed:
- `pipeline.publish_queue` -> `pipeline.admin_publish_queue`;
- `analytics.events_for` -> `analytics.admin_events_for`.

LEAD-026 independently found a remaining raw reader:
- `RuntimeState.content_history()` remains an ordinary publicly named whole-runtime reader, even though its docstring says ADMIN.

Also, the new static/bypass regression guards only the queue/analytics old names, so it is not exhaustive.

Independently inspect/probe the **complete** six-store surface:
- content history;
- publish queue;
- experiments;
- analytics/history;
- action history;
- decision history.

Determine whether every persona-facing sanctioned reader is persona-scoped and every raw whole-runtime reader is explicitly admin/internal/private. Confirm or disprove the `RuntimeState.content_history()` finding. Report exact symbols/call sites and distinguish legitimate runtime-wide admin/reconciliation reads from persona-facing reads.

If Core pushes a narrow LEAD-026 fix while you are working, fetch it and verify that current final SHA rather than reporting only the superseded f73c337 state.

## Priority 2 — V2 integration acceptance preparation

After the Core verification report, continue the non-runtime integration harness/checklist:
- merge-order checklist for Core + Intelligence;
- CI commands;
- full traceability assertions;
- persona isolation assertions;
- missing/stale/authority/no-public-effect scenarios;
- fixture-vs-operational distinction.

Do not edit Core/Intelligence runtime implementation.

## V0.4 canary

Dedicated local lane `claude/social-bots-v04-live-canary` owns `SB-V04-005`.
Do not switch this QA branch to the canary branch. Current canary branch still lacks a worker execution commit; QA must not fabricate it.

## Safety

No runtime feature implementation, public/account effects, paid API/new spend, secrets, fake evidence, or SwarmAI dependency.
