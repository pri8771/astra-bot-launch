# Claude execution contract — current state through V0.7

Owner direction: Claude is the primary implementation worker. ChatGPT lead should stay ahead on planning, architecture, independent review, acceptance and downstream task decomposition rather than duplicating routine implementation.

Repository: `pri8771/astra-bot-launch`  
Canonical coordination branch: `chatgpt/social-bots-plan-20260920`

Repository truth always outranks this file if later lead evidence changes a status.

## Session start

At the beginning of every fresh Claude worker session:

1. `git fetch --all --prune`.
2. Read:
   - `social-bots/STATE.json`
   - `social-bots/ARTIFACT_INDEX.json`
   - `social-bots/MILESTONE_MANIFEST.md`
   - `social-bots/VERSION_ROADMAP.md`
   - `social-bots/WORK_QUEUE.md`
   - `social-bots/SESSION_ROUTER.md`
   - `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
   - latest `social-bots/lead-reviews/`
   - unread relevant tail of `social-bots/AGENT_MESSAGES.md`
   - any artifact packet named by the current assignment.
3. Inspect current worker branch evidence/diffs before claiming status.
4. Emit exactly **one** durable session heartbeat using the `SESSION_ONCE` policy.
5. Begin work immediately.

Do not run a recurring heartbeat loop.

## Current official phase

V0.3 is accepted/closed.

Official phase: **V0.4.x / V0.4 in progress**.

Accepted:
- SB-V04-001
- SB-V04-003
- SB-V04-005
- SB-V05-001

Blocked/withheld:
- SB-V04-002 — BLOCKED_OWNER_AUTHORIZATION
- SB-V04-004 — BLOCKED_OWNER_AUTHORIZATION
- SB-EVD-002 — WITHHELD until V04-002/V04-004 are accepted

No additional adaptive/model call is currently authorized.

The accepted first V0.4 canary remains valid SB-V04-005 evidence.
The later unauthorized second live call is permanently excluded from acceptance evidence.

## Implementation order

### Phase A — make V0.4 execution-ready without a model call

Core-owned work may proceed now:

1. Build the five-case prepare-only divergence matrix defined in `V04_DIVERGENCE_ACCEPTANCE_PLAN.md`:
   - social-a / E1
   - social-b / same E1
   - social-c / same E1
   - cultural/Primandir / same E1
   - social-a / E2
2. Emit immutable bounded context JSON per case.
3. Emit SHA-256 for:
   - captured evidence bytes/receipt;
   - bounded context JSON;
   - exact production prompt.
4. Automatically prove single-variable isolation.
5. Add proposal/receipt validation and material-divergence reporting.
6. Add a hard lead-created authorization-manifest requirement.
7. Add exact call-budget enforcement and atomic pre-spawn accounting.
8. Add no-retry semantics.
9. Missing/invalid/exhausted authorization must fail closed before spawning Claude.
10. Tests may use fixtures/injected runners but must label them engineering-only.

**Do not execute a live Claude/adaptive provider call.**

Submit source/tests/report and state honestly that empirical V0.4 acceptance remains owner-authorization-blocked.

### Phase B — dependency-safe V0.7 engineering can run in parallel

SB-V07-001 is READY because V0.3 is accepted.

Build:
- bounded worker-once entrypoint;
- safe one-task claim;
- invocation receipt schema;
- OS scheduler adapters/runbooks;
- crash-safe/no-overlap behavior;
- Git fetch/read-assignment/acknowledgement flow;
- session-once durable heartbeat that works even without `gh`;
- best-effort Issue #3 visibility;
- local durable evidence first, remote visibility second;
- zero-live-model test harness.

Preferred scheduling targets:
- Windows Task Scheduler;
- Linux systemd timer;
- macOS launchd if useful.

One real owner-authorized host is sufficient for V0.7 acceptance.

### Phase C — Intelligence/evidence work

Follow current lane ownership and lead status.

Immediate known work:
- close SB-V15-001 structural admin boundary;
- finish SB-V05-002 evidence/factual-support trust boundary;
- create/implement missing V0.5 artifact packets for:
  - SB-V05-003 platform-native formatting/repair;
  - SB-V05-004 cultural-review evidence binding;
  - SB-V05-005 current-source evidence bundle.

Do not cross-edit another active lane's source without reconciling ownership first.

### Owner gate — V0.4 empirical batch

Do not execute until BOTH exist:
1. fresh explicit owner authorization; and
2. lead-created canonical scope-specific authorization manifest.

Then exactly one designated lane runs the fixed five-call batch.

Rules:
- subscription-authenticated Claude Code provider only;
- ANTHROPIC_API_KEY absent;
- no injected runner;
- same provider/model config across batch;
- no public effect;
- exactly five maximum calls;
- no automatic retry;
- persist context/prompt/provider/output hashes/receipts;
- do not use the unauthorized second historical call.

Worker submits results; ChatGPT lead accepts or rejects V04-002/V04-004 and then independently owns SB-EVD-002.

### Phase D — V0.5 closure

Close:
- SB-V05-002
- SB-V05-003
- SB-V05-004
- SB-V05-005

Operational evidence must be real where the artifact contract requires it.
Model-backed evidence requires its own bounded authorization manifest.

### Phase E — V0.6 dry runs

Only after canonical dependencies permit operational execution:

For each of social-a, social-b and social-c perform one bounded dry run:

observe
-> orient
-> real adaptive reasoning
-> choose
-> create
-> factual review
-> voice review
-> platform review
-> experiment registration
-> persisted learning
-> schedule next check

Requirements:
- real newly acquired current evidence;
- zero public publication;
- no fake operational evidence;
- attributable final-candidate review;
- complete run manifest;
- exact model-call accounting;
- no automatic retry.

Required artifacts:
- SB-V06-001
- SB-V06-002
- SB-V06-003
- SB-V06-004
- SB-V06-005

Before live/model-backed dry runs, generate an exact maximum model-call plan and wait for explicit owner + lead authorization if no applicable manifest exists.

### Phase F — V0.7 operational proof

Engineering may be built earlier, but operational promotion follows the version gates.

On one owner-authorized always-on host prove:
1. OS scheduler launches bounded worker sessions without a chat staying awake.
2. Every scheduled session emits exactly one durable session heartbeat.
3. Worker claims at most one task.
4. No-overlap/lease behavior holds.
5. Worker writes invocation receipt and exits.
6. Crash/restart/stale-takeover behavior is proven.
7. Worker consumes new ChatGPT lead direction from GitHub without owner copy/paste.
8. Complete two real cycles:
   - Claude session -> artifact/evidence -> ChatGPT review/new direction
   - later scheduled Claude session -> consumes new direction -> artifact/evidence
9. No public social effect is needed for V0.7.

Required artifacts:
- SB-V07-001
- SB-V07-002
- SB-V07-003
- SB-V07-004
- SB-V07-005

Only ChatGPT lead marks V0.7 complete.

## Working behavior

- Work artifacts, not vague goals.
- If a dependency blocks one artifact, move to a dependency-safe assigned artifact instead of idling.
- Reuse existing libraries/infrastructure before building substitutes.
- Keep Social Bots independent of SwarmAI.
- Keep deterministic policy in charge of authority/effects.
- Do not interpret passing unit tests as milestone acceptance.
- Push exact source SHA, exact commands/tests, evidence refs, limitations and requested `SUBMITTED` state.
- Do not self-mark `ACCEPTED`.

## Safety

No public posting/replies/messages, PAYG/API fallback/new spend, credential exposure, destructive actions, engagement manipulation, fake evidence or SwarmAI dependency unless a later explicit owner authorization changes the relevant gate.
