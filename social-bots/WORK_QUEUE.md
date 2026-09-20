# Work queue

This is the execution view of the artifact registry. `ARTIFACT_INDEX.json` is the durable machine-readable artifact state; `artifact-packets/` contains bounded execution contracts.

Priority is strict unless a task is blocked by an external gate; then continue the next independent ready artifact. Lead acceptance is evidence-gated; implementation self-reports do not close artifacts.

## SB-R0 — P1 correctness repairs
Owner: Claude
Status: READY — highest priority before further autonomy claims.

Execution split:
- `SB-R0A1` -> artifact `SB-V03-002` — signal-delta consumption/persistence — **SP3** — packet: `artifact-packets/SB-V03-002.md`
- `SB-R0A2` -> artifact `SB-V03-003` — failed-review stop semantics + regressions — **SP2** — packet: `artifact-packets/SB-V03-003.md`
- `SB-R0B1` -> artifact `SB-V03-004` — race-safe stale takeover — **SP5** — packet: `artifact-packets/SB-V03-004.md`
- `SB-R0B2` -> artifact `SB-V03-005` — shared-runtime persona state/lease isolation — **SP4**
- `SB-R0B3` -> artifact `SB-V03-006` — adversarial concurrency integration acceptance — **SP3**

Complete A1/A2 first. Push a reviewable checkpoint before B1/B2/B3. See `WORK_MANAGEMENT.md`.

Goal: fix the four correctness defects found by independent PR review on implementation commit `689cfe12ea4eed502e42b37d8e7305c77b3cb4aa`.

Required repairs:
- `research.new_signals` must process only evidence not already consumed; later or batched signals must not be lost when the fingerprint changes.
- A failed factual/voice/cultural review must stop experiment registration and must not enter a publish queue as a successful candidate.
- Stale-lease takeover must be conditionally atomic so two takeover contenders cannot both believe they own the task.
- Lease scope must cover shared runtime state, or state must be split per persona. General and cultural personas on one runtime must not concurrently overwrite one `bot_state.json`.

Acceptance:
- regression tests for a new signal arriving after an earlier cycle and for multiple signals arriving before one cycle;
- regression test proving a withheld cultural candidate cannot reach the publish queue or a successful worker receipt;
- adversarial concurrent stale-takeover test proving one owner only;
- concurrent general+cultural invocation test proving no shared-state race/lost update;
- no public side effect;
- all prior tests still pass;
- exact commit/test evidence returned for lead review.

Source review threads: PR #2 comments `4058061254`, `4058061259`, `4058061263`, `4058061265`.

## SB-001 — Evidence and reuse reconciliation
Owner: Claude
Status: PARTIAL — implementation inspected `astra-bot-launch` and `pri8771/bots`, but standalone reuse pools were not fully reconciled.

Goal: inspect current repos/assets/accounts and produce a current `SOURCE_REUSE_MAP.md`.

Acceptance:
- current repo refs recorded;
- standalone One Person Ops, CommerceLint, Wait How Big and the current BidetFit source location inspected where accessible;
- old venture assets classified reusable/historical/irrelevant;
- current account aliases/emails identified without secrets where accessible;
- no September status treated as current without evidence;
- no source mutation outside the authorized Social Bots implementation/coordination paths.

Lead evidence already available: One Person Ops current README, CommerceLint current README, Wait How Big handoff; the historical BidetFit README path returned 404 and must be reconciled rather than assumed current.

## SB-002 — Worker/heartbeat bootstrap
Owner: Claude
Status: PARTIAL ACCEPT — in-session worker primitives demonstrated; always-on deployment/liveness not verified. SB-R0 lease defects must also be fixed before the no-overlap guarantee is accepted.

Goal: establish the supported no-additional-spend recurring worker on an authorized existing host.

Verified so far:
- two in-session invocation receipts;
- process heartbeat evidence;
- simple overlap rejection;
- restart/resume demonstration.

Open acceptance:
- SB-R0 stale-takeover and shared-runtime concurrency fixes/tests;
- actual always-on authorized-host deployment;
- two host-side invocation receipts and fresh heartbeat from that host;
- stale-lock recovery/reconciliation on corrected lease implementation;
- no public side effect.

Last verified heartbeat: `2026-09-20T20:36:15+00:00`, status `done`, worker `w-vm-726-415fed`. This is terminal in-session evidence, not recurring liveness.

## SB-003 — Persona/state contracts
Owner: Claude
Status: PROVISIONALLY ACCEPTED BY LEAD.

Goal: maintain three distinct general personas plus two isolated cultural/Primandir persona workspaces without fabricated human identities.

Acceptance already evidenced directionally:
- goal/audience/voice/success-metric contracts exist;
- distinctness detector exists;
- cultural personas require source/cultural review.

Reopen if SB-R0 state isolation changes invalidate the persona namespace contract.

## SB-004 — Autonomous decision loop
Owner: Claude
Status: CHANGES REQUIRED.

Goal: implement real adaptive `OBSERVE -> ORIENT -> GENERATE -> SCORE -> CHOOSE -> EXECUTE -> VERIFY -> LEARN -> SCHEDULE` behavior.

Lead finding:
- current changed-evidence path uses a fixed three-action set and hard-coded scores, causing all three dry-runs to choose the same action for the same numeric reason.

Acceptance:
- keep deterministic no-change, safety, authority, dedup, scheduling, leases and verification;
- use a SwarmAI-independent, no-additional-spend reasoning path for interpretation/uncertain prioritization/creative generation when available;
- alternatives, estimates and reasons materially respond to persona, evidence, objective and state;
- if the reasoning model is unavailable, fail closed to `NO_ACTION`/`BLOCKED` rather than claim adaptive autonomy;
- bounded retries and attributable decision records;
- no SwarmAI import/service/queue/model-gateway/runtime dependency.

## SB-005 — Browser/account map
Owner: Claude
Status: PARTIAL — metadata map exists; no live account verification.

Goal: reuse existing accounts/emails and document exact safe setup for TikTok, Reddit, X, Instagram and Facebook.

Acceptance:
- alias/login method/profile/workspace/last verification recorded only when actually observed;
- private credential references only;
- exact MFA/CAPTCHA/consent blocker;
- no public posting;
- supported route documented instead of bypasses.

## SB-006 — Content/experiment pipeline
Owner: Claude
Status: CHANGES REQUIRED.

Goal: real research -> persona ideation -> factual/voice/cultural review -> platform-native candidate -> experiment registration -> disabled publish queue -> observation plan.

Lead findings:
- current fact check proves only source-reference presence, not claim support;
- platform formatter can truncate an over-limit draft while the dry-run still passes;
- cultural review failure currently does not stop experiment registration/enqueue.

Acceptance:
- source retrieval/capture evidence tied to candidate claims;
- factual support check stronger than URL presence;
- failed required review blocks downstream experiment/publish-queue success;
- platform-native candidate passes required limits/asset requirements without silent acceptance by truncation;
- dedup and analytics schema remain intact;
- publish queue defaults disabled.

## SB-007 — Three real dry-run cycles
Owner: Claude
Status: CHANGES REQUIRED.

Goal: one end-to-end non-publishing cycle per general persona using newly acquired current research evidence.

Lead findings:
- `bin/dry_run.py` embeds research constants and lets the caller label them `live-capture`; this does not prove acquisition;
- Social-A showed `within_platform_limit=false` while the run still passed;
- no attributable independent review receipt exists for the three final candidates.

Acceptance:
- machine-captured current-source receipt per input: source/URL, retrieval timestamp, status and content/response hash, with provenance set by the collector rather than caller input;
- autonomous topic choice with adaptive reason record after SB-004 repair;
- factual/policy/voice/platform checks all explicitly pass;
- any required-check failure fails the run;
- experiment hypothesis/criteria, persisted learning and next check recorded;
- attributable independent review receipt per final candidate;
- no external publication.

## SB-R1 — Autonomous intelligence + live research repair
Owner: Claude
Status: READY AFTER SB-R0 for shared code; SB-001 reuse reconciliation may proceed in parallel.

Goal: close SB-001/SB-004/SB-006/SB-007 gaps without adding a SwarmAI dependency or public side effects.

Deliverable:
- corrected autonomy/research/review implementation;
- real capture receipts;
- three rerun evidence packets;
- independent review evidence;
- updated implementation `STATE.json`, `WORK_QUEUE.md` and `AGENT_MESSAGES.md` with exact refs/tests.

## SB-008 — Launch gate packet
Owner: Claude
Status: PREPARED ONLY — not accepted as launch-ready until correctness, autonomy, research, host and account gates clear.

Goal: reduce each external blocker to one exact human action and prepare one canary per persona.

No canary/public action is authorized yet.


## Groomed follow-on implementation backlog

These are pre-groomed worker tasks so external gates or lead review do not leave Claude idle. Do not start a task whose dependencies are not satisfied.

### V0.4
- `SB-R1A` — exact-source reuse reconciliation — **SP1**
- `SB-R1B` -> artifact `SB-V04-001` — reasoning-provider interface + fail-closed contract — **SP3** — packet: `artifact-packets/SB-V04-001.md`
- `SB-R1C` — adaptive alternative generation/scoring — **SP5**
- `SB-R1D` — deterministic policy boundary around reasoning proposals — **SP4**
- `SB-R1E` — persona/evidence-divergence acceptance suite — **SP3**

### V0.5
- `SB-R2A` — machine-captured source receipt collector — **SP3**
- `SB-R2B` — claim-to-source factual support review — **SP4**
- `SB-R2C` — platform-native formatter/repair loop — **SP3**
- `SB-R2D` — cultural-review evidence binding — **SP2**

### V0.6
- `SB-R3A` — three real general-persona dry runs — **SP3**
- `SB-R3B` — independent reviewer receipt pipeline — **SP2**
- `SB-R3C` — dry-run evidence validator — **SP2**

### V0.7
- `SB-R4A` — authorized-host worker packaging/config — **SP3**
- `SB-R4B` — recurring host execution + heartbeat/receipt proof — **SP4**
- `SB-R4C` — ChatGPT-direction consumption/ack loop — **SP3**
- `SB-R4D` — crash/restart/no-overlap host acceptance — **SP4**

Story points follow `WORK_MANAGEMENT.md`. ChatGPT lead may refine/split these as evidence changes.
