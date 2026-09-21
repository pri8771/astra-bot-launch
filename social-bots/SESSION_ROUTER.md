# Active session router — LEAD-038

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

Owns:
- no-live-call V0.4 empirical harness preparation;
- V0.7 SB-V07-001 host worker/runbook/scheduler/heartbeat durability after the prep submission.

Hard rule: no adaptive/model call until explicit owner authorization + canonical lead manifest.

## Lane 2 — Intelligence Builder

Branch: `claude/social-bots-intelligence-repair-v2`

Owns:
- current SB-V15-001 structural admin/read-boundary repair;
- later intelligence/evidence artifacts when lead releases them.

Do not edit Core-owned runtime areas without reassignment.

## Lane 3 — Acceptance / QA

Branch: `claude/social-bots-mac-qa-control`

Owns:
- independent source/evidence review;
- V0.6/V0.7 acceptance validators and fault cases;
- host/session-heartbeat truth checking.

Does not own live provider execution or Core/Intelligence runtime implementation.

## Live-canary branch

Branch: `claude/social-bots-v04-live-canary`

Status: FROZEN — evidence preservation only.

## ChatGPT lead role

ChatGPT stays ahead on:
- downstream artifact contracts;
- future version task planning;
- architecture/product decisions;
- independent review;
- acceptance;
- owner-gate manifests when explicitly authorized.

Claude remains the primary implementation worker.

## Worker-pc

Still outside the critical path until private-repo clone/auth is demonstrably repaired.

## Safety

No public effects, PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
