# Task directories and deterministic Jira projection

Proposed contract, not an installed compiler, claim service or Jira integration. Applies to [bot roadmaps](BOT_ROADMAPS.md) and future IDE packets. Windows is primary; Mac remains backup. Historical one-Mac SQLite locks do not prove cross-host exclusion.

## Portable task bundle

Under each canonical product repository, use `tasks/<mission>/<internal-id>/`. IDs are stable internal identities; store the real Jira key only after writer readback. Every bundle contains:

- `TASK.md`: goal, latest authority, source references, exact owned paths, prerequisites, runnable steps, acceptance, bounded repairs, review, stop/recovery and return instructions. This is the IDE entrypoint.
- `task.json`: schema/version, task/mission IDs, source repository/base, specification hash, dependency IDs, required capabilities, execution limits, output locations and proposed Jira mapping. Secrets are references only.
- `SPEC.md`: interface/design decisions and complete acceptance criteria; `EXPERIMENT.md` when applicable, using the current experiment template.
- `jira/`: immutable proposal files, validated projection, writer acknowledgements and native readback.
- `runs/<run-id>/`: append-only attempts, actual commands/results/usage, artifact hashes, proposed results and review receipts. Keep synthetic and real evidence distinct.
- `RETURN.md`: concise result, unresolved criteria, exact source tip and next eligible action. Unknown remains unknown.

Large Cursor batches consume a finite manifest of these bundles; smaller Antigravity assignments consume one bounded slice. Children require disjoint owned paths. Each host uses its own clone/worktree and preserves dirty source evidence. No shared mutable checkout or credentials in Git.

## File inbox compiler and sole writer

1. An author or qualified local/weak model proposes `inbox/<operation-id>.json` through temporary-file then atomic rename. Models draft content only; they cannot supply missing facts, grant authority or directly call Jira. Immutable revisions reference predecessors.
2. Deterministic validation checks schema, stable IDs, allowed fields, mission mapping, source/spec hashes, dependencies, path ownership, required planning content and secret exclusion. Reject incomplete records with actionable reasons; never guess values to satisfy a schema.
3. Verify/reuse designated Jira-writer task **`6046ab83-8402-47e3-b832-f4fe478da7f1`**. It alone reconciles native issue matches, types/field contexts and existing estimates before applying an allowed projection. Unavailable writer means queued proposals, not a replacement writer.
4. Persist operation ID, payload hash, previous native state, attempted mutation and readback. Ambiguous responses trigger reconciliation, not blind retry. Never duplicate comments/issues or infer success from an HTTP acknowledgement.
5. **Jira must be fully populated before task execution:** actual key, current scope/acceptance, accountability, applicable planning fields, original estimate, dates/dependencies and qualified capabilities. Preserve prior actuals; never derive worklogs from estimates. A matching native readback produces hash-bound admission. Specification changes invalidate admission until reconciled.

Documentation necessary to prepare Jira may proceed; implementation and experiments may not bypass that gate. Local inference receives bounded sanitized context, limited output/time and no write credentials. Unchanged inbox/evidence requires no model call. Existing limits remain; no paid fallback or expanded quotas by moving hosts.

## Atomic execution ownership

One authoritative transactional claim service must compare-and-set an admitted task from ready to claimed, recording owner, run ID, expiry, source/spec revision and monotonically increasing fencing token. Also reserve conflicting product paths/action scopes. All executors and effect adapters reject stale tokens. File copies and independent per-host lock files cannot provide this guarantee.

An expired heartbeat alone does not permit takeover: reconcile the prior process and uncertain destination effects, fence the old owner, then grant a new claim. Until this mechanism is qualified, use one verified execution owner and serialized admission; never represent parallel uncoordinated workers as safe failover.

## Completion

Require reproducible source/artifacts, relevant checks, actual review identity and acceptance evidence. Same-model self-review is not distinct-model approval. Record at most two targeted repairs unless the admitted contract is stricter. Failed/inconclusive experiments retain their valid evidence. The sole writer projects accepted outcomes and verifies readback; IDE “done” text alone cannot close Jira. Release, payment, publication and audience outcomes each need their own actual receiving-system evidence. No idle loops or backlog padding.
