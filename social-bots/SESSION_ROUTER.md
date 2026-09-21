# Active session router — reset execution

Lead-owned routing table.
Current plan: `RESET_EXECUTION_20260921.md`.

Official version remains V0.3.x.

## Lane 1 — Windows Core Builder

Branch: `claude/social-bots-windows-core-host`
Machine: Windows
Status: FRESH SESSION REQUIRED.

Owns:
- SB-V04-004 bounded divergence acceptance repair;
- dependency-safe Core work after acceptance.

Preserve final V03 implementation/evidence. Do not execute the live canary.

## Lane 2 — Mac Intelligence Builder

Branch: `claude/social-bots-intelligence-repair-v2`
Machine: Mac
Status: FRESH SESSION REQUIRED.

Owns:
1. SB-V05-001 actual pinned-IP HTTPS/TLS/SNI/certificate repair;
2. SB-V15-001 persona-scoped experiment persistence/read boundary;
3. later dependency-safe Intelligence repairs.

No Core runtime edits.

## Lane 3 — Mac Acceptance / Canary

Primary branch: `claude/social-bots-mac-qa-control`
Second isolated worktree: `claude/social-bots-v04-live-canary`
Machine: actual local Mac with working Claude Code subscription auth.
Status: FRESH SESSION REQUIRED.

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

All three fresh lanes:
- Stage 1: three real 5-minute intervals;
- Stage 2: every 15 minutes for 24 hours;
- keep real work running in parallel;
- use `social-bots/bin/heartbeat_reporter.py`;
- update `CURRENT_PROGRESS.md`;
- every timed heartbeat posts a concise comment to private GitHub Issue #3.

ChatGPT automated lead review remains hourly due platform limits, but Issue #3 provides 5/15-minute worker-visible progress.

## Lead

ChatGPT owns acceptance, canonical reconciliation, next assignments, and hourly monitoring.
No worker self-accepts a milestone.

## Safety

No public social effects, paid API/PAYG/new spend, destructive actions, credentials/secrets, fabricated evidence, engagement manipulation or SwarmAI dependency.
