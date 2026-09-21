# Active session router — LEAD-045

## Cursor Recovery — STALE / ACTION REQUIRED
Branch: `cursor/social-bots-recovery-v07-20260921`.

Owns existing recovery runtime surfaces. Immediate and only released implementation: repair **SB-R07-041** direct `ModelReasoningProvider` callable authorization boundary with zero live calls, add direct-library sentinel regression, run tests, push exact evidence. Preserve submitted R07 artifacts; do not install a scheduler on the unsuitable Cursor host.

## Fable V2.3 Fast-track — PAUSED FOR REVIEW
Branch: `fable/social-bots-v23-fasttrack-20260921`.

Fresh session `s-20260921T211438Z-d5589881` completed all currently released non-overlapping new-files-only engineering and submitted **SB-S20-001 + SB-S23-001..008**. Current branch head reviewed: `a204ad0827748a4e9661f1945b8e025d53d0ae09`.

No new source is released now. Preserve evidence and wait for explicit lead reassignment. Do not edit Cursor-owned existing source. Engineering/fixture submissions do not promote operational V2.3.

## Mac Acceptance — STALE / ACTION REQUIRED
Branch: `claude/social-bots-mac-qa-control`.

Review-only. Start one fresh review session and emit one real `SESSION_ONCE` heartbeat. Then:
1. independently execute **SB-R07-071** multiprocess race;
2. after Cursor repair, audit **SB-R07-041** through the direct-library path with a harmless sentinel and no real model call;
3. independently rerun/audit Fable **SB-S23-008** fixture lifecycle evidence.

No runtime source edits or live model calls.

## Legacy Core / Intelligence / Canary
- Core: parked evidence-only.
- Intelligence: parked evidence-only; V15 structural issue remains unresolved.
- Canary: frozen evidence preservation only; prior live-call authorization is consumed.

## External worker
`worker-pc` remains outside the critical path until private-repository clone/auth is demonstrably repaired. Do not redispatch merely because capacity is free.

## Heartbeat policy
Canonical policy is **ONE SESSION = ONE HEARTBEAT**. The prior FAST_5M/SOAK schedule is superseded. Heartbeat is observability only and never artifact acceptance evidence.

## Operational gates
- V0.4 five-call causal-divergence batch requires fresh explicit owner authorization plus a scope-specific lead manifest.
- V0.7 LIVE requires repeated native OS-scheduled bounded worker sessions on a verified owner-controlled persistent host.
- Operational V2.3 requires `SB-V23-003` and the full LIVE dependency chain. `SB-V23-099` is engineering-readiness only.

ChatGPT lead alone accepts artifacts and promotes versions from independently verified evidence.
