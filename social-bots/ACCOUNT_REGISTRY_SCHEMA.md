# Safe account registry schema

Credentials-free canonical mapping for V0.8+.

## AccountRoute

- schema_version
- route_id
- platform
- account_alias
- public_profile_url_or_platform_id
- bot
- persona
- ownership_type
- login_method_label
- credential_reference_alias
- route_type: API | browser | Buffer | manual | unsupported
- capabilities:
  - read
  - draft
  - publish
  - reply
  - dm
  - analytics
  - delete_or_correct
- publish_authorized: false by default
- reply_authorized: false by default
- analytics_route
- last_verified_at
- verification_method
- health_status
- exact_owner_gate
- notes

## Rules

- Never store passwords, tokens, cookies, TOTP seeds, recovery codes or session state.
- Credential reference is only an alias to an external secret store/keychain.
- A persona/destination mismatch is a hard stop.
- Stale verification cannot be presented as current connectivity.
