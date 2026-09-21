# Work queue — LEAD-041 V0.7 recovery

Official phase remains **V0.4.x**. No artifact/version promotion occurred in this review.

Primary recovery contract: `RECOVERY_TO_V07.md`.
Primary implementation branch: `cursor/social-bots-recovery-v07-20260921`.
Latest inherited report history transferred into recovery: `2f14a5cb08c9019fd174c1f54ecda130fa9308d4`.
Latest material source inside that history: `a73b7b58de8f3669795b81637bff55247d67943c`.
LEAD-041 assignment commits then add the recovery worker instructions/ack on top of that history.

## Verified delta since LEAD-040

LEAD-040 created the recovery branch at `918c42e...`, but the verified Core descendant continued immediately afterward. `a73b7b5...` materially hardened the real Claude route by enforcing the canonical authorization-manifest refusal at the `ClaudeCodeReasoningProvider` spawn point, preventing alternate entrypoints from bypassing the gate. The worker-reported full suite is **312 passed, 1 skipped**, and no live model call occurred. Corrected reports/progress continue through `2f14a5c...`.

The recovery branch was fast-forwarded to that descendant history before new work was assigned so recovery does not begin from a stale safety baseline.

## Primary Cursor recovery queue

READY / ordered:
1. **SB-R07-071** — make `SESSION_ONCE` uniqueness atomic across concurrent processes; include an adversarial cross-process duplicate-session race regression.
2. **SB-R07-041** — independently audit the inherited `a73b7b5...` live-route/authorization hardening; preserve fail-closed spawn-point behavior and fix only evidence-backed defects.
3. **SB-R07-044** — divergence verifier.
4. **SB-R07-072** — persistent-host preflight; do not treat a temporary/CCR host as persistent-host acceptance.
5. **SB-R07-042** — controlled V0.4 input freeze.
6. **SB-R07-051** — operational factual-review integration.

Then pull dependency-ready SB-R07 artifacts from `ARTIFACT_INDEX.json` and `RECOVERY_TO_V07.md`.

## Independent Acceptance

`claude/social-bots-mac-qa-control` is review-only. When SB-R07-071 lands, independently execute the concurrency race and verify exactly one durable record wins for a duplicate session ID; then audit SB-R07-041 when explicitly assigned. No runtime source edits.

## Hard gates

- **SB-R07-043 live five-call adaptive divergence is BLOCKED** until fresh explicit owner authorization **and** a matching canonical lead authorization manifest exist.
- `SB-V04-002` / `SB-V04-004` remain blocked and `SB-EVD-002` remains withheld until that causal evidence exists.
- V0.7 native scheduler acceptance still requires real owner-controlled persistent-host OS-scheduler evidence over repeated bounded sessions; chat liveness and fixtures do not count.
- `worker-pc` remains outside the critical path until private-repo clone/auth is demonstrably fixed.

## Legacy branches

- Core: PARKED evidence-only.
- Intelligence: PARKED evidence-only; SB-V15-001 remains changes-required.
- Acceptance: REVIEW-ONLY standby.
- Live canary: FROZEN evidence preservation; no additional live calls.

Do not start overlapping source ownership on legacy branches while Cursor recovery is active unless a later canonical lead review explicitly reassigns a separate non-overlapping task.