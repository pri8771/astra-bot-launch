# START NOW — no heartbeat prerequisite

Lead review: LEAD-025

The owner has requested faster execution. Run this canary immediately from an ACTUAL LOCAL host with working Claude Code subscription authentication. Do not wait for heartbeat validation. If this environment is a remote/container session without subscription auth, stop truthfully and submit a BLOCKED worker report; do not substitute fixtures, injected output, API PAYG or hand-authored model JSON.

No Claude worker-generated canary commit/evidence is visible yet. Priority Zero is therefore stalled on execution, not on project planning.

# SESSION_INSTRUCTIONS — V0.4 Real Live Canary

Lane: dedicated V0.4 live-canary execution
Branch: `claude/social-bots-v04-live-canary`

## Priority

This is **Priority Zero**.

The owner has explicitly required that V0.4 is not complete until at least one real, non-fixture example is executed and independently audited.

Do not replace the real example with unit tests.

Read canonical:
- `git fetch origin`
- `git show origin/chatgpt/social-bots-plan-20260920:social-bots/artifact-packets/SB-V04-005.md`
- `git show origin/chatgpt/social-bots-plan-20260920:social-bots/REASONING_PROPOSAL_SCHEMA.md`
- `git show origin/chatgpt/social-bots-plan-20260920:social-bots/CLAUDE_REASONING_ROUTE_RESEARCH.md`

## Owner authorization for this canary

The owner has explicitly requested **one real V0.4 test example**.

Authorized for this artifact:
- one bounded live public-source retrieval;
- one bounded Claude Code subscription reasoning call, using the already-paid subscription only;
- local persistence of the decision/evidence;
- no public social effect.

NOT authorized:
- Anthropic API PAYG/API-key billing;
- creating API credits/keys;
- public posting/replies/messages;
- purchases or other external effects.

## Preflight

1. Confirm this is an actual local host environment.
2. Record:
   - OS;
   - Python;
   - Claude Code CLI version;
   - whether `ANTHROPIC_API_KEY` is present (boolean only);
   - whether normal Claude Code subscription auth is usable.
3. If `ANTHROPIC_API_KEY` is present:
   - do not print it;
   - do not use it;
   - remove it only from the child invocation environment where safe;
   - verify the CLI is still authenticated through subscription/OAuth/keychain before proceeding.
4. If the real subscription route is not authenticated, mark BLOCKED. Do not fake.

## Real source

Use ONE real, current public source retrieved live at test time.

Requirements:
- HTTP(S), no login/cookies/private browser state;
- no fixture;
- no manually pasted article body;
- record URL, retrieval timestamp, status, byte length, SHA-256;
- retain only a bounded title/summary/excerpt needed for the canary evidence, not a full copyrighted page in Git.

Prefer a reputable first-party/public source relevant enough for The Ledger to form a bounded analysis.

Do not use political campaign/election content for this canary.

## Real adaptive run

Use `social-a` / The Ledger.

The provider invocation must use the actual `ClaudeCodeReasoningProvider` path.

Disallowed:
- injected runner;
- mocked subprocess;
- fixture model output;
- deterministic baseline/contextual provider;
- hand-authored proposal JSON.

Required:
- actual `claude` process invocation;
- bounded non-interactive call;
- no effect tools;
- structured result;
- schema validation;
- deterministic policy after the proposal.

Use an isolated canary `SBOTS_HOME` so the test does not pollute durable production-like state.

The source/model are real even though the state directory is isolated.

## Valid outcomes

Any truthful schema-valid result is acceptable:
- NO_ACTION
- RESEARCH_MORE
- CREATE_CANDIDATE
- safe blocked/unsupported no-effect action

If CREATE_CANDIDATE:
- local only;
- unpublished;
- `publish_authorized=false`.

Do not retry repeatedly just to get a preferred answer. One successful real provider invocation is enough.

## Evidence

Create:
`social-bots/receipts/evidence/SB-V04-live-canary/`

Required:
- SOURCE.json
- PROVIDER.json
- DECISION.json
- SUMMARY.json

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

Expected successful values are defined in SB-V04-005.

Do not store secrets or hidden chain-of-thought.

## Submission

Write:
`social-bots/worker-reports/v04-live-canary/SB-V04-005.md`

Include exact command(s), host metadata, provider version, source URL/hash/time, decision outcome, evidence paths, known limits.

Commit and push.

Request SUBMITTED.

Then STOP and wait for ChatGPT lead independent audit. Do not self-mark V0.4 complete.

## Heartbeat

During the live canary, update:
`social-bots/worker-reports/v04-live-canary/HEARTBEAT.json`

Submission sets notification_pending=true.

## Safety

No public posting/replies/messages, no API PAYG/new spend, no credentials in Git, no fake evidence, no SwarmAI dependency.
