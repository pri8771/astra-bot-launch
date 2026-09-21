# SESSION_INSTRUCTIONS — Windows Core / Host

Lead review: LEAD-018
Branch: `claude/social-bots-windows-core-host`

## Coordination loop

At session start and after every parent artifact checkpoint:

1. `git pull --ff-only`
2. `git fetch origin`
3. Read this file.
4. Read the current canonical router without merging:
   `git show origin/chatgpt/social-bots-plan-20260920:social-bots/SESSION_ROUTER.md`
5. Read the latest CHATGPT -> CLAUDE lead entry from canonical AGENT_MESSAGES.
6. Update and push `social-bots/worker-reports/windows-core/HEARTBEAT.json`.
7. Execute the next dependency-ready artifact.

Do not rewrite this file. Lead owns it.

## Current disposition

- SB-V03-004: ACCEPTED by LEAD-018 for code-level ownership fencing.
- SB-V03-005: CHANGES_REQUIRED, narrow follow-up.
- SB-V03-006: next after V03-005.
- V04 adaptive provider / V07 host proof follow.

Mac QA owns SB-CTL-006 CI unless canonical router explicitly reassigns it.

## Next 1 — finish SB-V03-005

Keep the RuntimeState / PersonaState architecture.

Repair migration consistency:

- Current run_cycle loads RuntimeState before PersonaState.
- Persona migration can save a fresh runtime marker, then the older in-memory RuntimeState can later overwrite the marker.
- Migration currently marks runtime migrated before the persona file is durably saved, creating a crash window.

Required:
1. make migration crash-safe and idempotent;
2. persona file becomes durable before final migrated marker, or use equivalent recoverable two-phase semantics;
3. the RuntimeState eventually committed by the real cycle contains the final migration marker;
4. test the actual run_cycle load/save ordering;
5. simulate interruption at the migration boundary where practical.

Also close the canonical logical-isolation read boundary:
- persona-specific production reads for content history, experiments, queue, analytics, actions, decisions must go through authoritative persona-scoped APIs;
- raw whole-runtime reads may remain explicit admin/internal APIs;
- real mixed-persona production-path regressions must prove no bleed.

Submit updated SB-V03-005.

## Next 2 — SB-V03-006

After V03-005 passes your own tests, generate a fresh V0.3 acceptance bundle from current code.

Do not reuse superseded evidence.

## Next 3 — V04 real adaptive reasoning

Then repair/complete SB-V04-001/002:
- production changed-evidence posture fails closed by default without adaptive provider;
- baseline/contextual deterministic providers remain explicit test/debug modes;
- use REASONING_PROPOSAL_SCHEMA.md;
- inspect actual host environment before claiming Windows.

For host reasoning:
- determine whether you truly have native Windows shell, WSL, or a Linux/container execution context;
- record safe metadata only;
- if ANTHROPIC_API_KEY exists, record boolean only and do not use/print it;
- use existing Claude Code subscription route only if actually authenticated and no PAYG key path is selected;
- bounded non-interactive structured result;
- no tools/external effects;
- auth/quota/parse/schema failure => fail closed.

If your execution environment is Linux/container rather than the actual Windows host, mark Windows host proof BLOCKED rather than fabricating it.

## Next 4 — SB-V07-WIN-001

Only on an actually supported Windows/WSL host:
- prove strong locking path;
- prove two separate recurring invocations;
- heartbeat/receipt/lease/fence/clean exit;
- restart/no-overlap.

## Ownership

Core owns state, leasing, worker, decision, reasoning, host runtime.
Do not edit Intelligence modules.

## Heartbeat

Path:
`social-bots/worker-reports/windows-core/HEARTBEAT.json`

Push heartbeat on START/WORKING/SUBMITTED/BLOCKED/IDLE/STOPPED state transitions, not every few minutes.

## Safety

No public posting/replies/messages, purchases, paid APIs/new spend, destructive actions, secrets, fake evidence or SwarmAI dependency.
