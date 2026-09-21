# Cursor recovery contract — get Social Bots to V0.7

Repository: `pri8771/astra-bot-launch`  
Implementation branch: `cursor/social-bots-recovery-v07-20260921`  
Canonical coordination: `chatgpt/social-bots-plan-20260920`

The implementation branch was created from the current best Core submission:
`claude/quirky-shannon-t1377u@918c42e2a4602589997a7c625d994e049f266d6d`.

## Start

1. Fetch all refs.
2. Confirm your branch/head ancestry.
3. Read:
   - social-bots/RECOVERY_TO_V07.md
   - social-bots/ARTIFACT_INDEX.json
   - social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md
   - latest lead review
   - every recovery packet before working it.
4. Emit exactly one SESSION_ONCE heartbeat for this fresh Cursor session under lane `cursor-recovery`.
5. Work artifacts, not vague phases.

## Rules

- Do not merge/cherry-pick blindly from other active branches after start. Inspect exact diffs first.
- One artifact per commit whenever practical.
- After each artifact: focused tests, relevant full suite, report/evidence, push, then continue.
- Do not wait for ChatGPT acceptance before starting another dependency-safe recovery artifact.
- Do not mark ACCEPTED.
- Never use fixture/replay/direct CLI demo as LIVE evidence.
- No public post/reply/message through V0.7.
- No PAYG/API-key fallback/new spend.
- No live adaptive/model call until BOTH fresh explicit owner authorization and a canonical lead authorization manifest exist.
- Keep Social Bots independent of SwarmAI.

## First work order

1. SB-R07-071
2. SB-R07-041
3. SB-R07-044
4. SB-R07-072
5. SB-R07-042
6. SB-R07-051
7. SB-R07-052
8. SB-R07-053
9. SB-R07-061
10. SB-R07-073 if host preflight passes
11. SB-R07-074
12. SB-R07-075
13. SB-R07-076
14. SB-R07-077

Then continue every dependency-safe item in RECOVERY_TO_V07.md. When the V0.4 live-call gate is the only blocker, report the exact required owner authorization and keep progressing host/evidence scaffolding rather than idling.
