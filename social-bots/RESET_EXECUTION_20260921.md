# Social Bots reset execution plan — 2026-09-21

## Why this reset exists

Previous execution proved that four manually managed lanes created coordination drag and stale sessions. The project is now restarting from audited repository evidence with three fresh human-started lanes plus one optional remote verifier.

## Authoritative current state

Official product version: **V0.3.x**

### V0.3
- SB-V03-002: ACCEPTED
- SB-V03-003: ACCEPTED
- SB-V03-005: ACCEPTED
- SB-V03-004: source repair is positive but still requires packet-mandated independent lifecycle execution
- SB-V03-006: final/prepared from implementation 796d4e3 and evidence 436787b; 130-test committed output; blocked on V03-004 acceptance + final reconciliation
- SB-V03-001 / SB-EVD-001: final reconciliation waits on V03-004 acceptance

### V0.4
- adaptive provider implementation exists
- deterministic policy/authority wall direction is positive
- SB-V04-004: CHANGES_REQUIRED because current divergence tests are confounded and use adaptive=false contextual provider
- SB-V04-005: READY but real canary has never produced worker evidence
- SB-EVD-002: BLOCKED until real canary exists

### Intelligence
- SB-V13-001 and SB-V14-001: ACCEPTED
- SB-V05-001: CHANGES_REQUIRED; actual HTTPS pinned-IP TLS/SNI/cert path must be repaired
- SB-V15-001: CHANGES_REQUIRED; production experiment persistence/read APIs must be persona-scoped
- SB-V16-001 / V17-001 / V20-002: useful submitted work but still need fresh lead audit after dependencies clear

### worker-pc
- remote worker infrastructure is real and online
- Social Bots critical path does NOT depend on worker-pc
- repeated Social Bots tasks failed before Claude/tests because private repo clone/auth is still broken
- use worker-pc only after access is demonstrably fixed and capacity is free

## New execution topology

### Lane 1 — Windows Core Builder
Branch: claude/social-bots-windows-core-host
Machine: Windows
Owns:
- SB-V04-004 bounded repair
- Core V0.4 dependency-safe work after acceptance
Does not own:
- live canary
- Intelligence source
- independent V03 fencing acceptance

### Lane 2 — Mac Intelligence Builder
Branch: claude/social-bots-intelligence-repair-v2
Machine: Mac
Owns:
- SB-V05-001
- SB-V15-001
- later dependency-safe Intelligence repair
Does not edit Core runtime.

### Lane 3 — Mac Acceptance / Canary
Primary branch: claude/social-bots-mac-qa-control
Second isolated worktree: claude/social-bots-v04-live-canary
Machine: actual local Mac with working Claude Code subscription auth
Order:
1. independently execute SB-V03-004 lifecycle gate against final Core source
2. push QA report; if PASS recommend ACCEPT-READY
3. then use a second worktree for dedicated live-canary branch
4. execute exactly one real SB-V04-005 canary
5. push canary evidence and stop canary execution for ChatGPT audit
6. continue QA/integration work on primary branch

This lane does not modify Core runtime source.

## Heartbeat + live visibility

Private GitHub Issue #3 — "Social Bots — Live Progress & Heartbeats" is the human-readable progress feed.

Every active lane must:
1. maintain CURRENT_PROGRESS.md with one concise current-status sentence;
2. launch social-bots/bin/heartbeat_reporter.py once at fresh-session start;
3. Stage 1: T0/+5/+10/+15 minutes;
4. Stage 2: every 15 minutes for 24 hours;
5. the reporter posts CURRENT_PROGRESS.md to Issue #3 at every heartbeat;
6. Claude updates CURRENT_PROGRESS.md whenever task/subtask/blocker changes;
7. heartbeat never blocks real work.

Git heartbeat logs remain useful audit evidence, but Issue #3 is the primary human-readable live view for this reset.

## Lead automation

ChatGPT lead automation remains hourly because platform scheduling cannot run faster.
At each review it must:
- inspect Issue #3 heartbeat comments;
- inspect branch heads/reports/tests;
- reconcile artifact statuses;
- update assignments/LEAD_ACK;
- immediately flag stale lanes or blockers;
- review real canary evidence when it lands;
- use worker-pc automatically for useful independent work only after clone/auth works.

## Shortest path

A. Acceptance lane clears SB-V03-004 -> ChatGPT closes V0.3.
B. Core lane fixes SB-V04-004.
C. Acceptance lane executes real SB-V04-005 -> ChatGPT performs SB-EVD-002.
D. With V0.3 accepted + V04 artifacts cleared -> promote V0.4.
E. Intelligence closes V05-001 then V15-001 in parallel.
F. Proceed to V0.5/V0.6 real research and three-persona dry runs.
G. Build V0.7 recurring worker proof using OS-level scheduling rather than trusting a chat session as the scheduler.

## Safety

No public social effects, API/PAYG/new spend, destructive actions, secrets, fake evidence, engagement manipulation, or SwarmAI dependency.
