# SESSION_INSTRUCTIONS — Acceptance / Independent Review Lane

Mode: **LEAD-042 — INDEPENDENT R07-071 EXECUTION -> R07-041 AUDIT**  
Branch: `claude/social-bots-mac-qa-control`

Canonical coordination is `chatgpt/social-bots-plan-20260920`. Primary implementation remains `cursor/social-bots-recovery-v07-20260921`.

## Session start

Start one genuinely fresh review session, sync current canonical/recovery refs, and emit exactly one real durable `SESSION_ONCE` heartbeat. Do not run a periodic heartbeat soak.

## Review target 1 — SB-R07-071

No runtime/source edits.

Independently execute the submitted implementation at source SHA:
`0c74336b793189b4ba32d1f1229de0fb4d3e5ebb`

Required checks:
1. inspect `runtime/session_heartbeat.py` and verify duplicate check + durable append are in one exclusive cross-process critical section;
2. execute the real cross-process duplicate-session race, not a mocked/thread-only substitute;
3. verify exactly one durable heartbeat wins and all other same-session processes are refused;
4. verify the durable ledger contains exactly one record for each raced session id;
5. report exact commands, host/OS scope, results, source SHA, and any limitation. Do not broaden a POSIX/single-filesystem result into Windows/cross-host acceptance.

Submit PASS/FAIL evidence and stop for lead acceptance if a material defect is found.

## Review target 2 — repaired SB-R07-041

Only after Cursor pushes the bounded LEAD-042 repair.

Lead found a real defect in source `21cc2e7...`: `ModelReasoningProvider` can invoke a process-registered `_MODEL_CALLABLE` without a canonical live-authorization manifest when direct/ad-hoc code bypasses `worker_once` / `run_worker`.

Independently audit the repaired source by constructing the direct-library path:
- register a callable;
- select `SBOTS_REASONING=model`;
- bypass worker entrypoints;
- prove the callable cannot execute without a valid canonical manifest;
- confirm the Claude CLI real-spawn guard still fails closed too.

**Do not execute any real model/provider call.** Use a sentinel/counter callable that proves invocation/non-invocation locally without external inference.

After these two targets, audit R07-044/R07-072 only if explicitly dependency-ready; no runtime implementation edits.

Canary evidence remains frozen. No additional Claude CLI/adaptive/model call is authorized. No public effects, PAYG/new spend, destructive actions, credential exposure, fabricated evidence, engagement manipulation, or SwarmAI dependency.
