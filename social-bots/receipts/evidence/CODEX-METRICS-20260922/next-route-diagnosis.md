# SB-S08 freshness diagnosis

Canonical contract: `origin/chatgpt/social-bots-plan-20260920` at `0d5b183c9b6d0b3a30307b4b4ddbb49b3a297960`.

Source exercised: `/Users/pchordia/Downloads/swarm_codex/review/bots-metrics-source/social-bots/runtime/account_routes.py` from base HEAD `9d497b4567e022a8e7f93a3ee890af206272b5be` (the worktree's unrelated metrics edit does not touch this module).

Contract:

- `ACCOUNT_REGISTRY_SCHEMA.md`: `last_verified_at` is part of AccountRoute and “Stale verification cannot be presented as current connectivity.”
- `SB-S08-001.md`: registry must implement freshness, health and authority defaults.
- `account_routes.py` module truth table says availability requires a healthy exact route and `_route_ok`'s own negative reason names absent/stale `last_verified_at`.

Reproduced symptom with synthetic registry files only:

- `health_status="verified"` and no `last_verified_at` returned `account_available=True`, `authorized=True`.
- The same route with `last_verified_at="2020-01-01T00:00:00+00:00"` also returned `account_available=True`, `authorized=True`.

Output: `/tmp/bots-s08-stale-route-repro-20260922.out`.

Root cause: `_route_ok` lines 93-101 examines only `route_type` and the health-status string. It never parses, requires or ages `last_verified_at`. Any health label outside the small negative sets succeeds indefinitely. `availability_for` then grants account availability and draft authorization from that result.

Smallest repair direction, after the lead fixes the contract's freshness horizon: require a valid timezone-aware `last_verified_at`, reject future timestamps outside an explicit clock-skew allowance, and fail closed when age exceeds that fixed horizon. Return the existing unavailable/unauthorized structure with a precise freshness reason. Tests should inject `now` or call a pure freshness helper so they remain deterministic. Do not infer the horizon from this diagnosis or use filesystem mtime.

No live account, provider, model, public, network or scheduler action occurred. No source or coordination file was edited.
