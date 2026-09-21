## Priority Zero — real V0.4 canary

V0.4 is NOT complete from implementation/tests alone.

Required before V0.4 promotion:
- `SB-V04-005` — one real current public source -> actual Claude Code subscription adaptive call -> validated proposal -> deterministic policy -> persisted local decision -> zero public effect.
- `SB-EVD-002` — independent ChatGPT audit/acceptance.

Dedicated branch prepared:
`claude/social-bots-v04-live-canary`

Owner authorization is already present for **one bounded existing-subscription canary call at zero additional spend**. Anthropic API/PAYG use is not authorized. The remaining execution gates are genuine heartbeat validation and an actually authenticated Claude Code subscription host.

Execution order:
1. finish current two-Mac-target heartbeat validation with durable real intervals;
2. lead acknowledges the valid bootstrap;
3. repurpose Mac QA session to the dedicated canary branch;
4. if that execution environment is not subscription-authenticated, run the canary branch from another authorized authenticated host rather than faking evidence;
5. run exactly one real canary;
6. lead audits it as `SB-EVD-002`;
7. only then may V0.4 be called complete, subject to the rest of the V0.4 manifest.

Intelligence may continue non-overlapping repair work in parallel, but later-version implementation does not advance the official version past V0.4 without the real canary.

# Work queue

Artifact-first, pull-driven coordination is active.

Canonical lead review: `lead-reviews/LEAD-020_2026-09-20T2251.md`.

Workers should pull their own branch and read `social-bots/SESSION_INSTRUCTIONS.md`. See `SESSION_ROUTER.md` and `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`.

## Heartbeat validation — current truth

Neither target lane has passed bootstrap.

### Intelligence / Evidence
Branch: `claude/social-bots-intelligence-repair-v2`

Source progress is real through signed head `feb30f4c3fd00ae1fa0bb115a92bdb767ae9f67d`, but `worker-reports/intelligence-repair/HEARTBEAT_LOG.jsonl` contains only the seed sequence 0 record. The sequence-4 snapshot does not count as missing durable history.

- verified consecutive ~15m worker intervals: **0**
- steady hourly authorized: **false**
- do not backfill heartbeat history

### Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`

Worker activity is real through signed head `ede387e256be19d6aaaf1e6c96151d7218221d33`, but heartbeat seq 1-4 are burst updates at 02:35:33Z, 02:37:49Z, 02:41:13Z and 02:42:30Z, not three consecutive ~15-minute intervals.

- verified consecutive ~15m worker intervals: **0**
- steady hourly authorized: **false**
- do not backfill heartbeat history
- current worker evidence says Linux container / no usable subscription OAuth; lane name alone is not Mac-host proof

## Session A — Windows Core / Host

Branch: `claude/social-bots-windows-core-host`

Status: **STANDBY by owner/lead during the two-Mac-target heartbeat validation.**

Do not assign new Windows work in this phase. Preserve branch state.

Canonical correctness note: `SB-V03-004` is **CHANGES_REQUIRED** per LEAD-019 until side-effectful legacy migration writes are ownership-fenced; `SB-V03-005` remains CHANGES_REQUIRED and `SB-V03-006` remains BLOCKED. Do not rely on older optimistic labels.

## Session B — Intelligence / Evidence

Branch: `claude/social-bots-intelligence-repair-v2`

Verified head: `feb30f4c3fd00ae1fa0bb115a92bdb767ae9f67d`.

Lead dispositions this review:
- `SB-V13-001` — ACCEPTED engineering artifact.
- `SB-V14-001` — ACCEPTED engineering artifact.
- `SB-V05-001` — CHANGES_REQUIRED.
- `SB-V05-002` — CHANGES_REQUIRED / fail-closed pending accepted semantic-provider integration.
- `SB-V15-001` — CHANGES_REQUIRED.
- `SB-V16-001`, `SB-V17-001`, `SB-V20-002` — remain CHANGES_REQUIRED pending deeper independent source audit; worker submission/tests alone are not acceptance.

Next:
1. repair `SB-V05-001`: current HTTPS live path passes unsupported `server_hostname` to `http.client.HTTPSConnection`; implement valid pinned-IP TLS with hostname SNI/certificate verification and add a regression exercising the real connection-construction path;
2. repair `SB-V15-001`: provide authoritative bot+persona production experiment readers/writers so normal persona reads cannot enumerate another workspace’s private experiment state;
3. append genuine prospective heartbeat history at approximately 15-minute cadence; do not synthesize/backfill missing records;
4. hold additional higher-version expansion until V05/V15 repairs and pending V16/V17/V20-002 audits are reconciled.

Do not edit Core state/decision/reasoning/leasing/worker.

## Session C — Mac QA / Integration Control

Branch: `claude/social-bots-mac-qa-control`

Lead dispositions:
- `SB-CTL-012` — ACCEPTED. Artifact graph validator/readiness reporter independently reviewed.
- `SB-CTL-006` — ACCEPTED. GitHub-hosted CI independently verified; workflow run `35555060783` succeeded at `ede387e...`.
- V2 acceptance harness prep is useful but does **not** promote `SB-V20-099`.

Next:
1. stay on this branch until three consecutive real approximately-15-minute worker heartbeat intervals are present in `HEARTBEAT_LOG.jsonl`;
2. no burst heartbeats and no backfill;
3. wait for lead acknowledgement setting `steady_hourly_authorized=true`;
4. then switch to `claude/social-bots-v04-live-canary` and execute `SB-V04-005` before ordinary QA/CI expansion resumes;
5. if the current environment still lacks actual Claude Code subscription authentication, stop the canary truthfully and move execution to an authorized authenticated host. Owner permission for the bounded zero-additional-spend call is already granted.

No runtime source edits in the QA lane except on the dedicated canary branch as required by its packet.

## Current version

**V0.3.x**.

V0.3 still requires final V03 fencing/isolation reconciliation and a fresh V03-006 bundle. V0.4 is additionally hard-gated by the real canary and independent acceptance.

`SB-V20-099` is not engineering-ready yet. Operational V2.0 remains separately gated by real account/public/measurement evidence.

## Concurrency

Do not start a fourth worker. Current phase is two active target lanes plus ChatGPT lead; Windows remains standby.

## Authority

No public posting/replies/messages, purchases, paid APIs/additional spend, destructive actions, credentials/secrets, fake operational evidence, engagement manipulation or SwarmAI dependency.
