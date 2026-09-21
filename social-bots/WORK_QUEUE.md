# Work queue

Artifact-first management is authoritative. Current deep audit: `LEAD_AUDIT_TWO_LANE_BATCH.md` / LEAD-015.

## Verified completed worker batches

Audited heads:
- Core: `claude/social-bots-core-to-v2@874b6992fb4fff3e4832dcb8ae078828525f6a51`
- Intelligence: `claude/social-bots-intelligence-to-v2@3d249ec885706380a6a12934042ed03c1e15b831`

Both branches contain final batch reports and no newer repository activity was observed in this review. This verifies the submitted code batch, not the state of the local Claude UI/process.

No GitHub status checks exist at either head. Worker-reported suites: Core 85, Intelligence 128.

## Current version

**V0.3.x**

Accepted:
- SB-V03-002
- SB-V03-003

V0.3 blockers:
- SB-V03-004 CHANGES_REQUIRED
- SB-V03-005 CHANGES_REQUIRED
- SB-V03-006 BLOCKED until 004/005 accepted

## Next execution mode — two separate Claude instances

Plan: `NEXT_PHASE_TWO_INSTANCE_PLAN.md`

### Instance A — Windows Core / Host

Suggested branch:
`claude/social-bots-windows-core-host`

Packet:
`artifact-packets/repair-waves/WINDOWS_CORE_WAVE1.md`

Order:
1. SB-V03-004 complete durable-write fencing; fix post-fence decision log/latest-decision writes; remove false transactionality claim.
2. Prove native-Windows strong lock/fence OR explicitly choose/prove an already-installed WSL/POSIX supported host path.
3. SB-V03-005 split shared RuntimeState from private PersonaState. Persona-private: seen/consumed signals, hypotheses, working state, pending decisions, strategy-private state.
4. SB-V03-006 fresh acceptance bundle.
5. SB-V04-001/002 real adaptive provider via existing authenticated Claude Code subscription if host checks pass; fail closed on API-key/payg risk or provider failure.
6. SB-CTL-006 CI.
7. SB-V07-WIN-001 two genuinely separate recurring worker invocations with heartbeats/receipts.

### Instance B — Intelligence / Evidence Integrity

Suggested branch:
`claude/social-bots-intelligence-repair-v2`

Packet:
`artifact-packets/repair-waves/INTELLIGENCE_WAVE1.md`

Order:
1. SB-V05-001 trusted live transport + SSRF/redirect/extraction validity.
2. SB-V05-002 attributable factual support assessor; caller stance test-only.
3. SB-V13-001 cumulative_snapshot/delta/gauge/rate semantics + safe aggregation.
4. SB-V14-001 persona-scoped memory + safe segment allowlist + correct fork semantics.
5. SB-V15-001 measurement/evidence refs.
6. SB-V16-001 ClaimSupport validation + persona-scoped history/novelty.
7. SB-V17-001 receipt-backed, persona-scoped community memory/themes.
8. SB-V20-002 typed accepted-evidence inputs.

## Current deep-audit verdicts

### Core
- SB-V03-003 ACCEPTED.
- SB-V03-004 CHANGES_REQUIRED.
- SB-V03-005 CHANGES_REQUIRED.
- SB-V04-001 CHANGES_REQUIRED.
- SB-V04-002 CHANGES_REQUIRED.
- SB-V04-003 source direction positive, BLOCKED on V04-001.

### Intelligence
- SB-V05-001 CHANGES_REQUIRED.
- SB-V05-002 CHANGES_REQUIRED.
- SB-V13-001 CHANGES_REQUIRED.
- SB-V14-001 CHANGES_REQUIRED.
- SB-V15-001 CHANGES_REQUIRED.
- SB-V16-001 CHANGES_REQUIRED.
- SB-V12-001 BLOCKED on corrected V13 inputs.
- SB-V17-001 CHANGES_REQUIRED.
- SB-V20-002 CHANGES_REQUIRED.

## After repair Wave 1

Do not immediately add more coding lanes.

Lead first:
1. accept/reject repaired artifacts;
2. create/assign one integration owner;
3. merge corrected Core + Intelligence into an integration branch;
4. run independent CI;
5. execute `V2_ENGINEERING_ACCEPTANCE.md`.

Then:
- implement SB-V20-001 strategy revision engine;
- integrate V20-002;
- build SB-V20-099 engineering-readiness bundle;
- proceed V2.1 -> V2.2 -> V2.3.

A third Claude session becomes useful **after** these shared contracts are stable.

## Authority

No public posting/replies/messages, purchases, paid APIs/additional spend, destructive actions, credentials in Git, fake operational evidence, engagement manipulation or SwarmAI dependency.


## Optional Mac QA / Control lane — READY

One additional Claude session on Mac is safe now because it does not touch Core or Intelligence runtime source.

Suggested branch:
`claude/social-bots-mac-qa-control`

Packet:
`artifact-packets/repair-waves/MAC_QA_CONTROL_WAVE1.md`

Primary artifact:
- `SB-CTL-012` — artifact graph validator/readiness reporter — SP3.

Purpose:
- mechanically validate artifact/dependency/manifest consistency;
- report milestone/readiness blockers;
- help implement CI/control if Windows has not already claimed it;
- prepare V2 integration acceptance fixtures/harness without runtime edits.

Do not add a second Mac implementation lane yet. Current practical concurrency target is 3 Claude sessions total: two repair workers + one QA/control worker.
