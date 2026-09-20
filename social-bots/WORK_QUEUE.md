# Work queue

Priority is strict unless a task is blocked by an external gate; then continue the next independent ready task.

## SB-001 — Evidence and reuse reconciliation
Owner: Claude
Status: DONE — SOURCE_REUSE_MAP.md refreshed with pinned refs (astra @9f2f4d2, bots @7f2ec1a); reuse-pool repos flagged BLOCKED (not attached).

Goal: inspect current repos/assets/accounts and produce `SOURCE_REUSE_MAP.md`.

Acceptance:
- current repo refs recorded;
- old venture assets classified reusable/historical/irrelevant;
- current account aliases/emails identified without secrets where accessible;
- no September status treated as current without evidence;
- no source mutation outside the coordination branch.

## SB-002 — Worker/heartbeat bootstrap
Owner: Claude
Status: IMPLEMENTED + VERIFIED IN SESSION — receipts/evidence/SB-002-run (all_pass). Blocked only on owner always-on-host deploy (G1).

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
Status: DONE — 3 distinct general personas + 2 cultural workspaces; distinctness test green.

Goal: create three general persona specs plus two isolated cultural persona workspaces, without fabricated human identities.

Acceptance:
- each has goal, audience, voice constraints, success metric, memory namespace, experiment namespace and correction policy;
- distinctness test catches overly similar voices;
- cultural personas include source/cultural review requirement.

## SB-004 — Autonomous decision loop
Owner: Claude
Status: DONE — runtime/decision.py; per-bot isolation, no-change path, bounded retries, crash/restart + no-overlap tests green.

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
Status: DONE (metadata only) — ACCOUNT_BROWSER_MAP.md; no verification/secret; exact human gates listed.

Goal: reuse existing accounts/emails and document exact safe setup for TikTok, Reddit, X, Instagram and Facebook.

Acceptance:
- alias/login method/profile/workspace/last verification recorded;
- private credential references only;
- exact MFA/CAPTCHA/consent blocker;
- no public posting;
- supported route documented instead of bypasses.

## SB-006 — Content/experiment pipeline
Owner: Claude
Status: DONE — runtime/pipeline.py + analytics.py; dedup, review hooks, publish queue disabled.

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
Status: DONE — receipts/evidence/SB-007-dryruns (3 general + cultural WITHHELD), real research inputs, no publish.

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
Status: PREPARED — LAUNCH_GATE_PACKET.md; each blocker reduced to one exact human action.

Goal: reduce each external blocker to one exact human action and prepare one canary per persona.

Acceptance:
- exact account destination;
- explicit required human step;
- no duplicate setup;
- no publish until authorization;
- rollback/readback/analytics plan ready.
