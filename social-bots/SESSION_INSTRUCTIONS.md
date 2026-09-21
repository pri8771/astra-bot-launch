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

## Heartbeat / lead coordination

Read `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`.

This lane starts in `BOOTSTRAP_15M` mode.

While this Claude session is active:
- check in every 15 minutes for the bootstrap phase, even if the current artifact has not finished;
- after each parent-artifact submission or blocker, check in immediately instead of waiting;
- after 3 consecutive approximately-15-minute heartbeats, REMAIN on 15-minute cadence until `social-bots/worker-reports/mac-qa/LEAD_ACK.json` says `steady_hourly_authorized=true`;
- once authorized, switch to hourly check-ins;
- do not exit merely because one artifact finished: pull instructions and take the next dependency-ready assignment unless blocked or explicitly told to stop.

For every heartbeat:
1. pull/fetch your branch;
2. re-read this SESSION_INSTRUCTIONS file;
3. inspect `social-bots/worker-reports/mac-qa/LEAD_ACK.json`;
4. run the heartbeat helper;
5. append the generated record to `social-bots/worker-reports/mac-qa/HEARTBEAT_LOG.jsonl`;
6. commit and push the heartbeat files;
7. set a notification reason for any new submission, blocker, completed artifact, changed assignment, or important finding.

Use:
`social-bots/bin/worker_heartbeat.py`

The heartbeat is a GitHub coordination signal, not proof of artifact correctness.

If the lead updates this file between heartbeats, follow the newest pulled version.



Path:
`social-bots/worker-reports/mac-qa/HEARTBEAT.json`.

## Safety

No runtime feature implementation, public/account operations, paid API/new spend, secrets, fake operational evidence or SwarmAI dependency.
