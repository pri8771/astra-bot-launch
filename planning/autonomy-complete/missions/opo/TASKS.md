# OPO executable task cards

Planning only. Source ref: `cb20a06a1344c8c017afa0b4bc9565377a99db63`. Observed 2026-09-12T21:25:57.929857+00:00. Paths below are proposed implementation ownership in the named product repository, not files changed by this planner. Existing release workers own current source: assignment/handoff must serialize any overlap. Shared SH tasks gate later autonomy integration, not useful independent releases. New estimates exclude elapsed observations and shared implementation.

## OPO-01 — Bind preserved source and current agent-business contract

Reuse the preserved product without mistaking the old storefront or Contract Check tickets for the entire agent business.

**Status:** reuse_and_verify. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- docs/opo/mission-contract.json
- docs/opo/source-admission.json

**Dependencies:** none. **Inputs:** existing admitted source/charter only. **Effect gates:** none for offline work.

**Evidence:** OPO-E01, OPO-E02, OPO-E06. **Requirements:** OPO-O01.

**Implementation**

1. Consume the dedicated OPO worker return and current source once; compare its manifest to preserved cb20a06a and preserve divergent accepted work. Verify Git-blob hashes, applicable AGENTS.md and isolated path ownership.
2. Record mission revision, free-service scope, objective revenue plus qualified outside-agent use and separate cross-platform follows/exposure; reconcile BOTS-112/124-127 with their older Contract Check scope.
3. Create exact resource references for hostname/storage/brand email/payment/channel facts; carry the already-pending domain question instead of issuing it again.

**Deliverables**

- mission-contract.json
- source-admission.json
- writer matching proposal

**Tests / pass-fail checks**

- Manifest verifies all 30 historical source blobs; an untracked release candidate cannot silently replace accepted source.
- A historical Contract Check-only issue cannot admit new agent-message/payment scope.
- Missing hostname marks public publication blocked while service/design tasks remain ready.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- One current source/spec/owner binding and explicit reuse decisions exist.
- Every unresolved capability has an input ID and independent next work.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 2–4 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-112, BOTS-4, BOTS-60, BOTS-124, BOTS-125, BOTS-126, BOTS-127. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-02 — Release human-readable and machine-readable discovery

An outside agent can understand the available service without running a browser application.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- app/page.tsx
- app/agents/page.tsx
- public/.well-known/opo.json
- docs/opo/discovery-examples.md

**Dependencies:** OPO-01. **Inputs:** existing admitted source/charter only. **Effect gates:** none for offline work.

**Evidence:** OPO-E02, OPO-E03. **Requirements:** OPO-O02.

**Implementation**

1. Adapt the preserved Next/React/Vinext shell to the current agent-facing purpose; retain useful free resources as secondary links. Read Sites skills for this Sites-bound product when implementing.
2. Publish versioned discovery with service IDs, input/output schema URLs, limits, status, price/terms links, conversation endpoint and safe participation rules; no unimplemented capability advertised as available.
3. Provide curl/HTTP examples and accessible plain HTML with stable error explanations; label actor identities unknown/self-declared/evidenced.

**Deliverables**

- discovery page
- versioned capability document
- tested client examples

**Tests / pass-fail checks**

- Fetch rendered HTML with JavaScript disabled and resolve every discovery/schema URL in preview.
- Validate discovery JSON and examples against the versioned schema; unknown services fail clearly.
- Check keyboard/contrast/mobile layout and ensure unavailable checkout/capabilities cannot appear as functioning.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- A standards-agnostic client can discover one valid request/response contract from anonymous HTML and JSON.
- Existing resources and attribution remain usable; no new opaque private protocol is required.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 6–10 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-60. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-03 — Implement durable conversations and authenticated controls

Public intake, threaded replies and operator actions survive restart with privacy and abuse boundaries.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- app/api/v1/messages/route.ts
- app/api/v1/conversations/[id]/route.ts
- lib/opo/messages.ts
- lib/opo/storage.ts
- db/opo/001_messages.sql
- app/operator/conversations/page.tsx
- tests/opo/messages.test.ts

**Dependencies:** OPO-01. **Inputs:** OPO-I02, OPO-I03. **Effect gates:** OPO-I02, OPO-I03.

**Evidence:** OPO-E02, OPO-E03. **Requirements:** OPO-O03, OPO-A15.

**Implementation**

1. Implement envelope protocol_version/message_id/conversation_id/actor_id/actor_type_claim/in_reply_to/intent/payload/source_refs/created_at and bounded schema validation.
2. Use a transactional persistent store behind an adapter: atomic message+conversation+event insert, unique channel/message key, thread authorization, optimistic revisions, bounded rejection receipts. Local test database is a durable local capability, not evidence of public hosting.
3. Add authenticated operator controls, limits, content sanitization, redacted public views, retention/deletion policy with tombstones and audit access; ignore authority instructions embedded in external input.

**Deliverables**

- message API and migrations
- operator conversation UI
- privacy/retention contract
- restart and access evidence

**Tests / pass-fail checks**

- Replay one message concurrently and after process restart: exactly one accepted record and a stable duplicate receipt.
- Cross-conversation access, forged operator request, oversize payload, script markup, SSRF/private callback and secret-like input are rejected/redacted as specified.
- Kill after DB commit before HTTP response; retry returns the existing message and thread history remains intact.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- Persistent threaded request/reply intake and bounded rejection evidence work in a qualified storage environment.
- Public and internal conversation views expose only the allowed records, with edit/moderation/deletion lineage.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 12–22 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates none yet. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-04 — Deliver one deterministic service with attributable results

The site provides useful bounded work beyond a message board.

**Status:** reuse_and_verify. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- lib/opo/services/registry.ts
- lib/opo/services/workflow-roi.ts
- app/api/v1/services/[serviceId]/route.ts
- tests/opo/services.test.ts
- docs/opo/service-selection.md

**Dependencies:** OPO-02, OPO-03. **Inputs:** existing admitted source/charter only. **Effect gates:** none for offline work.

**Evidence:** OPO-E03, OPO-E06. **Requirements:** OPO-O04.

**Implementation**

1. Use the existing ROI calculation as the immediately inspectable deterministic candidate; assess optional retained Contract Check only if its exact source is returned and relevant. Compare target agent task, alternatives, cost and verification before selecting the initial advertised service.
2. Wrap the selected calculation/validator in a pure versioned service with input limits, deterministic result hash, explanation, service/source version and request linkage; clients poll authorized result IDs without giving shell access.
3. Implement job states accepted/running/completed/rejected/failed and truthful no-capacity errors; isolated external patches are proposals for review, never executable code received through messages.

**Deliverables**

- selected service adapter
- decision comparing alternatives
- result examples and fixtures

**Tests / pass-fail checks**

- Known ROI fixtures, zero/negative/nonfinite/overflow inputs and schema version mismatch have documented outputs or rejections.
- Repeated equivalent request produces a reproducible result; unsupported service and visitor-supplied commands never reach tools.
- A synthetic outside-format client obtains attributable result and can follow its source/version explanation.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- One useful service has real execution, verifiable outputs and bounded resource cost.
- Contract Check remains an optional evidence-selected service, not a forced business identity.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 6–12 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-124, BOTS-125. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-05 — Define a concrete agent-service offer and economic decision

Requests can become a viable offer with transparent terms instead of treating conversation as demand.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- docs/opo/offer-v1.json
- app/offers/page.tsx
- app/terms/page.tsx
- app/privacy/page.tsx
- app/support/page.tsx

**Dependencies:** OPO-01, OPO-04. **Inputs:** OPO-I04. **Effect gates:** none for offline work.

**Evidence:** OPO-E03, OPO-E04. **Requirements:** OPO-O05.

**Implementation**

1. Select a bounded offer from the admitted service and actual demand evidence when present: deliverable, eligible customer/authorized payer, turnaround, price currency, capacity, exclusions and quality remedy. Before outside evidence, mark price/value assumptions explicitly.
2. Calculate per-request compute/storage/provider costs and contribution scenarios; keep the legacy $9 digital kit as historical pricing, not an imposed price for the new service.
3. Update terms/support/privacy for actual service, delivery, retention, refunds and processor use; show free/quote-ready mode until merchant capability qualifies.

**Deliverables**

- offer-v1 contract
- economic scenarios
- updated customer policies

**Tests / pass-fail checks**

- Offer examples disclose full scope/price/currency and match delivered service limits.
- Unit-economics scenarios include zero demand, full capacity and refund/fee cases with unknown costs explicit.
- No live checkout or paid-service availability is displayed with an absent payment capability.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- A specific reviewable offer and honest free alternative are available.
- Acceptance distinguishes willingness to pay, requested quote, payment and delivered value.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 5–9 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-124, BOTS-127. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-06 — Qualify merchant checkout and payment reconciliation

Authorized customer payment can be confirmed independently and never inferred from redirects.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- lib/opo/payments/adapter.ts
- app/api/v1/payments/webhook/route.ts
- db/opo/002_payments.sql
- tests/opo/payments.test.ts
- docs/opo/payment-readiness.json

**Dependencies:** OPO-05. **Inputs:** OPO-I04. **Effect gates:** OPO-I04, OPO-I08.

**Evidence:** OPO-E04, OPO-E07. **Requirements:** OPO-O06, OPO-A11.

**Implementation**

1. Inspect the existing merchant candidates without creating duplicates; choose only an eligible merchant/hosted route with verified ownership, permitted product, payouts, currency/tax handling, fees and exact checkout destination.
2. Implement provider adapter with order/action idempotency, webhook signature/replay validation, return-page pending state and receiving-system transaction lookup. Keep credentials in host secret references.
3. Run provider-supported test mode distinctly from live; perform a bounded authorized real transaction only with explicit amount/payment authority and verify transaction/status, fee and order mapping.

**Deliverables**

- merchant capability record
- payment adapter
- test-mode receipts
- bounded real transaction/readback when eligible

**Tests / pass-fail checks**

- Forged/replayed/out-of-order webhooks do not create paid orders; client success redirect alone remains pending.
- Timeout after provider acceptance reconciles by stable order/action key without a second charge.
- Test and real transaction IDs cannot mingle; payment amount/currency/offer mismatch blocks fulfillment.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- Qualified checkout yields an independently verified payment record or exact unresolved merchant gate.
- No revenue claim occurs before real settled/authorized payment evidence; refunds/fees retained separately.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 8–16 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-126, BOTS-127. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-07 — Complete fulfillment, support, refunds and accounting

A paid or free request reaches a verified useful result and support can resolve failures.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- lib/opo/fulfillment.ts
- lib/opo/refunds.ts
- lib/opo/accounting.ts
- db/opo/003_fulfillment.sql
- tests/opo/fulfillment.test.ts
- docs/opo/support-runbook.md

**Dependencies:** OPO-03, OPO-04, OPO-05. **Inputs:** OPO-I03, OPO-I04. **Effect gates:** OPO-I04, OPO-I08.

**Conditional dependency:** Any payment-dependent fulfillment, paid entitlement, refund or real-money accounting effect additionally requires OPO-06 merchant/payment acceptance and exact amount/currency/order/grant/provider receipt. The free fulfillment branch remains independent; absent payment gate leaves paid acceptance incomplete.

**Evidence:** OPO-E04, OPO-E07. **Requirements:** OPO-O06, OPO-O07.

**Implementation**

1. Create delivery receipt keyed to request/order/result hash with completion time, access expiry and client acknowledgement where available; payment-dependent branch must additionally satisfy OPO-06 before effect.
2. Implement support cases, retry failed deliveries within offer limits, cancellation/refund proposal-to-provider adapter and receiving-system reconciliation; separate refund authority and maximum amount.
3. Reconcile gross sales, fees, refunds, net collected cash, outstanding liability and compute costs; preserve provider currency/period and avoid converting synthetic jobs into demand.

**Deliverables**

- fulfillment receipts
- support/refund runbook
- reconciled economic ledger

**Tests / pass-fail checks**

- Free and paid fixtures deliver once; payment-pending orders cannot take the paid branch.
- Duplicate refund, crash after refund acceptance, expired delivery link and wrong order access preserve one outcome and correct permissions.
- Accounting reconciles known fixtures and flags missing provider data rather than setting it to zero.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- End-to-end delivery/support works for the useful free release.
- Paid fulfillment/refund acceptance is separately gated by OPO-06 and exact provider receipts; no fabricated commercial validation.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 8–14 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-127. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-08 — Add qualified distribution and honest channel attribution

Relevant agents can discover the service through a small measurable channel set.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- lib/opo/channels/registry.ts
- lib/opo/channels/publish.ts
- lib/opo/analytics/channel-scorecard.ts
- docs/opo/distribution-experiment.json
- tests/opo/channels.test.ts

**Dependencies:** OPO-02, OPO-05. **Inputs:** OPO-I01, OPO-I05, OPO-I06. **Effect gates:** OPO-I01, OPO-I05, OPO-I06, OPO-I08.

**Evidence:** OPO-E05, OPO-E07. **Requirements:** OPO-O08.

**Implementation**

1. Verify the existing OPO X identity and allowed route; keep WHB and other accounts isolated. Choose one initial referral/content experiment and prepare readable announcements that link the exact service.
2. Qualify GitHub under existing ownership/scoped app, Substack publication or LinkedIn Page only when evidence justifies expansion and supported routes exist; routine authorized account organization does not justify fabricated users or website automation.
3. Record per-account baseline, date-added channel, follower/end/net counts, gross cross-platform follows, post-defined impressions, consent-aware referrals and received conversations; subscribers/unknown actor types remain separate.

**Deliverables**

- account capability references
- one initial distribution experiment
- channel scorecard
- publication/readback receipts when eligible

**Tests / pass-fail checks**

- Wrong account/channel/hostname/unsupported route blocks publication while drafts remain ready.
- Fixture with two channels and missing impressions reports comparable gross follows, not unique people; missing remains unknown.
- Synthetic workers/crawlers and real outside users cannot be merged; X AI reply capability stays disabled without X written approval and consent qualification.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- At least one eligible useful distribution route has exact-account delivery/readback or explicit blocked effect with ready content.
- Per-channel exposure and qualified agent participation are measured separately from transactions.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 7–13 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates none yet. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-09 — Ship and verify the useful public service release

Release readable discovery, durable intake, one service and offer through the exact qualified destination.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- docs/opo/releases/release-manifest.json
- docs/opo/releases/public-readback.json
- docs/opo/releases/rollback-runbook.md
- tests/opo/public-journey.test.ts

**Dependencies:** OPO-02, OPO-03, OPO-04, OPO-05. **Inputs:** OPO-I01, OPO-I02, OPO-I03. **Effect gates:** OPO-I01, OPO-I02, OPO-I03, OPO-I08.

**Evidence:** OPO-E01, OPO-E02, OPO-E04. **Requirements:** OPO-O09.

**Implementation**

1. Receive the independent exact-source review and source owner handoff; run appropriate npm lint/test/build checks on the admitted source with required Sites skills.
2. Qualify the exact confirmed hostname, HTTPS, hosting storage binding and public access; retain preview while domain/storage facts are missing. Historical .openai/hosting.json is not authority to publish a guessed destination.
3. Deploy through the selected supported Sites route, perform anonymous HTML/API/request/result readback from outside the owner session, verify version binding and record reversible deployment pointer.

**Deliverables**

- release manifest
- anonymous readback
- restart exchange evidence
- rollback receipt

**Tests / pass-fail checks**

- Anonymous discovery, service request, operator response, restart continuity and abuse rejection pass at the actual public endpoint.
- Public URL/source version match manifest; no owner-only deployment is labeled public.
- Rollback restores previous reviewed release while preserving newly accepted durable conversations.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- A useful public service has exact source review, destination receipt and working recovery.
- Shared autonomy tasks do not delay already-authorized useful worker releases; payment/channel gates apply to their own effects.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 5–9 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-126. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-10 — Integrate durable mission jobs and deterministic events

Message, job, payment and observation events schedule eligible work with a single fenced owner.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- operator/opo/events.py
- operator/opo/state.py
- operator/opo/schedule.json
- tests/opo/test_events.py

**Dependencies:** OPO-03, OPO-04, SH-02, SH-03, SH-04. **Inputs:** existing admitted source/charter only. **Effect gates:** none for offline work.

**Evidence:** OPO-E02, OPO-E05. **Requirements:** OPO-A01, OPO-A02.

**Implementation**

1. Map message.accepted, service.completed, payment.verified, delivery.failed, support.opened, metrics.updated, experiment.due and direction.changed into shared durable events with source revisions.
2. Bind mission jobs/experiments/receipts and append-only decisions to transactional state; claim by mission/resource/epoch and reject stale ownership on state and effect writes.
3. Schedule cheap due checks with next_check_at/evidence_version/decision_fingerprint; retain one active experiment default and avoid any model call for unchanged not-due input.

**Deliverables**

- mission state/event integration
- deterministic schedule
- race/replay/idle evidence

**Tests / pass-fail checks**

- Two Windows processes race for the same conversation job: one owner executes; expired owner cannot finish after fenced takeover.
- Replay webhook/event and restart before acknowledgement: exactly one eligible job and stable next due time.
- A 24-hour synthetic idle clock makes zero inference calls and no outbound effects.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- OPO event processing is replay-safe, durable and independent of the mobile Mac.
- Events reopen only materially changed or due work with explicit ownership.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 8–14 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates none yet. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-11 — Implement evidence-led offer and product experiments

The operator chooses useful next work from actual requests and economics within limits.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- operator/opo/decisions.py
- operator/opo/experiments.py
- operator/opo/budgets.json
- tests/opo/test_decisions.py

**Dependencies:** OPO-05, OPO-07, OPO-10, SH-05, SH-07, SH-14. **Inputs:** OPO-I07. **Effect gates:** OPO-I07, OPO-I08.

**Evidence:** OPO-E05, OPO-E07. **Requirements:** OPO-A03, OPO-A05, OPO-A16, OPO-O10.

**Implementation**

1. Compute eligible decision facts from qualified request/return/use/channel/payment evidence; separate self-generated/synthetic/crawler data and record alternative tactics.
2. Persist predeclared discovery/service/offer/channel experiment baseline, primary metric, harm/quality controls, budget and due window before effects. Choose continue/adopt/amend/revert/stop or waiting_for_evidence without retroactive threshold changes.
3. Route only material reasoning to a qualified measured model; enforce per-job/day/mission tool/token/cash caps before call and prohibit surprise paid fallback. Next experiments may improve the service, terms, onboarding or channel mix within charter.

**Deliverables**

- decision adapter
- experiment contracts
- budget enforcement evidence

**Tests / pass-fail checks**

- High impressions but no qualified requests cannot mark business validated; missing payment evidence cannot produce revenue.
- Low/no traffic closes inconclusive or waits to an explicitly bounded amendment; repeated unchanged metrics cause no model calls.
- Exhausted budget or two unsuccessful repairs yields one blocked record; no fallback can bypass the cap.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- Each decision stores observed facts, chosen hypothesis, an alternative, constraints, next due/action and outcome classification.
- Second experiment is chosen from first-cycle evidence without a fresh launch prompt.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 8–15 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-127, BOTS-60. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-12 — Integrate eligible service and external effect receipts

Autonomous responses, releases, posts and payment-related actions execute only with verified destinations.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- operator/opo/actions.py
- operator/opo/reconcile.py
- tests/opo/test_actions.py

**Dependencies:** OPO-07, OPO-08, OPO-10, SH-06. **Inputs:** OPO-I04, OPO-I05, OPO-I08. **Effect gates:** OPO-I01, OPO-I02, OPO-I04, OPO-I05, OPO-I06, OPO-I08.

**Evidence:** OPO-E05, OPO-E07. **Requirements:** OPO-A04, OPO-A10, OPO-A11.

**Implementation**

1. Register separate action capabilities for internal service job, website reply, release, channel post, hosted checkout creation, delivery and refund; bind account/host/resource, revision, budget and exact content/result hash.
2. Write durable attempt before send, verify service result or provider/public receiving-system identity after send and retain queued/accepted/sent/verified distinctions. Payment branches require completed OPO-06.
3. Derive action key from mission/experiment/version/action/resource; reconcile unknown provider outcomes by stable key/receipts before retry and prevent cross-mission adapter credentials.

**Deliverables**

- mission action registry
- reconciliation adapters
- fault-injection receipts

**Tests / pass-fail checks**

- Kill between effect acceptance and ledger write: resumed operator locates existing reply/post/payment and never doubles it.
- Mutated destination, stale direction or stale fencing token blocks the action.
- No public/paid action occurs for dry-run records, incomplete Jira registration or unqualified account.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- Every admitted action has a durable attempt and result verified at the appropriate destination.
- Uncertainty creates reconciliation work instead of blind retry.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 9–16 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates none yet. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-13 — Wire owner direction, questions and writer outboxes

The operator acknowledges precise owner revisions, asks once and resumes the correct blocked work.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- operator/opo/direction.py
- operator/opo/projection.py
- tests/opo/test_direction.py

**Dependencies:** OPO-10, SH-08, SH-09. **Inputs:** OPO-I08. **Effect gates:** OPO-I08.

**Evidence:** OPO-E01, OPO-E05, OPO-E06. **Requirements:** OPO-A06, OPO-A07, OPO-A08.

**Implementation**

1. Consume authenticated mission direction revisions, acknowledge source/revision actually used and cancel queued effects when pause or changed limits apply. Example: pause paid services and prioritize free format conversion while public messages continue.
2. Bind existing hostname question and future needs_input to one ID/responder/resource; validate supplied resource scope, preserve prior answers and resume only affected preconditions. No asking for secret values.
3. Emit immutable experiment-before-action, outcome and review outboxes keyed to dedicated OPO writer; require native source/scope/readback receipt before registered experiment actions, reconcile writer outage or duplicate response.

**Deliverables**

- owner direction adapter
- question registry integration
- Jira/docs outbox contracts

**Tests / pass-fail checks**

- Replay owner message gives one acknowledgement; pause received after decision but before effect prevents that effect.
- A WHB response or untrusted visitor cannot answer OPO hostname authority; a validated owner revision resumes exactly the dependent job once.
- Writer outage preserves outbox, blocks unregistered experiment action, and permits independent engineering/observation.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- Direction and missing-input handling survive restart without question spam or authority confusion.
- OPO proposals never use the combined parent as a competing issue writer.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 5–10 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates none yet. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-14 — Qualify Windows operations, recovery and privacy

OPO runs independently with bounded failure handling and a portable optional R730 handoff.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- operator/opo/windows-service.json
- operator/opo/ops.py
- docs/opo/restore-runbook.md
- tests/opo/test_recovery.py

**Dependencies:** OPO-10, OPO-12, OPO-13, SH-10, SH-11, SH-12, SH-13. **Inputs:** OPO-I02, OPO-I03, OPO-I07, OPO-I09. **Effect gates:** OPO-I09.

**Evidence:** OPO-E01, OPO-E05, OPO-E07. **Requirements:** OPO-A09, OPO-A12, OPO-A13, OPO-A14, OPO-A15, OPO-A18.

**Implementation**

1. Configure temporary independent Windows execution with host-local secrets/store, mission service identity, process-tree timeout/cleanup and finite retry/repair classes; no worker or inherited schedule modification without recorded handoff.
2. Back up state/receipt manifests with retention and secret exclusion; restore into isolated rehearsal, fence old owner and reconcile unknown effects before enabling writes. Add actionable alerts for failed delivery, store unavailability, spend exhaustion and privacy incidents with one deduplicated escalation.
3. Exercise optional R730 migration only after shared target qualification: export sanitized state version, inject host-local secret references, verify destination ownership and controlled cutover. Keep Windows useful without migration and keep i9 deferred.

**Deliverables**

- Windows service contract
- restore/secret/alert evidence
- optional cutover runbook

**Tests / pass-fail checks**

- Kill a parent with child/grandchild and held pipes: Windows cleanup finishes within configured bound with no surviving mission process.
- Restore latest backup with an in-flight reply/refund; one owner reconciles it and excludes secrets from portable artifacts.
- Pause/resume, storage outage and Mac-disconnected interval preserve useful operation; no unchanged alert repeats.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- Windows start/restart/restore/stop has evidence, bounded failure and actionable alerting.
- Optional R730 acceptance proves fenced takeover; migration is neither claimed nor a release prerequisite.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Conditional dependency:** Optional R730 migration only requires SH-16 qualified target/fence/restore/receipt/rollback acceptance. Independent Windows recovery and runtime acceptance remain eligible without migration.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 6–12 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates none yet. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.

## OPO-15 — Prove two autonomous service-business cycles

Independent review demonstrates the whole cycle and its next decision with genuine external receipts.

**Status:** planned. **Owner:** OPO dedicated Windows release owner / admitted implementation lane. **Source:** https://github.com/pri8771/one-person-ops.

**Owned proposed paths**

- docs/opo/acceptance/cycles.json
- docs/opo/acceptance/review.md
- tests/opo/test_full_cycle.py

**Dependencies:** OPO-09, OPO-11, OPO-12, OPO-13, OPO-14, SH-15. **Inputs:** OPO-I07, OPO-I08. **Effect gates:** OPO-I01, OPO-I02, OPO-I03, OPO-I05, OPO-I07, OPO-I08.

**Evidence:** OPO-E01, OPO-E05, OPO-E07. **Requirements:** OPO-A17, OPO-O10.

**Implementation**

1. Recheck exact released source and run labeled synthetic discovery/request/fulfillment cycle with crash points; keep these separate from real adoption.
2. Within qualified grants, observe a legitimate external request or a declared observation window, decide/register/execute a useful service or distribution experiment, verify actual receiving-system receipt and evaluate evidence.
3. Without a new launch instruction, select and complete a second justified real allowed cycle; include an authenticated owner amendment, pause/resume and restart. A durable evidence wait with a precise due/trigger is a valid operational state, but runtime autonomy acceptance remains incomplete until the second real allowed cycle is completed and verified. Genuine outside-agent adoption and paid business outcome remain separately pending if absent.

**Deliverables**

- cycle traces
- real destination receipts
- distinct independent review
- next experiment or evidence-wait record

**Tests / pass-fail checks**

- Trace every transition observation -> decision -> registered action -> verified receipt -> evaluation -> next decision for two cycles.
- Independent reviewer reproduces source/hash/test selection and inspects real receipts; synthetic markers cannot satisfy external/business criteria.
- Direction and crash tests show no duplicate response/post/charge and zero idle inference between eligible decisions.

**Independent review**

A reviewer other than the implementer records actual identity, model/effort and host; distinct-model review when required by the admitted contract. Self-review does not qualify. Review exact Git commit and SHA256 manifest of changed source/assets/config; distinguish Windows CRLF worktree bytes from Git blobs. Any repair invalidates affected prior approval. At most two repair/review attempts per candidate within admitted budget; unresolved failure creates one actionable block and leaves independent work eligible.

**Acceptance**

- Runtime autonomy acceptance includes repeated operation, owner direction, restart and exact-source independent review.
- Real outside-agent use/revenue only reported when their own evidence exists; absent adoption is honestly inconclusive, not fabricated completion.

**Rollback:** Disable this capability, retain immutable evidence/receipts, restore the last reviewed source/config version and reconcile attempted external effects before any retry.

**Next eligible action:** Designated owner matches the proposed scope to current Jira/source and assigns disjoint paths; then perform implementation step 1. External gates block only the named effects.

**New planning estimate:** 6–12 engineering hours. New planning estimate, not historical estimate or worklog. Reuse accepted returned implementation where its exact source passes this contract. Excludes elapsed observation windows, account waiting and shared SH implementation. Host/provider/account qualification or conflicting release-worker ownership can delay dependent effects; offline work remains eligible.

**Jira:** key null; matching candidates BOTS-60, BOTS-127. Writer: Dedicated owner-started OPO Cursor Windows writer. Compare current description, accepted source and dependencies; reuse/extend only exact matching scope, otherwise propose a linked missing-scope task. Preserve original estimates, actuals and historical evidence; record native readback before admitted effects.
