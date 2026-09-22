# Agent operating contract

Applies to ChatGPT, Claude/Fable, Cursor and Codex working in this repository.

## Authority

1. Explicit current owner instructions control scope and permissions; do not infer new permissions from a version target.
2. ChatGPT is engineering/product lead and owns artifact acceptance and version promotion unless the owner explicitly changes that role.
3. Implementation workers produce code, tests and truthful evidence and request SUBMITTED; no self-acceptance.
4. Fresh canonical Git evidence outranks historical chats, memories, snapshots and stale branch notes for project status.

## Start

For Social Bots only: read `social-bots/coordination/SESSION_START.md`, then `social-bots/delivery/V17_LIVE.md` and the active artifact card.

When the owner explicitly asks Codex to coordinate Bots, Jobs and Swarm together: read **`coordination/codex/START.md`**. That directory contains the consolidated handoff, source-pinned project routes, owner decisions and per-project heartbeat rules. Do not automatically start the other projects for an ordinary Social Bots task.

The current Social Bots target is **LIVE V1.7, then stop development**. Older V2.3/V3 instructions and the historical worker branch name do not widen that scope. Preserve later code; do not finish it merely to clear the queue.

## Work model

- Work small, reviewable artifacts with explicit dependencies and completion tests; reuse existing implementation.
- One artifact per commit when practical. Refresh current direction before selecting the next dependency-safe task.
- Check current ownership before changing source. A coordinator must not become a second simultaneous implementation owner.
- When an external gate blocks one task, continue other released in-scope work. Do not cross a version cap or grant yourself authority.
- Engineering, production integration and real operational acceptance are different facts. No fabricated evidence, provenance, liveness or test results.

## Heartbeat

**Social Bots:** one durable SESSION_ONCE after reading current coordination per genuinely fresh worker session. No periodic in-session heartbeat loop and no duplicate on resume. Lease renewals and invocation completion receipts are separate.

This rule does not override Jobs or SwarmAI. Their observed contracts each require one owned local five-minute worker heartbeat producer. Codex must follow each repository's current rule without adding duplicate watchers or treating a timer as model activity. See `coordination/codex/HEARTBEATS_AND_HANDOFFS.md`.

## Safety and efficiency

No credentials in Git; no implicit paid/API fallback; no unauthorized model batch, public effect, employer submission, mailbox access, destructive operation or main/public release. Account setup permission is not permission for another action. No engagement manipulation or CAPTCHA/MFA bypass. Social Bots remains independent of SwarmAI.

Read the active card and relevant diffs, not every roadmap. Available memory explains intent, not execution evidence or candidate facts. Use lower-cost already-authorized subagents only for bounded nonconflicting work; never invent model availability, delegation, independent review or background execution.
