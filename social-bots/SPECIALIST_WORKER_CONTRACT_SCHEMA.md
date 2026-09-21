# Temporary specialist worker contract schema

Reusable contract for V2.3+ temporary workers. These are Social Bots components, not SwarmAI.

## WorkerContract

- worker_id
- parent_run_id
- role: researcher | analyst | writer | reviewer | media | qa
- objective
- bounded_context_refs[]
- allowed_tools[]
- denied_tools[]
- authority_scope[]
- input_artifacts[]
- expected_output_schema
- time_budget
- model_call_budget
- external_effect_budget (normally zero)
- scratch_scope
- stop_conditions[]
- created_at
- expires_at

## WorkerResult

- worker_id
- started_at/finished_at
- source_ref
- outputs[]
- evidence_refs[]
- calls_used
- effect_attempts
- result
- limitations[]
- cleanup_status

## Rules

- Least authority.
- No implicit inheritance of parent credentials/effect authority.
- Parent validates/integrates or rejects result.
- Scratch state is isolated and retired after completion except attributable evidence.
- A specialist may not create unrestricted child workers.
