# Cursor Recovery — SESSION_INSTRUCTIONS — LEAD-046

You are the primary Social Bots implementation lane for the existing recovery runtime surfaces.

Branch: `cursor/social-bots-recovery-v07-20260921`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Official phase: **V0.4.x / V0.4 in progress**

Before editing, sync/fetch and read current canonical coordination:
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/ARTIFACT_INDEX.json`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- latest `social-bots/AGENT_MESSAGES.md`
- `social-bots/artifact-packets/recovery-v07/SB-R07-041.md`

## Session start

Start a genuinely fresh implementation session and emit exactly one real durable `SESSION_ONCE` heartbeat for the new session ID after reading current coordination. Do not run a periodic heartbeat loop.

## Immediate and only released implementation — SB-R07-041

`SB-R07-041` remains **CHANGES_REQUIRED**.

Repair the direct/ad-hoc `ModelReasoningProvider` registered-callable route so **every live-capable route fails closed without a valid canonical authorization manifest**, even when `worker_once` / `run_worker` and other normal entrypoints are bypassed.

Required proof:
1. construct the direct-library `SBOTS_REASONING=model` route;
2. register a harmless local sentinel/counter callable;
3. with no valid canonical authorization manifest, prove the provider refuses **before** invoking the sentinel;
4. retain the inherited Claude CLI real-spawn authorization guard;
5. add focused adversarial regression coverage for the direct-library bypass;
6. run focused tests and the full suite;
7. push exact source/report evidence and request `SUBMITTED` only — do not self-accept.

**Zero real model/provider calls.** The sentinel must be local and harmless.

## Preserve submitted evidence

- `SB-R07-071` remains SUBMITTED pending independent Mac Acceptance multiprocess execution. Do not rewrite it unless the independent review identifies a defect.
- Preserve `SB-R07-044`, `SB-R07-072`, and later recovery engineering submissions for review.
- Do not install or claim the V0.7 LIVE scheduler on the current unsuitable Cursor host.
- Do not edit Fable's submitted new-files-only specialist/strategy source unless a later explicit lead reassignment says otherwise.

After the bounded R07-041 repair is pushed, pause overlapping runtime expansion while Acceptance independently reviews R07-071 and repaired R07-041.

## Hard authority limits

No live Claude/adaptive/model call, public posting/reply/message, account action, PAYG/new spend, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, or SwarmAI dependency is authorized.
