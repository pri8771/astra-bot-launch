# SESSION_INSTRUCTIONS — Acceptance / Independent Review Lane

Mode: **LEAD-045 — INDEPENDENT R07-071 -> R07-041 -> S23-008**  
Branch: `claude/social-bots-mac-qa-control`

Canonical coordination is `chatgpt/social-bots-plan-20260920`. Primary existing-runtime implementation remains `cursor/social-bots-recovery-v07-20260921`. Fable's new-files-only V2.3 batch is submitted and paused for review.

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
5. report exact commands, host/OS scope, results, source SHA, and limits. Do not broaden a POSIX/single-filesystem result into Windows/cross-host acceptance.

Submit PASS/FAIL evidence. If a material defect is found, stop that target and report it precisely.

## Review target 2 — repaired SB-R07-041

Only after Cursor pushes the LEAD-045 bounded repair.

Independently audit the repaired direct-library path:
- register a harmless sentinel callable;
- select `SBOTS_REASONING=model`;
- bypass `worker_once` / `run_worker`;
- prove the sentinel cannot execute without a valid canonical authorization manifest;
- confirm the Claude CLI real-spawn guard still fails closed too.

**Do not execute any real model/provider call.**

## Review target 3 — Fable SB-S23-008 fixture lifecycle evidence

After the immediate R07 targets are complete or blocked on a missing Cursor repair, independently rerun/audit Fable's submitted fixture lifecycle evidence at:
- source: `e33de096c7da2633376794b3297d82b320f6229d`
- evidence commit: `bbbb7b2df473a61c029a3098361cd0a084577d38`

Required checks:
1. inspect the specialist lifecycle/integrator/budget/sandbox source actually used by the proof;
2. rerun the focused acceptance proof and relevant unit suite on the pinned source;
3. verify fixture classification, no provider/model call, no public/account effect, no child authority escape, lease/fence handling, cleanup, and tamper rejection;
4. report exact commands/results and the real scope limits (in-process/thread-based, POSIX/single-host unless independently shown otherwise).

A green fixture rerun is engineering acceptance evidence only; it cannot promote operational V2.3.

Canary evidence remains frozen. No additional Claude CLI/adaptive/model call is authorized. No public effects, account actions, PAYG/new spend, destructive actions, credential exposure, fabricated evidence, engagement manipulation, or SwarmAI dependency.
