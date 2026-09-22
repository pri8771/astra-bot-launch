# Next-round closure cards

These are bounded integration/verification additions to the existing SB-* cards, not replacements for their complete implementations. Ownership is assigned at NR-01; role names do not authorize extra workers. The running Fable/Cursor tasks are untouched. Open only the current section. Build prerequisites and external/live gates are separate in NEXT_ROUND_TASKS.json.

Common return: exact source/evidence refs, changed paths, command/results including skips, evidence class by stage, failed predicates, limitations, requested SUBMITTED status, and the next permitted action. Use a separate isolated test state. No real external call, scheduler installation, account action or publication without its applicable scope. Every proposed signature is resolved against the pinned source before implementation.

## NR-01

**Baseline and predicates.** Input: fresh canonical review, registry, current worker submissions and exact branch diffs. Output: BASELINE.json, an ownership map and a lead-approved predicate map. Reconcile schema versions, stale READY/SUBMITTED status and build-versus-LIVE prerequisites. Split SB-S20-007 rehearsal evidence from its live acceptance; SB-V23-099 cannot depend on a fake LIVE pass. Allowed changes: coordination only, followed by an integration worktree. Test: a missing dependency, mixed candidate SHA, unresolved owner collision or stale lead decision blocks release. Do not rebuild accepted artifacts. Done when every next action names one owner, pinned inputs and the specific evidence predicate it needs.

## NR-02

**Wire compatibility.** Input: actual specialist v2, strategy, planner and evidence records. Output: a schema compatibility table and serializers/validators in their existing modules or a small adapter. Preserve current Fable APIs where sound. Specialist v1/unknown widening fields cannot silently deserialize as v2. Tests: round-trip, missing fields, old-version handling, NaN/infinity, malicious authority fields and cross-persona IDs. Add explicit migration rather than broad dict merges. Done when production producers and consumers agree on the same bytes/schema for an integrated candidate.

## NR-03

**Trusted model dispatch.** Input: the current R07-041 repair and every CLI/library/specialist route. Output: a reviewed provider factory/handle boundary at actual call/spawn. No adaptive=False flag, arbitrary callable, local manifest path or source label may grant production execution. Tests use spies, not real models: direct-library bypass, false fixture provider, revoked/expired/wrong-scope grant, configured-mode/object mismatch and key/PAYG fallback. Done when all unauthorized variants produce zero dispatches and attributable refusal receipts.

## NR-04

**Shared call reservations.** Input: trusted dispatch and parent/specialist budgets. Output: atomic reservation/outcome/reconciliation through the existing ledger. Tests: two processes racing the last slot; exception after dispatch; crash before result; deleted/torn slot; duplicate attempt ID; nested specialist sum; exhausted allowance. Require one winner and no regained budget after uncertainty. A real smoke call needs its own bounded grant. Done when every actual dispatch has a durable pre-dispatch reservation and no unaccounted child call.

## NR-05

**Final-content review binding.** Input: real-source-compatible candidate/evidence objects and fact/voice/cultural review modules. Output: hashes binding final payload, material claims, source bytes and attributable review. Test relabeling a fact as framing, changed number/negation after review, forged operational stance, unsupported PARTIAL and copied reviewer identity. Repair or reject; never silently retain a prior pass after material text changes. Done when normal formatting/generation paths cannot enqueue a payload whose required reviews belong to different content.

## NR-06

**Honest dry-run experiment state.** Input: V0.6 runner and experiment/learning stores. Output: prospective experiment registration and evidence-based learning without public treatment/performance claims. Tests: absent measured baseline, no publication, missing analytics, repeated run, withheld candidate and restart. Persist PLANNED/AWAITING_PUBLICATION or the existing equivalent; do not create success/failure engagement outcomes. Done when all three bot runs can produce complete truthful manifests with missing measurement explicitly represented.

## NR-07

**Due-task scheduler and target host.** Input: accepted host preflight and existing worker_once/lease/scheduler assets. Output: a due/last-served ordering rule plus real native-scheduler/job receipts on the approved host. Test all three bots eligible, one repeatedly blocked, all leases held, crash and restart, unavailable filesystem locking and stale direction. A process inside a cloud container does not become an owner Mac because the user opened Claude on a Mac. Done when repeated native firings serve all three eligible bots without overlap/starvation and exit cleanly.

## NR-08

**Bounded developer invocation.** Input: approved engineering assignment and verified installed worker client. Output: a separate ENGINEERING_ARTIFACT adapter with fixed path/tool/budget/branch scope, child invocation receipt and material work result or blocker. Test denied command, no authorization, timeout, dirty worktree and rejected output path. Use supported noninteractive operation, not a kept-open chat or a bot NO_ACTION as evidence of coding. Real invocation consumes its own authorized development-worker budget. Done when the scheduler actually launches and records bounded implementation work.

## NR-09

**Actual lead round trip.** Input: worker submission A and a functioning authorized lead-review transport. Output: lead review/new direction B at a new canonical SHA, then a later independently scheduled worker consuming B. Tests: replayed direction, stale/offline read, halt and wrong-lane assignment. Record actual lead execution plus worker acknowledgement; a worker-authored pretend lead comment is invalid. Done when two documented cycles complete without the owner copying tasks. No automation is installed by this plan itself.

## NR-10

**Account capability dossier.** Input: verified owned existing accounts and, only when necessary, the verified Unsubscriber alias route. Output: exact five-platform identity/route/scopes/quota/readback map and one compact owner action list. Check current official support rules at execution. Unknown/paid/review-gated routes stay blocked. Credentials remain in the approved secret store. No unrelated account is created merely to show activity. Done when setup blockers and the smallest remaining owner steps are precise; V0.8 only closes after all required real routes are actually verified.

## NR-11

**Uncertain effects.** Input: verified destination registry and publication wrapper. Output: one durable attempt/reservation and external readback/reconciliation state. Engineering tests crash after send, return ambiguous HTTP success, replay IDs, mismatch account and delete/private a post. Real canaries need explicit grants. Do not resend an UNCERTAIN effect until resolved. Done when attainable delivery/deduplication guarantees are stated accurately and each authorized canary has verified destination/permalink or a retained unresolved failure.

## NR-12

**Measurement-to-learning adapter.** Input: real raw analytics, publication lineage, experiment windows and existing metric/audience engines. Output: compatible observations -> honest experiment closeout -> hypothesis/strategy evidence refs. Test repeated cumulative snapshots, missing denominator, partial pagination, lagging windows, timezone boundaries and cross-persona data. Insufficient evidence yields INCONCLUSIVE. Done when a real measurement is consumed by a later production decision, not just stored or plotted.

## NR-13

**Persistent version publication.** Input: current Fable strategy store and existing lease/fence. Output: no-overwrite versions, expected-version CAS, authoritative transaction record and recoverable indexes. Test concurrent version allocation, missing/stale fence, crash at each durable write, duplicate proposal and rollback. Test stores may be unfenced only in explicitly isolated engineering mode. Done when no interrupted write exposes a partially published active state and prior accepted bytes never change.

## NR-14

**H1: strategy -> context.** Input: scoped active strategy and normal decision.run_cycle. Output: actual ReasoningContext carries the strategy ref/objective/allowed priorities. Tests: priority change, expired strategy fallback, wrong persona and authority-bearing strategy fields. Safety remains deterministic. Done when the normal worker demonstrably uses the active strategy rather than only loading the module in a standalone test.

## NR-15

**H2: revision -> commit.** Input: valid bounded proposal and H1 integration. Output: validated immutable revision and adoption receipt inside the production fence transaction. Tests: lost fence after reasoning, stale version, unresolved evidence, duplicate proposal_id, negative/non-finite weights and nested-lock deadlock. Done when one cycle commits exactly the allowed revision and restart/replay does not duplicate it.

## NR-16

**H3: plan -> work.** Input: active PlanDAG with due dependency-ready tasks. Output: normal worker claims one actual plan task and stores terminal evidence. Tests: parent cancellation, wrong plan version, unavailable route, completed-task preservation on replan, fairness and crash recovery. A plan that can only be printed is incomplete. Done when planned work rather than a fixed demo task drives the production dispatcher.

## NR-17

**H4: task -> specialist.** Input: real SPECIALIST task, canonical contract and safe runner. Output: child invocation/result validation and fenced parent adoption or rejection. Tests: unexpected authority, result for another persona/parent, tampered output hash, late response, duplicate result and lost parent fence. Parent changes only approved adopted records; rejected output changes no parent-private state. Done when a specialist result affects the remaining plan through the real dispatcher.

## NR-18

**Context/tool broker.** Input: specialist contract and trusted adapters. Output: scoped materialized inputs, allowlisted broker operations and validated output paths. Tests: traversal, absolute path, symlink, unapproved evidence ref, secret-bearing context, forged cross-brand identity and false fixture provider. Default specialists cannot execute arbitrary generated code/shell. Declare logical isolation honestly; arbitrary plugins need a real OS boundary before release. Done when every supported tool/data access is checked rather than relying on the model to obey prose.

## NR-19

**Deadline and late-result closure.** Input: brokered runner and durable reservations. Output: actual deadline supervision, cancellation/revocation, kill/wait cleanup and truthful terminal receipt. Test an adapter that ignores cooperative checks, a hanging provider and a child process; verify zero late adoption after expiry/lease loss. Do not mistake Future timeout for task termination. Any real provider case requires a grant. Done when timeout cannot leave a continuing writer or adoptable late result behind.

## NR-20

**Integrated rehearsal.** Input: pinned combined runtime and all four hooks. Output: one fixture-labeled run through normal entrypoints: strategy -> goal -> task -> researcher/reviewer -> adoption -> next decision. Block network/model/public dispatch for the rehearsal. Test positive, insufficient-evidence, malicious-result, timeout and resume paths. Attach this as engineering evidence only; it does not mark SB-S20-007 LIVE or operational V2.3 accepted. Done when isolated module success is no longer the only proof of composition.

## NR-21

**Real V2.3 mission.** Input: accepted prior operational gates, approved persistent host, real scoped goal, compatible measurements and exact bounded model grants. Output: normal production path invokes at least two distinct real specialist roles, validates outputs, changes/holds strategy appropriately and schedules subsequent work. Independent review verifies raw receipts against the candidate. No-action-only output cannot prove unused generation/specialist stages. Done only on accepted real evidence; retain precise BLOCKED/INCONCLUSIVE/FAIL instead of manufacturing a change.

## NR-22

**Operator status and restore.** Input: actual running candidate, receipt store and retained non-secret backup. Output: read-only status command plus tested restore/rollback runbook. Show source ref, due/blocked work, last real invocation, grants/budget state and missing acceptance predicates without inferred green status. Restore on a separate supported data root and verify hashes/restart/no-duplicate effects. Done when the system can be inspected and recovered without hidden chat state or a fake dashboard.

## NR-23

**Memory feedback hook.** Reuse SB-S24 modules. Input: real accumulated lessons/strategy/incidents. Output: scoped retrieval refs in the next production context. Tests: stale, contradicted, seasonal and tombstoned entries; no cross-persona retrieval. Existing history age is reported honestly. Done when an actual recorded lesson is retrieved and affects a later decision through the normal path, not merely a memory-store unit test.

## NR-24

**Segment feedback hook.** Reuse SB-S25 modules. Input: sufficiently populated compatible aggregate observations. Output: segment-ref-bound strategy/experiment proposals. Tests: sparse/identical observations, sensitive features, tiny-cohort disclosure, unstable split and another persona's segment. Insufficient data stays insufficient. Done when a supported real aggregate distinction drives scoped behavior; never force fake audience clusters to obtain a passing test.

## NR-25

**Trend feedback hook.** Reuse SB-S26 modules. Input: newly captured canonical trends and persona context. Output: relevant bounded experiment in the actual queue or explicit NO_ACTION. Tests: duplicate syndication, old story newly retrieved, unknown velocity, expiry and irrelevant virality. Done when current trend evidence is traceable to actual selected or declined work and the original source claims remain supported.

## NR-26

**Idea/sequence execution hook.** Reuse SB-S27 modules and public-effect wrapper. Input: a supported canonical idea and verified platform capabilities. Output: materially native reviewed variants, explicit sequence and shared lineage in real scheduler receipts. Tests: factual drift, duplicate variants, incompatible metrics and media that does not meet the route requirement. Public effects remain separately granted. Done when scheduler execution follows the sequence and readback/analytics remain linked without conflation.

## NR-27

**Allocation enforcement hook.** Reuse SB-S28 modules. Input: candidate work, real quota/capacity and reserves. Output: reservations that the actual scheduler obeys. Tests: last-slot race, exhausted account/provider, double reservation on restart, reliability reserve and exploration starvation. Done when changing an allowed budget changes executed work, rather than merely returning a different score list.

## NR-28

**Self-audit to reviewed work.** Reuse SB-S29 modules. Input: actual telemetry and separately labeled seeded defects. Output: deduplicated bounded repair artifacts with evidence/tests/rollback. Tests: detector self-acceptance, direct deployment, recursive repair spam, inadequate telemetry and private data leakage. Done when a meaningful finding reaches normal lead review and cannot silently change production code or authority.

## NR-29

**Brand migration.** Reuse SB-S30-001/002/004. Input: approved brand-to-bot/persona mapping and verified backup. Output: explicit unambiguous scopes with preserved legacy state. Test repeated/partial migration, ID collision, stale worker, missing map and restore. Do not share a default brand implicitly. Done when both old and new scoped data are reconciled and cross-brand negative access tests pass on the supported deployment.

## NR-30

**Shared knowledge boundary.** Reuse SB-S30-003/008. Input: an explicitly approved reusable public fact/lesson and consumer scope. Output: permission-checked retrieval plus evidence and revocation handling. Tests: private hypothesis, raw community personal data, secret ref, unauthorized consumer, altered source and stale cached permission after revocation. Done when one allowed fact can be reused and a forbidden private fact cannot, without global unscoped memory.

## NR-31

**Portfolio-to-runtime integration.** Reuse SB-S30-005/006/007/009. Input: actual brand goals, scoped specialist contracts and fixed budgets. Output: bounded per-brand planned/claimed work and later portfolio evaluation. Tests: shared-budget overrun, starvation, wrong-brand specialist result and unsupported authority widening. Done when the same deployed runtime carries portfolio decisions through execution and outcome evidence instead of running a separate portfolio demonstration.

## NR-32

**Final V3.0 packet.** Input: pinned candidate, all required accepted predecessor artifacts, actual concurrent multi-brand run, restore and independent evidence review. Output: one release dossier with requirement-to-run mapping and exact limitations. Check every LIVE stage separately, including real brands/personas, shared fact, denied private access, actual allocation/specialists, organizational lesson and bounded repair proposal. No stage may pass because a fixture flag says LIVE. Only the lead accepts the version; open host/account/model/data gates remain explicit blockers.
