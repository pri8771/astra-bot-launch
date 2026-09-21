# Cursor Recovery — SESSION_INSTRUCTIONS — LEAD-041

You are the primary Social Bots implementation lane for recovery through V0.7.

Branch: `cursor/social-bots-recovery-v07-20260921`
Current inherited source/report head: `2f14a5cb08c9019fd174c1f54ecda130fa9308d4`
Material source baseline inside that history: `a73b7b58de8f3669795b81637bff55247d67943c`

Before editing, read canonical coordination from `chatgpt/social-bots-plan-20260920`:
- `social-bots/RECOVERY_TO_V07.md`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/ARTIFACT_INDEX.json`
- latest `social-bots/AGENT_MESSAGES.md`

Execution order now:
1. `SB-R07-071` — make `SESSION_ONCE` uniqueness atomic across concurrent processes, with a real cross-process race regression. This is the immediate source blocker identified by LEAD-040.
2. `SB-R07-041` — independently audit the inherited live-route/authorization hardening at `a73b7b5`; retain the spawn-point fail-closed behavior and add/fix only evidence-backed defects.
3. `SB-R07-044` — divergence verifier.
4. `SB-R07-072` — persistent-host preflight. Do not claim persistent-host acceptance on a temporary/CCR environment.
5. Continue dependency-ready no-live-call recovery artifacts from `RECOVERY_TO_V07.md` and canonical `WORK_QUEUE.md`.

Rules:
- One fresh worker session emits exactly one durable `SESSION_ONCE` heartbeat. Do not run an in-session periodic heartbeat soak.
- No live Claude/adaptive/model call is authorized. The future five-call V0.4 batch requires fresh explicit owner authorization AND a matching canonical lead authorization manifest.
- No public posting/replies/messages, purchases, new spend/PAYG, destructive actions, credential exposure, or SwarmAI dependency.
- One small artifact per commit where practical. Run focused and full tests, preserve exact commands/results, and push evidence.
- Do not edit or restart the legacy Core/Intelligence/Acceptance/canary branches. They are evidence/source branches during recovery.
- Do not self-accept artifacts or versions. Stop only for a real owner/admin/login/spend/public-effect gate; otherwise continue to the next dependency-safe artifact.

When `SB-R07-071` is pushed, update this lane's `CURRENT_PROGRESS.md` with exact SHA, tests, evidence, next artifact, and blockers.