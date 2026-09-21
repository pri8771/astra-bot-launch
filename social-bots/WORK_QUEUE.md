# Work queue — LEAD-042 V0.7 recovery

Official phase remains **V0.4.x**. V0.3 is accepted/closed. No product-version promotion occurred in this review.

Primary recovery contract: `RECOVERY_TO_V07.md`.  
Primary implementation branch: `cursor/social-bots-recovery-v07-20260921`.  
Current verified recovery head: `d7ecb256d430f437f4ad9249480b6430af52ecf9`.  
Current recovery session: `s-20260921T191500Z-a23cc77e` with one durable `SESSION_ONCE` heartbeat.

## Verified recovery delta since LEAD-041

Cursor Recovery is no longer merely assigned: it is materially active and has pushed signed source/report commits.

- `SB-R07-071` source `0c74336b793189b4ba32d1f1229de0fb4d3e5ebb`: atomic `fcntl.flock` around duplicate check + append, real 8-process x 20-round race, worker-reported 314 passed / 1 skipped. **SUBMITTED; independent Acceptance execution required before lead acceptance.**
- `SB-R07-041` source `21cc2e7a65750d20dc609b9e9517f920157389a2`: real Claude CLI spawn-point guard improved, but **CHANGES_REQUIRED** because `ModelReasoningProvider` can invoke a process-registered `_MODEL_CALLABLE` without consulting the canonical live-authorization manifest when a direct/ad-hoc caller bypasses `worker_once` / `run_worker`.
- `SB-R07-044` source `5179217ea222e94caa5580104fbc6aaacd4b2192`: engineering-only divergence verifier; **SUBMITTED / pending audit**.
- `SB-R07-072` source `7f59f915b9f5bb60691d06215a463518fd4519c7`: current Cursor machine truthfully classified `UNSUITABLE_NOT_PERSISTENT_OWNER_HOST`; **SUBMITTED**. Do not install native scheduler there.
- Worker also reports later engineering submissions `SB-R07-042`, `SB-R07-051`, `SB-R07-052`, `SB-R07-053`, `SB-R07-061` with cumulative 416 passed / 2 skipped. They remain pending lead/independent audit and do not advance the official version.

## Primary Cursor recovery queue

IMMEDIATE / bounded:
1. **Repair SB-R07-041 only**: structurally guard the `SBOTS_REASONING=model` / registered model-callable route so it cannot execute a live-capable callable without the same canonical authorization manifest. Add a direct-library adversarial regression that bypasses worker entrypoints and proves zero callable invocation without authorization. No model call.
2. Push exact repair SHA, focused/full commands/results and evidence.
3. Preserve `SB-R07-071`, `SB-R07-044`, `SB-R07-072` submissions; do not self-accept them.
4. Do **not** run/install `SB-R07-073` on the current Cursor host because the preflight says it is not an owner-controlled persistent host.
5. Dependency-safe packaging/review of already-submitted Wave-1 artifacts may continue, but avoid new overlapping runtime expansion while Acceptance executes the immediate gates.

## Independent Acceptance

`claude/social-bots-mac-qa-control` remains review-only but is now **STALE / ACTION REQUIRED** because no worker QA commit followed LEAD-041.

Next review session:
1. emit exactly one real `SESSION_ONCE` heartbeat;
2. independently execute `SB-R07-071` against submitted source `0c74336b793189b4ba32d1f1229de0fb4d3e5ebb`, including the real cross-process duplicate-session race; report exact commands/results and whether exactly one durable record wins;
3. after Cursor submits the bounded `SB-R07-041` repair, independently audit the direct-library `model` route with worker entrypoints bypassed;
4. no runtime source edits and no model calls.

## Hard gates

- **SB-R07-043 live five-call adaptive divergence remains BLOCKED** until fresh explicit owner authorization **and** a matching canonical lead authorization manifest exist.
- `SB-V04-002` / `SB-V04-004` remain blocked and `SB-EVD-002` remains withheld until genuine controlled causal evidence exists.
- No additional Claude/adaptive/model call is authorized now.
- V0.7 native scheduler acceptance requires real owner-controlled persistent-host OS-scheduler evidence over repeated bounded sessions; the current Cursor host is explicitly unsuitable.
- `worker-pc` remains outside the critical path until private-repo clone/auth is demonstrably fixed.

## Legacy branches

- Core: PARKED evidence-only.
- Intelligence: PARKED evidence-only; `SB-V15-001` remains changes-required.
- Acceptance: REVIEW-ONLY, immediate independent R07-071 then repaired R07-041 audit.
- Live canary: FROZEN evidence preservation; no additional live calls.

## Heartbeat truth

Canonical heartbeat policy is **ONE SESSION = ONE HEARTBEAT**. The earlier FAST_5M / SOAK_15M_24H experiment is superseded. V0.7 recurring liveness is a sequence of independently native-OS-scheduled sessions, each with one heartbeat plus an invocation receipt; a kept-open chat is not scheduler evidence.
