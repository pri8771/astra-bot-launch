# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Lead review: LEAD-018
Branch: `claude/social-bots-mac-qa-control`

This is a QA/control lane, not runtime implementation.

## Coordination loop

At start and after every artifact:
1. `git pull --ff-only`
2. `git fetch origin`
3. Read this file.
4. Read canonical router:
   `git show origin/chatgpt/social-bots-plan-20260920:social-bots/SESSION_ROUTER.md`
5. Read latest canonical lead message.
6. Update/push `social-bots/worker-reports/mac-qa/HEARTBEAT.json`.
7. Continue.

Do not rewrite this file.

## Next 1 — SB-CTL-012

Build artifact graph validator/readiness reporter per:
`social-bots/artifact-packets/SB-CTL-012.md`

Validate:
- IDs/statuses/dependencies/cycles;
- manifest refs;
- packet/canonical refs when locally determinable;
- deterministic milestone blockers;
- V2 engineering-ready vs operational-promotion distinction.

Add unit tests for invalid/valid graphs.

## Next 2 — SB-CTL-006 CI

Mac QA owns CI/control now.

Implement GitHub Actions that:
- runs artifact validator;
- parses artifact JSON;
- runs Social Bots tests available on the branch/integration target;
- uses no secrets/network/model/deploy/public effect.

Do not edit runtime source to make CI pass.

## Next 3 — V2 acceptance harness prep

Prepare non-runtime fixtures/assertion helpers for `V2_ENGINEERING_ACCEPTANCE.md`.

Focus:
- evidence traceability;
- persona isolation;
- missing/stale evidence;
- authority blocks;
- fixture vs operational distinction;
- no-public-effect;
- strategy revision trace chain.

Do not fake an integrated passing system before merged runtime exists.

## Ownership

Do NOT edit Core/Intelligence runtime modules.
If you find a runtime defect, report file/symbol/scenario/expected behavior to lead.

## Heartbeat

Path:
`social-bots/worker-reports/mac-qa/HEARTBEAT.json`.

## Safety

No runtime feature implementation, public/account operations, paid API/new spend, secrets, fake operational evidence or SwarmAI dependency.
