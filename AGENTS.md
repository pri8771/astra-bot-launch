# Agent operating contract

Applies to ChatGPT, Claude/Fable, Cursor and future workers in this repository.

## Authority

1. Owner controls identity, account, public-action, destructive-action and spending gates.
2. ChatGPT is engineering/product lead and owns artifact acceptance and version promotion.
3. Workers implement, test, produce evidence and request `SUBMITTED`.
4. GitHub canonical coordination outranks past chats, memories and stale branch notes.

## Work model

- Work artifacts, not vague milestones.
- Prefer small reviewable artifacts with explicit dependencies and definitions of done.
- One artifact per commit when practical.
- After finishing an artifact, refresh canonical coordination and pull the next dependency-safe, non-conflicting assignment.
- If a live/owner gate blocks one artifact, continue other dependency-safe engineering instead of idling.

## Evidence

Classify evidence as:
- `ENGINEERING`: tests, fixtures, mocks, replay, direct CLI demonstrations.
- `LIVE`: genuine external/provider/account/scheduler/public/analytics/host evidence required by the artifact.

Never upgrade ENGINEERING evidence to LIVE by wording.

## Worker isolation

Before changing source:
- check SESSION_START / current assignment;
- inspect active worker branches;
- do not edit another active worker's owned artifact unless reassigned.

## Heartbeat

One fresh session emits exactly one durable `SESSION_ONCE` heartbeat after reading current coordination. No periodic in-session heartbeat loop.

## Safety

No fabricated evidence; no credentials in Git; no implicit PAYG fallback; no unauthorized public effects; no engagement manipulation; no SwarmAI runtime dependency.
