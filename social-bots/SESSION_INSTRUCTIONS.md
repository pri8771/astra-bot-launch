# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-mac-qa-control`
Lead review: LEAD-025

## Heartbeat

Lead has accepted the durable Mac-QA bootstrap heartbeat evidence and authorized HOURLY cadence.
Routine heartbeat stays hourly. Artifact submissions and blockers push immediately.
Heartbeat is coordination observability only and must not pause useful QA/integration work.

Your last durable worker heartbeat is seq10 at `2026-09-21T03:57:57Z`; no worker heartbeat/report has appeared since. Resume the authorized hourly heartbeat now and continue QA work. Lead-only instruction commits do not count as worker liveness.

## Existing accepted controls
- `SB-CTL-012` artifact validator — ACCEPTED.
- `SB-CTL-006` GitHub CI/control — ACCEPTED.

Preserve these.

## Priority 1 — independently verify CURRENT Core repair `7e4345b...`

Do not edit Core runtime source. The prior LEAD-024 defect state has changed; verify the repaired implementation, not the superseded code.

### SB-V03-004 — post-cycle success-receipt fence

Core `7e4345b041b59b9d1b1036dfea388cedf79b4d3d` now writes the finish/success receipt through `fence.fenced_commit` and includes `test_stale_owner_cannot_write_success_finish_receipt_after_takeover`.

Independently execute/probe this scenario:
1. cycle durable commit succeeds under owner A;
2. A stalls before completion receipt;
3. force lease expiry + generation takeover by B;
4. resume A;
5. prove A emits no finish/success receipt and cannot delete B's lease;
6. verify any A evidence is a truthful fenced-out/failure record with `candidate_succeeded=false`.

Also spot-check that the earlier side-effect-free migration and fenced cycle writes remain intact.

Report PASS/FAIL with exact commands and results. Do not self-accept the Core artifact.

### SB-V03-005 — structural raw-reader/persona boundary

Lead source review still finds a contract gap after `7e4345b...`:
- scoped facade and real production-path tests are useful;
- `_reconcile` correctly uses `isolation.admin_all_records`;
- but ordinary raw whole-runtime APIs still exist, including `pipeline.publish_queue(bot)`, `analytics.events_for(bot)`, `RuntimeState.content_history()` and analogous direct store readers.

Independently determine whether a normal persona-facing production caller can still bypass the persona boundary and enumerate another persona's private records. The packet requires raw enumeration to be structurally admin/internal or equivalent, not merely documented by comments.

Test/trace actual production-facing APIs and report exact symbols/call sites. Distinguish legitimate runtime-wide admin/reconciliation reads from persona-facing reads.

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
