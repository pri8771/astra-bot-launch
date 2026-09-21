# Heartbeat and assignment protocol

Lead-owned control contract.

## Goal

Keep Claude workers observable and continuously assignable through GitHub without owner relay.

## Cadence

### Bootstrap phase
Each worker heartbeat is due every **15 minutes** while its lane is active.

Bootstrap continues until:
- at least 3 consecutive heartbeat sequences were pushed approximately 15 minutes apart;
- ChatGPT lead has reviewed/acknowledged those sequences in the lane's `LEAD_ACK.json`.

Because ChatGPT scheduled automations cannot execute more frequently than hourly, the lead may acknowledge several 15-minute worker heartbeats together on its next hourly review. The worker remains on 15-minute cadence until that acknowledgement is visible.

### Steady phase
After lead acknowledges at least 3 consecutive bootstrap heartbeats, the worker switches to **hourly** heartbeat checks.

Artifact submissions and blockers still push immediately; do not wait for the next heartbeat.

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

- schema_version
- lane
- branch
- sequence
- cadence_mode: BOOTSTRAP_15M | HOURLY
- session_status
- current_artifact
- started_at
- last_updated_at
- next_due_at
- last_commit_sha
- canonical_seen_sha
- instructions_seen_sha
- lead_message_seen
- next_artifact
- blocker
- notification_pending
- notification_reason
- notes

## LEAD_ACK.json fields

- schema_version
- lane
- reviewed_through_sequence
- reviewed_at
- lead_review
- bootstrap_consecutive_verified
- steady_hourly_authorized
- next_assignment
- notification_delivered
- notes

## Worker update triggers

Every heartbeat update also appends the full heartbeat record to `HEARTBEAT_LOG.jsonl`, so cadence can be verified without relying on the current snapshot alone.

Push heartbeat immediately:
- on session start/resume;
- every due heartbeat interval while active;
- before new parent artifact;
- after artifact submission;
- on blocker;
- after detecting new lead instructions;
- before idle/stop.

Artifact submission/blocker heartbeats set:
- notification_pending=true
- notification_reason to a short factual reason.

## Lead behavior

At every lead review:
1. inspect worker branches and heartbeat histories/commits;
2. audit new source/tests/reports;
3. update canonical artifact state;
4. update each lane's LEAD_ACK.json;
5. update SESSION_INSTRUCTIONS.md with next work;
6. when meaningful new activity exists, use the available parent-notification mechanism to notify the owner thread;
7. keep dependency-ready work assigned so a worker does not idle unnecessarily.

## Truth rules

- Scheduler/heartbeat claims do not prove artifact correctness.
- Git commits/receipts/source review remain stronger evidence.
- Three bootstrap heartbeats prove GitHub coordination liveness only, not V0.7 Social Bots runtime liveness.
- V0.7 requires the separate recurring runtime artifacts.

## Platform limitation

ChatGPT scheduled automations support hourly cadence at fastest. Therefore:
- worker check-ins may be every 15 minutes;
- lead automated review is hourly;
- event-driven immediate GitHub-to-ChatGPT webhook notification is not currently exposed in this environment.
- artifact submissions remain visible immediately in GitHub and are reviewed on the next lead run or any manual lead review.
