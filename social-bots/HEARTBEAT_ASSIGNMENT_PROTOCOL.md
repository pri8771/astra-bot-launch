# Heartbeat and assignment protocol

Lead-owned control contract.

## Goal

Keep Claude workers observable and continuously assignable through GitHub without owner relay.

## Temporary soak policy — 2026-09-21

For today's fresh-session validation, every active Claude lane uses a two-stage heartbeat soak.

### Stage 1 — FAST_5M bootstrap

Each fresh worker session must produce **3 consecutive real five-minute intervals**.

For avoidance of ambiguity, this means four timestamped heartbeat records:

- T0
- approximately T0 + 5 minutes
- approximately T0 + 10 minutes
- approximately T0 + 15 minutes

Those four records create three consecutive elapsed intervals.

Acceptance:
- each interval should be approximately 5 minutes, with reasonable execution/Git jitter;
- timestamps must be real, never fabricated/backfilled;
- every record must be durably appended to `HEARTBEAT_LOG.jsonl` and pushed;
- burst artifact/status updates do not substitute for elapsed-time heartbeat intervals.

After the third successful five-minute interval, the worker immediately enters Stage 2. It does NOT need to wait for ChatGPT acknowledgement to begin the 24-hour soak.

### Stage 2 — SOAK_15M_24H

After Stage 1 succeeds, heartbeat is due every **15 minutes for the next 24 hours**.

Target:
- 96 consecutive 15-minute intervals after the Stage-1 completion timestamp;
- a final soak-complete record after the 24-hour window.

Rules:
- heartbeat runs in parallel with useful project work;
- do not stop coding/review work merely to wait for heartbeat;
- artifact submissions and blockers still push immediately;
- a material state-transition heartbeat does not reset the 15-minute soak clock;
- missed intervals are reported truthfully and are not backfilled;
- if the loop/process dies, restart prospectively and record the interruption.

ChatGPT's automated lead review remains hourly because the platform does not support faster scheduled reviews. Manual checks may inspect GitHub at any time.

## Files per lane

Worker heartbeat:
`social-bots/worker-reports/<lane>/HEARTBEAT.json`

Heartbeat history:
`social-bots/worker-reports/<lane>/HEARTBEAT_LOG.jsonl`

Lead acknowledgement:
`social-bots/worker-reports/<lane>/LEAD_ACK.json`

Lead-owned assignment:
`social-bots/SESSION_INSTRUCTIONS.md`

## HEARTBEAT.json fields

Existing fields remain authoritative. For today's soak, use these cadence values:
- `FAST_5M`
- `SOAK_15M_24H`
- `SOAK_COMPLETE`

In `notes`, include:
- soak start time;
- Stage-1 progress or Stage-2 interval count;
- latest real interval duration;
- any interruption.

## Worker update triggers

Every timed heartbeat appends the full heartbeat record to `HEARTBEAT_LOG.jsonl` and pushes it.

Also push immediately:
- on session start/resume;
- before/after a parent artifact checkpoint where useful;
- on blocker;
- after detecting new lead instructions;
- before stop.

Immediate material updates do not count as timed soak intervals unless the elapsed clock also satisfies the due interval.

## Work-concurrency rule

Heartbeat must not serialize engineering work.

Preferred implementation:
- run a separate lightweight heartbeat loop/process from the same repository checkout;
- stage/commit only heartbeat files;
- never stage unrelated source changes;
- do not perform destructive reset/clean/stash operations;
- if concurrent source work makes a Git operation unsafe, record the heartbeat locally and push it at the next safe moment with the original real timestamp; do not invent a timestamp.

## Lead behavior

At lead review:
1. inspect worker branches and heartbeat histories;
2. independently calculate elapsed intervals;
3. audit new source/tests/reports;
4. update canonical state and lane acknowledgements;
5. flag stale/missed soak intervals;
6. keep dependency-ready work assigned.

## Truth rules

- Heartbeat proves coordination/liveness only, not artifact correctness.
- Git commits/receipts/source review remain stronger evidence.
- Today's 5-minute + 24-hour soak does not by itself prove V0.7 recurring Social Bots runtime liveness.
- No synthetic/backfilled heartbeat may be presented as successful cadence.

## Platform limitation

ChatGPT scheduled automations support hourly cadence at fastest. Workers may heartbeat faster because their own local process/scheduler supplies the clock.
