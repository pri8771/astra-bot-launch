# Work queue — LEAD-039 lane-start review

Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

Primary worker contract: `CLAUDE_EXECUTION_TO_V07.md`.
Forward planning: `FORWARD_PLAN_V06_TO_V30.md`.

## Heartbeat

Owner policy is **ONE SESSION = ONE HEARTBEAT**. The old FAST_5M / 24-hour soak is superseded.

Every fresh worker session syncs/reads canonical coordination, appends exactly one real `SESSION_ONCE` heartbeat, then works normally. V0.7 recurring liveness must come from repeated OS-scheduled bounded sessions, each with one heartbeat and an invocation receipt.

## Current lane state

- **Core — ACTIVE:** Issue #3 shows fresh session `s-20260921T174817Z-0e532933` starting at 17:48:17Z. No new worker source/report commit from that session was visible on the authoritative Core branch during LEAD-039, so no artifact acceptance is inferred yet.
- **Intelligence — STALE:** no fresh post-LEAD-038 session or repair submission. Start fresh, emit one heartbeat, finish only the narrow SB-V15-001 alias/admin-boundary repair, test, submit, stop.
- **Acceptance — STALE:** no fresh post-LEAD-038 session or QA submission. Start fresh, emit one heartbeat, independently review new submissions and continue V0.7 acceptance/fault preparation.
- **Canary — FROZEN:** evidence preservation only. No further live/model call or new canary source retrieval.
- **worker-pc:** outside the critical path until private-repo clone/auth is demonstrably fixed.

## V0.4 critical path

- SB-V04-001 ACCEPTED.
- SB-V04-003 ACCEPTED.
- SB-V04-005 ACCEPTED from the first authorized real canary.
- SB-V04-002 BLOCKED_OWNER_AUTHORIZATION.
- SB-V04-004 BLOCKED_OWNER_AUTHORIZATION.
- SB-EVD-002 WITHHELD.

No additional model call is currently authorized.

Core may complete the prepare-only five-context matrix/hash/isolation/authorization/call-budget harness with fixtures/replay labeled engineering-only, then proceed to dependency-ready SB-V07-001. Synthetic/replayed receipts do not satisfy causal adaptive divergence acceptance.

## Intelligence path

- SB-V05-001 ACCEPTED.
- SB-V05-002 CHANGES_REQUIRED.
- SB-V15-001 CHANGES_REQUIRED: normal persona-facing APIs are structurally scoped, but ordinary whole-runtime `load` / `load_all` aliases remain and must be removed/private/renamed; explicit admin/internal readers may remain.
- V16/V17/V20-002 stay pending lead/independent audit after V15 closure.

## V0.6 / V0.7

Operational V0.6 dry runs remain dependency-gated, but validators/scaffolding may be prepared without fake operational evidence.

SB-V07-001 is dependency-ready for no-live-call host-worker/runbook/OS-scheduler/session-heartbeat/invocation-receipt/crash/no-overlap engineering.

## Safety

No public social effects, paid API/PAYG/new spend, secrets, destructive actions, fabricated operational evidence, engagement manipulation or SwarmAI dependency.
