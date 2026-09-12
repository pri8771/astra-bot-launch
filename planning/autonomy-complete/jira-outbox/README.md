# Jira proposal outbox — no writes performed

Each *-v1.jsonl record is a reviewable proposal with stable operation ID, complete task payload and SHA256. Bindings are null pending designated writer admission. Candidates are search/matching pointers. Root's dated read-only snapshots confirm named records exist; a summary/status is not proof a new task's entire scope is covered.

The rightful writer compares exact scope against current descriptions, source receipts and links; returns reuse, extend, split-delta, or genuinely missing scope; preserves original estimates, actuals/worklogs, accepted artifacts and native history; records account/field context and source/spec hashes. Only after that may it project an allowed change and verify current native readback. Unknown/null keys must never clear fields. Do not invent Jira keys, migrate old estimates into new estimates or turn observation windows into worklogs.

OPO proposals route to the dedicated owner-started OPO Cursor Windows writer. WHB/CommerceLint/BidetFit/Guru proposals route to the Windows release parent. Lipi/shared scope requires explicit designation by the current coordinator/owner; old Mac writer availability is not a prerequisite. This package neither starts a writer nor sends proposals by message. It publishes sanitized files through the authorized private Git route for consumption.

Before replay, verify operation ID and payload hash against the writer ledger. If an earlier mutation has an uncertain response, reconcile native state before retrying; no duplicate issues/comments. Changed scope becomes a new immutable revision referencing its predecessor after writer reconciliation. Freeze these v1 proposals at publication; the generator is for pre-publication assembly, not overwriting submitted revisions.
