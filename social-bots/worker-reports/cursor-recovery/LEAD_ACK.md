# Cursor Recovery — LEAD_ACK

## LEAD-042 — 2026-09-21 15:56 ET

Canonical lead review has inspected the submitted recovery source and changed the immediate assignment.

- Primary branch remains `cursor/social-bots-recovery-v07-20260921`.
- Current verified worker head before this acknowledgement: `d7ecb256d430f437f4ad9249480b6430af52ecf9`.
- Existing session `s-20260921T191500Z-a23cc77e` already emitted its one durable `SESSION_ONCE` heartbeat; do not emit another for the same session.
- `SB-R07-071`: SUBMITTED, lead source inspection is positive, but independent Acceptance execution is required before acceptance.
- `SB-R07-044`: SUBMITTED / pending audit.
- `SB-R07-072`: SUBMITTED; current Cursor host is unsuitable for LIVE V0.7 scheduler evidence. Do not install/run `SB-R07-073` here.
- `SB-R07-041`: **CHANGES_REQUIRED**. The CLI spawn guard is good, but `ModelReasoningProvider` can invoke a process-registered `_MODEL_CALLABLE` without the canonical manifest when a direct/ad-hoc caller bypasses worker entrypoints.
- Immediate work: repair only that direct `model` callable authorization boundary, add the direct-library adversarial regression, run focused/full tests, push exact evidence, and request SUBMITTED.
- No live model call, public effect, PAYG/new spend, destructive action, credentials exposure, or SwarmAI dependency is authorized.

After the bounded R07-041 repair is pushed, avoid new overlapping runtime expansion while independent Acceptance executes R07-071 and audits the repaired R07-041. Do not infer milestone acceptance from green tests or later scaffolding.
