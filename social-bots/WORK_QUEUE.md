## Current heartbeat epoch

Started: **2026-09-21 12:07 ET** (`2026-09-21T16:07:00Z`).

Only these fresh sessions count:
- CORE — `claude/social-bots-windows-core-host`
- INTELLIGENCE — `claude/social-bots-intelligence-repair-v2`
- ACCEPTANCE — `claude/social-bots-mac-qa-control` (with isolated canary worktree when Mission B begins)

All previous lane heartbeats are CLOSED/HISTORICAL and do not count toward today's FAST_5M or SOAK_15M_24H validation.

# Work queue — reset execution

Canonical plan: `RESET_EXECUTION_20260921.md`.
Lead review: `LEAD-035` at 2026-09-21T15:52:53Z.

## Current lane truth

All three fresh human sessions are **STALE / NOT STARTED** in repository evidence after the reset handoff. Issue #3 has no worker heartbeat comment after the lead reset comments, and the Core / Intelligence / Mac-QA progress files still say the fresh session has not started. The dedicated canary worktree remains unexecuted. Heartbeat remains observability only and never blocks source/acceptance work.

## Critical path

1. Mac Acceptance lane independently clears SB-V03-004.
2. ChatGPT reconciles SB-V03-001 / SB-V03-006 / SB-EVD-001 and closes V0.3 if evidence passes.
3. Windows Core repairs SB-V04-004 in parallel.
4. Mac Acceptance lane executes real SB-V04-005 canary from the isolated canary worktree.
5. ChatGPT performs SB-EVD-002 and reconciles V0.4.
6. Intelligence repairs V05-001 then V15-001 in parallel.

## Lane 1 — Windows Core

Branch: `claude/social-bots-windows-core-host`
Status: **STALE — fresh reset session has not started**.
Next: start now; SB-V04-004 isolated persona/evidence acceptance repair + adaptive receipt seam.
Do not churn final V03 without a concrete independent QA defect.
Do not execute SB-V04-005.

## Lane 2 — Intelligence

Branch: `claude/social-bots-intelligence-repair-v2`
Status: **STALE — fresh reset session has not started**.
Next:
1. start now and implement SB-V05-001 real HTTPS pinned-IP TLS/SNI/cert path;
2. SB-V15-001 persona-scoped production experiment APIs;
3. stop expansion for lead audit.

## Lane 3 — Mac Acceptance / Canary

Primary: `claude/social-bots-mac-qa-control`
Second worktree: `claude/social-bots-v04-live-canary`
Status: **STALE — fresh Acceptance session has not started; canary remains unexecuted**.

Next:
1. start now and independently execute V03-004 lifecycle gate;
2. push exact independent QA result;
3. if PASS, use isolated canary worktree for exactly one real SB-V04-005 canary;
4. stop canary execution for lead audit;
5. integration/CI QA after the gate/canary where dependency-safe.

## Live progress

Private GitHub Issue #3 is the live human-readable heartbeat feed.
Each timed heartbeat must post a concise lane update, even when no code was pushed.
Current reset soak status: **0 verified FAST_5M intervals on every lane; no reset T0 is visible yet**.

## Remote worker-pc

Not on critical path until Social Bots clone/auth is fixed.
Do not redispatch Social Bots merely because capacity is free.
Use for independent read-only audits or isolated branch work only after private-repo access is demonstrably repaired.

## Official version

V0.3.x. No artifact status changed in LEAD-035.

## Authority

No public effects, API/PAYG/new spend, destructive actions, secrets, fake evidence or SwarmAI dependency.
