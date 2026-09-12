# CommerceLint executable planning task cards

All proposed work is undispatched. Paths are future source ownership reservations; exact admission and current operator remain authoritative. Conditional capability/effect branches never block useful independent work.

## CL-01 — Admit existing product and operator capabilities without replacement

Bind useful existing capabilities to a current source and exclusive execution contract, consuming release-worker returns when available.

Status: reuse_and_verify. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `coordination/autonomy/admission.json`, `coordination/autonomy/capabilities.json`, `coordination/autonomy/source-manifest.json`

Dependencies: None. Inputs: CL-I01.

Evidence: CL-E01, CL-E02, CL-E06, CL-E08

Implementation:

1. Compare fresh source with the inspected ref and any returned release manifest; qualify scanner, CLI, lead intake, operator, watchdog and deployment map individually.
2. Read existing coordination claim and latest run metadata read-only at admission; record active owner and allowed action scopes without changing schedules.
3. Ask the designated Jira writer to match BOTS and PCH scope and return current native fields, source/spec hash and path reservation; retain accepted work.
4. Record same-business integration interface: runtime proposals enter the existing operator; a later takeover requires destination reconciliation and fencing before activation.

Deliverables: source-manifest.json; capabilities.json; admission request and writer readback

Tests:

- Manifest validates every capability against source path/ref and test or receipt limits; absent payment and private CRM evidence remain unknown.
- Reject admission for a conflicting path owner, wrong source hash, unqualified account or stale release receipt.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Exact source/ref and current owner are recorded; every reused capability has bounded proof and a verification action.
- Product tasks can proceed under their existing release admission; wider autonomy dependencies do not halt the running operator.

Rollback: Revoke only the new admission/proposal version; leave existing scheduler, source and deployment ownership intact.

Next eligible action: Read the current release return and prepare scope-matching outbox; do not dispatch a scheduler.

Estimate: 3–6 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Current active owner and newer release changes may require a narrow rebase.

Jira key: null. Candidates: BOTS-114, BOTS-5, BOTS-6, BOTS-7, PCH-139. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G01. Requirements: CL-O01, CL-A01

## CL-02 — Complete reliable scan and saved useful-result continuity

Turn pasted HTML or a permitted public page into actionable evidence that survives navigation without implying a full commerce audit.

Status: reuse_and_verify. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `docs/scanner.html`, `docs/assets/scanner-result.js`, `cli/commercelint.py`, `tests/test_scanner_contract.py`, `tests/browser/scanner.spec.js`

Dependencies: CL-01. Inputs: None beyond admission.

Evidence: CL-E01, CL-E03

Implementation:

1. Reuse analyzeMarkup, the CLI checks, JSON export and browser last-report storage; version result schema with observed/expected values, severity, repair owner and limitations.
2. Provide restore/export/delete controls with explicit local storage retention and a safe fallback when storage is unavailable; never retain pasted HTML without a stated local opt-in.
3. Keep paste mode useful without network; disclose that URL mode uses an external retrieval service, reject private/credential-bearing URLs and provide bounded timeout/CORS/size/redirect failure states.
4. Add keyboard/screen-reader flows, clear malformed/multiple Product/Offer handling and result-to-offer context using an opaque local request reference.

Deliverables: versioned result schema; browser/CLI fixtures and receipts; accessible saved report flow

Tests:

- Run existing five CLI fixtures and browser cases for malformed JSON-LD, missing Offer, multiple products, empty input, HTML injection, unavailable storage and reload.
- Network interception shows zero HTML/URL/title leakage to analytics and zero requests in paste mode; URL timeout gives paste fallback.
- Local result restore retains schema/version and deletion removes stored result; displayed score never claims rendered checkout or variant validation.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- A visitor produces, understands, saves/restores and exports a prioritized report and follows a concrete next step.
- Each failure explains retry/paste/manual verification without asserting a storefront defect from retrieval failure.

Rollback: Restore previous scanner assets and preserve export compatibility; migrate or invalidate only unsupported cached schema versions with a visible explanation.

Next eligible action: Build fixture-based result/restore changes in an admitted isolated source worktree.

Estimate: 12–22 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Browser harness availability and safe retrieval design need qualification; no paid proxy required.

Jira key: null. Candidates: BOTS-115. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: None for offline work. Requirements: CL-O02, CL-O03, CL-A15

## CL-03 — Make request intake and verified response delivery restart-safe

Persist a qualified request through scan, clarification and delivered result without duplicate comments or public private-data exposure.

Status: planned. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `operator/lead_intake.py`, `operator/request_delivery.py`, `operator/request_ledger.py`, `.github/workflows/lead-intake.yml`, `tests/test_request_delivery.py`

Dependencies: CL-01, CL-02. Inputs: CL-I02.

Evidence: CL-E01, CL-E04

Implementation:

1. Reuse public GitHub request form, public-host validation and preliminary findings; distinguish public request fields from private customer records.
2. Add immutable request revision, event ID, consent/source, scope, job/attempt IDs and response artifact hash; use private storage for private delivery and public-safe projections only.
3. Persist response intent before effect; identify intended repository/issue and use an action-ID marker plus receiving-system comment lookup/readback before retry.
4. Process edited request/missing-URL answers once, preserving earlier evidence; verify rendered destination response belongs to intended request; advance fulfilled/needs-input only from receipts.

Deliverables: request/response ledger schema; delivery and reconciliation adapter; fault-injection and real receipt bundle

Tests:

- Replayed opened/edited events increment neither lead count nor verified response count twice.
- Kill after comment creation but before local acknowledgement; recovery locates same comment ID/body hash and never posts again.
- SSRF/redirect/private URL and injection fixtures fail closed; rejected requests do not leak submitted private material into public summaries.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- One authorized real inbound request yields one verified public or scoped private response receipt.
- Synthetic request fixtures are labeled; durable states remain separate from commercial lead and revenue counts.
- Offline adapter readiness is established by request/delivery/replay fixtures and review. A permitted real inbound request is required only to accept live response capability; its absence does not block scanner/result/offer release.

Rollback: Disable new response delivery, preserve intent and receipts, reconcile in-flight response, continue existing public utility.

Next eligible action: Implement durable intent and destination lookup against captured request fixtures before any authorized response test.

Estimate: 14–26 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Receiving-system read permissions and private storage gate private intake only.

Jira key: null. Candidates: BOTS-115, BOTS-116. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G02, CL-G03. Requirements: CL-O03, CL-A04, CL-A10, CL-A11

## CL-04 — Operationalize the scoped audit offer and fulfillment

Make the existing $49 up-to-15-public-URLs audit deliverable truthful, repeatable and supportable before accepting obligations.

Status: planned. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `docs/founding-audit.html`, `docs/sample-audit.html`, `docs/service.json`, `docs/downloads/commercelint-audit-report-template.md`, `operator/fulfillment.py`, `config/offer-policy.json`, `tests/test_fulfillment.py`

Dependencies: CL-01, CL-02. Inputs: CL-I03.

Evidence: CL-E01, CL-E04, CL-E05

Implementation:

1. Reuse current offer and defect-pack template; specify scope agreement, sample selection, exclusions, turnaround, one clarification round, cancellation/refund terms and capacity.
2. Build scoped audit jobs for visible versus structured values, variants, policies and representative catalog evidence; any uninspected feed/checkout remains explicitly unverified.
3. Persist intake->scope accepted->queued->evidence complete->reviewed->delivered->clarification closed with revision and private receipt references.
4. Generate prioritized repair backlog with reproduction and acceptance steps; require independent artifact QA before delivery; bounded clarification/support is tied to agreed scope.
5. Define follow-on remediation/agency QA as separately scoped proposals from actual defects and repeat demand; do not silently change free scanner claims.

Deliverables: offer/terms and capacity policy; fulfillment adapter; reviewed sample pack; order lifecycle contract

Tests:

- Fixture order of 15 URLs stays within budget/scope; over-scope or private access enters needs-input without fetching.
- Reviewer can reproduce each sampled defect and distinguish real from illustrative sample.
- A capacity-full state blocks paid intake while free scans and waiting list remain useful; delivery acknowledgement is reconciled once.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- A complete sample defect pack and verifiable fulfillment run exist with observable quality gates.
- An authorized real order, when available, can be delivered and supported from saved evidence; no order or satisfaction is invented.

Rollback: Stop new paid intake, preserve accepted obligations, restore prior offer content and reconcile or hand off open orders under their accepted terms.

Next eligible action: Prepare the scope/capacity contract and fixture fulfillment pack; keep payments disabled until CL-05 eligibility passes.

Estimate: 16–30 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Actual delivery timing and customer acceptance require a real agreed order; planning hours exclude waiting.

Jira key: null. Candidates: BOTS-115, BOTS-116. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G03, CL-G04. Requirements: CL-O04, CL-O05

## CL-05 — Qualify payments, refunds and settled cash accounting

Accept eligible scoped payments and reconcile funds, fees, refunds and fulfillment separately.

Status: planned. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `operator/payments.py`, `operator/financial_ledger.py`, `config/payment-policy.json`, `tests/test_payments.py`, `tests/test_financial_ledger.py`

Dependencies: CL-03, CL-04. Inputs: CL-I04.

Evidence: CL-E02, CL-E05

Implementation:

1. After a prospect accepts scope, reuse owner merchant route if eligible; collect only credential references, exact account/currency/capability and signed webhook/lookup contract.
2. Create invoice or checkout intent keyed to accepted order revision and idempotency key; verify receiving merchant account and provider transaction state.
3. Reconcile authorized/captured/settled/refunded/disputed states, fees and cash actually received; append adjustments instead of rewriting history.
4. Bind scoped refund eligibility, identity/policy and amount limit to provider action; preserve unknown response and reconcile before retry.
5. Enforce zero pre-revenue spending and one bundled reinvestment event capped at 50% available settled cash, preserving reserve and rejecting transaction splitting.

Deliverables: payment/refund adapter; private financial ledger; sandbox results and eligible provider receipts; cash reserve policy

Tests:

- Sandbox duplicate webhook, delayed settlement, partial/full refund, charge timeout and fee correction fixtures preserve exact cents and no duplicate charge/refund.
- Wrong account, unsigned webhook, unaccepted scope and unknown budget deny effect.
- Provider reconciliation readback matches ledger balances; settled funds differ from pending payout and invoice totals.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Payment taking remains gated until actual merchant route and scope are verified.
- Any revenue claim includes actual provider cash receipt, fees/refunds and linked fulfilled value; lack of transactions remains unvalidated.

Rollback: Disable checkout/invoice creation; retain reconciliation and fulfill existing obligations; never auto-refund merely because a deployment rolls back.

Next eligible action: Implement deterministic sandbox ledger and adapter contract; queue one merchant-readiness question only when an accepted scope makes it necessary.

Estimate: 16–30 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Merchant onboarding is non-delegable where provider requires it; no new account/budget assumed.

Jira key: null. Candidates: BOTS-116, BOTS-118. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G04, CL-G05. Requirements: CL-O05, CL-O06, CL-A04, CL-A10, CL-A11, CL-A16

## CL-06 — Connect qualified acquisition and consent-aware funnel evidence

Acquire relevant merchants/agencies through allowed routes and measure useful scans, accepted scope and money without fabricated traffic.

Status: reuse_and_verify. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `operator/acquisition.py`, `operator/analytics_collector.py`, `docs/assets/analytics.js`, `config/acquisition-policy.json`, `tests/test_acquisition.py`, `tests/test_analytics.py`

Dependencies: CL-01, CL-02, CL-04. Inputs: CL-I05.

Evidence: CL-E01, CL-E03, CL-E05

Implementation:

1. Reuse existing consent-gated GA4 configuration, CRM public/private distinction and deployment IndexNow route; verify data access before claiming live counts.
2. Define events with denominators: consent-eligible visits, completed scans, evidence downloads, explicit requests, accepted scopes, delivered orders and settled revenue; exclude internal tests and unknown actor categories.
3. Prepare one relevant guide/CLI/agency hypothesis and a bounded prospect/draft cohort; every send requires exact channel/account and explicit communication authority, existing recipient limits and opt-out handling.
4. Collect aggregate analytics and private CRM activity through scoped adapters; reconcile the historical sent-message disagreement from narrowly verified records, without bulk mail reads.
5. Record acquisition source and attribution confidence; missing access/counts stay null, and nonconsenting visitors are not silently treated as measured drop-offs.

Deliverables: event metric dictionary; aggregate collector; qualified acquisition proposal and source artifact; consent test receipt

Tests:

- Consent denied yields no GA network calls; consent granted sends allowlisted non-sensitive properties only.
- Duplicate visitor/request events, internal fixtures, revoked consent and unavailable metrics do not inflate qualified conversion.
- Unapproved send/account, duplicate recipient and exhausted cap deny publication/outreach; drafts remain executable.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Funnel scorecard connects acquired qualified use to scoped demand and paid fulfillment with coverage/attribution limits.
- One admitted useful acquisition intervention has destination evidence; message drafts are never counted as sent.
- Offline candidate/metric readiness is established by consent/denominator tests and reviewed draft. Actual acquisition intervention/destination receipt is conditional on release and channel authority; absent demand or permission does not block useful utility deployment.

Rollback: Revert only the intervention, suppress pending sends and retain baseline/observations; keep original consent controls.

Next eligible action: Define event denominators and build one source-grounded no-send acquisition candidate.

Estimate: 12–24 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: GA4/CRM route and explicit send authority may be unavailable; content and fixtures proceed.

Jira key: null. Candidates: BOTS-113, BOTS-115, BOTS-118. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G02, CL-G06. Requirements: CL-O07, CL-O08, CL-A03, CL-A15

## CL-07 — Release through the preserved portfolio deployment route

Ship qualified product improvements with exact source and public readback while preserving other ventures.

Status: reuse_and_verify. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `coordination/autonomy/release-contract.json`, `coordination/autonomy/release-receipts/`

Dependencies: CL-02, CL-04. Inputs: CL-I01.

Evidence: CL-E02, CL-E06

Implementation:

1. Submit source candidate to existing CommerceLint operator/release owner; deployment owner reserves portfolio production scope shared with BidetFit, never concurrent competing deployments.
2. Require reviewed immutable autonomous_apps source and portfolio mount revision; consume existing sync_commercelint.py and pages.yml rather than starting another route.
3. Verify homepage, scanner, offer, service JSON, privacy, result path, canonical/legacy redirect and intended assets at public destination; compare release receipt to selected commit. Keep unqualified new request/acquisition capabilities disabled, preserve existing qualified routes and never require a real inbound customer or outbound message before useful utility deployment.
4. Run one permitted real scan plus representative local edge fixtures; perform rollback to prior reviewed source through the same deployment owner and verify restoration.

Deliverables: release interface contract; review/source manifest; real public readback and rollback receipts

Tests:

- Release/source hash mismatch blocks release; current source HEAD alone is not proof of live version.
- Smoke checks include both CL and BF critical routes because portfolio deployment is shared.
- A failed or ambiguous deployment is reconciled by workflow/artifact/public readback before retry.
- Absent real inbound request, unavailable channel permission and no acquisition receipt do not block scanner/result/offer deployment; disabled new adapters cannot send or claim completed live acceptance.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Exact-source independent review, deployment receipt and public readback identify the same selected product version.
- Useful release can be accepted with payment taking disabled and broader autonomy still pending.
- Offline request/acquisition code readiness and reviewed candidates are separate from conditional live capability receipts; useful release cannot deadlock waiting for an intervention that requires that release.

Rollback: Existing deployment owner restores prior reviewed artifact and verifies both ventures; preserve customer/action ledger.

Next eligible action: Prepare candidate manifest and route-specific acceptance bundle for release owner; do not change its assignment.

Estimate: 6–12 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Shared portfolio destination must be serialized by existing deployment owner.

Jira key: null. Candidates: BOTS-116. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G01, CL-G07. Requirements: CL-O09, CL-A04, CL-A17

Conditional dependency branch: Enable the new request intake/response adapter in this release; scanner/result/offer release and preserved previously qualified route remain independent. Dependencies: CL-03. Require CL-03 adapter fixture/readback qualification for the enabled response capability; real inbound-request evidence is its own capability acceptance, not a prerequisite for scanner utility deployment.

Conditional dependency branch: Enable the new acquisition/analytics adapter or claim its actual intervention acceptance; public scanner/result/offer deployment remains independent. Dependencies: CL-06. Qualify consent-aware collector/allowed channel before enabling it. With absent customer/channel evidence, release the useful product with existing consent controls and reviewed acquisition drafts only.

## CL-08 — Integrate durable events, ownership and due decisions into existing operator

Extend the current operator into a fenced mission adapter with zero idle inference.

Status: planned. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `operator/autonomy_adapter.py`, `operator/main.py`, `operator/growth_planner.py`, `config/autonomy.json`, `tests/test_autonomy_events.py`

Dependencies: CL-01, CL-03, SH-01, SH-02, SH-03, SH-04. Inputs: CL-I06.

Evidence: CL-E02, CL-E04

Implementation:

1. Bind existing hourly/growth/lead triggers to one authoritative mission claim and action ledger; map existing state IDs without deleting runs or resetting business clock.
2. Add event types request_received, scan_completed, scope_accepted, delivery_due, source_changed, metric_window_due, cash_settled and owner_direction_changed with dedup key/evidence revision.
3. Persist next_check_at, decision fingerprint, owner fence and checkpoint atomically; dispatch only eligible declared action types into existing route.
4. Keep existing Actions concurrency as local serialization; reject expired/stale host tokens and require reconciliation before Windows executor takeover.
5. Use deterministic observation collectors; unchanged or not-due evidence returns without a model invocation, with per-event retries and finite queue capacity.

Deliverables: mission event/action adapter; migration manifest; claim and schedule integration tests

Tests:

- 100 unchanged timer checks produce zero model calls and zero duplicated jobs.
- Simultaneous Actions/Windows claims yield one accepted owner; stale token cannot deliver response or release content.
- Duplicate event and crash at checkpoint boundary retain one job and monotonic event cursor.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Existing operator remains the single mission effect owner or has a recorded fenced handoff.
- Changed evidence/due work executes without a manual launch prompt while idle ticks stay deterministic.

Rollback: Disable new adapter dispatch and return to prior qualified owner only after uncertain-effect reconciliation; preserve migrated records and cursor.

Next eligible action: Implement adapter against shared contract fixtures; keep it disconnected from existing production triggers until admission.

Estimate: 18–32 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Depends on shared transactional claims and Windows capability; no migration required for useful release.

Jira key: null. Candidates: BOTS-5, BOTS-6, BOTS-7. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G01, CL-G08. Requirements: CL-A01, CL-A02, CL-A09, CL-A16

## CL-09 — Consume owner direction, questions and documentation outboxes

Make owner nudges change the next decision once and resume blocked work from the accepted answer.

Status: planned. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `operator/owner_direction.py`, `operator/autonomy_outbox.py`, `config/direction-schema.json`, `tests/test_owner_direction.py`

Dependencies: CL-08, SH-08, SH-09. Inputs: None beyond admission.

Evidence: CL-E02, CL-E07

Implementation:

1. Map owner-authenticated directions to mission charter revision and current CONTROL RUN/PAUSE/STOP state; persist recorded/seen/applied/waiting-reconciliation/needs-input acknowledgements.
2. Example: prioritize agency repeat audits reorders future candidates; pause acquisition blocks pending sends while submitted comments/payments reconcile.
3. Ask once for a permitted storefront URL or accepted-order merchant route; reuse still-valid answers, bind answer identity/revision and resume only dependent job.
4. Write experiment-before-action and result/review outboxes keyed by payload hash for sole Jira writer; queue documentation projection during outage and require experiment admission readback before external launch.

Deliverables: direction/question handlers; mission outbox schema; revision/resume acceptance receipts

Tests:

- Duplicate direction and answer delivery applies once; superseding nudge wins without rewriting old experiment evidence.
- Pause received immediately before effect denies submission; if already submitted records waiting-for-reconciliation.
- Unavailable Jira writer or unanswered question produces one pending entry and no repeated notification/model loop.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Owner sees the exact revision consumed and concrete next action or bounded blocker.
- Answered missing input resumes saved work without restarting unrelated fulfilled jobs; matching outboxes project once.

Rollback: Pause affected adapter and preserve all direction revisions/outbox IDs; replay only unacknowledged safe projections after readback.

Next eligible action: Build direction fixtures for agency-priority, pause and missing storefront URL.

Estimate: 10–18 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Trusted input route and writer acknowledgement must be qualified separately.

Jira key: null. Candidates: BOTS-5, BOTS-7. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G01, CL-G09. Requirements: CL-A06, CL-A07, CL-A08

## CL-10 — Evaluate experiments and select the next profitable-use hypothesis

Continuously choose justified product, offer or acquisition work from observed business evidence.

Status: planned. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `operator/experiment_engine.py`, `config/experiment-policy.json`, `coordination/autonomy/experiment-template.json`, `tests/test_experiment_engine.py`

Dependencies: CL-04, CL-06, CL-08, CL-09, SH-05, SH-07. Inputs: None beyond admission.

Evidence: CL-E01, CL-E02, CL-E07

Implementation:

1. Predeclare baseline, hypothesis, alternatives, exact intervention, denominator, useful exposure criterion, window, stop rule and budget from current qualified traffic; do not copy old 500-visitor heuristic as a universal threshold.
2. First candidate compares a clearer defect-to-repair result/offer path or focused agency sample; choose from measured bottleneck rather than generating more guides automatically.
3. Evaluate supported/not-supported/inconclusive/invalidated and retain confounders; select adopt/revert/one bounded extension/stop plus next candidate or explicit no-action.
4. Connect scope acceptance, delivered value, repeat use and settled cash as separate evidence; without payment proof optimize useful demand while leaving commercial validation open.
5. A price/remediation/channel change stays within existing scope and explicit grants; preserve original hypothesis and dated amendment when owner direction changes active work.

Deliverables: experiment schema/engine; predeclared first protocol; evaluation/next-action receipts

Tests:

- Clock advance before window/threshold triggers no premature evaluation; insufficient traffic closes inconclusive or one justified extension without fabricated sample.
- Bad measurement coverage invalidates conversion claim; zero paid receipts cannot yield revenue success.
- Closed experiment generates one reviewed next decision and cannot relaunch the same action on replay.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Each closed experiment has an attributable evaluation and next decision linked to actual observations.
- At least two consecutive cycles can run from new evidence/due events without new owner prompting, while no-evidence state stays idle.

Rollback: Stop next experiment effects; retain original protocol/measurements and restore selected intervention only through release owner.

Next eligible action: Draft two bounded hypotheses using verified current denominators; implement decision tests against sparse and contradictory evidence.

Estimate: 14–26 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Traffic volume governs elapsed evidence window; software can qualify with labeled fixtures first.

Jira key: null. Candidates: BOTS-118, BOTS-5. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G01, CL-G06, CL-G08. Requirements: CL-O08, CL-O10, CL-A03, CL-A05

## CL-11 — Qualify mission recovery, privacy, alerts and budget enforcement

Keep independent Windows work recoverable and bounded across failures without duplicate business effects.

Status: planned. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `operator/runtime_limits.py`, `operator/recovery_adapter.py`, `config/autonomy-limits.json`, `tests/test_runtime_faults.py`, `coordination/autonomy/windows-runbook.md`

Dependencies: CL-08, CL-09, SH-10, SH-11, SH-12, SH-13, SH-14. Inputs: CL-I06.

Evidence: CL-E02, CL-E04, CL-E07

Implementation:

1. Wire Windows process-tree termination and timeout receipt to every scanner/model/tool child; preserve authoritative job checkpoint before process cleanup.
2. Restore from encrypted host-local backups and replay event cursor into same authoritative store; reconcile in-flight delivery/payment/deployment before lease takeover.
3. Enforce per-job, mission and daily model/tool/time limits with unknown budget fail-closed; use existing zero-dollar grants, no unapproved paid fallback.
4. Redact private CRM/customer/HTML data, store only secret references, test deletion/retention and keep private runtime outside public repository.
5. Emit one actionable alert per changed incident with job, failed prerequisite, owner action and resume pointer; suppress identical failures until change.

Deliverables: Windows fault/restore report; limits/privacy policy; alert adapter; backup/recovery runbook

Tests:

- Kill parent with child process alive: process tree terminates and receipt/checkpoint survives.
- Restore after power loss and stale host return does not duplicate a comment/payment; quota exhaustion stops before next paid/tool effect.
- Secret/PII canaries never reach Git/Jira/public logs; retry count and two repair limit are enforced.
- Mac-disconnected interval retains Windows execution and one actionable incident; unchanging failure sends no repeated alerts.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Recovery drill proves restart/restore, ownership fencing and zero unknown effects replayed.
- Measured model/tool counters, redaction, private storage boundaries and actionable-alert receipts are retained.

Rollback: Quarantine affected adapter, retain journal and read-only reconciliation, restore last good config only with same fence authority.

Next eligible action: Run non-effect child-process and backup fixtures on Windows; do not stop existing workers.

Estimate: 16–28 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Actual Windows service identity/storage and model access require capability qualification.

Jira key: null. Candidates: BOTS-5, BOTS-6. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G03, CL-G08, CL-G09. Requirements: CL-A09, CL-A12, CL-A13, CL-A14, CL-A15, CL-A16, CL-A18

## CL-12 — Prove repeated real operation and optional hub transfer

Distinguish deployed utility, autonomous operation and verified business outcome through exact-source independent acceptance.

Status: planned. Mission: CL. Owner: Designated Windows release parent assigns one admitted implementation owner; separate exact-source reviewer; existing scheduled operator retains integration/effect ownership.

Repository: pri8771/autonomous_apps

Owned paths: `coordination/autonomy/acceptance-plan.json`, `coordination/autonomy/acceptance-receipts/`, `coordination/autonomy/migration-interface.json`

Dependencies: CL-07, CL-10, CL-11, SH-06, SH-15. Inputs: CL-I07.

Evidence: CL-E01, CL-E02, CL-E07

Implementation:

1. Bind reviewer identity and exact source for product/runtime candidate; run fault suite before a real allowed cycle.
2. Cycle 1 observes permitted real public scan/request evidence, records an admitted usefulness/acquisition decision, executes one eligible result/approved content action, verifies destination and schedules evaluation.
3. Cycle 2 starts from later real changed evidence/due window without a new launch prompt, evaluates honestly and performs the justified next eligible action with a second receipt.
4. Inject owner pause/supersession, missing-input answer and crash after submission; verify consumed revision, safe resumption, same effect receipt and no duplicate.
5. Run Windows independently with Mac disconnected. Prepare R730 transfer manifest; optional SH-16 activation needs authority, restored state, old-owner fence and equivalent real receipts, and does not gate release.

Deliverables: independent exact-source acceptance report; two real cycle bundles; owner/restart receipts; optional R730 migration interface

Tests:

- Two distinct real cycle IDs link observation->decision->admitted action->destination receipt->evaluation->next decision.
- Synthetic scans, internal clients and sandbox payments remain labeled and excluded from external demand/revenue.
- No payment/CRM access means explicit scoped autonomy acceptance for eligible product/acquisition routes; money and private fulfillment acceptance stays pending CL-05 receipt.
- Independent reviewer reproduces candidate hashes and all critical failures are closed or block affected acceptance.

Review: Reviewer-authored record with actual reviewer identity, model/effort and host; distinct-model qualification is required for runtime/release acceptance and is not supplied by this plan. Bind immutable implementation commit, task/spec hash, artifact hashes, executed test receipts and any destination receipt. New source invalidates prior approval. At most two targeted repair/review cycles; unresolved findings become a linked blocked task, preserving attempts.

Acceptance:

- Runtime autonomous-operation claim is limited to exercised eligible capabilities, with owner-direction and restart proof.
- Business-validation status remains unvalidated unless actual paid-and-fulfilled evidence exists; no guarantee of revenue.

Rollback: Withdraw only unsupported autonomy/capability acceptance and disable its new effects; existing useful release remains under original owner.

Next eligible action: Assemble exact-source acceptance protocol and reserve a permitted non-spending real cycle with the existing owner.

Estimate: 10–18 engineering hours. New planning range for admitted implementation and bounded review; reuses evidenced assets; excludes observation waiting, non-delegable account work and shared-platform implementation. Not a replacement for historical Jira estimates or measured actuals. Dependency risk: Real observations and destination access govern elapsed windows; acceptance cannot be fabricated.

Jira key: null. Candidates: BOTS-118, BOTS-5. Designated release writer compares this exact scope with current native issues and retained accepted artifacts; reuse/extend matching scope, create only missing linked scope; preserve original estimates, remaining estimates, actuals, statuses and history; return hash-bound native readback. Null is unknown, never a request to clear a field. Writer: Windows release parent, sole writer for non-OPO missions; this lane is outbox-only

Effect gates: CL-G01, CL-G02, CL-G07, CL-G08. Requirements: CL-O10, CL-A04, CL-A05, CL-A17, CL-A18

Conditional dependency branch: Payment, refund or real-money autonomy acceptance; free source/product/acquisition cycles remain independent. Dependencies: CL-05. Complete merchant/payment qualification and actual provider/fulfillment receipts before accepting this capability. Missing gate leaves it disabled and money validation incomplete.

### CL-08 horizon acceptance addendum

Implementation: Schedule mission_horizon_due from the preserved config/business.json deadline_at_utc 2026-11-22T04:59:59Z (November 21 local close), not a reset 90-day timer. Produce one durable decision event at the boundary.

Pass/fail test: Cross deadline with unchanged traffic: exactly one horizon event becomes due and no duplicate model decision appears on repeated polls; original start/deadline remain unchanged.

Acceptance: Original mission clock is preserved and its end triggers one reviewed horizon decision; post-horizon effects require valid extension authority.

### CL-10 horizon acceptance addendum

Implementation: At mission_horizon_due, close the original 90-day accounting/experiment window and issue a reviewed continue/change/stop decision. New experiments or external expansion after the horizon require a valid owner charter extension; without it pause new effects while reconciling existing obligations and preserving useful offline work and original results.

Pass/fail test: At 2026-11-22T04:59:59Z, one terminal review is due; absent valid extension denies new experiment effects after expiry. A validated extension creates a new dated charter/window and never rewrites original cash/results or abandons accepted customer obligations.

Acceptance: Original mission clock is preserved and its end triggers one reviewed horizon decision; post-horizon effects require valid extension authority.
