# Social Bots Control

This directory is the canonical coordination home for the social-bots initiative.

It does **not** replace product source repositories and does not absorb SwarmAI, Jobs Bot, Lipi/Shopify, personal assistants, or Home Assistant. It coordinates three autonomous social-bot runtimes and their persona/account surfaces.

## Canonical model

- **Three autonomous bot runtimes**: `social-a`, `social-b`, `social-c`.
- Each runtime has isolated mission state, memory, experiment state, leases and receipts.
- **Public persona/account surfaces are separate from runtime identity.** The three general social personas remain required. The two Indian religious/cultural personas supporting a future Primandir launch remain required persona workspaces, but they do not require two additional always-on runtimes.
- Shared code, credentials references, analytics plumbing and account administration may be reused where permitted.
- Never make one public account deceptively impersonate three unrelated humans. If one public profile carries multiple characters, present them as distinct AI-managed characters/series. Prefer separate public profiles when practical because attribution and audience learning are cleaner.

## Canonical source/reuse boundaries

- Coordination: `pri8771/astra-bot-launch/social-bots/`
- Agent-side shared infrastructure/memory conventions: `pri8771/bots`
- Wait How Big source/operator assets: `pri8771/orchestrator/wait-how-big-social/`
- One Person Ops source/assets: `pri8771/one-person-ops`
- CommerceLint source/assets: `pri8771/autonomous_apps`
- BidetFit source/assets: `pri8771/priyanshchordia.com/ventures/bidetfit/`
- Guru cultural/editorial references: `reference/guru-sadhana-candidate/`

These older ventures are reuse pools, not the new inventory by definition. Existing emails, account aliases, analytics, publishing adapters, research code, content assets and verified operational patterns may be reused only after current verification.

## Start here

1. `TODAY_EXECUTION_PLAN.md`
2. `AUTONOMY_CONTRACT.md`
3. `PROJECT_MEMORY.md`
4. `STATE.json`
5. `WORK_QUEUE.md`
6. New entries in `AGENT_MESSAGES.md`
7. `CLAUDE_BOOTSTRAP.md`

No spend, public posting, customer messaging, purchases, destructive actions, quota evasion or credential material is authorized by these files.
