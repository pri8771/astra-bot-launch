# SESSION_INSTRUCTIONS — Windows Core / Host

Lead review: LEAD-019 (reconciliation after LEAD-018)
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

## Reconciled disposition

- SB-V03-004: **CHANGES_REQUIRED again**. LEAD-018 accepted the final ownership-fenced commit, but deeper source review found cycle-triggered durable legacy-migration writes in `PersonaState.load()` / `_migrate_from_legacy()` that execute before `Fence.fenced_commit`. The canonical V03-004 contract says an obsolete owner cannot commit state after fence loss; load/migration side effects are state writes and must be staged/fenced too.
- SB-V03-005: CHANGES_REQUIRED.
- SB-V03-006: BLOCKED until both V03-004 and V03-005 pass.
- V04 adaptive provider / V07 host proof follow.

Mac QA owns SB-CTL-006 CI unless canonical router explicitly reassigns it.

## Next 1 — finish SB-V03-004 + SB-V03-005 migration safely

Keep the current generation-fence / fenced-commit design and RuntimeState / PersonaState architecture.

### V03-004 fencing repair

Required:
1. make RuntimeState/PersonaState cycle load paths side-effect free;
2. no `PersonaState.save()` or `RuntimeState.save()` may occur from legacy migration before ownership is checked;
3. stage migration in memory and persist the persona file + migration marker only inside the ownership-fenced commit, or perform an explicitly fenced migration before any durable write;
4. force stale owner A into the legacy migration path, allow B to take over, then prove A cannot leave persona state or migration-marker writes behind;
5. preserve honest guarantee language: ownership fencing, not ACID multi-file transactionality.

The actual Windows/WSL strong-lock and recurring-host proof remains `SB-V07-WIN-001`; Linux/container test evidence does not prove native Windows or WSL host behavior.

### V03-005 migration consistency

After the fencing rule above is satisfied:
- migration must be crash-safe and idempotent;
- persona file becomes durable before the final migrated marker, or use equivalent recoverable semantics within the fence;
- the RuntimeState eventually committed by the real cycle contains the final marker;
- test the real run_cycle load/save ordering;
- simulate interruption at the migration boundary where practical.

### V03-005 production persona read boundary

Close the canonical logical-isolation read boundary:
- persona-specific production reads for content history, experiments, queue, analytics, actions, decisions and other private append-only history must go through authoritative persona-scoped APIs;
- raw whole-runtime reads may remain explicit admin/internal APIs, not normal persona-facing production helpers;
- real mixed-persona production-path regressions must prove no bleed.

Submit updated SB-V03-004 and SB-V03-005 as independently reviewable checkpoints where possible.

## Next 2 — SB-V03-006

Only after V03-004 and V03-005 pass your own repaired contracts, generate a fresh V0.3 acceptance bundle from current code.

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

## Heartbeat / lead coordination

Read `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`.

This lane starts in `BOOTSTRAP_15M` mode.

While this Claude session is active:
- check in every 15 minutes for the bootstrap phase, even if the current artifact has not finished;
- after each parent-artifact submission or blocker, check in immediately instead of waiting;
- after 3 consecutive approximately-15-minute heartbeats, REMAIN on 15-minute cadence until `social-bots/worker-reports/windows-core/LEAD_ACK.json` says `steady_hourly_authorized=true`;
- once authorized, switch to hourly check-ins;
- do not exit merely because one artifact finished: pull instructions and take the next dependency-ready assignment unless blocked or explicitly told to stop.

For every heartbeat:
1. pull/fetch your branch;
2. re-read this SESSION_INSTRUCTIONS file;
3. inspect `social-bots/worker-reports/windows-core/LEAD_ACK.json`;
4. run the heartbeat helper;
5. append the generated record to `social-bots/worker-reports/windows-core/HEARTBEAT_LOG.jsonl`;
6. commit and push the heartbeat files;
7. set a notification reason for any new submission, blocker, completed artifact, changed assignment, or important finding.

Use:
`social-bots/bin/worker_heartbeat.py`

The heartbeat is a GitHub coordination signal, not proof of artifact correctness.

If the lead updates this file between heartbeats, follow the newest pulled version.

Path:
`social-bots/worker-reports/windows-core/HEARTBEAT.json`

Push heartbeat on START/WORKING/SUBMITTED/BLOCKED/IDLE/STOPPED state transitions, not every few minutes.

## Safety

No public posting/replies/messages, purchases, paid APIs/new spend, destructive actions, secrets, fake evidence or SwarmAI dependency.
