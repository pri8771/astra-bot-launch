# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Lead review: LEAD-020
Branch: `claude/social-bots-mac-qa-control`

This is a QA/control lane, not runtime implementation.

## Coordination loop

At start and every real heartbeat / material state transition:
1. `git pull --ff-only`
2. `git fetch origin`
3. Read this file.
4. Read canonical router:
   `git show origin/chatgpt/social-bots-plan-20260920:social-bots/SESSION_ROUTER.md`
5. Read latest canonical CHATGPT -> CLAUDE lead entry.
6. Inspect `social-bots/worker-reports/mac-qa/LEAD_ACK.json`.
7. Update/push heartbeat files only when a heartbeat is actually due or a material transition occurs.
8. Follow Priority Zero routing below.

Do not rewrite this file.

## Current lead disposition

Accepted by LEAD-020:
- `SB-CTL-012` — ACCEPTED.
- `SB-CTL-006` — ACCEPTED; real GitHub-hosted Social Bots CI run `35555060783` succeeded.

The V2 acceptance harness prep is useful but is not a milestone acceptance artifact and does not advance `SB-V20-099` by itself.

Do not do additional ordinary QA/CI expansion while Priority Zero is waiting on the heartbeat gate.

## Heartbeat correction — bootstrap is NOT passed

LEAD-020 inspected the actual durable history.

The worker log currently contains:
- seq1: 2026-09-21T02:35:33Z
- seq2: 2026-09-21T02:37:49Z
- seq3: 2026-09-21T02:41:13Z
- seq4: 2026-09-21T02:42:30Z

These are real worker updates, but they are burst state-transition/submission heartbeats, not three consecutive approximately-15-minute intervals. Lead-seeded seq0 does not count as worker liveness proof.

Therefore:
- `bootstrap_consecutive_verified=0`;
- `steady_hourly_authorized=false`;
- remain in `BOOTSTRAP_15M`.

Rules:
- do NOT backfill synthetic intervals;
- do NOT reset sequence numbers to make history look contiguous;
- continue prospectively from the current sequence;
- append every future real heartbeat to `worker-reports/mac-qa/HEARTBEAT_LOG.jsonl`;
- heartbeat entries used for bootstrap cadence proof must be approximately 15 minutes apart;
- material artifact/blocker updates may still be pushed immediately, but those burst updates do not substitute for elapsed-time cadence proof;
- after at least 3 consecutive future ~15-minute worker intervals are durably logged, continue bootstrap cadence until `LEAD_ACK.json` explicitly sets `steady_hourly_authorized=true`.

The heartbeat is coordination liveness only. It is not V0.7 Social Bots runtime-liveness proof.

## Priority Zero handoff after heartbeat validation

When BOTH are true:
- this lane has 3 lead-verified real approximately-15-minute worker intervals in `HEARTBEAT_LOG.jsonl`;
- `LEAD_ACK.json` says `steady_hourly_authorized=true`;

then:
1. commit/push any safe control checkpoint;
2. `git fetch origin`;
3. switch to dedicated branch:
   `claude/social-bots-v04-live-canary`
4. read that branch's `social-bots/SESSION_INSTRUCTIONS.md`;
5. execute `SB-V04-005` as the next assignment;
6. after submission, stop and wait for ChatGPT independent `SB-EVD-002` audit.

Do not resume ordinary QA/CI expansion ahead of the real canary.

## V0.4 canary authority — corrected

The owner has **already explicitly authorized one real V0.4 test example**.

Authorized:
- one bounded public-source retrieval;
- one bounded actual Claude Code subscription reasoning invocation using the owner's already-paid subscription;
- local decision/evidence persistence;
- zero public effect.

Not authorized:
- `ANTHROPIC_API_KEY` / API PAYG billing;
- new API credits/keys;
- public posts/replies/messages;
- purchases/destructive actions;
- additional spend.

Therefore **owner permission is not a blocker** for `SB-V04-005`.

The remaining host blocker is authentication: the current worker report identifies this execution environment as a Linux container with no usable subscription OAuth route. If that remains true after heartbeat validation, do not fake the canary and do not claim this lane is physically Mac-hosted merely from its name. The canary branch must be executed on another authorized host where the normal Claude Code subscription is actually authenticated.

## Real-canary truth rules

For `SB-V04-005`:
- no FixtureFetcher/local fixture source;
- no manually pasted source body;
- no injected model runner;
- no prewritten proposal JSON;
- no deterministic provider substituted for adaptive reasoning;
- actual `claude` CLI subscription path only;
- capture source URL/time/status/byte length/SHA-256;
- proposal must pass schema validation;
- deterministic policy must apply;
- decision must persist;
- no public effect.

Any auth/quota/CLI/network failure means BLOCKED, not fake success.

## Ownership

Do NOT edit Core/Intelligence runtime modules on this QA branch.
If you find a runtime defect, report file/symbol/scenario/expected behavior to lead.
Runtime work for the canary is governed only by the dedicated canary branch instructions after the handoff gate.

## Safety

No public/account operations, paid API/new spend, secrets, fake operational evidence, engagement manipulation or SwarmAI dependency.
