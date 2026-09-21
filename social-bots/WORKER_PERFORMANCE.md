# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current review: `LEAD-014` (`lead-reviews/LEAD-014_2026-09-20T2054.md`).

Both Claude lanes are actively committing. No GitHub status checks existed at the verified heads, so test counts below are worker-local unless the lead independently inspected the source/acceptance logic.

## Current observations

The first broader SP2–SP5 sample is now useful enough to guide decomposition:
- SP2 bounded test/evidence repair (`SB-V03-003`) closed cleanly after one lead-found coverage gap.
- SP3 state/collector artifacts have been strong: V03-002 was first-pass accepted; V05-001 is accepted after source review.
- SP4 artifacts are the main current risk cluster: workers often implement the local behavior correctly but miss a cross-runtime/persona or interface-boundary invariant (V03-005, V13, V14, V16, V17, V20-002).
- SP5 fencing improved after one independent lifecycle defect and is now accepted for its explicit single-host scope. SP5 adaptive reasoning remains blocked by the distinction between deterministic context sensitivity and truly adaptive provider invocation.

This supports the worker-first strategy while keeping SP4/SP5 work decomposed with adversarial integration acceptance.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> worker added forced FACT + VOICE failures | ACCEPTED | good bounded repair behavior |
| SB-V03-004 | 5 | PARTIAL | lead found active-cycle fence-loss defect; worker added generation fence + atomic fenced commit | ACCEPTED | one POSIX host/local FS only; cross-host/Windows not claimed |
| SB-V03-005 | 4 | PARTIAL | first repair reconciled docs + logical isolation; LEAD-014 found isolation helpers remain bypassable by raw bot-wide readers | CHANGES_REQUIRED | second repair required; production read paths must hard-scope persona-private data |
| SB-V03-006 | 3 | BLOCKED | depends on accepted V03-005 | BLOCKED | regenerate only after repair |
| SB-V04-001 | 3 | PARTIAL | schema validation fixed; production default still baseline/non-adaptive unless env opt-in | CHANGES_REQUIRED | repair default posture; preserve validation |
| SB-V04-002 | 5 | PARTIAL | contextual provider materially varies by context but truthfully reports adaptive=false | CHANGES_REQUIRED | useful component, not real V0.4 adaptive provider |
| SB-V04-003 | 4 | PASS-LIKE source review | dependency V04-001 unresolved | BLOCKED | policy boundary looks sound; avoid churn unless upstream repair affects it |

## Intelligence lane task results

| Artifact | SP | First submission | Independent review finding | Current lead disposition |
|---|---:|---|---|---|
| SB-V05-001 | 3 | PASS | collector-derived provenance/hash/status; fixtures cannot masquerade as live | ACCEPTED |
| SB-V05-002 | 4 | PARTIAL | support engine is good but packet-required material-claim identification is caller-supplied/out-of-scope | CHANGES_REQUIRED |
| SB-V13-001 | 4 | FAIL acceptance invariant | no snapshot/delta/gauge/rate kind; aggregate sums cumulative snapshots | CHANGES_REQUIRED |
| SB-V14-001 | 4 | FAIL isolation invariant | hypothesis/persistence bot-scoped; no persona/workspace boundary | CHANGES_REQUIRED |
| SB-V15-001 | 4 | PASS-LIKE source review | honest INCONCLUSIVE/window/learning behavior; depends on V13/V14 correctness | BLOCKED |
| SB-V16-001 | 4 | PARTIAL | bot-wide history/novelty lacks persona and can cross-contaminate shared-runtime personas | CHANGES_REQUIRED |
| SB-V12-001 | 3 | PASS-LIKE source review | good no-fabricated-history/availability behavior; depends on V13 | BLOCKED |
| SB-V17-001 | 4 | PARTIAL | no-public-effect boundary good; bot-wide community themes can feed another persona's audience memory | CHANGES_REQUIRED |
| SB-V20-002 | 4 | PARTIAL | good missing/no-spend behavior; missing full cross-lane bot/persona/authority/availability/cost contract; upstream V13/V14 defective | CHANGES_REQUIRED |

## Independent defect themes

### Persona/workspace isolation
Repeated across SP4 Intelligence/Core work:
- V03-005 safe filters not enforced;
- V14 audience memory bot-wide;
- V16 novelty/history bot-wide;
- V17 community themes bot-wide;
- V20-002 lacks explicit persona scope.

Action: future SP4+ packets that touch memory/history/analytics must explicitly state whether data is runtime-shared, persona-private, or organization-shared and include mixed-persona tests.

### Metric semantics
V13 preserved missing-vs-zero but missed the stronger semantic-kind contract despite it being groomed before implementation. This is a meaningful first-pass miss, not a vague requirement. Future analytics/experiment work must carry cumulative/delta/gauge/rate semantics through interfaces and acceptance examples.

### Dependency discipline
Workers are moving faster than lead acceptance and sometimes build dependent artifacts early. Early additive implementation is useful, but lead status should remain BLOCKED where accepted dependencies are missing. Avoid rework by consuming the current canonical packet before each artifact.

### Worker-local tests vs independent CI
Core reports 85 tests at its latest reviewed V04-003 checkpoint; Intelligence reports 128 at V20-002. Both current verified heads had zero GitHub status checks. Implement `SB-CTL-006` after V0.3 repair to improve independent acceptance evidence.

## Metrics to continue accumulating

For each SP level:
- attempts;
- first-pass accepted;
- first-pass partial/failed;
- repair cycles;
- independent findings;
- dependency violations/early-start incidents;
- escaped defects;
- acceptance after repair;
- CI vs worker-local evidence.

Do not infer worker quality from one artifact. The current pattern supports high worker throughput with stronger lead review at cross-cutting SP4/SP5 boundaries.
