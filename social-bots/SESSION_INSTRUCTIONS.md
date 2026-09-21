## TODAY-ONLY HEARTBEAT SOAK — 2026-09-21

For this fresh session, start the heartbeat soak immediately and keep useful lane work running in parallel.

Stage 1:
- produce heartbeat records at T0, ~T0+5m, ~T0+10m, ~T0+15m;
- this is 3 consecutive real 5-minute intervals;
- use cadence_mode `FAST_5M`;
- append every timed record to the lane's HEARTBEAT_LOG.jsonl and push it;
- no fabricated/backfilled timestamps and no burst updates counted as timed success.

Stage 2:
- after the third successful 5-minute interval, switch immediately to `SOAK_15M_24H`;
- continue every 15 minutes for 24 hours (target 96 intervals);
- do not wait for lead acknowledgement to start Stage 2;
- keep engineering/review work running between heartbeat intervals;
- if an interval is missed or the heartbeat process dies, record it truthfully and continue prospectively.

Read canonical `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md` before starting.

# START NOW — no heartbeat prerequisite

Lead review: LEAD-033

Run this canary immediately from an ACTUAL LOCAL host with working Claude Code subscription authentication. Do not wait for heartbeat validation. If this environment lacks subscription auth, submit a truthful BLOCKED worker report; do not substitute fixtures, injected output, API PAYG or hand-authored model JSON.

No Claude worker-generated canary commit/evidence is visible as of LEAD-033. Priority Zero remains stalled on execution, not planning.

# SESSION_INSTRUCTIONS — V0.4 Real Live Canary

Lane: dedicated V0.4 live-canary execution
Branch: `claude/social-bots-v04-live-canary`
Artifact: `SB-V04-005`

## Hard acceptance chain

V0.4 requires one real non-fixture example:

real current public HTTP(S) source -> live retrieval/hash/timestamp/status/byte length -> actual `ClaudeCodeReasoningProvider` / `claude` CLI invocation using existing subscription authentication -> REASONING_PROPOSAL_SCHEMA validation -> deterministic policy -> durably persisted local decision -> zero public effect.

Unit tests, fixture signals, injected runners, deterministic providers and prewritten proposal JSON do not count.

## Owner authorization

Authorized: one bounded public-source retrieval, one bounded existing-subscription Claude Code call, local evidence/decision persistence, zero public social effect.

Not authorized: Anthropic API/PAYG/API-key billing, purchases, public posts/replies/messages, or other external effects.

## Preflight

- record OS/Python/Claude CLI version and boolean presence of `ANTHROPIC_API_KEY` only;
- never print/use a key; child invocation must not use API-key/PAYG path;
- verify normal subscription/OAuth/keychain route is usable or submit BLOCKED;
- use isolated canary `SBOTS_HOME`.

## Evidence

Create `social-bots/receipts/evidence/SB-V04-live-canary/` with `SOURCE.json`, `PROVIDER.json`, `DECISION.json`, `SUMMARY.json`.

SUMMARY must truthfully state: `real_network_source`, `fixture_source`, `injected_model_runner`, `actual_claude_cli_invoked`, `api_key_path_used`, `proposal_schema_valid`, `deterministic_policy_applied`, `public_effect_performed`, `decision_persisted`.

Write `social-bots/worker-reports/v04-live-canary/SB-V04-005.md` with exact commands, host/provider metadata, source URL/hash/time, decision outcome, evidence paths and limits. Do not store secrets or hidden chain-of-thought.

Commit/push and request SUBMITTED, then STOP for independent lead audit. Do not self-mark V0.4 complete.

## Safety

No public posting/replies/messages, no API PAYG/new spend, no credentials in Git, no fake evidence, no SwarmAI dependency.
