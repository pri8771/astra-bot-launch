# Bot roadmaps: launch, validation and continuing operation

Planning contract, 12 September 2026; no jobs, Jira writes or releases performed. Latest priority is **OPO + WHB + CommerceLint before other backlog**. All IDs below (`opo.01`, etc.) are proposed internal task IDs, not Jira keys; matching directories now exist under tasks/. Execution requires the [task-directory contract](TASK_DIRECTORY_CONTRACT.md).

Authority: [current mission register](../bots-focus-2026-09-12/MISSION_GOALS.md), [OPO decision](../bots-focus-2026-09-12/OPO_AGENT_BUSINESS.md), [account/channel/host policy](../bots-focus-2026-09-12/ACCOUNTS_CHANNELS_AND_HOSTS.md) and [experiment policy](../bots-focus-2026-09-12/AUTONOMOUS_EXPERIMENTS.md). The [original catalog](/Users/pchordia/.codex/.chatgpt-projects/g-p-6a8a5b1660588191b47da9d545cc013e/bots-repo/README.md) names five business missions plus shared services. Latest decisions supersede older product selections. Saved receipts below are not fresh live verification.

## Common progression

Every mission follows: source/account baseline → fully populated Jira contracts/readback → isolated implementation → exact-source review → qualified launch/readback → measured business experiment → reviewed continue/change/stop decision. Independent tasks may overlap; dependencies and account/write ownership may not. External actions use current authority and verified routes, never historical handoff instructions alone.

Launch is a finite milestone. Business validation is a separate milestone, requiring real evidence. Ongoing operation has no permanent “finished” state: each experiment closes with an honest result, then schedules a justified next action or waits cheaply for evidence. Negative/inconclusive results may complete an experiment without validating the business. Preserve old estimates, actuals, accepted artifacts and dated observations.

## Priority 1: One Person Ops

**Goal:** agent-facing revenue website, preferred genuine AI/bot audience, cumulative followers/exposure across useful channels, including existing X. Contract Check is optional.

**Evidence:** original site/resources exist, but recorded Sites deployment is private; staged checkout is not live payment. Retained Contract Check is a local candidate. See [source/hosting inventory and packet](CURSOR_MAC.md). Root subsequently published the preserved working source privately at `pri8771/one-person-ops` (`cb20a06a…`); see CLOUD_PUBLICATION.md. Full `shivangchordia` domain remains pending. No verified outside-agent adoption or OPO revenue is established here.

| ID | Deliverable and dependency |
|---|---|
| `opo.01` | Reconcile source, canonical GitHub destination, existing account identities, domain/storage and revised Jira scope. Preserve dirty original assets. |
| `opo.02` | After 01: readable discovery page, versioned service/message contracts, one useful demonstrator and examples. |
| `opo.03` | After 01; integrates 02: persistent intake/conversation ledger, operator authentication, validation, deduplication, privacy/moderation and restart recovery. |
| `opo.04` | After 01: concrete offer, price/terms, eligible payment route and verifiable fulfillment/refund plan; qualify alongside engineering. No placeholder checkout. |
| `opo.05` | After 02–03, review and target confirmation: release/readback and one labeled synthetic exchange. Add a verified social route without waiting for every platform. |
| `opo.06` | After 05: first outside request/use experiment; monetize when 04 passes. Record actual transactions, costs, repeat use and channel metrics; choose next experiment. |

**Smallest ship:** one documented service/discovery page plus durable message exchange; no framework rewrite. **Launch done:** anonymous discovery works, exchange survives restart, controls/review/rollback pass and actual public URL is verified. **Revenue validation:** real authorized payment plus fulfilled value and net accounting; interest or synthetic clients cannot substitute.

## Priority 2: Wait, How Big?

**Goal:** X/Twitter-first relevant audience growth; science/scale remains a candidate theme, not an immutable business. [Saved baseline](../cursor-overnight-2026-09-11/returns/missions_commerce/evidence/BOTS-117_BASELINE.md) found historical operator assets but no qualified active checkout/account route or verified cycle permalink.

- `whb.01`: recover/qualify canonical `pri8771/orchestrator/wait-how-big-social` source, account and supported route; reconcile Jira and current metrics.
- `whb.02` → 01: prepare one sourced, unit-checked explainer with accessible assets and a predeclared audience experiment.
- `whb.03` → 02/review: publish one qualified canary, verify intended permalink/account and receipt; reconcile ambiguity before retry.
- `whb.04` → 03: measure the declared window, relevant engagement and repeat interest; review continue/change/stop. Monetization is a later explicit hypothesis if audience evidence supports it, not invented sponsorship income.

**Smallest ship/launch done:** one accurate public explainer, correct-account receipt, working measurement and duplicate/stop controls. More platforms and large content reserves are unnecessary prerequisites. No real audience outcome is declared by publication alone.

## Priority 3: CommerceLint

**Goal:** money-making website. Preserve `pri8771/autonomous_apps` and the existing website mount. [Saved September 12 baseline](../cursor-overnight-2026-09-11/returns/missions_commerce/evidence/BOTS-114_BASELINE.md) recorded public HTTP 200, healthy status, $0 revenue, qualified-traffic bottleneck and missing payment endpoint. Existing operation is not paused by this roadmap.

- `cl.01`: refresh source/operator/public/analytics/payment baseline and revised Jira scope; inspect existing authority without replacing the running loop.
- `cl.02` → 01: qualify one scanner/guide→useful-result path and a concrete paid offer; reuse accepted scanner/CLI assets.
- `cl.03` → 02/review: deliver one bounded conversion/acquisition change through the existing release route, with readback and rollback.
- `cl.04` → 03: evaluate qualified use and actual requests; verify payment/fulfillment when eligible, then compare costs and net receipts before deciding the next experiment.

**Smallest ship/launch done:** the existing website's selected improvement is publicly verified, useful result and recovery work, and measurement is trustworthy. **Monetization validation:** actual paid/fulfilled demand; uptime, generated guides and visits are not revenue.

## Deferred: Affiliate / BidetFit

Deferred behind the first three, not canceled; do not infer that any existing independent operation stopped. [Retained return](../cursor-overnight-2026-09-11/returns/missions_other/SESSION_RETURN.md) preserves a guide/checker candidate; current hosting, affiliate approval and commission evidence remain unverified.

`bf.01` source/program/site/Jira reconciliation → `bf.02` one conservative guide/checker improvement with dated sources/disclosure → `bf.03` reviewed release/readback and recovery → `bf.04` usefulness/click experiment and commission reconciliation. Reuse `pri8771/priyanshchordia.com/ventures/bidetfit`; no repeated niche selection. **Launch done:** verified helpful guide/checker without unsupported fit guarantees. **Money validation:** distinguish pending, approved, reversed, paid commissions and collected cash. No forced purchase or invented program acceptance.

## Deferred: Guru Social

Deferred behind the first three. Goal is engaged Hindu-spirituality audience, currently X/Twitter-first. Sadhana Notes/Instagram are reusable editorial candidates, not mandatory identities/channels. [Retained return](../cursor-overnight-2026-09-11/returns/missions_other/SESSION_RETURN.md) records content preparation, with source/cultural/account acceptance unresolved.

`guru.01` audience/account/source/cultural/Jira reconciliation → `guru.02` one original reviewed piece and measurement plan → `guru.03` qualified publication/readback → `guru.04` trust/engagement evaluation. **Launch done:** accurate attributed content, correct account, accessible presentation and moderation/recovery. Monetization requires a separately justified offer; no follower-to-revenue inference. Digital Temple integration remains excluded.

## Services and repository placement

**Kai and Pri 2.0 are assistant services, not sixth/seventh businesses.** `kai.s1` refresh ingress ownership/auth evidence → `kai.s2` verify one owner request through tools to reply → `kai.s3` qualify restart, isolation and stop. [Saved status](../bots-focus-2026-09-12/SUMMARY_AND_DIRECTION.md) is dated; do not infer current Slack acceptance. For Pri, preserve the reported wife acceptance; `pri.s1` reconcile remaining technical criteria → `pri.s2` review exact pilot → `pri.s3` accepted handoff/recovery. No repeated spouse test or unsolicited integration expansion. These service tasks do not displace the first three business outcomes.

Recommend GitHub-backed canonical source for each independently deployable product, reusing established homes. Keep the charter monorepo; share small versioned framework libraries/contracts for receipts, scheduling and adapters. One repository per account is unnecessary. Maintain separate mission data/capabilities. Windows is primary, mobile Mac backup; only qualify needed portability. Lipi and other products remain separate; Digital Temple and Retell are excluded. No elapsed-time or revenue promise is implied.
