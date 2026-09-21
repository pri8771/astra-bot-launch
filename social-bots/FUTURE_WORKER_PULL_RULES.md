# Future worker pull rules

This file lets future worker sessions continue useful work without owner prompt-copying.

## Algorithm

1. Fetch canonical coordination branch.
2. Read STATE, ARTIFACT_INDEX, MILESTONE_MANIFEST, WORK_QUEUE, SESSION_ROUTER and latest lead review.
3. Emit one SESSION_ONCE heartbeat for the fresh session.
4. Identify artifacts where:
   - owner/lane matches;
   - status is READY / IN_PROGRESS / CHANGES_REQUIRED, or PLANNED with all dependencies accepted and canonical instructions permit prep;
   - no missing owner-only authority gate exists.
5. Prefer the lowest-version artifact on the critical path.
6. If blocked by owner/account/public/model authority, take the earliest dependency-safe engineering or acceptance-prep artifact instead.
7. Work one bounded artifact/checkpoint; run tests; commit/push evidence.
8. Request SUBMITTED and exit. Never self-accept.
9. A later OS-scheduled fresh session repeats from step 1.

## Conflict rule

Never edit another active lane's owned runtime paths unless current canonical coordination explicitly reassigns them. Lead-owned coordination/schema/packet work should not be overwritten by workers.

## Evidence rule

Fixtures are welcome for engineering tests when labeled. They never become operational proof by renaming them.
