# Cursor Recovery — SESSION_INSTRUCTIONS — LEAD-047

Branch: `cursor/social-bots-recovery-v07-20260921`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Canonical release commit: `eece1d3a62417802e4316f028fbec098f3220128`
Official phase: **V0.4.x / V0.4 in progress**

## Status — PARKED_SAFE_HANDOFF

Do **not** start new overlapping runtime implementation. Fable is now the sole primary implementation/integration owner under `social-bots/delivery/FINAL_RUN.md`, including the R07-041/shared recovery repair that was previously assigned here.

Your responsibility is preservation and handoff only:

1. If this worktree has any uncommitted or just-finished material work that predates this park instruction, preserve it at a safe recoverable boundary and push it with exact source/test evidence.
2. Do not overwrite or reset existing recovery evidence (`SB-R07-071`, `SB-R07-044`, `SB-R07-072`, later recovery submissions).
3. Do not begin a second implementation of R07-041 or shared runtime fixes while Fable owns those files.
4. Do not install or claim the V0.7 LIVE scheduler on the previously classified unsuitable Cursor host.
5. If no material local work exists, remain parked; no periodic heartbeat is required. A genuinely fresh future released session emits one `SESSION_ONCE` heartbeat after reading current coordination.

No live Claude/adaptive/product-model call, public/account effect, PAYG/new spend, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized.
