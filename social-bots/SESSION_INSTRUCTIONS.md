# SESSION_INSTRUCTIONS — Cursor Recovery

Mode: **LEAD-042 — R07-041 AUTHORIZATION-BOUNDARY REPAIR**  
Branch: `cursor/social-bots-recovery-v07-20260921`

Read canonical first:
- `social-bots/lead-reviews/LEAD-042_2026-09-21T1556.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `social-bots/artifact-packets/recovery-v07/SB-R07-041.md`

## Hard rule

**DO NOT execute Claude CLI, adaptive reasoning, any registered live model callable, or any other live model/provider call.** No live authorization manifest exists. No public effect, PAYG/new spend, destructive action, credential exposure, or SwarmAI dependency is authorized.

## Immediate artifact — SB-R07-041 only

Lead source audit found one remaining live-route bypass at source `21cc2e7a65750d20dc609b9e9517f920157389a2`:

- `ClaudeCodeReasoningProvider` CLI spawn-point guard is materially improved and should be retained.
- But `runtime/reasoning.py::ModelReasoningProvider` is `adaptive=True`, accepts the process-registered `_MODEL_CALLABLE`, and calls it directly without checking the canonical live-authorization manifest.
- A direct/ad-hoc caller can select `SBOTS_REASONING=model`, register a live-capable callable, bypass `worker_once` / `run_worker`, and reach that callable without the manifest gate.
- The R07-041 packet requires **every live-capable entrypoint** to fail closed, so this artifact is CHANGES_REQUIRED.

Repair requirements:
1. Structurally guard the `model` callable route at provider/registration/invocation boundary with the canonical live-authorization contract, **or** make the route structurally diagnostic-only so a registered live-capable callable cannot execute outside the manifest gate.
2. Add a direct-library adversarial regression that:
   - registers a callable;
   - selects `SBOTS_REASONING=model`;
   - bypasses `worker_once.py` and `run_worker.py`;
   - proves the callable is **not invoked** without a valid canonical manifest.
3. Retain injected fixture seams only where they are structurally non-live and clearly engineering-only.
4. Run focused tests and the full suite.
5. Push exact source SHA, commands/results, evidence paths, and limitations. Request SUBMITTED only.

## Preserve existing submissions

Do not rewrite acceptance history or self-accept:
- `SB-R07-071` remains SUBMITTED pending independent Acceptance execution.
- `SB-R07-044` remains SUBMITTED pending audit.
- `SB-R07-072` remains SUBMITTED and says this Cursor host is **UNSUITABLE** for V0.7 LIVE scheduler proof.
- Do **not** install/run `SB-R07-073` on this host.
- R07-042/051/052/053/061 are useful worker submissions but remain pending lead/independent audit.

After the R07-041 repair is pushed, stop overlapping runtime expansion while Acceptance executes R07-071 and audits repaired R07-041. Dependency-safe report/evidence packaging may continue, but no live path.

Heartbeat: this existing session already emitted `s-20260921T191500Z-a23cc77e`; do not emit a second heartbeat for the same session. A genuinely fresh later session emits exactly one new `SESSION_ONCE` heartbeat.
