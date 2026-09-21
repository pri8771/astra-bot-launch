# SESSION_INSTRUCTIONS — Cursor Recovery

Mode: **LEAD-045 — R07-041 AUTHORIZATION-BOUNDARY REPAIR / WAKE-UP**  
Branch: `cursor/social-bots-recovery-v07-20260921`

Read canonical first:
- `social-bots/lead-reviews/LEAD-045_2026-09-21T1758.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `social-bots/next-round/BASELINE.json`
- `social-bots/artifact-packets/recovery-v07/SB-R07-041.md`

## Session start

The prior recovery session is stale relative to this assignment. Start a genuinely fresh implementation session and emit exactly one durable `SESSION_ONCE` heartbeat for the new session ID after reading current coordination. Do not emit repeated in-session heartbeats.

## Hard rule

**DO NOT execute Claude CLI, adaptive reasoning, any registered live model callable, or any other live model/provider call.** No live authorization manifest exists. No public effect, PAYG/new spend, account action, destructive action, credential exposure, engagement manipulation, or SwarmAI dependency is authorized.

## Immediate artifact — SB-R07-041 only

Lead source audit still has one unresolved live-route bypass at prior source `21cc2e7a65750d20dc609b9e9517f920157389a2`:

- `ClaudeCodeReasoningProvider` CLI spawn-point guard is materially improved and should be retained.
- `runtime/reasoning.py::ModelReasoningProvider` is live-capable via the process-registered `_MODEL_CALLABLE` and can be reached by a direct/ad-hoc library caller that bypasses `worker_once` / `run_worker`.
- The canonical live-authorization manifest must protect that path too.

Repair requirements:
1. Structurally guard the registered `model` callable route at registration/invocation boundary with the canonical live-authorization contract, or make it structurally diagnostic-only so a live-capable callable cannot execute outside that contract.
2. Add a direct-library adversarial regression that registers a harmless sentinel callable, selects `SBOTS_REASONING=model`, bypasses normal worker entrypoints, and proves the sentinel is **not invoked** without a valid canonical manifest.
3. Preserve fixture seams only when structurally non-live and explicitly engineering-only.
4. Run focused tests and the full suite.
5. Push exact source SHA, commands/results, evidence paths, and limitations. Request SUBMITTED only.

## Preserve existing submissions / ownership

- `SB-R07-071` remains SUBMITTED pending independent Acceptance execution.
- `SB-R07-044` and `SB-R07-072` remain submitted/pending review.
- Current Cursor host is unsuitable for LIVE scheduler proof; do not install/run R07-073 here.
- Do not edit Fable's newly submitted specialist/strategy files unless a later lead finding explicitly reassigns ownership.

After the bounded R07-041 repair is pushed, stop overlapping runtime expansion while Acceptance independently executes R07-071 and audits the repaired R07-041.
