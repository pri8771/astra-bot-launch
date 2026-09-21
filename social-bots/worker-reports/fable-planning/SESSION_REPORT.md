# fable-planning — session report

Session: `s-20260921T202026Z-a90ea082` (SESSION_ONCE, one durable heartbeat, `HEARTBEAT_LOG.jsonl`)  
Branch: `claude/inspiring-ride-3pj8bo` (cut from canonical `chatgpt/social-bots-plan-20260920` @ `b022646`)  
Assignment: `assignments/FABLE_5_1.md` (senior planning architect; no runtime source edits while Cursor owns recovery)  
Requested status for every artifact below: **PROPOSED / READY_FOR_LEAD_REVIEW** — nothing self-accepted.

## Exact SHAs

| Commit | Content |
|---|---|
| `8335fc6` | heartbeat (lane `fable-planning`), Issue #3 comment `5766952853` |
| `0a49525` | `V23_CRITICAL_PATH.md`, `V20_TO_V23_IMPLEMENTATION_SPEC.md`, SB-S20-001/004/007, SB-S23-001..008, proposed SB-S20-000 + SB-V23-099 |
| `136cc65` | SB-S20-002/003/005/006, SB-S21-001..006 |
| `4352745` | SB-S22-001..007, SB-S20-000 ancestry note — **content head** |

Diff vs canonical: 35 files, +2086 / −396, all under `social-bots/`; no edits to `ARTIFACT_INDEX.json`, `STATE.json`, `WORK_QUEUE.md`, `MILESTONE_MANIFEST.md`, `WORKER_PERFORMANCE.md`, `SESSION_ROUTER.md`, or any `runtime/`, `bin/`, `tests/` file.

## Audited current state (verified against live Git)

- Canonical `b022646` / LEAD-042; official V0.4.x; Cursor Recovery ACTIVE at `488ce0c` (source `d7ecb25`) on the bounded SB-R07-041 repair; Acceptance STALE; no live model gate open.
- Intelligence modules V2.0 consumes (`growth_evaluator`, `metrics`, `audience`, `experiment_engine`, `community`, `platform_selection`) exist only on `claude/social-bots-intelligence-repair-v2` @ `33b9c7b`; dry merge into the Cursor branch conflicts in three source files only.
- The 28 SB-S20..S23 packets were ~1 KB templates with a one-line goal; milestone packets SB-V20-001..SB-V23-002 are outlines.

## Planning files changed

- New: `V23_CRITICAL_PATH.md` (lead-facing), `V20_TO_V23_IMPLEMENTATION_SPEC.md` (worker-facing), `artifact-packets/v18-v30/SB-S20-000.md` (proposed consolidation slice), `artifact-packets/SB-V23-099.md` (proposed engineering-readiness twin of SB-V20-099).
- Rewritten: all 28 `artifact-packets/v18-v30/SB-S20-*`, `SB-S21-*`, `SB-S22-*`, `SB-S23-*` — each now has interfaces, reuse targets, owned new-file paths, deterministic-vs-model split, fail-closed behavior, 8–12 focused/adversarial tests, evidence class, gates, non-goals and DoD. Canonical dependency lists preserved verbatim with an explicit "Engineering:" clarification; proposed index corrections are tabulated in `V23_CRITICAL_PATH.md` §3 for the lead to apply.

## Critical path to V2.3 (summary; detail in `V23_CRITICAL_PATH.md` §4)

Engineering-ready (proposed SB-V23-099): three new-files-only tracks that can run in parallel from the Cursor head — strategy (S20→S21, ≈27 SP, longest), planner (S22, ≈15 SP), specialist (S23, ≈18 SP) — converging on four fixture-labeled acceptance bundles; runtime hooks H1–H4 are separate lead-assigned tasks. Operational V2.3 (SB-V23-003) stays entirely behind the LIVE chain (V0.4 five-call batch → V0.7 persistent host → V1.x → SB-V20-004); no engineering shortcut is proposed.

## First five executable non-conflicting tasks

1. SB-S23-001 specialist contract (new files; base only).
2. SB-S20-001 strategy store (new files; base only).
3. SB-S20-000 Intelligence consolidation (Cursor, after the R07-041 push; lead to confirm it is dependency-safe packaging).
4. SB-S23-002 sandbox (after 1).
5. SB-S20-003 revision proposal types (after 2); planner lane can meanwhile start `planner_limits` defaults inside SB-S22-002.

## Blockers / owner gates

Owner: SB-R07-043 authorization; persistent host for V0.7 LIVE; analytics/account read for S20-007 LIVE; any live specialist run. Lead: §3 dependency deltas, creation of SB-S20-000 / SB-V23-099, lane split decision, hook assignment; Acceptance still must execute SB-R07-071 and the repaired R07-041 first (LEAD-042) — this plan does not displace that.

## Method and limits

- Model/effort: as configured for this session; runtime and Intelligence modules were read at the SHAs above, not executed. No test was run because no source was written.
- Seventeen packets (S20-002/003/005/006, S21-*, S22-*) were expanded by a lower-cost subagent from the spec and three exemplars, then reviewed by this session for spec conformance (structure, dependency wording, forbidden-name scan, sampled full reads of S20-003, S21-001, S21-006, S22-002).
- Known limits: story-point estimates are complexity buckets copied from the existing packets; the `live_route_guard.check` signature may move under the in-flight R07-041 repair (S23-007 is the single adaptation point); no LIVE evidence of any kind is claimed.
