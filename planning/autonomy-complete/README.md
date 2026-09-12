# Complete six-mission autonomy plans

This package plans One Person Ops, Wait How Big, CommerceLint, BidetFit, Guru and Lipi from inspected current source and retained evidence through useful releases and repeatable autonomous operation. Implementation, public release, runtime autonomy and business validation remain separate states; this planning package does not claim them achieved.

The isolated branch is `codex/autonomy-complete-six-missions-20260912`, based on private control source `3833a1b392b140f0a4f79ac4ba00e39dcad383fb`. All changes are confined to `planning/autonomy-complete/`. Separate Windows release workers retain their assignments. Jira was read for bounded matching evidence and never written. The canonical handover was resolved to root `WINDOWS_ASTRA_ULTRA_HANDOVER.md` and read fully; see [intake and ownership](evidence/INTAKE_AND_OWNERSHIP.md).

## Start here

- [Coverage matrix](COVERAGE_MATRIX.md): every outcome and all eighteen autonomy requirements for each mission, plus shared controls, mapped to tasks, dependencies, evidence and acceptance.
- [Shared architecture](ARCHITECTURE.md) and [shared task cards](shared/TASKS.md): durable state, claims/fencing, scheduling, decisions, effects/receipts, experiments, direction/questions, outboxes, recovery, alerts, privacy and limits.
- [Dependency graph](DEPENDENCY_GRAPH.md), [machine graph](DEPENDENCY_GRAPH.json) and [phased release queue](RELEASE_QUEUE.md): executable ordering, conditional capability branches and shared resource conflicts.
- [Effect gates and shared inputs](PERMISSIONS_AND_INPUTS.md), [acceptance protocol](EXECUTION_ACCEPTANCE.md), [planning estimates](ESTIMATES.md) and [Jira outbox](jira-outbox/README.md).
- [Review summary](reviews/REVIEW_SUMMARY.md), [validation receipt](validation/PLANNING_VALIDATION.json), [artifact audit](validation/ARTIFACT_AUDIT.json), [checkpoint](CHECKPOINT.md) and [continuation](CONTINUE.md).

## Mission entrypoints and inspected evidence

| Mission | Complete plan / tasks / inputs | Current source observation and proof limit |
| --- | --- | --- |
| One Person Ops | [Plan](missions/opo/PLAN.md) · [Tasks](missions/opo/TASKS.md) · [Inputs](missions/opo/UNRESOLVED_INPUTS.md) | Preserved `one-person-ops@cb20a06a1344c8c017afa0b4bc9565377a99db63`; all thirty provenance hashes match Git blobs. Historical site, optional service candidates and staged checkout do not establish public host, durable hosted storage, merchant or outside-agent use. |
| Wait How Big | [Plan](missions/whb/PLAN.md) · [Tasks](missions/whb/TASKS.md) · [Inputs](missions/whb/UNRESOLVED_INPUTS.md) | `orchestrator@270ccb5a59e053df1ec5f415358b03f93bf9c69e`; retained operator ZIP inspected without execution. Reuse Buffer/publishing code; repair account selection, state/deduplication and receiving-system verification. |
| CommerceLint | [Plan](missions/commercelint/PLAN.md) · [Tasks](missions/commercelint/TASKS.md) · [Inputs](missions/commercelint/UNRESOLVED_INPUTS.md) | `autonomous_apps@ec4d10c0e02fc09465535a0b3da019a9c3f73bf9`; five CLI fixture tests passed. Extend existing operator/scanner/offer and preserve deployment owner; current merchant, customer delivery and public release remain separately qualified. |
| BidetFit | [Plan](missions/bidetfit/PLAN.md) · [Tasks](missions/bidetfit/TASKS.md) · [Inputs](missions/bidetfit/UNRESOLVED_INPUTS.md) | `priyanshchordia.com@02c3df999a2d052810e0f265d5cb40d865861042`; guide/checker/operator reused, exact-model evidence and affiliate eligibility still need their task receipts. Shared portfolio deployments serialize actual conflicting effects. |
| Guru | [Plan](missions/guru/PLAN.md) · [Tasks](missions/guru/TASKS.md) · [Inputs](missions/guru/UNRESOLVED_INPUTS.md) | Ten preserved editorial Git blobs match provenance. They are references, not a runnable bot or required Instagram identity. Bind canonical product home, source/cultural review and X-first account route. |
| Lipi Standard | [Plan](missions/lipi/PLAN.md) · [Tasks](missions/lipi/TASKS.md) · [Inputs](missions/lipi/UNRESOLVED_INPUTS.md) | `lipi-standard-store@0d896016f2fa113ce07e504bc5d6528717598b5f`; fresh aggregate 31/31 passes with launch readiness false, seven records and 23 unknowns. Eleven read/proposal tools have no mutation executor. Retained 25 contracts/56 checks at another revision remain separate evidence, with exact unavailable artifacts explicitly reconciled. |

Each mission also provides TASKS.json, requirements.json, EVIDENCE.md, evidence.json, Jira reconciliation and current local checkpoint/continuation. Evidence classifications distinguish inspected source, executed local checks, dated reports, live receiving-system observations and missing facts. A source status flag is not a runtime receipt.

## Proceeding from this package

The existing OPO writer consumes OPO proposals; the Windows parent consumes WHB/CommerceLint/BidetFit/Guru proposals. Lipi/shared writer designation is a named remaining input. Matching comes before any issue creation: reuse accepted scope and preserve all original estimates, actuals, links and history. All new task bindings stay null until current native admission. The outbox contains complete reviewable payloads and stable operation IDs; no messages or mutations are sent automatically.

Select eligible work from the queue and its exact source/task card. Current release-worker returns are consumed before duplicate implementation. Obtain only a genuinely missing effect-specific input; prepare useful independent work while that effect is blocked. A free product need not wait for payment, a non-affiliate guide need not wait for program approval, original posts need not wait for AI-reply approval, and Windows operation need not wait for R730. Existing precise grants are reused. No new purchases, paid plans, unspecified spend, i9 work or private Kai/Pri data export is authorized here.

The final runtime acceptance requires two completed real eligible cycles, verified destination receipts, owner-direction acknowledgement, question/resume, bounded usage, pause and restart/restore, plus attributable exact-source review. Waiting for evidence is valid operation but does not replace those cycle receipts. Lipi physical/sample and seven-day observations must actually occur. Revenue, profitable delivered orders, affiliate cash and engaged audience growth are measured outcomes, never promises from passing software checks.

## Reproducible planning checks

From this checkout, run `python -B planning/autonomy-complete/_tools/assemble.py --validate-only` and `python -B planning/autonomy-complete/_tools/audit_artifacts.py`. They check planning structure/references/dependencies and bounded artifact format/ownership/common-secret patterns. They do not start bots, invoke models, contact providers or write Jira. The assembler without `--validate-only` regenerates pre-publication aggregate files and proposals; do not overwrite already-submitted immutable outbox revisions after publication. Use a new reviewed revision for later changes.

Exact-source review records distinguish commands run from material inspected, and independent same-model planning review from distinct-model product approval. Git-blob and Windows working-file hashes are explicitly distinguished. The latest publication commit/readback is in PUBLICATION_RECEIPT.json; current checkpoint/continuation records the last stable commit and next action.
