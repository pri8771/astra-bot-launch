# Five-bot Windows release packet — AUTHORIZED FOR DISPATCH, NOT YET SUBMITTED

12 September 2026. **Owner explicitly resumed release execution and separately requested comprehensive Astra Ultra planning for all five bots plus Lipi. This packet is authorized for dispatch; submission is not yet evidenced.** Execute the already-specified release work below while the independent planner completes the wider backlog. The existing 22 internal tasks are not a complete autonomy backlog; [AUTONOMY_BACKLOG_GAP.md](AUTONOMY_BACKLOG_GAP.md) records that historical correction, not a continuing launch pause. [WINDOWS_ASTRA_ULTRA_HANDOVER.md](WINDOWS_ASTRA_ULTRA_HANDOVER.md) defines the parallel planning assignment. Do not wait for its complete plan before implementing these releases, or mistake this packet for completed implementation or operating services.

## Latest ownership correction

The owner is manually starting a dedicated Cursor Windows One Person Ops session using `CURSOR_WINDOWS_ONE_PERSON_OPS.md`. **Reserve OPO for that session; do not launch an OPO worker from this combined packet.** It owns OPO issue writes and source integration. The combined parent owns only the other four missions and their issue writes. The Astra Ultra planner remains outbox-only. Manual submission is not yet independently verified.

## Authority and execution ownership

Windows and Jira setup are accepted by the latest owner direction. Do not repeat authentication discovery or stop at another Phase 0 report. Diagnose only an actual encountered error, narrowly. Earlier documents’ unavailable Mac writer freeze and preparation-only restrictions are superseded for this wave. The single Windows Cursor parent owns Jira projection, integration and conflicting external actions. Other lanes, including the Astra Ultra planner, write immutable outboxes only; the old Mac writer is not a prerequisite or a second writer. Proceed with already-authorized ordinary work without seeking another generic approval.

Use Cursor Auto with desktop Multitask for isolated implementation lanes for **CommerceLint and then BidetFit** (OPO belongs to the dedicated owner-started session). A small **WHB editorial/review lane** uses available Gemini/Antigravity; if unavailable, assign another available executor without repeating platform setup. Record the actual session/model, never infer Multitask from CLI availability. Move BidetFit into the first free engineering lane and Guru into the free editorial lane. Keep at most two heavy implementations plus one small editorial/review job initially. A genuinely blocked effect frees capacity while its release’s remaining work continues.

R730 remains the central hub target; Windows provides temporary independent execution and development. The Mac must not be a runtime dependency. i9 and new Kai/Pri 2.0 product work stay paused; the separate planner now includes Lipi through autonomous operation and only necessary Kai/Pri shared-capability boundaries. No hardware migration or shared-framework rewrite is a launch prerequisite.

## Reuse source and work already done

Read `FIVE_BOT_KICKOFF.md`, `BOT_ROADMAPS.md`, `REPO_CLOUD_AUDIT.md`, `CLOUD_PUBLICATION.md` and the targeted mission task bundle. Reuse `returns/cursor-mac/` and `returns/claude-mac-runtime/`; their readiness work does not need repetition. Their restrictions and status are historical where this packet states newer direction.

Create separate Windows worktrees from current source, preserving original dirty trees. Record each base and owned paths:

| Mission | Source and retained evidence |
|---|---|
| OPO | `pri8771/one-person-ops`; preserved source at `cb20a06a…`, provenance and applicable `AGENTS.md`. Historical storefront and Sites binding are not launch destinations. |
| CommerceLint | `pri8771/autonomous_apps`; deployment map in `pri8771/priyanshchordia.com`. Old local clone was 356 commits behind; use fresh source. Preserve the existing operator and release route. |
| WHB | `pri8771/orchestrator/wait-how-big-social/`; inspect the retained operator bundle once, then implement its gaps. Historical state is not current account acceptance. |
| BidetFit | `pri8771/priyanshchordia.com/ventures/bidetfit/`; reuse the checker/guide and its `AGENTS.md`, mission state, runbook and diary. |
| Guru | `pri8771/astra-bot-launch/reference/guru-sadhana-candidate/` contains ten editorial references, not a working runtime. Establish a canonical implementation home without assuming the absent Sadhana path exists. |

The Windows parent reconciles relevant existing tickets directly, preserving estimates, actuals, dependencies, accepted artifacts and history. OPO candidates include BOTS-124–127/112; CommerceLint BOTS-114; WHB BOTS-117; retained Guru/BidetFit associations are in the missions-other return. These are matching candidates, not automatic edit targets. Internal IDs such as `opo.01` are not Jira keys. Expand missing implementation scope into coherent release work, reuse matching tickets, and create only genuinely missing linked scope. Capture actual native keys/readbacks; do not invent fields or estimates. Jira projection problems queue evidence and affect only the genuinely dependent operation, not all independent engineering.

## Five substantial release scopes

**OPO — agent service and business operation.** Deliver readable and machine-readable discovery, versioned service/message schemas, examples and a useful deterministic service. Add authenticated operator controls, persistent threaded intake and results, validation, deduplication, moderation, privacy/retention and safe handling of untrusted proposals. Complete a concrete offer with pricing/terms, fulfillment/refund handling and eligible payment integration where available. Wire incoming requests to bounded jobs, verified responses and experiments. Add a qualified social distribution route and channel attribution. Prove restart-safe exchanges; separate labeled synthetic clients, crawlers, humans, unknown actors and evidenced outside agents. An unresolved exact public hostname blocks that publication, while product, storage, preview, runtime and offer work continue.

**CommerceLint — useful scan to offer and fulfillment.** Deliver a complete scanner/guide-to-result path, actionable prioritized findings, saved request/result continuity, a concrete conversion/offer flow and useful failure states. Integrate lead/request intake, attribution and consent-aware measurement; qualify payment and fulfillment where available. Improve the existing operator with bounded acquisition/conversion experiments and trustworthy cost/result accounting. Preserve active ownership: extend its existing route or perform a recorded fenced handoff, never start a duplicate scheduler. Verify a permitted real scan plus representative edge cases, release rollback and public readback. Missing payment capability blocks taking payment, not the useful release.

**WHB — repeatable sourced editorial operation.** Deliver sourced scale explainers, unit/math checks, accessible assets, an editorial queue and independently reviewed candidates. Implement supported account-bound publishing, durable receipts, corrections, duplicate protection and engagement collection. Ship one excellent reviewed piece and a usable next-content pipeline; generation, review, publication and evaluation are separate states. Start one predeclared audience experiment. Missing publication access leaves the candidate ready and the rest of the runtime testable.

**BidetFit — compatibility product and affiliate operation.** Improve the interactive checker, explain compatible/uncertain outcomes with dated manufacturer evidence, and provide useful comparison/guide results. Implement source refresh, broken-link checks, disclosures, eligible affiliate routing, completed-check/referral measurement and commission reconciliation. Preserve pending, approved, reversed and paid amounts separately. Qualify corrections, restart and release rollback. No unsupported fit guarantees or invented program acceptance; unavailable affiliate approval blocks affected links, not the checker or publishing of useful non-affiliate guidance.

**Guru — reviewed publishing and audience operation.** Deliver an original Hindu-spirituality content pipeline with source attribution, contextual/cultural review, accessible presentation and an editorial queue. Implement account-bound publishing, corrections/moderation, receipts, meaningful engagement collection and a predeclared voice/usefulness experiment. Ship a reviewed piece and a repeatable next-piece workflow. Keep X-first direction; Sadhana/Instagram assets are optional reuse. Do not infer revenue from followers or expand into Digital Temple.

## Autonomy implementation missing from the old 22-task backlog

Each release must implement and test these shared behaviors **and its mission-specific adapters**:

- Durable jobs, experiments, receipts and an atomic single-owner claim. Persist revisions, attempt IDs and fencing; reject stale owners. Use Windows-native process-tree termination, timeout and restart handling, not copied POSIX-only controllers.
- Deterministic event/due-time scheduling with `next_check_at`, evidence version and decision fingerprint. Unchanged inputs trigger no inference. Bound job/model/tool usage and repairs; unknown or exhausted spending authority blocks paid effects without surprise fallback.
- Versioned owner nudges: record mission, request, source and direction revision; acknowledge the revision actually consumed. Pause/resume/amend without erasing old evidence. Ask once for genuinely missing input; bind the answer and resume dependent work. External messages cannot grant authority.
- Predeclared experiment baseline, hypothesis, intervention, measurement window, success/stop criteria and budget. Observe cheaply, then evaluate supported/unsupported/inconclusive outcomes and choose a justified next action.
- Reconcile uncertain external effects before retry; prevent duplicate posts, responses, charges and Jira operations. Prove crash/restart, stale-owner rejection, stop/resume and recovery with fault injection.

## Acceptance and return

Require relevant product checks, exact-source attributable independent review, bounded repair/review, real destination readback and restart/recovery evidence. Never label self-review as distinct-model approval. No new purchases, paid plans or unspecified budgets; no credentials in artifacts, fake followers, spam or platform evasion.

Each lane returns `SESSION_RETURN.md`, `WORK_QUEUE.json`, `DISTINCT_MODEL_REVIEW.md`, `JIRA_OUTBOX.jsonl` and hashed release/runtime evidence under its Windows return directory. Include source tip, actual executor, tests, unresolved criteria, external IDs/URLs, next eligible action and measured usage with unknowns explicit. Parent records **prepared, implementing, reviewed, released, autonomously operating and observed business outcome** separately. A launch or passing tests do not establish autonomous operation or commercial success.
