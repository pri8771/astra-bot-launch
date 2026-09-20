# Work queue

Priority is strict unless a task is blocked by an external gate; then continue the next independent ready task.

## SB-001 — Evidence and reuse reconciliation
Owner: Claude
Status: READY

Goal: inspect current repos/assets/accounts and produce `SOURCE_REUSE_MAP.md`.

Acceptance:
- current repo refs recorded;
- old venture assets classified reusable/historical/irrelevant;
- current account aliases/emails identified without secrets where accessible;
- no September status treated as current without evidence;
- no source mutation outside the coordination branch.

## SB-002 — Worker/heartbeat bootstrap
Owner: Claude
Status: READY after SB-001 local source paths are known

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
Status: READY

Goal: create three general persona specs plus two isolated cultural persona workspaces, without fabricated human identities.

Acceptance:
- each has goal, audience, voice constraints, success metric, memory namespace, experiment namespace and correction policy;
- distinctness test catches overly similar voices;
- cultural personas include source/cultural review requirement.

## SB-004 — Autonomous decision loop
Owner: Claude
Status: BLOCKED by SB-002/003

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
Status: READY after SB-001

Goal: reuse existing accounts/emails and document exact safe setup for TikTok, Reddit, X, Instagram and Facebook.

Acceptance:
- alias/login method/profile/workspace/last verification recorded;
- private credential references only;
- exact MFA/CAPTCHA/consent blocker;
- no public posting;
- supported route documented instead of bypasses.

## SB-006 — Content/experiment pipeline
Owner: Claude
Status: BLOCKED by SB-003/004

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
Status: BLOCKED by SB-006

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
Status: BLOCKED by account verification and owner authority

Goal: reduce each external blocker to one exact human action and prepare one canary per persona.

Acceptance:
- exact account destination;
- explicit required human step;
- no duplicate setup;
- no publish until authorization;
- rollback/readback/analytics plan ready.
