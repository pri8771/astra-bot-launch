# Assignment — Cursor Recovery — LEAD-045

Role: primary recovery implementation worker for existing recovery runtime surfaces.

Use:
- `../RECOVERY_TO_V07.md`
- exact `../artifact-packets/recovery-v07/<ARTIFACT>.md`
- `../next-round/BASELINE.json`

## Immediate released work — SB-R07-041 only

Repair the direct `ModelReasoningProvider` registered-callable authorization boundary.

Required result:
1. Every live-capable direct-library and worker entrypoint must fail closed without a valid canonical authorization manifest.
2. Add an adversarial direct-library regression that registers a harmless sentinel callable, bypasses normal worker entrypoints, and proves the sentinel is **not invoked** when authorization is absent/invalid.
3. No real provider/model invocation is permitted.
4. Run focused and full tests and submit exact source SHA, commands/results, and known limits.

## Preserve submitted work

- `SB-R07-071` remains SUBMITTED pending independent Acceptance multiprocess execution.
- Preserve `SB-R07-044`, `SB-R07-072`, and later no-live recovery submissions for review; do not self-accept or rewrite them without a concrete failing test/review finding.
- Do not install a scheduler on the current unsuitable Cursor host.

## Ownership / overlap

Do not edit Fable new-files-only specialist/strategy submissions unless explicitly reassigned after review. Legacy Core/Intelligence are parked. One fresh session = one durable `SESSION_ONCE` heartbeat.

## Hard gates

No live model call, public/account effect, new spend/PAYG, destructive action, credential exposure, engagement manipulation, or SwarmAI dependency.

Workers submit. ChatGPT lead accepts.
