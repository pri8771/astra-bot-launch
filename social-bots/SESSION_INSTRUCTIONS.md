# SESSION_INSTRUCTIONS — Lane 2 / Intelligence Builder

Mode: LEAD-039 — STALE WAKE-UP / NARROW SB-V15-001 REPAIR
Branch: `claude/social-bots-intelligence-repair-v2`

Read canonical:
- `social-bots/lead-reviews/LEAD-039_2026-09-21T1356.md`
- `social-bots/CLAUDE_EXECUTION_TO_V07.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`

## Lead classification

STALE. No fresh Intelligence worker session, heartbeat, source commit, or repair submission is visible after LEAD-038. The last verified worker implementation remains `205295531e7755a5045fb1e458d3964d986edd56`, which materially improved persona scoping but intentionally retained ordinary whole-runtime `load` / `load_all` aliases.

On the next fresh session, sync/read canonical coordination, emit exactly one real `SESSION_ONCE` heartbeat, then work normally. Do not run a timed heartbeat loop.

## Assignment

SB-V05-001 is accepted.

Repair **SB-V15-001 only**:
1. remove/private/rename ordinary whole-runtime `load(bot,id)` and `load_all(bot)` aliases;
2. preserve only explicit clearly named admin-only whole-runtime readers where required;
3. ensure normal production/persona APIs require bot + persona scope;
4. add structural regression proving ordinary production APIs cannot enumerate or read another persona's experiments;
5. retain provenance/compatibility/INCONCLUSIVE behavior;
6. run focused + full tests;
7. push source/report and STOP for lead audit before V16/V17/V20-002 expansion.

No live model call is needed or authorized.

No Core runtime edits, public effects, PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
