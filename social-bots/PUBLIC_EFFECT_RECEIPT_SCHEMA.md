# Public effect receipt and reconciliation schema

Used for any authorized public post/reply/message/delete/correction.

## Receipt

- schema_version
- effect_id
- authorization_manifest_ref
- bot/persona
- platform
- destination_route_id
- effect_type
- content_id
- content_hash
- preflight_verified_at
- attempt_started_at
- request/provider id if safe
- immediate_result: SUCCESS | FAILED | UNCERTAIN
- provider_status
- readback_status
- external_permalink_or_id
- readback_hash
- verified_at
- duplicate_check
- correction_parent_effect_id
- analytics_window_ref
- reconciliation_notes

## Exactly-once / uncertain-effect rule

An API/browser success response is not sufficient. A public effect becomes VERIFIED only after external destination readback.

If the process crashes after attempt but before readback, state is UNCERTAIN. Reconcile before any retry. Never retry blindly because that can duplicate an external effect.
