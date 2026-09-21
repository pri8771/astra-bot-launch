# Cursor Recovery — LEAD_ACK

## LEAD-045 — 2026-09-21 17:58 ET

Canonical lead review has inspected the newest repository evidence and refreshed the immediate assignment.

- Primary branch remains `cursor/social-bots-recovery-v07-20260921`.
- Current pre-assignment branch head was `488ce0c720d857473ab9f2ce448d9197a955df14`; no worker `SB-R07-041` repair had landed after LEAD-042/043.
- Start a genuinely fresh implementation session and emit exactly one durable `SESSION_ONCE` heartbeat for its new session ID.
- `SB-R07-071` remains SUBMITTED pending independent Acceptance multiprocess execution.
- `SB-R07-041` remains **CHANGES_REQUIRED**: the direct/ad-hoc `ModelReasoningProvider` registered-callable route must fail closed on the canonical authorization manifest even when normal worker entrypoints are bypassed.
- Immediate work is **SB-R07-041 only**: repair the direct callable boundary, add the harmless sentinel regression, run focused/full tests, push exact evidence, and request SUBMITTED.
- Preserve R07-044/R07-072 and later no-live submissions for independent review.
- Do not install the V0.7 LIVE scheduler on the current unsuitable Cursor host.
- Do not edit Fable's newly submitted new-files-only specialist/strategy source unless a later explicit lead reassignment says otherwise.

No live model call, public/account effect, PAYG/new spend, destructive action, credentials exposure, engagement manipulation, or SwarmAI dependency is authorized.

After the bounded R07-041 repair is pushed, pause overlapping runtime expansion while Acceptance executes R07-071 and audits repaired R07-041. Green worker-local tests do not self-accept the artifact.
