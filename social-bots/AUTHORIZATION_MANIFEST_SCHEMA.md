# Authorization manifest schema

Lead-created, scope-specific authorization record. Code support for an action does not authorize the action.

## Required fields

- schema_version
- authorization_id
- owner_authorization_ref
- created_by: ChatGPT lead
- artifact_scope[]
- allowed_action_types[]
- allowed_bots/personas[]
- allowed_destinations[] where applicable
- provider_constraints
- max_model_calls
- max_public_effect_attempts
- max_spend_usd
- no_retry
- valid_from
- expires_at or null when explicitly bounded by completion
- revoked
- notes

## Fail-closed rules

Execution must stop before spawning a model or external effect when:
- manifest is missing;
- artifact/run is outside scope;
- authorization expired/revoked;
- budget would be exceeded;
- provider/account/destination does not match;
- spend route differs from the manifest;
- a retry is attempted when no_retry=true.

Budget accounting is atomic before spawn/attempt where possible. A crashed process must reconcile uncertain usage before another attempt.

Owner conversation approval and a matching canonical lead manifest are both required where the current project contract says so.
