# Active session router — LEAD-041 recovery topology

## Primary implementation lane — Cursor Recovery

Branch: `cursor/social-bots-recovery-v07-20260921`  
Inherited verified report history: `2f14a5cb08c9019fd174c1f54ecda130fa9308d4`  
Latest material source inside inherited history: `a73b7b58de8f3669795b81637bff55247d67943c`  
Lead assignment/ack head after transfer: `33355b4fc3067a9c5c16ad61e93b876e4ea296ef`  
Status: ASSIGNED / primary implementation lane; no fresh worker execution evidence yet at LEAD-041 cutoff.

Owns, in order:
1. `SB-R07-071` atomic cross-process `SESSION_ONCE` heartbeat uniqueness.
2. `SB-R07-041` audit/retain the inherited live-route fail-closed authorization hardening.
3. `SB-R07-044` divergence verifier.
4. `SB-R07-072` persistent-host preflight.
5. Dependency-ready no-live recovery artifacts from `RECOVERY_TO_V07.md` / `WORK_QUEUE.md`.

One fresh worker session emits one durable `SESSION_ONCE` heartbeat. Do not run a periodic in-session heartbeat soak.

## Legacy Claude Core

Branch: `claude/social-bots-windows-core-host`  
Status: PARKED / evidence preservation only.

The verified post-LEAD-040 Core descendant history was transferred into Cursor Recovery. Do not continue implementation here unless a later canonical lead review explicitly assigns a non-overlapping evidence/audit task.

## Legacy Intelligence

Branch: `claude/social-bots-intelligence-repair-v2`  
Status: PARKED / evidence preservation only.

`SB-V15-001` remains changes-required. Do not continue source edits on this branch during consolidated recovery unless explicitly reassigned.

## Acceptance / independent QA

Branch: `claude/social-bots-mac-qa-control`  
Status: REVIEW-ONLY STANDBY.

No runtime/source edits. First independent recovery target is `SB-R07-071` when submitted: execute the cross-process duplicate-session race and verify exactly one durable heartbeat wins. Then audit `SB-R07-041` as explicitly assigned.

## Canary

Branch: `claude/social-bots-v04-live-canary`  
Status: FROZEN / evidence preservation only.

`SB-V04-005` remains accepted from the first authorized canary. No additional live call is authorized. The later historical duplicate call remains excluded from acceptance evidence.

## Live model gate

No live adaptive/model call is authorized. The future fixed five-call causal-divergence batch requires **both** fresh explicit owner authorization and a matching canonical lead-created authorization manifest before any provider process may spawn.

## Remote worker

`worker-pc` remains outside the critical path until private-repository clone/auth for `pri8771/astra-bot-launch` is demonstrably fixed. Do not redispatch merely because capacity is free.

## ChatGPT lead

Owns recovery artifact acceptance, owner-gate manifest creation after explicit authorization, milestone/version promotion, coordination truth, and the two-cycle V0.7 lead-direction proof.