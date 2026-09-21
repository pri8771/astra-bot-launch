# Astra Bot Launch — Claude / Fable entrypoint

This repository contains multiple historical projects and handoff documents. **Do not read the entire repo at startup.**

For Social Bots work, the canonical project lives under `social-bots/`.

## Roles

- Owner: product/authority decisions.
- ChatGPT: engineering/product lead and acceptance authority.
- Claude/Fable/Cursor: implementation/planning workers as assigned.
- GitHub canonical coordination is project truth. Past conversation/memory explains intent only.

## Social Bots startup

Read only:

1. `social-bots/coordination/SESSION_START.md`
2. `social-bots/state/CURRENT.md`
3. `social-bots/coordination/READ_ROUTER.md`
4. the assignment file named by SESSION_START
5. the active artifact packet(s) named by that assignment

Then use targeted git diff/search. Do not preload all roadmaps or artifact packets.

## Stable rules

- Artifact-oriented development; prefer SP1/SP2 work.
- One fresh worker session = one real `SESSION_ONCE` heartbeat.
- Engineering evidence and LIVE evidence are different.
- Workers submit; ChatGPT alone accepts/promotes.
- Never fabricate provenance, liveness, tests, or operational evidence.
- No public post/reply/message, new spend/PAYG, destructive action, account/MFA bypass, or live model call outside the current authorization contract.
- Social Bots must remain independent of SwarmAI.
- Reuse existing brownfield code before creating parallel subsystems.
- Do not overlap another active worker's source ownership.

## Efficiency

- Prefer specific symbols, diffs and current artifact cards over full-file rereads.
- Keep reports compact and machine-readable.
- If subagents/models are available, use lower-cost models for bounded mechanical work; reserve the strongest model for architecture, integration, concurrency, authority/safety and difficult debugging.

If instructions conflict, follow the current canonical Social Bots coordination and latest ChatGPT lead review.
