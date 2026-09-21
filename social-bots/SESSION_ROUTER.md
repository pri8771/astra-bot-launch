# Active session router — reset execution

Lead-owned routing table.
Current plan: `RESET_EXECUTION_20260921.md`.
Lead review: `LEAD-035` at 2026-09-21T15:52:53Z.

Official version remains V0.3.x.

## Lane 1 — Windows Core Builder

Branch: `claude/social-bots-windows-core-host`
Machine: Windows
Status: **STALE — fresh reset session not started**.

Evidence at LEAD-035:
- current branch head before lead refresh was reset-only `d3974de...`;
- `CURRENT_PROGRESS.md` still said the fresh session had not started;
- no worker Issue #3 heartbeat appeared after reset.

Owns:
- SB-V04-004 bounded divergence acceptance repair;
- dependency-safe Core work after acceptance.

Preserve final V03 implementation/evidence. Do not execute the live canary.

## Lane 2 — Mac Intelligence Builder

Branch: `claude/social-bots-intelligence-repair-v2`
Machine: Mac
Status: **STALE — fresh reset session not started**.

Evidence at LEAD-035:
- current branch head before lead refresh was reset-only `a11c7e4...`;
- `CURRENT_PROGRESS.md` still said the fresh session had not started;
- no worker Issue #3 heartbeat appeared after reset.

Owns:
1. SB-V05-001 actual pinned-IP HTTPS/TLS/SNI/certificate repair;
2. SB-V15-001 persona-scoped experiment persistence/read boundary;
3. later dependency-safe Intelligence repairs.

No Core runtime edits.

## Lane 3 — Mac Acceptance / Canary

Primary branch: `claude/social-bots-mac-qa-control`
Second isolated worktree: `claude/social-bots-v04-live-canary`
Machine: actual local Mac with working Claude Code subscription auth.
Status: **STALE — fresh Acceptance session not started; canary unexecuted**.

Evidence at LEAD-035:
- primary branch head before lead refresh was reset-only `196d9d6...`;
- primary `CURRENT_PROGRESS.md` still said the fresh session had not started;
- canary branch head before lead refresh was lead-only `1b2e67d...`;
- canary has no worker `CURRENT_PROGRESS.md` and no worker execution evidence;
- no worker Issue #3 heartbeat appeared after reset.

Order:
1. independently execute SB-V03-004 lifecycle gate against final Core source;
2. submit QA report and ACCEPT-READY recommendation or concrete defect;
3. then execute exactly one real SB-V04-005 canary from the second worktree;
4. push canary evidence and stop canary execution for ChatGPT lead audit;
5. continue QA/integration work on the primary branch.

No Core runtime source edits.

## Remote worker-pc

External optional verifier only.
Control plane: `pri8771/remote-workers`.
Not on critical path.

Current truth:
- worker infrastructure is real;
- Social Bots repository clone/auth still fails on worker-pc;
- do not redispatch Social Bots until access is demonstrably repaired.

## Heartbeat / visibility

All reset lanes:
- Stage 1: three real 5-minute intervals;
- Stage 2: every 15 minutes for 24 hours;
- keep real work running in parallel;
- use `social-bots/bin/heartbeat_reporter.py`;
- update `CURRENT_PROGRESS.md`;
- every timed heartbeat posts a concise comment to private GitHub Issue #3.

LEAD-035 truth: no reset FAST_5M T0 is visible on any lane. Historical Mac-QA hourly authorization remains historical coordination evidence only; it does not substitute for today's reset soak.

Heartbeat is observability only and must never block source, QA, or canary execution.

## Lead

ChatGPT owns acceptance, canonical reconciliation, next assignments, and hourly monitoring.
No worker self-accepts a milestone.

## Safety

No public social effects, paid API/PAYG/new spend, destructive actions, credentials/secrets, fabricated evidence, engagement manipulation or SwarmAI dependency.
