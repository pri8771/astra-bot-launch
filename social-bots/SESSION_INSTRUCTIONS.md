# SESSION_INSTRUCTIONS — V0.4 Live Canary

Lane: dedicated V0.4 live-canary evidence worktree
Branch: `claude/social-bots-v04-live-canary`
Lead review: LEAD-039
Lead check: 2026-09-21T17:56:20Z

# FROZEN — EVIDENCE PRESERVATION ONLY

SB-V04-005 is **ACCEPTED from the first chronological real canary at ~16:15Z**. That call consumed the owner's exactly-one existing-subscription Claude Code authorization.

This dedicated branch later executed a second real call at ~16:53Z. Although technically clean, it occurred after the one-call authorization was already consumed. It is preserved as a process/authorization incident and **excluded from acceptance evidence**.

## HARD STOP

**DO NOT execute `claude`, `ClaudeCodeReasoningProvider`, any adaptive provider, or any other live model call.**
Do not fetch new canary sources for another attempt.
Do not use API/PAYG/API keys or incur new spend.
Do not perform public effects.

## Allowed activity

- preserve existing evidence exactly;
- read canonical lead review/state;
- evidence-only documentation/metadata clarification if the lead explicitly assigns it;
- one real `SESSION_ONCE` heartbeat only when a fresh preservation/review session actually starts; never a periodic loop or backfill.

Do not rerun or “improve” the canary. Do not create a third call. Do not self-mark V0.4 complete.

V0.4 remains open because SB-V04-002 and SB-V04-004 are blocked on fresh explicit owner authorization for controlled causal-divergence evidence; SB-EVD-002 remains withheld.

No public posting/replies/messages, paid API/PAYG/new spend, credentials in Git, fabricated evidence, destructive actions or SwarmAI dependency.
