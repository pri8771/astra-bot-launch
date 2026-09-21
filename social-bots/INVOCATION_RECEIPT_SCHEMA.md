# Scheduled invocation receipt schema

Used by V0.7+ to prove worker liveness independently of chat presence.

## Required

- schema_version
- invocation_id
- host_alias
- scheduler
- scheduler_job_id
- session_id
- heartbeat_ref
- started_at
- finished_at
- source_ref_seen
- assignment_ref_seen
- claimed_artifact
- lease_id
- claim_result
- command/entrypoint version
- exit_status
- produced_commit
- evidence_refs[]
- next_safe_action
- error_class / safe_error when failed

## Rules

- Exactly one SESSION_ONCE heartbeat per fresh worker session.
- Scheduler configuration alone is not proof; receipts must come from actual invocations.
- A second overlapping invocation must either fail the claim or take another eligible task.
- Crash/restart tests preserve the prior receipt as incomplete/failed; never rewrite it to success.
- Receipt contains no credentials or private environment dump.
