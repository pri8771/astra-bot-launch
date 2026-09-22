# V2.3 critical path and dependency audit

Lane: `fable-planning`, session `s-20260921T202026Z-a90ea082`, branch `claude/inspiring-ride-3pj8bo`.  
Status: **PROPOSED — READY_FOR_LEAD_REVIEW.** No canonical status, index, state or queue file was edited. Worker-facing detail lives in `V20_TO_V23_IMPLEMENTATION_SPEC.md`; slice detail lives in the rewritten `artifact-packets/v18-v30/SB-S20-*`, `SB-S21-*`, `SB-S22-*`, `SB-S23-*` packets.

## 1. Audited current state (live Git, 2026-09-21)

| Item | Verified value |
|---|---|
| Canonical branch head | `chatgpt/social-bots-plan-20260920` @ `b022646a41f48e6aa582d2957973252e585c2cc7` (LEAD-042) |
| Official phase | V0.4.x; V0.3 accepted; no promotion since LEAD-041 |
| Primary implementation lane | `cursor/social-bots-recovery-v07-20260921` @ `488ce0c` (lead ack commits) over runtime source `d7ecb25`; session `s-20260921T191500Z-a23cc77e`; assignment: bounded `SB-R07-041` repair only, then pause overlapping runtime expansion pending Acceptance |
| Cursor-owned runtime surface | everything under `social-bots/runtime/`, `bin/`, `tests/` on that branch (47 runtime/bin files, 33 test files) |
| Intelligence modules needed by V2.0 | `runtime/{metrics,audience,experiment_engine,growth_evaluator,community,platform_selection}.py` + 6 test files exist **only** on `claude/social-bots-intelligence-repair-v2` @ `33b9c7b` (PARKED). Merge-base with the Cursor branch: `85c4414`; a dry `git merge-tree` of Intelligence into Cursor conflicts in exactly three source files: `runtime/factcheck.py`, `tests/test_factcheck.py`, `bin/heartbeat_reporter.py` (plus docs). |
| Acceptance lane | `claude/social-bots-mac-qa-control`: STALE / ACTION REQUIRED (LEAD-042); last durable heartbeat is the superseded timed cadence, seq 10, 2026-09-21T03:57Z |
| V2.x packets before this session | 28 one-line templates (~1 KB each) for SB-S20..S23; milestone packets SB-V20-001/SB-V21-001/SB-V22-001/SB-V23-001/002 are 0.7–2.2 KB outlines |
| Live model gate | none authorized; `social-bots/authorizations/` absent on every branch |
| This lane's heartbeat | `worker-reports/fable-planning/HEARTBEAT_LOG.jsonl`, commit `8335fc6`, Issue #3 comment `5766952853` |

Nothing in this audit changes: V0.4 remains owner-authorization blocked; V0.7 LIVE needs an owner-controlled persistent host; the current Cursor host is unsuitable.

## 2. Structural finding: V2.0 consumes modules that are not on the implementation branch

`STRATEGY_SCHEMA.md` and `CROSS_LANE_INTERFACES.md` §7 define V2.0 as Core consuming Intelligence's `GrowthOpportunity`, `ExperimentRecord`, `AudienceHypothesis` and `NormalizedMetricObservation`. Those producers were built on the Intelligence lane (SB-V13-001/SB-V14-001 ACCEPTED; SB-V15-001, SB-V20-002 CHANGES_REQUIRED) and never merged toward the recovery branch, which was cut from the Core lineage. Consequence: any S20 slice that *imports* those modules cannot run its tests on the primary branch today.

Proposed remedy (lead decision): a new SP2 slice **SB-S20-000 — Intelligence module consolidation onto the primary branch** (`artifact-packets/v18-v30/SB-S20-000.md`, written as a proposal). It merges the six modules and their tests from `33b9c7b` (last lead-verified Intelligence head `2052955`), resolves the three conflicts by keeping the Cursor-side `factcheck.py`/`test_factcheck.py` (SB-R07-051 integrated the operational assessor there) and the canonical `heartbeat_reporter.py`, and re-runs the full suite. It does not accept SB-V15-001 or SB-V20-002; it only makes their code present so V2.0 engineering can proceed. Timing: after Cursor pushes the R07-041 repair; it is "dependency-safe packaging" under LEAD-042's pause rule, but the lead should confirm.

What does **not** wait for S20-000: the spec deliberately has S20-001/003/004/006, the whole S21 track, the whole S22 track and the whole S23 track depend only on the accepted V0.3/V0.4 base (`paths`, `jsonstore`, `leasing`, `decision.Authority`, `live_route_guard`, `authorization`). S20-002 and S20-005 validate/score the **dict** form of `GrowthOpportunity` (CROSS_LANE §7), so they can be built and tested with fixture dicts before consolidation and only need the real module for S20-007.

## 3. Proposed dependency corrections (lead applies to `ARTIFACT_INDEX.json`; not edited here)

The canonical graph chains V2.x *engineering* slices behind *operational* milestone bundles. That is correct for promotion and wrong for build order; it would make V2.3 engineering wait on V0.4 owner authorization. Proposed engineering dependencies (operational gates are kept where they belong: S20-007, SB-V20-004, SB-V23-003):

| Artifact | Canonical `depends_on` | Proposed | Why |
|---|---|---|---|
| SB-S20-000 (new) | — | `[]`, owner Cursor, SP 2 | §2 |
| SB-S20-001 | `SB-V19-005` | `[]` | store needs only paths/jsonstore/leasing; V1.9 LIVE gate moves to S20-007 |
| SB-S20-002 | `SB-S20-001, SB-V20-002` | `SB-S20-001, SB-S20-000` | validates §7 dict shape; SB-V20-002 repair status is a gate for S20-007 LIVE inputs, not for intake code |
| SB-S20-005 | `SB-S20-002, SB-S19-004` | `SB-S20-002` | `BudgetView` protocol + static fixture; S19-004 adapter is a later one-file addition |
| SB-S21-001 | `SB-V20-004` | `SB-S20-004, SB-S20-006` | lifecycle is engineering over the store/policy, not over operational V2.0 |
| SB-S22-001 | `SB-V21-001` | `SB-S20-001, SB-S21-001` | goals reference `StrategyState` + `is_authoritative` |
| SB-S23-001 | `SB-V22-001` | `[]` | contract type needs no planner; specialists can be spawned by the parent directly |
| SB-V23-099 (new) | — | `SB-S20-006, SB-S20-007(rehearsal), SB-S21-006, SB-S22-007, SB-S23-008` | "V2.3 engineering-ready" twin of SB-V20-099, so the lead can accept engineering readiness without faking operational V2.3 |
| SB-V23-003 | unchanged | unchanged (`SB-V20-004, SB-V21-001, SB-V22-001, SB-V23-002`) | operational checkpoint stays behind the real LIVE chain |

Milestone packets SB-V20-001, SB-V21-001, SB-V22-001, SB-V23-001, SB-V23-002 remain the *acceptance* summaries; the S-slices are their execution decomposition (already the canonical pattern per `DETAILED_EXECUTION_V18_TO_V30.md`). No slice was added or removed except the two proposals above.

## 4. Critical path to V2.3

### 4.1 Engineering-ready V2.3 (SB-V23-099)

Three independent tracks, each **new files only** (spec §0.1), so they can run on three branches cut from the Cursor head with zero shared-file edits:

```
strategy   : S20-001 → S20-003 → S20-004 → S20-006 → S21-001 → S21-002 ─┐
                       S20-002 → S20-005 (dict fixtures)      S21-003 ─┼→ S21-004 → S21-005 → S21-006
             S20-000 (consolidation) ──────────────────────→ S20-007 rehearsal
planner    : S22-001 → S22-002(+limits defaults) → S22-003 → S22-004 → S22-005 → S22-006 → S22-007
specialist : S23-001 → S23-002 → {S23-003, S23-004, S23-005} → S23-006 → S23-007 → S23-008
                                                                                     ↓
             all four acceptance harnesses green + S20-007 rehearsal  →  SB-V23-099 (lead)
```
Longest chain is the strategy track (≈27 SP sequential); planner ≈15 SP; specialist ≈18 SP. Story points are complexity buckets, not hours (`TEAM_LANES.md`). Integration hooks H1–H4 (spec §7) into `decision.py`/`worker.py` are four small lead-assigned tasks for the runtime owner after the relevant track is accepted; they are outside the engineering-ready definition on purpose so no track ever edits a Cursor-owned file.

### 4.2 Operational V2.3 (SB-V23-003)

Unchanged and entirely owner/LIVE-gated: `SB-V23-003 ← SB-V20-004 ← SB-V20-003 + SB-V19-005 ← V1.x LIVE ← V0.7 LIVE (persistent host, SB-R07-074..079) ← V0.4 LIVE (SB-R07-043 five-call batch: owner authorization + lead manifest) ← current recovery Wave 0/1`. No later engineering promotes any of these. S20-007's LIVE bundle is the first point where the two chains meet.

## 5. Ownership and collision audit

- **Cursor Recovery** keeps sole ownership of every existing runtime/bin/test file. In-flight `SB-R07-041` touches `runtime/reasoning.py`, `runtime/live_route_guard.py`, `runtime/reasoning_cli.py` and their tests. V2.x modules only *import* `live_route_guard.check(*, artifact, lane, run_scope, …)` and `authorization.authorize/CallBudget`; if the R07-041 repair changes those signatures, S23-007 (`BudgetedProvider`) is the single adaptation point and its packet says so.
- **Proposed new lanes** (lead decision; names used in packets): `strategy` (S20/S21), `planner` (S22), `specialist` (S23). Suggested branches `claude/social-bots-strategy-v20`, `claude/social-bots-planner-v22`, `claude/social-bots-specialist-v23`, each cut from the Cursor head **after** the R07-041 push, reports under `worker-reports/<lane>/`, one `SESSION_ONCE` heartbeat per fresh session. If the lead prefers Cursor to do everything sequentially, the packets work unchanged; the parallelism is optional.
- **Legacy Intelligence** stays parked; S20-000 copies its modules, it does not reopen SB-V15-001.
- **Fable lane** owns only: `V20_TO_V23_IMPLEMENTATION_SPEC.md`, this file, the 28 rewritten S20–S23 packets, the two proposed packets (SB-S20-000, SB-V23-099), `worker-reports/fable-planning/`, and an appended `AGENT_MESSAGES.md` handoff.

## 6. Acceptance and test architecture

Spec §6 is the contract. Summary: every slice ships success/failure/adversarial/persona-scope/missing≠zero tests as new files; the four acceptance slices (S20-007 rehearsal, S21-006, S22-007, S23-008) each ship a `bin/prove_*.py` writing a hashed evidence bundle under `receipts/evidence/<ARTIFACT>/` with `classification: "fixture"` (S20-007 alone has a `live` mode that structurally refuses fixture provenance). Independent Acceptance re-executes each bundle before lead acceptance, as it does for SB-R07-071. Engineering readiness (SB-V23-099) is accepted on those bundles; operational V2.3 is not.

## 7. First five executable, non-conflicting tasks (any Sonnet-class worker; new files only)

1. **SB-S23-001** specialist contract runtime — no dependencies beyond base; starts today on the specialist branch.
2. **SB-S20-001** versioned strategy store — no dependencies beyond base; starts today on the strategy branch.
3. **SB-S20-000** Intelligence consolidation — Cursor, immediately after the R07-041 push (lead to confirm it counts as dependency-safe packaging).
4. **SB-S23-002** specialist sandbox — after 1.
5. **SB-S20-003** revision proposal types + deterministic proposer — after 2 (S22-001 goal contract is the equivalent first planner task once S21-001 exists; until then the planner lane can start S22-006 `planner_limits` defaults since S22-002 must import them).

## 8. Blockers and owner gates

- Owner: SB-R07-043 five-call live divergence batch (V0.4); an owner-controlled persistent host for V0.7 LIVE; analytics/account read authorization for S20-007 LIVE inputs; any live specialist/provider run (SB-V23-003).
- Lead: accept/adjust §3 dependency deltas; create SB-S20-000 and SB-V23-099 in the index; decide lane split (§5); assign hooks H1–H4 when tracks are accepted; Acceptance lane must first execute SB-R07-071 and the repaired SB-R07-041 (LEAD-042) — that remains the immediate project-wide critical action and is not displaced by this plan.
- Engineering: none identified that blocks tasks 1–2 today.

## 9. V2.4–V3.0 compatibility (no implementation)

`StrategyState`, `PlanDAG`, `WorkerContract`/`WorkerResult` carry `bot`, `persona`, `schema_version`, `provenance` and evidence refs so `ORGANIZATIONAL_MEMORY_SCHEMA.md`, `PORTFOLIO_RESOURCE_BUDGET_SCHEMA.md` and the V3 brand plane can consume them unchanged; specialist execution is in-process with a documented process-pool option (`V3_TARGET_ARCHITECTURE.md`). Nothing brand-specific was added and no V2.4+ packet was touched.
