# START NOW — no heartbeat prerequisite

Lead review: LEAD-026

Run this canary immediately from an ACTUAL LOCAL host with working Claude Code subscription authentication. Do not wait for heartbeat validation. If this environment is a remote/container session without subscription auth, stop truthfully and submit a BLOCKED worker report; do not substitute fixtures, injected output, API PAYG or hand-authored model JSON.

No Claude worker-generated canary commit/evidence is visible as of LEAD-026. Priority Zero is stalled on execution, not planning.

# SESSION_INSTRUCTIONS — V0.4 Real Live Canary

Lane: dedicated V0.4 live-canary execution
Branch: `claude/social-bots-v04-live-canary`
Artifact: `SB-V04-005`

## Priority

This is **Priority Zero**.

V0.4 is not complete until at least one real, non-fixture example is executed and independently audited. Unit tests, fixture signals, injected runners, deterministic providers and prewritten proposal JSON do not satisfy this artifact.

Read canonical:
- `git fetch origin`
- `git show origin/chatgpt/social-bots-plan-20260920:social-bots/artifact-packets/SB-V04-005.md`
- `git show origin/chatgpt/social-bots-plan-20260920:social-bots/REASONING_PROPOSAL_SCHEMA.md`
- `git show origin/chatgpt/social-bots-plan-20260920:social-bots/CLAUDE_REASONING_ROUTE_RESEARCH.md`

## Owner authorization for this canary

Authorized:
- one bounded live public-source retrieval;
- one bounded Claude Code subscription reasoning call using the already-paid subscription only;
- local persistence of the decision/evidence;
- zero public social effect.

NOT authorized:
- Anthropic API PAYG/API-key billing;
- creating API credits/keys;
- public posting/replies/messages;
- purchases or other external effects.

## Preflight

1. Confirm this is an actual local host environment.
2. Record OS, Python, Claude Code CLI version, whether `ANTHROPIC_API_KEY` is present (boolean only), and whether normal Claude Code subscription auth is usable.
3. If `ANTHROPIC_API_KEY` is present, never print/use it; strip it from the child invocation where safe and verify subscription/OAuth/keychain auth still works.
4. If the real subscription route is not authenticated, mark BLOCKED and push that truthful report. Do not fake.

## Required live chain

Use `social-a` / The Ledger and exactly one bounded real example:

real current public source -> live retrieval/hash/timestamp -> actual `ClaudeCodeReasoningProvider` invocation using subscription auth -> proposal schema validation -> deterministic policy -> persisted local decision -> zero public effect.

Source requirements:
- HTTP(S), no login/cookies/private browser state;
- no fixture or manually pasted article body;
- record URL, retrieval timestamp, status, byte length and SHA-256;
- commit only a bounded title/summary/excerpt needed for evidence.

Provider requirements:
- actual `claude` process invocation;
- no injected runner/mock subprocess/fixture model output/deterministic baseline/prewritten JSON;
- bounded non-interactive call;
- no effect tools;
- structured result + schema validation;
- deterministic policy after the proposal.

Use isolated canary `SBOTS_HOME` so the test does not pollute durable production-like state.

Any truthful schema-valid outcome is acceptable: NO_ACTION, RESEARCH_MORE, CREATE_CANDIDATE, or safe blocked/unsupported no-effect action. Do not retry just to obtain a preferred result.

If CREATE_CANDIDATE, local only and `publish_authorized=false`.

## Evidence

Create `social-bots/receipts/evidence/SB-V04-live-canary/` with:
- `SOURCE.json`
- `PROVIDER.json`
- `DECISION.json`
- `SUMMARY.json`

SUMMARY must explicitly state:
- real_network_source
- fixture_source
- injected_model_runner
- actual_claude_cli_invoked
- api_key_path_used
- proposal_schema_valid
- deterministic_policy_applied
- public_effect_performed
- decision_persisted

Do not store secrets or hidden chain-of-thought.

## Submission

Write `social-bots/worker-reports/v04-live-canary/SB-V04-005.md` with exact commands, host metadata, provider version, source URL/hash/time, decision outcome, evidence paths and known limits.

Commit/push and request SUBMITTED, then STOP for independent ChatGPT lead audit. Do not self-mark V0.4 complete.

## Heartbeat

During the live canary update `social-bots/worker-reports/v04-live-canary/HEARTBEAT.json`; submission sets `notification_pending=true`. Heartbeat is not a prerequisite.

## Safety

No public posting/replies/messages, no API PAYG/new spend, no credentials in Git, no fake evidence, no SwarmAI dependency.
