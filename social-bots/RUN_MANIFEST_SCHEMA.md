# Run manifest schema

Reusable contract for any bounded operational or acceptance run from V0.6 onward.

## Required fields

- schema_version
- run_id
- artifact_id
- version_target
- bot
- persona
- started_at
- finished_at
- source_code_ref
- config_hash
- persona_hash
- objective_hash
- host_alias
- scheduler_or_invoker
- authorization_manifest_ref
- evidence_refs[]
- provider_runs[]
- model_call_budget
- model_calls_used
- public_effect_budget
- public_effects_attempted
- public_effects_verified
- result
- limitations[]
- receipt_refs[]

Each provider run records provider id/version/config, prompt/context hashes, started/finished timestamps, success/failure, output hash and whether it was operational or fixture.

## Rules

- A manifest is immutable after the run except for an append-only reconciliation section.
- Missing data is UNKNOWN, never inferred.
- Failed or unavailable calls still consume a call if the external provider was actually spawned.
- No retry is implicit.
- Public-effect attempts use PUBLIC_EFFECT_RECEIPT_SCHEMA.md.
- The manifest never contains credentials or hidden chain-of-thought.
