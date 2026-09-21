# Cursor Recovery — LEAD_ACK

## LEAD-046 — 2026-09-21 18:56 ET

Canonical lead review found no new worker-generated repair after LEAD-045 and refreshed the immediate assignment without broadening scope.

- Primary branch remains `cursor/social-bots-recovery-v07-20260921`.
- Pre-review head was `4ab497f234877e0516f80b1fb9c99ee24dc5a834`, a lead acknowledgement commit rather than new worker implementation.
- The newest durable Cursor heartbeat remains session `s-20260921T191500Z-a23cc77e` from LEAD-041; there is no fresh post-LEAD-045 session heartbeat.
- Start a genuinely fresh implementation session and emit exactly one durable `SESSION_ONCE` heartbeat for its new session ID.
- `SB-R07-071` remains SUBMITTED pending independent Mac Acceptance multiprocess execution.
- `SB-R07-041` remains **CHANGES_REQUIRED**: the direct/ad-hoc `ModelReasoningProvider` registered-callable route must fail closed on the canonical authorization manifest even when normal worker entrypoints are bypassed.
- Immediate work is **SB-R07-041 only**: repair the direct callable boundary, add the harmless direct-library sentinel regression, run focused/full tests, push exact evidence, and request SUBMITTED.
- Preserve R07-044/R07-072 and later no-live submissions for independent review.
- Do not install the V0.7 LIVE scheduler on the current unsuitable Cursor host.
- Do not edit Fable's submitted new-files-only specialist/strategy source without explicit reassignment.

No live model call, public/account effect, PAYG/new spend, destructive action, credentials exposure, fabricated operational evidence, engagement manipulation, or SwarmAI dependency is authorized.

After the bounded R07-041 repair is pushed, pause overlapping runtime expansion while Acceptance executes R07-071 and audits repaired R07-041. Green worker-local tests do not self-accept the artifact.
