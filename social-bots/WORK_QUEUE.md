# Work queue — LEAD-036

Canonical plan: `RESET_EXECUTION_20260921.md`.
Lead review: `LEAD-036` at 2026-09-21T17:10:00Z.
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed. V0.4 is not complete.

## Current lane truth

### CORE — `claude/social-bots-windows-core-host`
Status: **ACTIVE / SUBMITTED**.

Verified:
- corrected deterministic SB-V04-004 persona-only/evidence-only comparisons are present at `a19046d` / `74a357d`;
- production adaptive-required/fail-closed launch contract is accepted as SB-V04-001;
- deterministic policy boundary is accepted as SB-V04-003.

Next:
1. **Do not execute another Claude CLI/adaptive model call.** Owner's one-call authorization is consumed.
2. Preserve final V03 source/evidence.
3. Continue only non-live SB-V04-004 seam/test/integration work.
4. Do not claim synthetic/replayed receipts prove causal adaptive divergence.
5. Keep the unresolved real-adaptive divergence requirement explicit for lead/owner decision.

### INTELLIGENCE — `claude/social-bots-intelligence-repair-v2`
Status: **ACTIVE / SUBMITTED**.

Verified:
- **SB-V05-001 ACCEPTED** at `a462bd6` for actual pinned-IP HTTPS + original-host SNI/certificate/Host behavior and production-path regression.
- SB-V15-001 at `2052955` materially improves physical persona partitioning and persona-facing APIs.

Next:
1. Repair **SB-V15-001** only: remove/private/rename ambiguous whole-runtime `load(bot,id)` and `load_all(bot)` aliases; explicit `admin_*` readers may remain.
2. Add a regression proving normal production experiment APIs cannot enumerate another persona's experiments.
3. Run focused/full tests, commit/push report, then stop for lead audit before V16/V17/V20-002 expansion.

### ACCEPTANCE — `claude/social-bots-mac-qa-control`
Status: **ACTIVE / SUBMITTED**.

Verified:
- **SB-V03-004 ACCEPTED** from `72e380b`: 37/37 independent invariant checks, focused 36 tests, full 130-test suite.
- V0.3 manifest reconciliation is complete: SB-V03-001, SB-V03-006 and SB-EVD-001 are accepted.
- V03 acceptance guarantee is single POSIX host/filesystem only; actual execution was Linux CCR, not the reset-plan physical Mac.

Next:
1. **No more model calls.** Canary authorization is consumed.
2. Continue non-overlapping QA/CI/V2 acceptance-harness work; no Core/Intelligence runtime source edits.
3. Repair heartbeat durability prospectively: commit real reset-epoch `HEARTBEAT_LOG.jsonl` records; no backfill.

### LIVE CANARY — `claude/social-bots-v04-live-canary`
Status: **FROZEN — EVIDENCE PRESERVATION ONLY**.

- **SB-V04-005 ACCEPTED** from the first chronological real canary at ~16:15Z on `claude/social-bots-mac-qa-lane3-ordpt6`.
- A second real canary at ~16:53Z on this dedicated branch occurred after the exactly-one owner authorization was already consumed. It is preserved as a process/authorization incident and excluded from acceptance evidence.
- **No further Claude CLI/adaptive model calls are authorized.**

## Milestone critical path

1. V0.3 — **CLOSED / ACCEPTED**.
2. SB-V04-002 — CHANGES_REQUIRED: real adaptive persona/evidence causal-divergence evidence still missing.
3. SB-V04-004 — CHANGES_REQUIRED: deterministic experimental design is repaired, but real adaptive divergence remains missing.
4. SB-EVD-002 — WITHHELD until SB-V04-002 and SB-V04-004 are accepted.
5. Only then may V0.4 be marked complete.
6. In parallel, Intelligence closes SB-V15-001 and then lead audits V16/V17/V20-002.

## Heartbeat truth

Issue #3 has active worker heartbeat/progress comments, but the reset soak is judged from durable `HEARTBEAT_LOG.jsonl` records. Current durable logs contain no reset-epoch FAST_5M records for Core, Intelligence or Mac QA.

**Verified reset soak: 0 FAST_5M intervals on all three human lanes.**

Do not backfill. Heartbeat remains observability only and never blocks useful source/QA work.

## Remote worker-pc

Outside the critical path. Do not redispatch Social Bots until `pri8771/astra-bot-launch` private-repo clone/auth is demonstrably fixed.

## Safety / authority

No public social effects, paid API/PAYG/new spend, destructive actions, credentials/secrets, fabricated evidence, engagement manipulation or SwarmAI dependency.
