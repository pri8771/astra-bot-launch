# Heartbeat and assignment protocol

Lead-owned control contract.

## Owner policy — one session, one heartbeat

Effective 2026-09-21, the previous timed FAST_5M / SOAK_15M_24H experiment is superseded.

**Each fresh worker session emits exactly one heartbeat. That is all.**

There is:
- no five-minute heartbeat loop;
- no fifteen-minute soak;
- no 24-hour heartbeat requirement;
- no requirement to keep a chat session alive for liveness;
- no background heartbeat daemon requirement.

A restarted/resumed worker process that constitutes a new fresh execution session emits one new heartbeat for that new session.

## Purpose

The session heartbeat answers only:

> Did this worker session actually start, read current coordination, and begin the assigned work?

It is coordination/liveness evidence, not artifact correctness and not version acceptance.

Git commits, tests, receipts and lead review remain stronger evidence.

## Required timing

Emit the one heartbeat after:
1. syncing/fetching repository state;
2. reading current canonical lead instructions;
3. identifying the session's branch/lane and current artifact;

and before or alongside substantive implementation.

Do not delay useful engineering to wait for a clock interval.

## Durable evidence

Per lane:

Latest session heartbeat:
`social-bots/worker-reports/<lane>/HEARTBEAT.json`

Append-only session history:
`social-bots/worker-reports/<lane>/HEARTBEAT_LOG.jsonl`

Human-readable progress:
`social-bots/worker-reports/<lane>/CURRENT_PROGRESS.md`

Lead acknowledgement:
`social-bots/worker-reports/<lane>/LEAD_ACK.json`

Lead-owned assignment:
`social-bots/SESSION_INSTRUCTIONS.md`

Each fresh session appends exactly one real heartbeat record to `HEARTBEAT_LOG.jsonl` and updates `HEARTBEAT.json`.

Never backfill or invent a heartbeat.

## Minimum heartbeat fields

The durable record should include:
- `schema_version`;
- `session_id`;
- `lane`;
- `branch`;
- `started_at` using a real timestamp;
- `session_status` = `STARTED`;
- `current_artifact` or assignment;
- `canonical_seen_sha`;
- `lead_review_seen`;
- non-secret host/runtime identifier if available;
- concise notes/blocker.

Legacy cadence fields may remain for backward compatibility, but new sessions should use `cadence_mode: "SESSION_ONCE"`.

## GitHub Issue #3 visibility

Private Issue #3 remains an optional human-readable progress feed.

For the one session heartbeat:
- post one concise Issue #3 comment if authenticated GitHub transport is available;
- if `gh` is missing or unauthenticated, do not block work;
- durable local/repository heartbeat logging must still occur;
- do not fabricate an Issue comment.

Normal commits, reports and blocker submissions may still appear later in the session. They are not additional heartbeats.

## V0.7 recurring-liveness interpretation

V0.7 does **not** require repeated heartbeats inside one long-running chat/session.

V0.7 recurring liveness is proven by repeated real OS-scheduled worker invocations over time.

Each invocation is a bounded worker session and therefore emits exactly one session heartbeat plus its normal invocation receipt.

Example:

scheduler invocation A -> one heartbeat -> one bounded task -> receipt -> exit  
scheduler invocation B -> one heartbeat -> one bounded task -> receipt -> exit  
scheduler invocation C -> one heartbeat -> one bounded task -> receipt -> exit

The sequence of independently scheduled sessions proves recurring liveness.

## Truth rules

- One session = one heartbeat.
- No periodic heartbeat requirement exists.
- No synthetic/backfilled heartbeat is valid.
- A heartbeat does not prove code correctness.
- Issue comments are visibility, not stronger evidence than durable records.
- V0.7 requires real recurring OS-level invocations, not a chat kept awake.
