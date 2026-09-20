# Work queue

Priority is strict unless a task is blocked by an external gate; then continue the next independent ready task.

## SB-001 — Evidence and reuse reconciliation
Owner: Claude
Status: PARTIAL — lead rejected completion because standalone reuse-pool repos were not inspected; repair in SB-R1.

Goal: inspect current repos/assets/accounts and produce `SOURCE_REUSE_MAP.md`.

Acceptance:
- current repo refs recorded;
- old venture assets classified reusable/historical/irrelevant;
- current account aliases/emails identified without secrets where accessible;
- no September status treated as current without evidence;
- no source mutation outside the coordination branch.

## SB-002 — Worker/heartbeat bootstrap
Owner: Claude
Status: PARTIAL ACCEPT — worker primitives verified in-session; always-on-host deployment remains open.

Goal: establish the supported no-additional-spend Claude recurring worker on an authorized existing host.

Acceptance:
- one atomic execution lease;
- worker heartbeat emitted by running process;
- two actual invocation receipts;
- stale-lock recovery test;
- overlap attempt rejected;
- resumable state;
- no public side effect;
- exact install/scheduler/runner evidence committed as sanitized receipts.

## SB-003 — Persona/state contracts
Owner: Claude
Status: PROVISIONALLY ACCEPTED BY LEAD — 3 distinct general personas + 2 cultural workspaces; distinctness test green.

Goal: create three general persona specs plus two isolated cultural persona workspaces, without fabricated human identities.

Acceptance:
- each has goal, audience, voice constraints, success metric, memory namespace, experiment namespace and correction policy;
- distinctness test catches overly similar voices;
- cultural personas include source/cultural review requirement.

## SB-004 — Autonomous decision loop
Owner: Claude
Status: CHANGES REQUIRED — isolation/safety mechanics exist, but alternative generation and scoring are hard-coded rather than the requested adaptive autonomous thinking. Repair in SB-R1.

Goal: implement Observe -> Orient -> Generate -> Score -> Choose -> Execute -> Verify -> Learn -> Schedule with explicit reason records and bounded authority.

Acceptance:
- separate state per bot/persona;
- deterministic no-change path;
- bounded retries;
- uncertain-effect reconciliation;
- crash/restart test;
- no-overlap test.

## SB-005 — Browser/account map
Owner: Claude
Status: PARTIAL — metadata map exists; no live account verification yet.

Goal: reuse existing accounts/emails and document exact safe setup for TikTok, Reddit, X, Instagram and Facebook.

Acceptance:
- alias/login method/profile/workspace/last verification recorded;
- private credential references only;
- exact MFA/CAPTCHA/consent blocker;
- no public posting;
- supported route documented instead of bypasses.

## SB-006 — Content/experiment pipeline
Owner: Claude
Status: CHANGES REQUIRED — factual review only checks source presence and platform-fit acceptance is incomplete. Repair in SB-R1.

Goal: real research -> persona ideation -> reviewed candidate -> platform formatting -> experiment registration -> observation plan.

Acceptance:
- no operational mock data;
- source capture;
- factual/cultural review hooks;
- dedup;
- analytics event schema;
- publish queue defaults disabled.

## SB-007 — Three real dry-run cycles
Owner: Claude
Status: CHANGES REQUIRED — hard-coded inputs labeled live-capture are not sufficient proof; Social-A passes despite platform-limit failure; independent review receipt missing. Repair in SB-R1.

Goal: one end-to-end non-publishing cycle per general persona using current research inputs.

Acceptance:
- current source evidence;
- autonomous topic choice with reason record;
- candidate packet;
- experiment hypothesis/criteria;
- persisted learning;
- next scheduled check;
- independent review receipt.

## SB-008 — Launch gate packet
Owner: Claude
Status: PREPARED ONLY — not accepted as launch-ready until SB-R1 and host/account gates clear.

Goal: reduce each external blocker to one exact human action and prepare one canary per persona.

Acceptance:
- exact account destination;
- explicit required human step;
- no duplicate setup;
- no publish until authorization;
- rollback/readback/analytics plan ready.


## SB-R1 — Autonomous intelligence + live research repair
Owner: Claude
Status: READY — lead-assigned in PR #2 and AGENT_MESSAGES LEAD-003.

Goal: close the gaps found by independent lead audit without adding any SwarmAI dependency or public side effects.

Required work:
- Finish SB-001 using current standalone product-home evidence. Reconcile the missing/moved BidetFit source path instead of assuming the historical path is current.
- Add a SwarmAI-independent reasoning interface for changed-evidence cycles. Prefer an actually available no-additional-spend Claude/Claude Code host path. It must generate context-specific alternatives/rationale/estimates; deterministic code continues to own safety, authority, no-change, dedup, scheduling and verification. If no reasoning model is available, fail closed to NO_ACTION/BLOCKED rather than claim autonomy.
- Add real current-source acquisition with machine-verifiable capture receipts: URL/source, retrieval timestamp, status, content/response hash and provenance generated by the collector rather than caller-supplied.
- Strengthen factual review so source presence alone is insufficient.
- Produce platform-native candidates; do not accept a candidate merely because a formatter silently truncates an over-limit draft.
- Fix SB-007 pass criteria so any required platform/review check failure fails the run.
- Add attributable independent review evidence for the final three general-persona dry-run candidates.
- Rerun three general personas using newly acquired current evidence and preserve receipts.

Acceptance:
- alternatives/reasons differ when evidence/persona/objective differs;
- no changed evidence still follows deterministic NO_ACTION;
- real research capture can be independently traced and reproduced;
- false/unsupported or over-limit candidates do not pass;
- three reruns pass all explicit checks with independent review receipts;
- public posting/spend stay false;
- no SwarmAI imports/services/queues/model gateway/runtime dependency;
- tests include regressions for the lead findings.
