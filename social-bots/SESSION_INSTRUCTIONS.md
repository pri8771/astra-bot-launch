# SESSION_INSTRUCTIONS — Lane 2 / Intelligence Builder

Mode: LEAD-037 — NARROW SB-V15-001 REPAIR
Branch: `claude/social-bots-intelligence-repair-v2`

Read canonical:
- `social-bots/lead-reviews/LEAD-037_2026-09-21T1717.md`
- `social-bots/STATE.json`
- `social-bots/WORK_QUEUE.md`

## Assignment

SB-V05-001 is accepted.

Repair **SB-V15-001 only**:
1. remove/private/rename ordinary whole-runtime `load(bot,id)` and `load_all(bot)` aliases;
2. preserve explicit clearly named admin-only whole-runtime readers where required;
3. ensure normal production/persona APIs require bot + persona scope;
4. add structural regression proving ordinary production APIs cannot enumerate or read another persona's experiments;
5. retain provenance/compatibility/INCONCLUSIVE behavior;
6. run focused + full tests;
7. push source/report and STOP for lead audit before V16/V17/V20-002 expansion.

No live model call is needed or authorized.

No Core runtime edits, public effects, PAYG/new spend, secrets, destructive actions, fabricated evidence, engagement manipulation or SwarmAI dependency.
