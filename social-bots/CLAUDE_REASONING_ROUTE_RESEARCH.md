# V0.4 reasoning runtime route research

Lead research date: 2026-09-20.

## Finding

A plausible no-additional-spend adaptive reasoning route exists through an already-subscribed Claude Code installation, subject to actual host authentication and plan usage limits.

Current official Anthropic documentation states:
- Claude Code can use a Claude Pro or Max subscription with the same Claude account.
- Claude Code supports non-interactive print mode via `claude -p`.
- print mode supports JSON output and max-turn limits.
- If `ANTHROPIC_API_KEY` is set, Claude Code uses the API key instead of the subscription, which can create API charges.
- Pro/Max usage is shared across Claude and Claude Code and remains subject to plan limits.

Official sources:
- https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
- https://docs.anthropic.com/en/docs/claude-code/cli-usage
- https://docs.anthropic.com/en/docs/claude-code/getting-started

## Candidate adapter contract

Host-side adapter may invoke a bounded command conceptually equivalent to:

`claude -p <prompt> --output-format json --max-turns 1`

The adapter must:
1. fail closed if `ANTHROPIC_API_KEY` is present;
2. never create/use Console PAYG credentials;
3. require pre-existing subscription authentication established by the owner;
4. record provider identity, exit code, safe stderr classification, and structured result metadata;
5. treat auth/quota/model-unavailable/parse failure as BLOCKED_REASONING_UNAVAILABLE;
6. apply strict output schema validation before Core policy consumes a proposal;
7. use no tools / no external effects for reasoning-only calls unless a later artifact explicitly authorizes tools;
8. never log auth tokens/cookies.

## Acceptance needed before calling this available

- actual target host has Claude Code installed;
- owner-authenticated subscription session works;
- no API key environment variable is present;
- one bounded non-interactive test succeeds without prompting for billing/API credits;
- quota/auth failure path is tested fail-closed;
- no claim of unlimited/free inference; this consumes the user's existing subscription allowance.

## Current status

Lead research only. Not yet runtime-verified on the target host.
