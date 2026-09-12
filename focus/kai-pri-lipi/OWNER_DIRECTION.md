# Owner direction — a simple reusable contract

Proposed 12 September 2026 for Kai, Pri 2.0, Lipi and every business bot. No active worker or service consumes this contract yet. The first implementation must prove that behavior before claiming a nudge reached a running bot.

The owner can speak naturally in the current chat: “focus Lipi on getting its first customers,” “evaluate Indian clothing suppliers,” “make Pri's answers shorter,” or “pause OPO's current experiment.” The coordinating assistant records the instruction in the affected project's `DIRECTION.md` and explains the resulting next action. Later, Slack or another input adapter writes the same record; it does not require a different operating system for each bot.

## Files and roles

- Reuse the existing mission/charter/business-rules file for enduring goals, permissions and budgets. Do not duplicate all of it into each task.
- Use one small `DIRECTION.md` per mission for current owner direction: stable ID, issued time, source/owner, exact intent, scope, optional expiry, superseded direction and state. The first records in `directions/` are planning records based on this conversation, not executed commands.
- Reuse the existing task/state/decision log for the bot's acknowledgement and effect: direction ID, interpretation, affected experiment/task, next action, evidence and any actual blocker. Store concise business rationale, not internal reasoning transcripts. Preserve prior revisions in Git or the existing event log.
- Private Pri/Kai preferences and personal content belong in access-controlled runtime storage, not this shared cloud planning repository. Only non-sensitive operational direction appears here.

## Behavior

1. Validate the issuer and target mission. Read relevant current direction at job start and before an external action, using a content hash/version; do not reread the entire repository or all chats.
2. Interpret ordinary strategy/tone/prioritization nudges within the current mission. Latest explicit owner corrections supersede earlier conflicting preferences. A vague nudge does not silently widen data access, spending or account permissions. Reuse existing grants rather than asking again.
3. Record **seen**, then **applied**, **waiting for current action to reconcile**, **needs input**, **superseded** or **expired** with a short reason. A saved file alone is only **recorded, not consumed**. No fake acknowledgement from a worker.
4. Reorder unstarted work or amend the next experiment. If the change affects an active experiment, preserve its original hypothesis and mark interruption/amendment; do not rewrite its past result to fit the new goal.
5. A pause prevents new affected side effects at the next safe boundary. An already submitted order/post/payment must be checked at its destination; it cannot be assumed canceled or blindly replayed. Do not roll back irreversible actions automatically.
6. Ask once for a genuinely missing item, naming why it matters and the affected job. Persist the question; continue unrelated work. Silence is not an answer, and the same unresolved request must not be re-sent by every clock tick.
7. Record actual action/result and link its existing Jira task/experiment through the designated writer. Distinguish the owner's instruction, the model's proposed interpretation, the accepted plan and an executed effect.

## First implementation check

Use a local fixture and one non-publishing job: record a direction, show the next job consumes it once, show a superseding instruction takes precedence, and show a pause prevents a pending effect without erasing receipts. Restart and duplicate delivery must preserve the outcome. Then qualify one real route. Do not start recurring jobs or invoke paid models merely to test that a file changed.

Small local models can summarize a changed instruction; deterministic checks enforce identity, version, permissions, budgets, deduplication and stop state. Invoke a stronger model only for an identified ambiguity that local handling cannot resolve and that fits the existing model budget. Future Slack adapters preserve the same identity and acknowledgement rules.
