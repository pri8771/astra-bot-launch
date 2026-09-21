# Work queue

Artifact-first management is authoritative. Current heartbeat audit: `lead-reviews/LEAD-017_2026-09-20T2152.md`; foundational deep audit remains `LEAD_AUDIT_TWO_LANE_BATCH.md` / LEAD-015.

## Verified completed worker batches

Historical audited heads:
- Core: `claude/social-bots-core-to-v2@874b6992fb4fff3e4832dcb8ae078828525f6a51`
- Intelligence: `claude/social-bots-intelligence-to-v2@3d249ec885706380a6a12934042ed03c1e15b831`

Those are completed batch evidence, not the active repair lanes.

## Active repair-lane repository evidence — LEAD-017

- Windows Core/Host branch `claude/social-bots-windows-core-host`: visible and active at signed Claude head `5318065aad6e38de1e3313ad984d09451a2dfcb7`.
- Intelligence repair branch `claude/social-bots-intelligence-repair-v2`: visible and active at signed Claude head `cbd781cab4d751b2a0626c3ce060c5a217d771e9`.
- Mac QA/control expected branch `claude/social-bots-mac-qa-control`: **not visible remotely yet**.

Worker-local suite reports: Core 91, Intelligence 145. Independent GitHub CI remains absent.

## Current version

**V0.3.x**

Accepted:
- SB-V03-002
- SB-V03-003

V0.3 blockers:
- SB-V03-004 CHANGES_REQUIRED
- SB-V03-005 CHANGES_REQUIRED
- SB-V03-006 BLOCKED until 004/005 accepted

No milestone promotion is justified by later scaffolding while these required V0.3 artifacts remain unresolved.

## Instance A — Windows Core / Host

Branch: `claude/social-bots-windows-core-host`

Packet: `artifact-packets/repair-waves/WINDOWS_CORE_WAVE1.md`

Latest submitted checkpoint: `5318065a...` for SB-V03-004 + SB-V03-005.

### Positive changes

- decision log and last-decision writes were moved inside the fenced commit;
- false multi-file transactionality language was corrected;
- RuntimeState and PersonaState are now physically separated for consumed signals, hypotheses, working state, pending decisions and goals;
- same shared evidence can be independently consumed by multiple personas;
- worker added adversarial fencing/isolation tests and reports 91 passing locally.

### SB-V03-004 — still CHANGES_REQUIRED

1. **Unfenced migration writes:** `PersonaState.load()` can persist a persona file and update/save RuntimeState during legacy migration before `decision.run_cycle()` reaches `Fence.fenced_commit`. A stale worker can therefore still perform cycle-triggered durable migration writes before its final fence is checked.
2. **Windows host proof absent:** the worker report identifies the tested platform as Linux container/POSIX. It references a `WINDOWS_HOST_LOCKING.md` artifact that is not present in the reviewed `worker-reports/windows-core/` checkpoint. Native Windows or explicitly selected WSL/POSIX strong-lock evidence is still required.

Required next:
- stage migration without writes until the fenced commit, or explicitly fence the migration write;
- add stale-owner migration regression;
- provide actual Windows host readback and native-Windows or WSL supported-path proof.

### SB-V03-005 — still CHANGES_REQUIRED

The private mutable state split addresses the LEAD-015 root cause, but it does not close the full canonical packet:

1. Shared append-only non-public persona artifacts remain logically labeled only. Existing production readers such as `pipeline.publish_queue(bot)` and `RuntimeState.content_history()` still return whole-bot mixed-persona data.
2. The canonical packet requires one authoritative persona-scoped production read boundary and mixed-persona regressions through real production read paths.
3. Legacy migration inherits the unfenced durable-write defect above.

Required next:
- enforce persona-scoped production reads for content/experiments/analytics/actions and other non-shared persona history;
- make raw whole-runtime reads explicit admin/internal paths where needed;
- add mixed-persona contamination tests over real production APIs;
- fix migration under V03-004.

Only after both artifacts pass independent review should SB-V03-006 be regenerated.

## Instance B — Intelligence / Evidence Integrity

Branch: `claude/social-bots-intelligence-repair-v2`

Packet: `artifact-packets/repair-waves/INTELLIGENCE_WAVE1.md`

### SB-V05-001 at `ecad87e6...` — CHANGES_REQUIRED

Positive repair work:
- caller `mode="live"` alone no longer grants operational-live status;
- public destination checks, redirect policy structure and extraction_status were added;
- fixture evidence remains honestly fixture-labelled.

Independent LEAD-017 blockers:
1. `register_trusted_transport(cls)` is public/mutable. The tests register a caller-created `TrustedLiveStub`, after which it produces operational-live evidence. Trust is therefore still caller-grantable.
2. `to_signal()` accepts any `is_verified_capture()`, including verified-but-untrusted live receipts, into the normal signal bridge.
3. Redirect tests override `_perform()` and do not prove the real urllib 30x handling path.
4. DNS validation and socket connection resolve separately; DNS-rebinding/TOCTOU remains.

### SB-V05-002 at `cbd781ca...` — CHANGES_REQUIRED

Positive repair work:
- added attributable assessor records;
- added material-claim identification so caller omission no longer trivially bypasses review;
- preserved hash staleness and fail-closed missing-assessor behavior.

Independent LEAD-017 blockers:
1. `register_operational_assessor(cls)` repeats the public self-registration trust flaw; arbitrary runtime code can grant its own assessor operational authority.
2. `evidence_ref_from_receipt()` accepts verified fixture/untrusted captures; operational fact review must require accepted SB-V05-001 operational evidence.
3. `KeywordSupportAssessor` can mark full `SUPPORTED` from key-term co-occurrence. It must fail conservatively on negation, relation mismatch, numeric/date mismatch and subject-only mentions rather than overclaim factual support.

### Required repair order

1. Repair/resubmit SB-V05-001 against the tightened canonical packet.
2. Repair/resubmit SB-V05-002 against the tightened canonical packet.
3. SB-V13-001 cumulative_snapshot/delta/gauge/rate semantics + safe aggregation.
4. SB-V14-001 persona-scoped memory + safe segment allowlist + correct fork semantics.
5. SB-V15-001 measurement/evidence refs.
6. SB-V16-001 ClaimSupport validation + persona-scoped history/novelty.
7. SB-V17-001 receipt-backed, persona-scoped community memory/themes.
8. SB-V20-002 typed accepted-evidence inputs.

Scaffolding may be committed ahead, but canonical status remains dependency/evidence-gated.

## Current deep-audit dispositions

### Core
- SB-V03-003 ACCEPTED.
- SB-V03-004 CHANGES_REQUIRED after Windows repair audit.
- SB-V03-005 CHANGES_REQUIRED after Windows repair audit.
- SB-V04-001 CHANGES_REQUIRED.
- SB-V04-002 CHANGES_REQUIRED.
- SB-V04-003 source direction positive, BLOCKED on V04-001.

### Intelligence
- SB-V05-001 CHANGES_REQUIRED after LEAD-017 repair audit.
- SB-V05-002 CHANGES_REQUIRED after LEAD-017 repair audit.
- SB-V13-001 CHANGES_REQUIRED.
- SB-V14-001 CHANGES_REQUIRED.
- SB-V15-001 CHANGES_REQUIRED.
- SB-V16-001 CHANGES_REQUIRED.
- SB-V12-001 BLOCKED on corrected V13 inputs.
- SB-V17-001 CHANGES_REQUIRED.
- SB-V20-002 CHANGES_REQUIRED.

## Mac QA / Control lane

Branch: `claude/social-bots-mac-qa-control`

Packet: `artifact-packets/repair-waves/MAC_QA_CONTROL_WAVE1.md`

Primary artifact:
- `SB-CTL-012` — artifact graph validator/readiness reporter — SP3.

Branch is not yet visible remotely at LEAD-017.

Purpose:
- mechanically validate artifact/dependency/manifest consistency;
- report milestone/readiness blockers;
- help implement CI/control if Windows has not already claimed it;
- prepare V2 integration acceptance fixtures/harness without runtime edits.

Do not let Mac QA edit Core or Intelligence runtime implementation.

## After repair Wave 1

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

Do not misstate SB-V20-099 engineering readiness as operational V2.0 promotion. Operational promotion remains real account/public/analytics evidence-gated.

## Authority

No public posting/replies/messages, purchases, paid APIs/additional spend, destructive actions, credentials in Git, fake operational evidence, engagement manipulation or SwarmAI dependency.
