# Active session router — LEAD-042 recovery topology

## Primary implementation lane — Cursor Recovery

Branch: `cursor/social-bots-recovery-v07-20260921`  
Current verified head: `d7ecb256d430f437f4ad9249480b6430af52ecf9`  
Current verified session: `s-20260921T191500Z-a23cc77e`  
Status: **ACTIVE / primary implementation lane**.

Immediate assignment:
1. Repair `SB-R07-041` only: the process-registered `SBOTS_REASONING=model` callable path must structurally fail closed without a valid canonical live-authorization manifest even when worker entrypoints are bypassed.
2. Add a direct-library adversarial regression proving the registered callable is not invoked without authorization.
3. No live/model call while repairing; push exact source/tests/report.

Existing recovery submissions:
- `SB-R07-071` source `0c74336b...`: SUBMITTED, awaiting independent Acceptance execution.
- `SB-R07-044` source `5179217e...`: SUBMITTED, pending audit.
- `SB-R07-072` source `7f59f915...`: SUBMITTED; current Cursor host is unsuitable for LIVE scheduler evidence.
- `SB-R07-042`, `051`, `052`, `053`, `061`: worker-reported submissions awaiting lead/independent audit; do not infer acceptance.

Do not install `SB-R07-073` on the current Cursor host. One fresh worker session emits one durable `SESSION_ONCE` heartbeat; do not run a periodic in-session soak.

## Legacy Claude Core

Branch: `claude/social-bots-windows-core-host`  
Status: PARKED / evidence preservation only.

Do not continue implementation here unless a later canonical lead review explicitly assigns a non-overlapping evidence/audit task.

## Legacy Intelligence

Branch: `claude/social-bots-intelligence-repair-v2`  
Status: PARKED / evidence preservation only.

`SB-V15-001` remains changes-required. Do not continue source edits on this branch during consolidated recovery unless explicitly reassigned.

## Acceptance / independent QA

Branch: `claude/social-bots-mac-qa-control`  
Status: **REVIEW-ONLY / STALE / ACTION REQUIRED**.

Start one fresh review session and emit exactly one `SESSION_ONCE` heartbeat. No runtime/source edits.

Order:
1. Independently execute `SB-R07-071` against submitted source `0c74336b793189b4ba32d1f1229de0fb4d3e5ebb`, including the real cross-process duplicate-session race; report exact commands/results and exactly-one-winner outcome.
2. After Cursor pushes the bounded `SB-R07-041` repair, independently audit the direct-library `SBOTS_REASONING=model` route with `worker_once` / `run_worker` bypassed and verify no registered callable can execute without a valid manifest.
3. Then audit `SB-R07-044` / `SB-R07-072` as explicitly assigned and capacity permits.

No model calls.

## Canary

Branch: `claude/social-bots-v04-live-canary`  
Status: FROZEN / evidence preservation only.

`SB-V04-005` remains accepted from the first authorized canary. No additional live call is authorized. The later historical duplicate call remains excluded from acceptance evidence.

## Live model gate

No live adaptive/model call is authorized. The future fixed five-call causal-divergence batch requires **both** fresh explicit owner authorization and a matching canonical lead-created authorization manifest before any provider process/callable may execute.

## Remote worker

`worker-pc` remains outside the critical path until private-repository clone/auth for `pri8771/astra-bot-launch` is demonstrably fixed. Do not redispatch merely because capacity is free.

## ChatGPT lead

Owns recovery artifact acceptance, owner-gate manifest creation after explicit authorization, milestone/version promotion, coordination truth, and the two-cycle V0.7 lead-direction proof.
