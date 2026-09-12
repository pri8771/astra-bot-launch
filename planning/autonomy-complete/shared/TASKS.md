# Shared implementation task cards

Proposals only. Future exact-source admission and owned-path binding precede implementation. Existing release workers keep their separate scope. Each estimate is active engineering effort, not historical Jira effort or elapsed observation time.

## SH-01 — Bind capability, source, ownership and admission contracts

**Goal:** Make source reuse, named writer scope and current grants executable without replacing native product operators.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/contracts/; tests/autonomy/contracts/

**Evidence Refs:** TASK_DIRECTORY_CONTRACT.md; WINDOWS_RELEASE_EXECUTION.md; evidence/JIRA_READBACK.json

**Dependencies:** 

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Inspect exact portable returns and mission evidence; match reusable interfaces and accepted tests, record absent artifacts without fetching old Mac.; Bind proposed shared home and exact per-task path/action ownership; inventory any conflicting native scheduler from returned evidence.; Define versioned JSON schemas and admission compiler with source/spec/dependency/reviewer hashes, explicit unknowns and designated writer acknowledgement.; Record authority precedence: latest handover/release packet supersedes old Mac freeze; new experiments still require their native records.

**Deliverables:** Bind capability, source, ownership and admission contracts implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Reject unknown schema, mismatched spec/source hash, missing writer, overlapping path claim and forged grant.; Accept a current bounded prior grant without requesting generic approval again; reject cross-mission reuse.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** A second executor can validate one task's inputs and obtain a precise eligible/blocking reason.; Every source capability reused has an exact path/ref and proof scope; missing inputs have respondent and resume action.

**Rollback:** Unadmit revised tasks and restore prior schema reader; do not revoke other workers' valid admissions.

**Next Eligible Action:** Inspect exact portable returns and mission evidence; match reusable interfaces and accepted tests, record absent artifacts without fetching old Mac.

**Estimate:** unit: engineering_hours; low: 6; high: 12; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: BOTS-90; BOTS-111; BOTS-112; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-X01

## SH-02 — Persist events, jobs, attempts and consistent snapshots

**Goal:** Preserve acknowledged observations, action intent and revision history across process loss.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/ledger/; tests/autonomy/ledger/

**Evidence Refs:** ARCHITECTURE.md; reference/WINDOWS_PRIMARY_READINESS.md

**Dependencies:** SH-01

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Implement local transactional tables and unique mission/event/revision keys with append-only attempt/receipt history.; Use schema migrations with checksums and forward/backward-read rules; fsync acknowledged intent under selected durability mode.; Implement consistent snapshot/restore and replay into materialized job views; keep private payloads outside Git.; Add compare-and-set job state transitions and bounded SQLITE_BUSY handling; never fail open on persistence errors.

**Deliverables:** Persist events, jobs, attempts and consistent snapshots implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Kill before and after commit; acknowledged rows survive, uncommitted attempts cannot masquerade as dispatched.; Replay duplicate/out-of-order events and restore snapshot; no duplicate jobs, broken references or erased revisions.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Schema/migration/backup commands and fixture restore receipt are reproducible.; Every acknowledged intent survives restart; storage failure disables affected dispatch.

**Rollback:** Stop consumers, restore known schema-compatible snapshot in reconciliation mode and recover later effects from destinations.

**Next Eligible Action:** Implement local transactional tables and unique mission/event/revision keys with append-only attempt/receipt history.

**Estimate:** unit: engineering_hours; low: 10; high: 20; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A01

## SH-03 — Enforce single-owner claims and effect fencing

**Goal:** Reject stale owners at the actual mutation boundary even after lease expiry or network partition.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/claims/; tests/autonomy/claims/

**Evidence Refs:** TASK_DIRECTORY_CONTRACT.md; missions/whb/EVIDENCE.md

**Dependencies:** SH-02

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Implement atomic claim and resource reservations with mission/task/scope, worker, expiry and monotonically increasing epoch.; Put credential-bearing effect dispatch behind one broker; enforce epoch and current grant just before send.; For existing cloud operators admit a non-mutating bridge first; transfer ownership only after draining/revoking old route and reconciling pending effects.; Require process/credential fencing and destination reconciliation before expiry takeover; failure blocks that scope.

**Deliverables:** Enforce single-owner claims and effect fencing implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Race two claimants: exactly one wins and stale epoch cannot dispatch.; Partition old owner across expiry; restored old worker and bypass route cannot mutate; kill verification failure denies takeover.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Claim/fence audit includes failed contenders and broker enforcement.; No credential path can independently bypass current ownership; if it can, integration is not accepted.

**Rollback:** Disable new broker dispatch, reconcile inflight actions, fence new owner and restore one previously qualified owner.

**Next Eligible Action:** Implement atomic claim and resource reservations with mission/task/scope, worker, expiry and monotonically increasing epoch.

**Estimate:** unit: engineering_hours; low: 12; high: 24; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: BOTS-94; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A01

## SH-04 — Schedule only changed events and due decisions

**Goal:** Make deterministic wakeups and zero idle inference measurable.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/scheduler/; tests/autonomy/scheduler/

**Evidence Refs:** reference/AUTONOMOUS_EXPERIMENTS.md; WINDOWS_RELEASE_EXECUTION.md

**Dependencies:** SH-02

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Add due index, event cursor, next_check_at and decision fingerprint bound to evidence+charter+spec versions.; Coalesce duplicate webhooks/timer ticks; dispatch only eligible changed or due jobs with bounded collector pages/time.; Use existing CL/BF timers as ingress until an explicit ownership transfer; avoid second schedulers.; Persist needs_input/waiting_for_evidence and next justified observation; model calls occur only through SH-14.

**Deliverables:** Schedule only changed events and due decisions implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Advance fake clock across not-due, due, duplicate and changed input cases; exact inference eligibility counts match.; Restart at due time and deliver webhook twice; one evaluation job; clock skew never extends stale ownership.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** An unchanged 24-hour synthetic schedule produces zero model calls; actual deployed idle observation is separately required per mission.; Events and due windows have deterministic, documented wake reasons.

**Rollback:** Disable new trigger and restore last qualified native collector with its cursor and one owner.

**Next Eligible Action:** Add due index, event cursor, next_check_at and decision fingerprint bound to evidence+charter+spec versions.

**Estimate:** unit: engineering_hours; low: 8; high: 16; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: BOTS-148; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A02

## SH-05 — Persist evidence-based business decisions

**Goal:** Turn bounded new evidence into a valid decision without allowing a model to invent authority or outcomes.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/decisions/; tests/autonomy/decisions/

**Evidence Refs:** reference/MISSION_GOALS.md; reference/AUTONOMOUS_EXPERIMENTS.md

**Dependencies:** SH-01; SH-02; SH-04

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Define observation trust/synthetic labels and concise decision records: rationale, alternatives, evidence IDs, selected action or no-action reason.; Build deterministic eligibility and bounded prompt assembly excluding private unrelated content; accept typed proposals only.; Validate current mission goal, metric denominators, available capability and evidence provenance before promotion.; Route ambiguous consequential choices to qualified review within remaining budget; unresolvable proposals become a precise input gap.

**Deliverables:** Persist evidence-based business decisions implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Inject instructions into scan text/comment/source: proposal cannot change grant, mission or destination.; Unknown metrics remain null; synthetic visitors cannot become outside demand; invalid schema yields bounded rejection.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Every selected action references real input evidence and an allowed mission objective.; No model output can grant permission or mark its own remote action verified.

**Rollback:** Pin last accepted policy, archive rejected decision and requeue only on corrected evidence/revision.

**Next Eligible Action:** Define observation trust/synthetic labels and concise decision records: rationale, alternatives, evidence IDs, selected action or no-action reason.

**Estimate:** unit: engineering_hours; low: 8; high: 16; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A03

## SH-06 — Execute effects with deduplication and destination reconciliation

**Goal:** Provide reusable prepare/dispatch/verify/reconcile interfaces for mission-native effect adapters.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/effects/; tests/autonomy/effects/

**Evidence Refs:** ARCHITECTURE.md; reference/AUTONOMOUS_EXPERIMENTS.md

**Dependencies:** SH-01; SH-02; SH-03

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Persist exact payload/account/source/review hash, stable action ID and budget reservation before sending.; Define adapter capability matrix for idempotency, client reference lookup, readback lag, cancellation and pagination.; Implement bounded receiving-system readback; accepted/scheduled/public/delivered/refunded are distinct provider states.; After timeout or crash retain unknown effect and reservation; query destination before any retry; unresolved ambiguity requires intervention.

**Deliverables:** Execute effects with deduplication and destination reconciliation implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Crash before send, after remote success before receipt, and after receipt commit; no duplicate effect in idempotent fixture.; Provider without lookup remains unknown and is not retried; wrong account/readback payload fails; stale token denied.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Adapter can prove one match, qualified absence, or explicit unknown without guessing.; Unknown charged effects retain reserved spend; no duplicate charge/post/send/Jira mutation.

**Rollback:** Pause adapter, reconcile all inflight effects; restore code/config only for reversible local state, use separately granted corrective action for remote effects.

**Next Eligible Action:** Persist exact payload/account/source/review hash, stable action ID and budget reservation before sending.

**Estimate:** unit: engineering_hours; low: 16; high: 32; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A04; SH-A10; SH-A11

## SH-07 — Register experiments, evaluate and choose the next finite action

**Goal:** Make ongoing learning repeatable without substituting a launch for a business outcome.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/experiments/; tests/autonomy/experiments/

**Evidence Refs:** reference/EXPERIMENT_TEMPLATE.md; reference/AUTONOMOUS_EXPERIMENTS.md

**Dependencies:** SH-05; SH-06; SH-09

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Persist predeclared baseline/hypothesis/intervention/comparison/window/exposure/guardrails/budget and writer readback before new action.; Calculate mission metrics from dated receipts; separate gross/net/pending/paid and missing/zero/synthetic.; Evaluate supported/not_supported/inconclusive/invalidated; preserve confounders and original criteria.; Create next versioned experiment, bounded amendment, revert or stop record; wait cheaply for insufficient evidence.

**Deliverables:** Register experiments, evaluate and choose the next finite action implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Low traffic returns inconclusive and no unsupported success; amended window retains original revision.; Two simulated cycles select different next actions from changed evidence without owner launch prompt; no idle model calls.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Original experiment and subsequent decisions remain traceable and immutable.; Real operating acceptance remains in six mission tasks with actual elapsed observations.

**Rollback:** Pause next interventions; preserve measurements and use documented reversible preimage if rollback is qualified.

**Next Eligible Action:** Persist predeclared baseline/hypothesis/intervention/comparison/window/exposure/guardrails/budget and writer readback before new action.

**Estimate:** unit: engineering_hours; low: 10; high: 20; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A05

## SH-08 — Consume owner direction and resume answered questions once

**Goal:** Translate validated owner revisions into acknowledged execution changes and scoped missing-input resumes.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/direction/; tests/autonomy/direction/

**Evidence Refs:** focus/kai-pri-lipi/OWNER_DIRECTION.md

**Dependencies:** SH-01; SH-02

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Implement file input with authenticated issuer binding; optional later ingress uses same schema, not new private assistant roadmap.; Persist recorded/seen/applied/waiting_for_reconciliation/needs_input/superseded/expired states and consumed revision.; Recheck pause/changed direction at job start and before effect; amend experiments without rewriting results.; Create stable scoped question IDs, reuse valid prior answers, bind respondent and answer evidence, wake dependent jobs only.

**Deliverables:** Consume owner direction and resume answered questions once implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Duplicate/superseding/pause directions across restart apply once; untrusted external message cannot expand grants.; Silence leaves input pending, wrong-issuer answer rejected, valid answer resumes exact job once; unrelated job remains eligible.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Owner sees acknowledgement of actual consumed revision, not just saved file.; Question deduplication and safe pause boundary survive process loss.

**Rollback:** Disable faulty ingress, retain direction log and accepted prior revision; reconcile submitted effects before resume.

**Next Eligible Action:** Implement file input with authenticated issuer binding; optional later ingress uses same schema, not new private assistant roadmap.

**Estimate:** unit: engineering_hours; low: 10; high: 18; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A06; SH-A07

## SH-09 — Compile immutable Jira and documentation outboxes

**Goal:** Project plans and outcomes through designated writers with matching, deduplication and readback.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/outbox/; tests/autonomy/outbox/

**Evidence Refs:** TASK_DIRECTORY_CONTRACT.md; WINDOWS_RELEASE_EXECUTION.md; evidence/JIRA_READBACK.json

**Dependencies:** SH-01; SH-02

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Implement atomic immutable proposal files with operation ID, spec/payload hash and predecessor; local deterministic schema and secret checks.; Partition OPO vs four-bot writer queues; leave Lipi/shared writer unbound until designated; no fallback to old Mac writer.; Writer reconciles existing matches, allowed fields, original estimates/actuals, dependencies and accountable roles before admission.; Persist preimage, attempt and native readback; reconcile uncertain issue/comment effect by operation ID before retry; accepted docs use same evidence references.

**Deliverables:** Compile immutable Jira and documentation outboxes implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Replay same proposal and timeout after remote apply; simulated writer makes one effect and returns one matching readback.; Null candidate key cannot clear issue fields; spec revision invalidates old admission; outage leaves independent preparation runnable.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** A task cannot be marked admitted solely from queue placement or HTTP acknowledgement.; Every projection names its sole scope owner; history/actuals remain preserved.

**Rollback:** Stop projection, retain immutable proposals and native preimages; corrective Jira change is separately reviewed by rightful writer.

**Next Eligible Action:** Implement atomic immutable proposal files with operation ID, spec/payload hash and predecessor; local deterministic schema and secret checks.

**Estimate:** unit: engineering_hours; low: 10; high: 20; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A08

## SH-10 — Bound retries, reviews and repairs

**Goal:** Keep finite repair/review work and exact-source verdicts attributable.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/review/; tests/autonomy/review/

**Evidence Refs:** TASK_DIRECTORY_CONTRACT.md; WINDOWS_RELEASE_EXECUTION.md

**Dependencies:** SH-01; SH-02; SH-06

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Persist attempt counters across restart; retry only classified transient read failures or confirmed-absent effects.; Define max two targeted repairs per task unless stricter, finite reviewer call/time caps and no paid fallback.; Build review manifest of source/spec/fixture/artifact hashes and actual reviewer identity/model/commands vs inspection.; Any source change invalidates affected approval; unresolved review blocks dependent release only.

**Deliverables:** Bound retries, reviews and repairs implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Restart cannot reset attempts; deterministic failure is not retried; missing distinct-model identity cannot pass that gate.; Modify one reviewed file and reject stale approval; two failed repairs produce explicit residual and next independent action.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Reviews distinguish independent same-model review from distinct-model approval.; Repair exhaustion is durable and no retry storm occurs.

**Rollback:** Revert to prior reviewed candidate; retain failures and do not erase counters to regain budget.

**Next Eligible Action:** Persist attempt counters across restart; retry only classified transient read failures or confirmed-absent effects.

**Estimate:** unit: engineering_hours; low: 6; high: 12; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A09

## SH-11 — Qualify Windows runner, independent startup and restore

**Goal:** Run finite jobs without Mac/RDP dependency and recover without orphan processes or duplicate effects.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/hosts/windows/; tests/autonomy/hosts/windows/

**Evidence Refs:** reference/WINDOWS_PRIMARY_READINESS.md; ARCHITECTURE.md

**Dependencies:** SH-02; SH-03; SH-06; SH-13

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Implement Job Object process creation/assignment before resume, kill-on-close, non-inherited handles and finite limits; fail closed on unsupported assignment.; Persist startup epoch, task-source hash and host-local secret references; qualify noninteractive startup through approved existing host route.; On startup validate DB/schema then reconcile unknown effects before new claims.; Add consistent backup, restore dry-run, retention and fallback procedure; restore gap always starts reconciliation mode.

**Deliverables:** Qualify Windows runner, independent startup and restore implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Spawn child+grandchild and kill supervisor/timeout/stop; all descendants gone and receipt persisted.; Restart host process with mobile Mac disconnected/RDP absent; one queued job resumes once; corrupted backup fails closed.; Recover from pre-effect snapshot after destination success; reconcile destination rather than replay.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Actual Windows receipt proves tree cleanup, restart, one owner and independent startup.; Measured recovery target and observed limitations recorded; no claimed R730 migration.

**Rollback:** Disable owned new startup entry, fence its effects and restore previous qualified owner plus snapshot with reconciliation.

**Next Eligible Action:** Implement Job Object process creation/assignment before resume, kill-on-close, non-inherited handles and finite limits; fail closed on unsupported assignment.

**Estimate:** unit: engineering_hours; low: 16; high: 32; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: BOTS-100; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A12; SH-A13; SH-A18

## SH-12 — Deliver actionable incidents and operational status

**Goal:** Surface meaningful failures and owner decisions without repetitive messages.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/alerts/; tests/autonomy/alerts/

**Evidence Refs:** focus/kai-pri-lipi/OWNER_DIRECTION.md; ARCHITECTURE.md

**Dependencies:** SH-02; SH-08

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Define incidents for unknown effect, failed receipt, stale source/provider, expired grant, storage/restore fault and exhausted limit.; Persist incident fingerprint, severity, affected task and useful next action; deduplicate until material change.; Use owner-authorized delivery channel with receipt/ack, file queue if unavailable; store no private content in Git.; Expose separate prepared/reviewed/released/autonomous/business-result states using evidence-backed summaries.

**Deliverables:** Deliver actionable incidents and operational status implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Repeated same fault creates one notification; material escalation/new evidence can create one revision.; Delivery timeout reconciles or remains pending, never falsely acknowledged; channel outage preserves file incident.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** An operator can identify the affected task and execute a named recovery action.; Unknown or unobserved runtime state is not healthy/zero.

**Rollback:** Disable faulty notifier, retain file incident queue and last acknowledged state.

**Next Eligible Action:** Define incidents for unknown effect, failed receipt, stale source/provider, expired grant, storage/restore fault and exhausted limit.

**Estimate:** unit: engineering_hours; low: 6; high: 12; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A14

## SH-13 — Enforce mission privacy, secrets and source trust boundaries

**Goal:** Keep each mission's credentials and customer data scoped while allowing sanitized shared evidence.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/security/; tests/autonomy/security/

**Evidence Refs:** reference/ACCOUNTS_CHANNELS_AND_HOSTS.md; CLOUD_PUBLICATION.md

**Dependencies:** SH-01; SH-02

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Define data inventory/retention/access/delete/export for mission payloads and hashed public receipts.; Inject secrets by host-local reference; effect broker restricts resource scope and prevents secrets entering logs/prompts/outboxes.; Validate webhook signatures/replay, URL/protocol/redirect egress policy and untrusted content boundaries in adapters.; Provide redaction/sanitization before private Git publication and restore; no Kai/Pri personal-data export.

**Deliverables:** Enforce mission privacy, secrets and source trust boundaries implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Cross-mission read, forged webhook, private-network URL/redirect, secret-containing exception and over-retention fixtures fail safely.; Deletion removes eligible payloads while retaining minimal audit identifiers; backups follow declared retention.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Artifacts contain secret references only; customer/order content stays access-controlled.; Each adapter has explicit input trust, egress and payload-size rules.

**Rollback:** Revoke affected scoped capability, quarantine payloads and rotate only demonstrated exposed secret via authorized route.

**Next Eligible Action:** Define data inventory/retention/access/delete/export for mission payloads and hashed public receipts.

**Estimate:** unit: engineering_hours; low: 10; high: 20; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: BOTS-92; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A15

## SH-14 — Enforce model, tool and monetary limits at dispatch

**Goal:** Prevent unbounded usage and silent paid fallback, with truthful cost accounting.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/limits/; tests/autonomy/limits/

**Evidence Refs:** reference/AUTONOMOUS_EXPERIMENTS.md; reference/WINDOWS_PRIMARY_READINESS.md

**Dependencies:** SH-01; SH-02; SH-05

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Define job/mission/day ceilings for model tokens/time, tool calls/pages, money/currency and concurrent experiments; unknown monetary authority blocks paid effects.; Atomically reserve worst-case authorized cost before dispatch; reconcile actuals/refunds/released reservations without losing unknown-effect liability.; Route deterministic tasks without model, use only qualified existing local/cloud profiles; unavailable profile queues work.; Record actual model/provider/effort/host/tokens and cost or null reason; shared author totals once, observation waits never worklogs.

**Deliverables:** Enforce model, tool and monetary limits at dispatch implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Concurrent reservations cannot exceed cap; missing/exhausted cap rejects dispatch; restart preserves counters.; Provider/model fallback cannot occur implicitly; zero-idle test reports no inference calls; absent telemetry remains null.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Caps are enforced outside the model at the effect boundary and survive restart.; No install, subscription, purchase or new paid quota is inferred from this plan.

**Rollback:** Disable paid/model dispatch, keep deterministic eligible reads and settle reservations against actual receipts.

**Next Eligible Action:** Define job/mission/day ceilings for model tokens/time, tool calls/pages, money/currency and concurrent experiments; unknown monetary authority blocks paid effects.

**Estimate:** unit: engineering_hours; low: 10; high: 20; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A16

## SH-15 — Review shared faults and qualify integration harness

**Goal:** Provide exact-source independent acceptance of common mechanics before each mission claims autonomy.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/acceptance/; tests/autonomy/acceptance/

**Evidence Refs:** ARCHITECTURE.md; AUTHORING_CONTRACT.md

**Dependencies:** SH-03; SH-04; SH-06; SH-07; SH-08; SH-09; SH-10; SH-11; SH-12; SH-13; SH-14

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant

**Implementation Steps:** Freeze candidate source and evidence manifest; commission independent qualified reviewer and record actual identity without inventing distinct-model approval.; Run fault matrix for duplicate/out-of-order events, wrong account/mission, stale owner, pause, limits, crashes at all effect boundaries, restore gap and writer outage.; Use fixtures only for shared semantics; publish synthetic labels and map remaining real receipt requirements to mission acceptance tasks.; Issue versioned compatibility contract and repair only findings within bounded budget.

**Deliverables:** Review shared faults and qualify integration harness implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** All fault cases pass at exact candidate hash; mutation of a candidate invalidates review.; Every mission has an integration path and real-cycle criteria; common fixture success cannot set its runtime/business state complete.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Attributable verdict has exact source/test hashes and no unresolved critical findings.; Compatible shared version is available for native operator integrations; actual mission external receipts remain their own gates.

**Rollback:** Withdraw candidate version, pin prior approved version; affected integrations wait while independent releases continue.

**Next Eligible Action:** Freeze candidate source and evidence manifest; commission independent qualified reviewer and record actual identity without inventing distinct-model approval.

**Estimate:** unit: engineering_hours; low: 12; high: 24; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: Medium to high: existing-source qualification, writer admission and per-adapter limitations may narrow or amend scope

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G04

**Requirement Ids:** SH-A17

## SH-16 — Qualify optional R730 central-hub migration and fallback

**Goal:** Move qualified ownership and recoverable state one mission at a time without gating Windows releases.

**Status:** planned

**Owner Role:** Future admitted shared-runtime implementer; independent reviewer; designated shared Jira writer pending

**Source Repo:** pri8771/astra-bot-launch (proposed runtime home; SH-01 binds accepted equivalents)

**Owned Paths:** runtime/autonomy/hosts/r730/; tests/autonomy/hosts/r730/

**Evidence Refs:** focus/kai-pri-lipi/HOST_PLAN.md; WINDOWS_ASTRA_ULTRA_HANDOVER.md

**Dependencies:** SH-11; SH-15

**Prerequisite Inputs:** SH-I01: exact-source admission and writer scope; SH-I02: current capability/resource/budget grant; SH-I04: R730 destination/service/backup qualification

**Implementation Steps:** Verify current R730 capacity/storage/backup/official application route and required service identity; propose exact changes and reuse existing approvals.; Stage versioned source/schema/config templates and provision scoped host-local secrets without exporting credential stores.; Drain old mission owner, disable/revoke its mutation route, reconcile in-flight effects, snapshot and restore to new hub.; Advance ownership epoch, verify one allowed effect/readback and restart, then rehearse fenced rollback without concurrent owners.

**Deliverables:** Qualify optional R730 central-hub migration and fallback implementation and versioned contract; Exact-source test/receipt manifest and executor return

**Tests:** Partition old host during migration: no second effect owner; unresolved old action blocks promotion.; Restore checksum/schema/credentials verified; one correct-account receipt and next due decision; rollback has no duplicated effect.

**Review:** identity: Independent reviewer records actual model/provider/effort and author distinction; distinct-model approval only when evidenced; source_binding: Reviewed source/spec/test/artifact SHA256; changed bytes invalidate approval; max_targeted_repairs: 2; verdict: Accept or request bounded repair with unresolved criteria; no synthetic-as-real claims

**Acceptance:** Actual R730 migration/restore receipt exists per moved mission; Windows temporary independence already qualifies separately.; i9 remains deferred; no mobile Mac dependency; no unapproved installations/network changes.

**Rollback:** Fence R730, reconcile all inflight effects, restore known Windows/current-cloud owner and re-read destination before resuming.

**Next Eligible Action:** Verify current R730 capacity/storage/backup/official application route and required service identity; propose exact changes and reuse existing approvals.

**Estimate:** unit: engineering_hours; low: 12; high: 24; assumptions: Active implementation, relevant tests and one review plus bounded repair; excludes owner/provider/elapsed observation wait; Reuse qualified existing native operators and accepted contracts; do not sum duplicate scope after writer reconciliation; dependency_risk: High: host capacity, scope, credential and takeover evidence pending

**Jira:** key: None; candidates: ; matching_action: Compare exact requested scope against current candidate descriptions/evidence; reuse or extend only the delta; preserve original estimates/actuals and native links; return current source-bound readback before admission; writer: Shared scope writer designation required; planner outbox-only; never old-Mac fallback

**Effect Gates:** SH-G01; SH-G02; SH-G03; SH-G09; SH-G04

**Requirement Ids:** SH-A18
