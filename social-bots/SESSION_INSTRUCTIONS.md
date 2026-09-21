# SESSION_INSTRUCTIONS — Acceptance / Independent Review Lane

Mode: LEAD-041 — REVIEW-ONLY STANDBY
Branch: `claude/social-bots-mac-qa-control`

Canonical coordination is `chatgpt/social-bots-plan-20260920`. Primary implementation is now consolidated on `cursor/social-bots-recovery-v07-20260921`.

Do not edit runtime/source implementation. Preserve existing V0.3/V0.4 acceptance evidence. When a new recovery submission is explicitly available, perform independent read/test/audit work only.

Next dependency-ready review target: `SB-R07-071` atomic cross-process `SESSION_ONCE` uniqueness. Verify the implementation actually prevents two concurrent processes from both recording the same session ID, execute the adversarial race test independently, and report exact SHA/commands/results. Then independently audit `SB-R07-041` live-route fail-closed behavior when assigned.

Do not execute Claude CLI/adaptive/model calls. The canary evidence branch remains frozen and no additional live call is authorized.

One fresh QA session may emit one `SESSION_ONCE` heartbeat; do not run a periodic in-session soak. Do not self-accept artifacts.

No public effects, PAYG/new spend, destructive actions, credential exposure, fabricated evidence, engagement manipulation, or SwarmAI dependency.