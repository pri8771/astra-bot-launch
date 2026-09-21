# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current operating mode: FAST TRACK.
Current lead review: LEAD-033.

Read:
- `FAST_TRACK_EXECUTION.md`
- `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `lead-reviews/LEAD-033_2026-09-21T0955.md`

Heartbeat is observability only. It does not block implementation or the real V0.4 canary.

## Today's heartbeat soak — applies to all four Claude lanes

Fresh sessions on Core, Intelligence, Mac QA and V0.4 Canary must run:

1. `FAST_5M`: T0, +5m, +10m, +15m — three consecutive real 5-minute intervals.
2. `SOAK_15M_24H`: immediately thereafter, every 15 minutes for 24 hours (target 96 intervals).

The soak runs in parallel with lane work. It never blocks source/review/canary execution. No backfill or synthetic timestamps. See `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`.


## Lane A — Windows Core
Branch: `claude/social-bots-windows-core-host`
Status: ACTIVE / V0.3 SOURCE STABLE / SB-V04-004 REPAIR / NO NEW WORKER COMMIT AFTER LEAD-032.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Verified final V0.3 source/evidence:
- `796d4e3...` — final V03-005 six-store persona/admin read-boundary repair;
- `436787b...` — V03-006 regenerated from `796d4e3...`; exact full-suite output is 130 tests, OK;
- `SB-V03-005` is lead-ACCEPTED.

Signed Core `76e96dd...` is useful but its SB-V04-004 worker attempt remains CHANGES_REQUIRED: two divergence cases fail independent-variable isolation, and the suite uses `contextual-deterministic-v1` (`adaptive=false`). Canonical packet `artifact-packets/SB-V04-004.md` defines the repair. ARTIFACT_INDEX is reconciled to that disposition in LEAD-033.

Next: fix persona-only/evidence-only isolation, preserve contextual tests as diagnostics, add an acceptance seam for the real adaptive canary receipt, and do not execute another live model call from Core. Preserve the adaptive-required production launcher and deterministic policy wall.

## Lane B — Intelligence
Branch: `claude/social-bots-intelligence-repair-v2`
Status: ACTIVE ASSIGNMENT / WORKER STALLED.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Seq5→6 is a valid ~16m37s interval; seq6→7 is ~30m28s, so hourly remains unauthorized. No backfill. No worker source/heartbeat appeared after seq7 at `04:10:36Z`.

Next:
1. `SB-V05-001` real pinned-IP HTTPS/SNI/certificate path + production-constructor regression now;
2. `SB-V15-001` persona-scoped production experiment read/write boundary;
3. preserve V16/V17/V20-002 for later audit.

## Lane C — Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`
Status: ACTIVE / HOURLY AUTHORIZED / WORKER STALE / V0.3 GATING EXECUTOR.
Instruction: branch-local `social-bots/SESSION_INSTRUCTIONS.md`.

Immediate assignment:
1. resume hourly coordination heartbeat;
2. independently execute current Core `796d4e3...` V03-004 lifecycle regressions: post-cycle takeover success-receipt rejection, active-cycle lease-loss old-owner commit rejection, staged migration fencing;
3. report exact commands/results and ACCEPT-READY or concrete defect; no Core source edits;
4. then continue CI/control, artifact validation and V2 acceptance/integration harness.

This independent execution is the remaining high-risk technical gate for V0.3 acceptance. No new worker report has landed after seq10 at `03:57:57Z`.

## Lane D — local real V0.4 canary
Branch: `claude/social-bots-v04-live-canary`
Status: PRIORITY ZERO / READY / NO WORKER EXECUTION VISIBLE.

Execute `SB-V04-005` now on an actual local Claude Code subscription-authenticated host. Heartbeat is not a prerequisite. Required: real public source, actual subscription CLI invocation, no fixture/injected runner/API PAYG, schema validation, deterministic policy, persisted decision, zero public effect. If auth is unavailable, submit a truthful BLOCKED report.

## Lane E — worker-pc
Control plane: `pri8771/remote-workers`
Worker: `worker-pc`
Capacity: 1.

Latest Social Bots task reached the real runner but failed repository clone before Claude/tests. It contributes zero evidence. Social Bots clone/auth access remains unresolved.

The previous unrelated SwarmAI task ended failed at branch push. At LEAD-033 review time, new unrelated work is consuming/queueing the capacity-1 worker: SwarmAI retry run `35608406904` is in progress and Jobs run `35608634037` is pending. Do not dispatch Social Bots into that slot. Once free, still require demonstrably repaired private-repo clone/auth access before another Social Bots dispatch; do not weaken controls.

## Lead
ChatGPT audits artifacts/evidence, owns canonical reconciliation and acceptance, and keeps dependency-safe work stocked.

## Version truth
Official version remains `V0.3.x`. `SB-V03-005` is accepted, but V0.3 still requires packet-required independent acceptance of `SB-V03-004` plus final reconciliation of V03-001/V03-006/SB-EVD-001. V0.4 additionally requires corrected adaptive divergence evidence, the real `SB-V04-005` canary and independent `SB-EVD-002`.

## Safety
No public posting/replies/messages, purchases, paid API/new spend, destructive actions, credentials/secrets, fake evidence, engagement manipulation or SwarmAI dependency.
