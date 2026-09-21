# Active session router — LEAD-039

Official phase: **V0.4.x / V0.4 in progress**.

Primary execution contract: `CLAUDE_EXECUTION_TO_V07.md`.
Heartbeat contract: **one fresh worker session = one durable heartbeat**.

## Universal session start

Every fresh Claude session:
1. fetches current repository truth;
2. reads canonical state/queue/router/latest lead review/artifact packet;
3. inspects its branch and relevant worker evidence;
4. emits exactly one `SESSION_ONCE` heartbeat;
5. begins work.

No periodic heartbeat loop.

## Lane 1 — Core Builder

Branch: `claude/social-bots-windows-core-host`
Status: **ACTIVE** from Issue #3 fresh-session visibility at 2026-09-21T17:48:17Z; no new worker source/report commit from that session was visible on the authoritative branch during LEAD-039.

Owns:
- no-live-call V0.4 empirical harness preparation;
- then V0.7 SB-V07-001 host worker/runbook/scheduler/session-heartbeat/invocation-receipt durability.

Hard rule: no adaptive/model call until fresh explicit owner authorization plus a canonical lead authorization manifest.

## Lane 2 — Intelligence Builder

Branch: `claude/social-bots-intelligence-repair-v2`
Status: **STALE** after LEAD-038; no fresh session/repair commit visible during LEAD-039.

Owns:
- current SB-V15-001 structural admin/read-boundary repair only;
- later evidence/intelligence artifacts only when released by lead.

Next fresh session must emit one `SESSION_ONCE` heartbeat, remove/private/rename ambiguous whole-runtime `load` / `load_all` aliases, test, submit, and stop. Do not edit Core-owned runtime areas without reassignment.

## Lane 3 — Acceptance / QA

Branch: `claude/social-bots-mac-qa-control`
Status: **STALE** after LEAD-038; no fresh session/QA commit visible during LEAD-039.

Owns:
- independent source/evidence review;
- V0.6/V0.7 acceptance validators and fault cases;
- host/session-heartbeat/scheduler truth checking.

Next fresh session emits one `SESSION_ONCE` heartbeat, then resumes independent review and V0.7 acceptance preparation. No runtime source edits and no live provider execution.

## Live-canary branch

Branch: `claude/social-bots-v04-live-canary`
Status: **FROZEN — EVIDENCE PRESERVATION ONLY**.

The first authorized SB-V04-005 canary remains accepted. The later duplicate is excluded. No further model calls or new canary source retrieval are authorized.

## ChatGPT lead role

ChatGPT stays ahead on downstream artifact contracts, future version planning, architecture/product decisions, independent review, acceptance, and owner-gate manifests when explicitly authorized. Claude remains the primary implementation worker.

## Worker-pc

Outside the Social Bots critical path until private-repo clone/auth is demonstrably repaired. Do not redispatch merely because capacity is free.

## Safety

No public effects, PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
