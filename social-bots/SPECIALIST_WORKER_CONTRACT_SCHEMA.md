# Temporary specialist worker contract schema

Canonical schema version: **2**.

Reusable contract for V2.3+ temporary workers. These are Social Bots components, not SwarmAI.

## WorkerContract

Required fields:
- schema_version = 2
- worker_id
- parent_run_id
- bot
- persona
- role: researcher | analyst | writer | reviewer | media | qa
- objective
- bounded_context_refs[]
- allowed_tools[]
- denied_tools[]
- authority: SpecialistAuthority
- input_artifacts[]
- expected_output_schema
- time_budget_s
- model_call_budget
- external_effect_budget = 0
- scratch_scope
- stop_conditions[]
- created_at
- expires_at
- provenance

### SpecialistAuthority

Frozen least-authority fields only:
- read_context_refs
- write_scratch
- emit_result

It has no public-post, spend, message-user, credential, destructive-action or child-spawn authority fields. `external_effect_budget` is fixed at zero and cannot be caller-widened.

The earlier free-form `authority_scope[]` concept is superseded by schema v2 before implementation.

## WorkerResult

Required:
- schema_version = 2
- worker_id
- parent_run_id
- bot
- persona
- role
- started_at / finished_at
- source_ref
- outputs[]
- evidence_refs[]
- calls_used
- effect_attempts
- result
- limitations[]
- cleanup_status
- provenance

## Rules

- Least authority.
- No implicit inheritance of parent credentials/effect authority.
- No credential/token/cookie/session secret in bounded context refs.
- Parent validates/integrates or rejects result.
- Scratch state is isolated and retired after completion except attributable evidence.
- A specialist may not create unrestricted child workers.
- Model-call/time budgets are deterministic and fail closed.
- Live-capable providers require the canonical authorization gate.
- Persona/brand scope mismatches fail closed.
