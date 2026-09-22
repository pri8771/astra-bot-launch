# Fast-track execution plan — 2026-09-20

Owner directive: move faster. Heartbeat validation is observability only and must not block implementation or the V0.4 canary.

## Parallel lanes

### Lane A — Windows Core / V0.3 closure
Branch: `claude/social-bots-windows-core-host`

Priority:
1. repair SB-V03-004 migration writes so load/migration is side-effect free until ownership-fenced commit;
2. finish SB-V03-005 authoritative persona-scoped production readers;
3. regenerate SB-V03-006;
4. then reconcile V04-001/003 dependencies and prepare V0.4 acceptance.

No CI ownership.

### Lane B — Intelligence / evidence + experiments
Branch: `claude/social-bots-intelligence-repair-v2`

Priority:
1. fix SB-V05-001 actual HTTPS pinned-IP/SNI/cert-verification path;
2. fix SB-V15-001 persona-scoped production experiment persistence/read boundary;
3. preserve accepted V13/V14;
4. submit V16/V17/V20-002 for fresh lead audit after the two explicit repairs.

Heartbeat continues in background but does not block source work.

### Lane C — Mac QA / Integration control
Branch: `claude/social-bots-mac-qa-control`

Continue:
- heartbeat proof in background;
- GitHub CI/control;
- artifact graph validation;
- V2 acceptance harness;
- prepare integration checklist and branch-merge test plan.

Do not block on the heartbeat before doing QA work.

### Lane D — Mac LOCAL V0.4 live canary
Branch: `claude/social-bots-v04-live-canary`

This lane must run from an actual local Mac/host where normal Claude Code subscription authentication works.

Priority Zero:
- execute SB-V04-005 immediately;
- heartbeat validation is NOT a prerequisite;
- one real current public source;
- one actual Claude Code subscription call;
- no injected runner, no fixtures, no API PAYG;
- persist decision; no public effect;
- push evidence and stop for lead audit.

## Lead
ChatGPT:
- audits every checkpoint;
- updates artifact state;
- keeps lanes non-overlapping;
- immediately accepts/rejects the live canary;
- prepares V0.5/V0.6/V0.7 and V2 integration work ahead of workers.

## Concurrency
Target: four workers maximum for this fast-track phase:
- Windows Core
- Intelligence
- Mac QA
- Mac local canary

After canary completes, reuse that worker for whichever dependency-ready lane has the largest backlog.

## Promotion
Official version remains evidence-gated.
V0.4 still cannot complete without SB-V04-005 + SB-EVD-002.
Heartbeat success does not gate V0.4 or source development.

## Safety
No public posting/messages/purchases, no additional spend/API PAYG, no destructive actions, no secrets, no fake evidence, no SwarmAI dependency.
