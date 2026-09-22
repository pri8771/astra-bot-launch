# V2.0 → V2.3 implementation spec (worker-facing)

Author lane: `fable-planning` (session `s-20260921T202026Z-a90ea082`). Status: **PROPOSED for lead review** — nothing here changes canonical artifact status. This document is referenced by every `artifact-packets/v18-v30/SB-S20-*`, `SB-S21-*`, `SB-S22-*` and `SB-S23-*` packet so the packets stay short.

Read this once, then only the packet you are implementing. Verify every reuse target against the primary implementation branch head before coding; module line numbers below were observed at `cursor/social-bots-recovery-v07-20260921@488ce0c` (runtime source at `d7ecb25`).

## 0. Ground rules that apply to every slice

1. **New files only.** Every V2.x slice creates its own `runtime/<module>.py` and `tests/test_<module>.py`. No slice edits `decision.py`, `state.py`, `reasoning.py`, `worker.py`, `paths.py`, `leasing.py`, `pipeline.py` or `analytics.py`. Integration hooks into those files are separate lead-assigned tasks (§7).
2. **Engineering evidence only.** Every slice below S20-007 / S21-006 / S22-007 / S23-008 is `Evidence class: ENGINEERING`. Fixtures are labeled `provenance: "fixture"`; a fixture can never be presented as LIVE evidence and must be structurally rejected by any acceptance/validator path that claims operation (mirror `growth_evaluator.evaluate(require_evidence=True)` and `divergence_verifier`).
3. **Deterministic policy owns authority.** A model/provider may *propose* (typed, validated) and never *decide*. Authority, budgets, effects, dedup, scheduling and stop conditions are deterministic code with tests.
4. **No live model call** in any slice. Any provider seam must resolve through `runtime.live_route_guard.check()` / `runtime.authorization.authorize()`; without a canonical manifest the seam fails closed. Tests use deterministic fixture providers only.
5. **Persona scope is structural.** Every record carries `bot` + `persona`; every store path goes through `runtime.paths` namespace helpers; cross-persona reads are only via explicit `admin_*` functions (pattern: `runtime/isolation.py`).
6. **Durable writes inside the cycle go through the fence.** Any function that a future `decision.run_cycle` hook will call to persist state accepts an optional `fence` (`runtime.leasing.Fence`) and, when given, performs its writes inside `fence.fenced_commit(...)`. With `fence=None` (unit tests, dry runs) writes run unguarded, exactly like `decision._commit`.
7. **Immutable versions, append-only history.** Never rewrite a prior version file. Use `runtime.jsonstore.write_json` (atomic) for version files and `append_jsonl` for history.
8. **Missing ≠ zero.** Absent metrics/evidence stay `None`; they can never score, count toward a floor, or prove anything.
9. **Return contract.** Submit as `SUBMITTED` with exact source SHA, focused + full test commands and counts, evidence paths, fixture-vs-live classification, known limits. Only ChatGPT lead marks ACCEPTED.

## 1. Existing reuse targets (verified on the Cursor branch)

| Need | Reuse | Notes |
|---|---|---|
| Namespaced storage | `runtime/paths.py` — `state_dir(ns)`, `receipts_dir(ns)`, `base()`, `_SAFE` id regex | `SBOTS_HOME` overrides root for tests. Do not add helpers there; derive sub-dirs in your module from `paths.base()` / `paths.state_dir(bot)`. |
| Atomic JSON / JSONL | `runtime/jsonstore.py` — `write_json`, `read_json`, `append_jsonl`, `read_jsonl`, `now_iso` | |
| Ownership fence | `runtime/leasing.py` — `acquire`, `renew`, `release`, `inspect`, `Fence.fenced_commit`, `FenceLost` | Specialists get their own lease task id (`specialist:<worker_id>`). |
| Authority model | `runtime/decision.py::Authority` (`can_public_post=False`, `can_spend=False`, `can_message_users=False` never granted by the loop) | Specialists do NOT reuse `Authority`; they get a narrower type (§5.1) so public/spend fields cannot exist on them. |
| Proposal validation pattern | `runtime/reasoning.py::validate_candidate / validate_proposal`, `ReasoningProvider` protocol | Copy the *pattern* (validate before score, fail closed on malformed) for `StrategyRevisionProposal`, `PlanDAG`, `WorkerResult`. |
| Live gate | `runtime/live_route_guard.py::check`, `runtime/authorization.py::authorize / CallBudget` | Only path a provider may be constructed through. |
| Receipts | `runtime/receipts.py::write_receipt(namespace, kind, task_id, worker_id, ...)`, `runtime/invocation.py::InvocationReceipt` | Specialist receipts use `kind="specialist"`. |
| Persona-private reads | `runtime/isolation.py` (`persona_*` readers, `admin_all_records`) | Strategy/plan readers follow the same two-tier shape. |
| Intelligence inputs | `runtime/growth_evaluator.py` (`GrowthOpportunity`, `evaluate`), `runtime/experiment_engine.py` (`Experiment`, `to_learning_ref`), `runtime/audience.py` (`Hypothesis`, `confidence`), `runtime/metrics.py` (`NormalizedObservation`, `is_stale`) | **Currently only on `claude/social-bots-intelligence-repair-v2` (head `33b9c7b`), not on the Cursor branch.** See `V23_CRITICAL_PATH.md` §2 — consolidation is a prerequisite for S20-002/S20-005. |
| Decay pattern | `runtime/audience.py::_decayed` (half-life over observation age) | Reuse the formula for strategy confidence decay (S21-002). |
| Existing tests to mirror | `tests/test_policy_boundary.py`, `tests/test_isolation.py`, `tests/test_fencing.py`, `tests/test_v04_authorization_gate.py` | Adversarial style: authority smuggling, cross-persona leak, fence loss, no-manifest refusal. |

## 2. Shared record types

All dataclasses carry `schema_version: int = 1`, `bot: str`, `persona: str`, `created_at: str` (`jsonstore.now_iso()`), and `as_dict()`. Validation functions return `list[str]` of errors (empty = valid), like `reasoning.validate_candidate`.

### 2.1 StrategyState (`runtime/strategy.py`) — per `STRATEGY_SCHEMA.md`

```
StrategyState(
  strategy_id: str,           # stable per (bot, persona): f"strat-{bot}-{persona}"
  version: int,               # 1..N, strictly increasing, immutable once written
  bot, persona,
  objective: str,
  priority_audiences: list[str], priority_topics: list[str],
  platform_weights: dict[str, float], format_weights: dict[str, float],   # each sums to 1.0 (±1e-6), no negatives
  experiment_priorities: list[str], active_hypotheses: list[str],       # ids only, never copies
  constraints: list[str],
  evidence_refs: list[dict],  # CROSS_LANE §1 EvidenceRef dicts or {"kind","id"} refs; never raw numbers
  supersedes: int | None,     # previous version number
  status: str,                # S21-001 lifecycle: PROPOSED|ACTIVE|COOLING|SUPERSEDED|ROLLED_BACK|EXPIRED (S20 uses only ACTIVE|SUPERSEDED|ROLLED_BACK)
  confidence: float | None, review_by: str | None, expires_at: str | None,   # S21 fields; None allowed in S20
  revision: dict | None,      # {"proposal_id","policy_verdict_id","rollback_condition","restores_version"?}
  provenance: str,            # "fixture" | "evidence"
)
```

Storage (persona-private, derived in-module):
```
paths.state_dir(bot) / "strategy" / persona / f"v{version:04d}.json"   # immutable
paths.state_dir(bot) / "strategy" / persona / "HEAD.json"              # {"active_version": int|None, "updated_at"}
paths.state_dir(bot) / "strategy" / persona / "HISTORY.jsonl"          # append-only {version, event, proposal_id, verdict_id, at}
```
`persona` must match `paths._SAFE`; validate with the same regex (copy it; do not import the private name).

### 2.2 StrategyRevisionProposal + ChangeOp (`runtime/strategy_revision.py`)

Typed ops exactly per `STRATEGY_SCHEMA.md`: `SET_PLATFORM_WEIGHT`, `SET_FORMAT_WEIGHT`, `ADD_TOPIC_PRIORITY`, `REDUCE_TOPIC_PRIORITY`, `ADD_EXPERIMENT_PRIORITY`, `RETIRE_EXPERIMENT_PRIORITY`, `UPDATE_AUDIENCE_FOCUS`, `NO_CHANGE`, `REQUEST_MORE_EVIDENCE`.

```
ChangeOp(op: str, target: str | None, value: float | str | None, evidence_refs: list[dict])
StrategyRevisionProposal(
  proposal_id, bot, persona, current_strategy_id, current_version,
  changes: list[ChangeOp], reason: str, evidence_refs: list[dict],
  expected_effect: str, expected_learning: str,
  confidence: float | None, uncertainty: list[str],
  reversibility: str,              # "full" | "partial" | "none"
  rollback_condition: dict,        # {"metric": semantic, "direction": "below"|"above", "threshold": float, "window_hours": float}
  required_authority: str,         # always "none"; anything else is rejected by policy
  proposer_id: str,                # "deterministic-v1" | provider_id
  created_at,
)
```
`validate_proposal(p, current: StrategyState) -> list[str]`: unknown op, missing target, non-finite value, weight outside [0,1], `required_authority != "none"`, `current_version` mismatch, empty `evidence_refs` on any op other than `NO_CHANGE`/`REQUEST_MORE_EVIDENCE`, dict-merge payloads (any key not in the dataclass) → error.

### 2.3 PolicyVerdict (`runtime/strategy_policy.py`)

```
PolicyConfig(min_evidence_count=2, min_confidence=0.5, max_weight_delta=0.15, max_ops_per_revision=3,
             cooldown_hours=72, max_evidence_age_hours=24*14, allowed_platforms: set[str] | None=None)
PolicyVerdict(verdict_id, proposal_id, bot, persona, verdict: "ACCEPT"|"REJECT"|"REQUEST_MORE_EVIDENCE",
              reasons: list[str], applied_limits: dict, evaluated_at)
validate(proposal, current: StrategyState, *, evidence: EvidenceIndex, availability: dict,
         config: PolicyConfig, now: str | None = None) -> PolicyVerdict
apply(current: StrategyState, proposal, verdict) -> StrategyState   # pure; new version object, not persisted
```
`EvidenceIndex` is a small protocol: `resolve(ref) -> dict | None` and `age_hours(ref, now) -> float | None`. Provide `DictEvidenceIndex` for tests. A ref that does not resolve counts as **missing** (not present, not zero) and fails the evidence floor.

### 2.4 GrowthOpportunity intake (`runtime/growth_intake.py`)

Accepts the `dict` form emitted by `growth_evaluator.evaluate()` (`ranked[*]`, `blocked[*]`) and validates against CROSS_LANE §7. `validate_opportunity(d) -> list[str]`; `intake(batch: list[dict], *, bot, persona, require_evidence: bool) -> OpportunityBatch(accepted: list[dict], rejected: list[{"index","reasons"}])`. Scope mismatch, `required_authority` other than `"none"`, `cost_class` other than `"no_spend"`, `provenance="test-only"` under `require_evidence=True`, non-finite numerics, unknown keys → rejected. Intake never mutates strategy and never returns authority.

### 2.5 Goal / PlanDAG (`runtime/goals.py`, `runtime/goal_planner.py`)

```
Goal(goal_id, bot, persona, objective: str,
     success_metric: {"semantic": str, "direction": "up"|"down", "target": float | None, "baseline_ref": dict | None},
     evidence_baseline_refs: list[dict], time_horizon: {"start": iso, "end": iso},
     allowed_authority: list[str],           # subset of {"create_candidate","register_experiment","update_state"}; never public/spend/message
     budgets: {"model_calls": int, "external_effects": int (must be 0), "max_tasks": int, "max_workers": int, "max_depth": int},
     stop_conditions: list[{"kind": "time"|"budget"|"metric"|"blocker", ...}], status, created_at)
PlannedTask(task_id: str,                    # sha256(goal_id|kind|key)[:16] → deterministic, dedup-able
            kind: "RESEARCH"|"EXPERIMENT_DESIGN"|"CONTENT_CANDIDATE"|"MEASUREMENT"|"REVIEW"|"SPECIALIST",
            key: str, inputs: dict, expected_evidence: list[str], completion_test: dict,
            depends_on: list[str], required_authority: list[str], budget: dict, depth: int,
            status: "PLANNED"|"READY"|"RUNNING"|"DONE"|"BLOCKED"|"CANCELLED", evidence_refs: list[dict])
PlanDAG(plan_id, goal_id, bot, persona, version: int, tasks: list[PlannedTask], edges: list[[from,to]],
        limits_applied: dict, constraints_ref: str, reason: str, supersedes: int | None, planner_id, created_at)
```
Storage: `paths.state_dir(bot) / "plans" / persona / f"{goal_id}-v{version:04d}.json"` + `HEAD.json` + `HISTORY.jsonl` (same shape as strategy).

### 2.6 WorkerContract / WorkerResult (`runtime/specialist_contract.py`) — per `SPECIALIST_WORKER_CONTRACT_SCHEMA.md`

```
SpecialistAuthority(read_context_refs: bool = True, write_scratch: bool = True, emit_result: bool = True)
   # deliberately has NO public/spend/message/state fields; there is nothing to escalate.
WorkerContract(worker_id, parent_run_id, bot, persona, role: "researcher"|"analyst"|"writer"|"reviewer"|"media"|"qa",
               objective: str, bounded_context_refs: list[dict], allowed_tools: list[str], denied_tools: list[str],
               authority: SpecialistAuthority, input_artifacts: list[dict], expected_output_schema: str,
               time_budget_s: float, model_call_budget: int, external_effect_budget: int (must be 0),
               scratch_scope: str,                # == worker_id; sandbox derives the dir
               stop_conditions: list[dict], created_at, expires_at, provenance)
WorkerResult(worker_id, parent_run_id, bot, persona, role, started_at, finished_at, source_ref: str,
             outputs: list[{"schema": str, "path": str (inside scratch), "sha256": str}],
             evidence_refs: list[dict], calls_used: int, effect_attempts: int,
             result: "COMPLETED"|"FAILED"|"TIMED_OUT"|"BUDGET_EXHAUSTED"|"STOPPED",
             limitations: list[str], cleanup_status: "PENDING"|"RETIRED"|"FAILED", error: str | None)
```
`validate_contract(c) -> list[str]` rejects: `external_effect_budget != 0`, role not in enum, `allowed_tools ∩ denied_tools ≠ ∅`, any tool outside the role's allowlist (§5.2), `expires_at <= created_at`, `scratch_scope != worker_id`, unknown keys, any key named like `credential|token|password|cookie` in `bounded_context_refs`.

## 3. Strategy track (S20 → S21) — module map

| Slice | Module | Test file | Public functions |
|---|---|---|---|
| S20-001 | `runtime/strategy.py` | `tests/test_strategy_store.py` | `new_initial(bot, persona, objective, ...) -> StrategyState`, `save_version(state, *, fence=None)`, `load_version(bot, persona, version)`, `active(bot, persona) -> StrategyState | None`, `history(bot, persona) -> list[dict]`, `set_active(bot, persona, version, *, event, fence=None)`, `admin_all_strategies(bot)` |
| S20-002 | `runtime/growth_intake.py` | `tests/test_growth_intake.py` | `validate_opportunity`, `intake` |
| S20-003 | `runtime/strategy_revision.py` | `tests/test_strategy_revision.py` | `ChangeOp`, `StrategyRevisionProposal`, `validate_proposal`, `propose(current, batch: OpportunityBatch, *, evidence, proposer: Proposer | None = None) -> StrategyRevisionProposal` |
| S20-004 | `runtime/strategy_policy.py` | `tests/test_strategy_policy.py` | `PolicyConfig`, `PolicyVerdict`, `validate`, `apply`, `commit_revision(current, proposal, verdict, *, fence=None) -> StrategyState` (persist new version + HEAD + HISTORY; REJECT/REQUEST_MORE_EVIDENCE persist only the verdict to HISTORY) |
| S20-005 | `runtime/allocation_scorer.py` | `tests/test_allocation_scorer.py` | `BudgetView` protocol (`remaining(kind) -> int | None`), `StaticBudgetView`, `score(batch, *, budget: BudgetView, weights: ScoreWeights) -> list[ScoredOpportunity]` |
| S20-006 | `runtime/strategy.py::rollback_to(bot, persona, version, *, reason, evidence_refs, fence=None)` + `tests/test_strategy_rollback.py` | — | rollback creates version N+1 whose content equals target version and whose `revision.restores_version` = target; never edits target |
| S20-007 | `bin/prove_v20_strategy_change.py` + `tests/test_v20_strategy_change_acceptance.py` | — | LIVE gate; see packet |
| S21-001 | `runtime/strategy_lifecycle.py` | `tests/test_strategy_lifecycle.py` | `TRANSITIONS` table, `transition(state, to, *, reason, fence=None)`, `is_authoritative(state, now) -> bool` |
| S21-002 | `runtime/strategy_decay.py` | `tests/test_strategy_decay.py` | `decayed_confidence(state, evidence, now, half_life_hours)`, `expiry_check(state, availability, now) -> "OK"|"REVIEW_DUE"|"EXPIRED"|"PLATFORM_CHANGED"` |
| S21-003 | `runtime/strategy_reconcile.py` | `tests/test_strategy_reconcile.py` | `ContradictionRecord`, `reconcile(refs_a, refs_b, *, evidence, config) -> ReconcileOutcome` (HOLD / REQUEST_MORE_EVIDENCE / PREFER_A / PREFER_B with reasons; never deletes) |
| S21-004 | `runtime/strategy_cooldown.py` | `tests/test_strategy_cooldown.py` | `CooldownConfig`, `check(history, proposal, now) -> (ok: bool, reasons)`; S20-004 `validate` calls it when present |
| S21-005 | `runtime/strategy_rollback.py` | `tests/test_strategy_rollback_executor.py` | `evaluate_rollback_condition(state, evidence, now) -> bool | None` (None = cannot evaluate → no rollback), `execute(bot, persona, *, evidence, fence=None)` (calls S20-006 `rollback_to`, writes receipt) |
| S21-006 | `bin/prove_v21_lifecycle.py` + `tests/test_v21_lifecycle_acceptance.py` | — | engineering acceptance over scripted evidence histories |

The **only** strategy read the runtime loop will need is `strategy.active(bot, persona)`; the hook that makes `decision.run_cycle` consult it is a lead-assigned integration task (§7), not part of any slice.

## 4. Planner track (S22) — module map

| Slice | Module | Test file | Public functions |
|---|---|---|---|
| S22-001 | `runtime/goals.py` | `tests/test_goals.py` | `Goal`, `validate_goal`, `save_goal`, `load_goal`, `list_goals(bot, persona)` |
| S22-002 | `runtime/goal_planner.py` | `tests/test_goal_planner.py` | `PlannedTask`, `PlanDAG`, `plan(goal, *, strategy: StrategyState | None, opportunities: OpportunityBatch | None, constraints: PlannerConstraints, limits: PlannerLimits, proposer=None) -> PlanDAG | NoNewWork`, `save_plan`, `active_plan` |
| S22-003 | `runtime/planner_constraints.py` | `tests/test_planner_constraints.py` | `PlannerConstraints`, `compile(*, authority: decision.Authority, availability: dict, live_authorized: bool, budgets: dict) -> PlannerConstraints` |
| S22-004 | `runtime/plan_validator.py` | `tests/test_plan_validator.py` | `validate_plan(dag, constraints, limits) -> list[str]` (cycle via Kahn, authority, unbounded, missing completion_test, duplicate task_id, dangling edge, depth) |
| S22-005 | `runtime/replanner.py` | `tests/test_replanner.py` | `replan(previous: PlanDAG, goal, *, changed_evidence, blockers, ...) -> PlanDAG` (DONE tasks copied by id, unchanged; only unfinished regenerated; version+1, `supersedes`) |
| S22-006 | `runtime/planner_limits.py` | `tests/test_planner_limits.py` | `PlannerLimits(max_tasks=24, max_depth=4, max_workers=3, max_model_calls=0, max_external_effects=0)`, `enforce(dag, limits) -> list[str]` — **S22-002 must import and apply default limits from day one**; S22-006 adds the full enforcement + adversarial tests |
| S22-007 | `bin/prove_v22_decomposition.py` + `tests/test_v22_decomposition_acceptance.py` | — | engineering acceptance |

Planner is deterministic and template-driven: for each accepted opportunity/hypothesis it emits `RESEARCH → EXPERIMENT_DESIGN → CONTENT_CANDIDATE → MEASUREMENT → REVIEW` chains (only the kinds the authority allows); an optional `proposer` may *suggest* extra `PlannedTask`s which pass through the same `validate_plan` and limits; a rejected suggestion is logged, never executed. `NoNewWork(reason)` is returned when strategy is covered (all opportunities already have non-CANCELLED tasks).

## 5. Specialist track (S23) — module map

| Slice | Module | Test file | Public functions |
|---|---|---|---|
| S23-001 | `runtime/specialist_contract.py` | `tests/test_specialist_contract.py` | `SpecialistAuthority`, `WorkerContract`, `WorkerResult`, `ROLE_TOOLS`, `validate_contract`, `validate_result`, `new_contract(...)` (least-authority constructor: tools default to role allowlist only) |
| S23-002 | `runtime/specialist_sandbox.py` | `tests/test_specialist_sandbox.py` | `Sandbox(contract)`: `create()` (dir under `paths.base()/"scratch"/bot/worker_id`), `materialize_context()` (copies referenced read-only snapshots in; never hands a `PersonaState`/`RuntimeState` object or a path outside scratch), `write(relpath, data)` (rejects traversal / absolute / symlink), `retire(*, keep: list[relpath]) -> cleanup_status` (moves kept files to `paths.receipts_dir(bot)/"specialists"/worker_id/`, deletes the rest) |
| S23-003 | `runtime/specialist_research.py` | `tests/test_specialist_research.py` | `ResearchSpecialist.run(contract, sandbox, *, collector=None, provider=None) -> WorkerResult` — outputs only `EvidenceRef`/`CaptureReceipt`-shaped files (CROSS_LANE §1/§2); `collector` defaults to a no-network fixture; never calls `pipeline` or `decision` |
| S23-004 | `runtime/specialist_analysis.py` | `tests/test_specialist_analysis.py` | `AnalystSpecialist` (typed `AnalysisResult`: findings[], each with evidence_refs), `ReviewerSpecialist` (typed `ReviewResult`: verdict, issues[]; read-only over inputs; cannot write outside its own output file) |
| S23-005 | `runtime/specialist_writer.py` | `tests/test_specialist_writer.py` | `WriterSpecialist` (typed `DraftResult`: candidate draft dict compatible with `pipeline` candidate shape, status always `DRAFT_UNPUBLISHED`), `MediaBriefSpecialist` (`MediaBriefResult`) — neither can enqueue, publish, or touch `content_dir` |
| S23-006 | `runtime/specialist_integrator.py` | `tests/test_specialist_integrator.py` | `verify(result, contract, sandbox) -> list[str]`, `adopt(result, contract, *, bot, persona, fence=None) -> AdoptionReceipt` (copies attributable outputs into persona namespace via `receipts.write_receipt(kind="specialist")`), `reject(result, contract, reasons) -> RejectionReceipt` (parent state untouched; failure receipt only) |
| S23-007 | `runtime/specialist_budget.py` | `tests/test_specialist_budget.py` | `BudgetedProvider(provider, contract)` (counts calls, refuses at budget, refuses when no manifest via `live_route_guard.check`), `Deadline(contract)`, `SpawnGuard` (a specialist's `allowed_tools` never contains `spawn_specialist`; any attempt raises `ChildSpawnDenied`) |
| S23-008 | `runtime/specialist_lifecycle.py` + `bin/prove_v23_specialists.py` + `tests/test_v23_specialist_acceptance.py` | — | `run_specialist(contract, adapter, *, lease=True) -> WorkerResult` implementing CREATE→ASSIGN→RUN→RETURN→VERIFY→ADOPT/REJECT→RETIRE with `leasing.acquire(f"specialist:{worker_id}")`; concurrent acceptance via `concurrent.futures.ThreadPoolExecutor` (in-process; separate process pools are a V3 option per `V3_TARGET_ARCHITECTURE.md`) |

### 5.1 Why specialists do not reuse `decision.Authority`
`Authority` has `can_public_post/can_spend/can_message_users` fields (always False in the loop). A specialist type that *has* those fields can be mis-set. `SpecialistAuthority` has no such fields, so "specialist cannot exceed granted effect authority" is a type-level property, and `validate_contract` additionally rejects `external_effect_budget != 0`. Tests must show that passing an `Authority` object, or a dict containing `can_public_post`, to `new_contract` raises.

### 5.2 Role tool allowlists (`ROLE_TOOLS`)
```
researcher: {"read_context", "capture_source", "write_scratch"}
analyst:    {"read_context", "read_scratch_inputs", "write_scratch"}
reviewer:   {"read_context", "read_scratch_inputs", "write_scratch"}
writer:     {"read_context", "read_scratch_inputs", "write_scratch"}
media:      {"read_context", "read_scratch_inputs", "write_scratch"}
qa:         {"read_context", "read_scratch_inputs", "write_scratch"}
```
Nothing in any allowlist can publish, enqueue, spend, message, mutate persona/runtime state, register experiments, or spawn. `capture_source` in engineering tests is a fixture collector; a network-capable collector is only wired by a later LIVE artifact.

### 5.3 Model access for specialists
A specialist adapter receives `provider=None` by default and behaves deterministically. When a provider is supplied it must be wrapped by `specialist_budget.BudgetedProvider`, which (a) refuses construction unless `live_route_guard.check(...)` allows the configured mode, (b) counts every `propose` call into `WorkerResult.calls_used`, (c) raises `CallBudgetExhausted` at `model_call_budget`. No V2.3 engineering slice makes a live call; the LIVE owner gate for specialists is recorded in `SB-V23-003`.

## 6. Test architecture (applies to all three tracks)

Every slice ships: (1) success path; (2) failure path (invalid input → `list[str]` errors, no persistence); (3) at least one adversarial test at its trust boundary; (4) persona-scope test (two personas on one bot never see each other's versions/plans/scratch); (5) missing≠zero test where numerics exist. Acceptance slices (S20-007 LIVE, S21-006, S22-007, S23-008) add a `bin/prove_*.py` that writes an evidence bundle under `receipts/evidence/<ARTIFACT>/` with `manifest.json` (source SHA, command, fixture/live classification, file hashes) mirroring `bin/prove_cross_process_lock.py`.

Required adversarial cases by track:
- **Strategy:** raw dict merge into strategy; `required_authority="public_post"` in a proposal; weight delta above max; single anomalous observation; unresolvable evidence ref; stale evidence; second revision inside cooldown; rewrite attempt of a prior version file (must be detected by hash in `history`); cross-persona active pointer.
- **Planner:** cycle; task whose `required_authority` exceeds goal authority; `external_effects>0`; > `max_tasks`; depth > `max_depth`; duplicate `task_id` from two differently-worded but same-key tasks; blocked platform → only read-only preparatory tasks; replan must keep DONE task ids and hashes byte-identical.
- **Specialist:** contract with `can_public_post`; `external_effect_budget=1`; tool outside role allowlist; path traversal `../` and absolute paths and symlinks in `write`; output path outside scratch in `WorkerResult`; `effect_attempts>0`; `calls_used>budget`; `worker_id` mismatch; attempt to spawn child; adapter raising → parent state byte-identical and a FAILED receipt exists; retired worker lease released; two concurrent specialists with different personas cannot read each other's scratch; timeout produces `TIMED_OUT` not `COMPLETED`.

Full-suite command remains `python3 -m unittest discover -s tests` from `social-bots/` (report exact counts).

## 7. Integration hooks (NOT part of any slice; lead assigns to the runtime owner)

| Hook | File | Change | When |
|---|---|---|---|
| H1 | `runtime/decision.py::run_cycle` | read `strategy.active(bot, persona)`; if authoritative, use its `objective`/weights in `ReasoningContext.state_summary`; if `EXPIRED`/None fall back to persona objective (current behavior) | after S20-004 + S21-001 accepted |
| H2 | `runtime/decision.py::_commit` or worker | after a cycle, call `strategy_policy.commit_revision` inside the same fenced commit when a proposal exists | after H1 |
| H3 | `runtime/worker.py::run_one_unit` | optional: consult `goal_planner.active_plan` for the next READY task | after S22-004 |
| H4 | `runtime/decision.py::_execute` | new action `DELEGATE_SPECIALIST` guarded by `Authority` and `planner_limits.max_workers` | after S23-008 |

Until hooks land, every V2.x module is fully testable in isolation, which is the point: three lanes can build in parallel with zero shared-file edits.

## 8. Out of scope for V2.3 (compatibility only)

V2.4+ organizational memory (`ORGANIZATIONAL_MEMORY_SCHEMA.md`), V2.8 portfolio budgets (`PORTFOLIO_RESOURCE_BUDGET_SCHEMA.md`) and V3 brand plane must be able to *consume* `StrategyState`, `PlanDAG` and `WorkerResult` unchanged. Keep `bot`/`persona` scope fields, `schema_version`, evidence refs and provenance on every record for that reason; add nothing brand-specific now.
