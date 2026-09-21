# SESSION_INSTRUCTIONS — V0.4 Real Live Canary

Lane: dedicated V0.4 live-canary execution
Branch: `claude/social-bots-v04-live-canary`
Artifact: `SB-V04-005`
Lead review: LEAD-035
Lead check: 2026-09-21T15:52:53Z

# ACCEPTANCE-OWNED SECOND WORKTREE — READY, STILL UNEXECUTED

This branch has no worker-generated canary evidence, no worker CURRENT_PROGRESS file, and no durable FAST_5M T0. The fresh Acceptance session must execute this branch only after it pushes the independent SB-V03-004 Mission A report from `claude/social-bots-mac-qa-control`.

Heartbeat is observability only. Do not delay an otherwise-ready canary for heartbeat. Run from an ACTUAL LOCAL Mac host with working Claude Code subscription authentication. If subscription auth is unavailable, submit a truthful BLOCKED worker report; never substitute fixtures, injected output, API/PAYG, or hand-authored model JSON.

## Today's heartbeat soak — not started

If this worktree/session remains independently active, start prospectively in parallel:
- `FAST_5M`: T0, +~5m, +~10m, +~15m;
- then `SOAK_15M_24H`: every 15 minutes for 24 hours;
- append/push real timed records only; no backfill.

## Hard acceptance chain

V0.4 requires one real non-fixture example:

real current public HTTP(S) source -> live retrieval/hash/timestamp/status/byte length -> actual `ClaudeCodeReasoningProvider` / `claude` CLI invocation using existing subscription authentication -> REASONING_PROPOSAL_SCHEMA validation -> deterministic policy -> durably persisted local decision -> zero public effect.

Unit tests, fixture signals, injected runners, deterministic providers, and prewritten proposal JSON do not count.

## Owner authorization

Authorized: one bounded public-source retrieval, one bounded existing-subscription Claude Code call, local evidence/decision persistence, zero public social effect.

Not authorized: Anthropic API/PAYG/API-key billing, purchases, public posts/replies/messages, or other external effects.

## Preflight

- record OS/Python/Claude CLI version and boolean presence of `ANTHROPIC_API_KEY` only;
- never print/use a key; child invocation must not use API-key/PAYG path;
- verify normal subscription/OAuth/keychain route is usable or submit BLOCKED;
- use isolated canary `SBOTS_HOME`.

## Evidence

Create `social-bots/receipts/evidence/SB-V04-live-canary/` with:
- `SOURCE.json`
- `PROVIDER.json`
- `DECISION.json`
- `SUMMARY.json`

SUMMARY must truthfully state: `real_network_source`, `fixture_source`, `injected_model_runner`, `actual_claude_cli_invoked`, `api_key_path_used`, `proposal_schema_valid`, `deterministic_policy_applied`, `public_effect_performed`, `decision_persisted`.

Write `social-bots/worker-reports/v04-live-canary/SB-V04-005.md` with exact commands, host/provider metadata, source URL/hash/time, decision outcome, evidence paths and limits. Do not store secrets or hidden chain-of-thought.

Commit/push and request SUBMITTED, then STOP canary execution for independent lead audit. Do not self-mark V0.4 complete.

## Safety

No public posting/replies/messages, no API PAYG/new spend, no credentials in Git, no fake evidence, no SwarmAI dependency.
