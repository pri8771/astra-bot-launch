# Work queue — reset execution

Canonical plan: `RESET_EXECUTION_20260921.md`.

## Critical path

1. Mac Acceptance lane independently clears SB-V03-004.
2. ChatGPT reconciles SB-V03-001 / SB-V03-006 / SB-EVD-001 and closes V0.3 if evidence passes.
3. Windows Core repairs SB-V04-004 in parallel.
4. Mac Acceptance lane executes real SB-V04-005 canary.
5. ChatGPT performs SB-EVD-002 and reconciles V0.4.
6. Intelligence repairs V05-001 then V15-001 in parallel.

## Lane 1 — Windows Core

Branch: `claude/social-bots-windows-core-host`
Next: SB-V04-004 isolated persona/evidence acceptance repair + adaptive receipt seam.
Do not churn final V03 without a concrete independent QA defect.
Do not execute SB-V04-005.

## Lane 2 — Intelligence

Branch: `claude/social-bots-intelligence-repair-v2`
Next:
1. SB-V05-001 real HTTPS pinned-IP TLS/SNI/cert path.
2. SB-V15-001 persona-scoped production experiment APIs.
Then hold for lead audit.

## Lane 3 — Mac Acceptance / Canary

Primary: `claude/social-bots-mac-qa-control`
Second worktree: `claude/social-bots-v04-live-canary`

Next:
1. independent V03-004 lifecycle execution;
2. real SB-V04-005 canary;
3. integration/CI QA.

## Live progress

Private GitHub Issue #3 is the live human-readable heartbeat feed.
Each heartbeat must post a concise lane update, even when no code was pushed.

## Remote worker-pc

Not on critical path until Social Bots clone/auth is fixed.
Use automatically for independent read-only audits or isolated branch work once healthy.

## Official version

V0.3.x.

## Authority

No public effects, API/PAYG/new spend, destructive actions, secrets, fake evidence or SwarmAI dependency.
