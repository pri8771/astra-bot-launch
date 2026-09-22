> Latest owner instruction, 2026-09-22T17:32Z: PAUSED_BY_OWNER; target V2.0 for all three projects. See OWNER_PAUSE_V20_20260922.md. Earlier ceilings are superseded; no acceptance or live grant is implied.

# Compact project memory

Updated: 2026-09-20

## Owner intent

- Social bots are required.
- Autonomous thinking and adaptive learning are the most important capability.
- ChatGPT is engineering/product lead; Claude Code is the implementation workhorse.
- Finish the complete launch-ready system as quickly as possible today without fake completion.
- Reuse existing work, accounts and email infrastructure before creating new infrastructure.
- No additional spend.
- Keep this separate from SwarmAI implementation.

## Reconciled inventory

- Three autonomous bot runtimes are the active runtime scope.
- The later social plan requires three general personas with distinct voices.
- Two Indian religious/cultural persona workspaces supporting a future Primandir launch remain required and must not be silently dropped. They can share the three-runtime infrastructure rather than require two additional always-on processes.
- TikTok, Reddit, X, Instagram and Facebook are target surfaces subject to supported access and platform restrictions.

## Historical assets

- `astra-bot-launch` contains September launch planning for One Person Ops, Wait How Big, CommerceLint, BidetFit and Guru. Treat that as reuse evidence, not the current social-bot inventory.
- `bots/memory/shared/STATE.md` was last updated 2026-09-01 and is historical for current-state claims.
- Product homes have been verified as existing repositories; current runtime/account behavior still requires fresh evidence.

## Architecture decisions

- Canonical coordination: this directory in `pri8771/astra-bot-launch`.
- Agent/shared runtime code should reuse `pri8771/bots` where suitable.
- Product code stays in existing product homes.
- Social Bots is an independent system. It has no planned runtime dependency on SwarmAI and must remain fully functional if SwarmAI is absent. Any future integration would require a separate explicit owner decision.
- Public profiles and bot runtimes are separate concepts.
- Shared admin/account infrastructure is acceptable; deceptive human impersonation is not.

## Version contract

- Current lead-assigned version: V0.3.x — durable runtime foundation under correctness repair.
- Immediate target: V0.4 — real adaptive autonomous thinking.
- Near-term engineering target: V0.7 — always-on Claude worker + hourly ChatGPT lead loop proven end-to-end.
- First major product target: V1.0 — three real autonomous social bots operating continuously on verified social presences.
- V2.0 — autonomous growth engine.
- Strategic checkpoints are V1.7, V2.3 and V3.0.
- Today's acceleration goal is V2.0 engineering-ready, without misrepresenting blocked operational/public evidence as complete.
- V3.0 — autonomous multi-brand media organization.
- Full acceptance criteria live in `VERSION_ROADMAP.md`. Version promotion is lead/evidence-gated, never implementation-self-declared.

## Project-management style

- Artifact-oriented management is canonical.
- Durable progress is represented by artifact IDs in `ARTIFACT_INDEX.json`.
- Version promotion is derived from accepted artifacts in `MILESTONE_MANIFEST.md`.
- Tasks/prompts are temporary execution packets; they are not the source of truth.
- Claude submits artifacts; ChatGPT lead independently accepts/rejects them.
- Current execution packets live under `artifact-packets/`.

## Lead / worker execution model

- Two Claude implementation lanes may work in parallel under artifact-first ownership: Core Runtime/Autonomy and Intelligence/Growth.
- Claude receives the bulk of implementation work and especially the bulk of routine/easy work.
- ChatGPT stays ahead through product direction, research, repository/source inspection, acceptance design, backlog grooming, debugging, independent review and task decomposition.
- When current lead work is exhausted, ChatGPT should prepare useful future-version work rather than idle, while avoiding duplicate edits to Claude-owned implementation paths.
- Tasks are estimated on a 1–5 story-point complexity scale defined in `WORK_MANAGEMENT.md`; Claude performance is tracked in `WORKER_PERFORMANCE.md`.
- Difficult work remains Claude-owned but should be decomposed into smaller bounded tasks when doing so improves correctness, with final integration acceptance retained.

## Safety/authority

No spend, public posting/deployment, customer messages, purchases, destructive actions, fake engagement, coordinated voting manipulation or credential material without explicit authority.
