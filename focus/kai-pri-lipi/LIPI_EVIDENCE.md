# Lipi Standard — evidence and next milestone

Reviewed 2026-09-12. This is a planning snapshot; Lipi's existing ops files retain authority. No store, runtime, Jira, account, or product changes were made.

## Goal and why

The target is a business that independently maintains its catalog, merchandising, permitted acquisition, fulfillment monitoring, support preparation, and learning loop, asking the owner only for decisions outside explicit authority. The economic outcome is delivered orders with acceptable contribution and customer experience; passing repository checks is supporting infrastructure.

The user's Indian-apparel-to-America dropship idea remains a relevant business hypothesis. Current implemented sourcing is Shopify + Printful, with an English-first premium American apparel/accessories/home direction adopted August 21. An India-sourced apparel pilot needs a separate supplier/product/US-delivery proof before changing catalog claims or assuming existing Printful mappings apply. This review neither rejects that idea nor treats it as implemented. See [decisions](/Users/pchordia/Documents/Codex/2026-08-14/lipi-worktrees/CURSOR-LIPI-INTWAVE-S07-20260909/ops/DECISIONS.md).

## Current truth

| Area | Evidence-backed conclusion |
| --- | --- |
| Source | Canonical remote is `pri8771/lipi-standard-store`. Retained checkout `CURSOR-LIPI-INTWAVE-S07-20260909` is clean at `37c447bbd90b8aac86f768a480b25eb4d8fc6c44`; overnight checkout has the same tip. Main checkout `/Users/pchordia/Documents/Codex/2026-08-14/if` is clean at `9b10024`, behind its locally recorded origin/main by one commit. Remote was not fetched. |
| Latest worker evidence | [September 12 return](/Users/pchordia/Documents/ChatGPT/Astra/planning/cursor-overnight-2026-09-11/returns/lipi/SESSION_RETURN.md), recorded 04:31:30 UTC: no new source commits; all 25 admitted LIPI-63–87 local contracts already satisfied; all still have external/owner acceptance residual. Reviewer reused prior reviews; none dispatched this session. |
| Verification scope | [Recorded aggregate log](/Users/pchordia/Documents/ChatGPT/Astra/planning/cursor-overnight-2026-09-11/returns/lipi/logs/aggregate_launch_readiness_homebrew.stdout.log): 56/56 pass, repository consistent, launch/publication not ready; seven catalog records, six verification-pending, one blocked, 23 provider unknowns. Logs inspected; tests not rerun for this document review. |
| Commerce | [State ledger](/Users/pchordia/Documents/Codex/2026-08-14/lipi-worktrees/CURSOR-LIPI-INTWAVE-S07-20260909/ops/STATE.md) latest signed-in analytics evidence is August 30: zero completed checkouts/orders/sales in the described periods, setup/QA-contaminated traffic. August 30 owner receipt says Direction A theme was published while legacy products remained purchasable. September workers explicitly performed no publication, purchase, charged checkout, or elapsed fulfillment cycle. Current live state remains unverified. |
| Autonomy | [Service source contract](/Users/pchordia/Documents/Codex/2026-08-14/lipi-worktrees/CURSOR-LIPI-INTWAVE-S07-20260909/services/lipi-control-plane/README.md) provides eleven read-only/proposal tools, disconnected providers, repository-only answers, and no mutation executor. Plans/fixtures exist for approvals, rollback, support, measurement, and seven-day operations; these do not establish a running autonomous store. |

September 1 decisions move store execution to Windows. The [September 7 removal receipt](/Users/pchordia/Documents/ChatGPT/Astra/planning/scheduler-removal-2026-09-06/LIPI_WATCHDOG_REMOVAL_RECEIPT.json) records the Mac watchdog disabled, unloaded, and its definition moved. This supersedes older MEMORY/PLAN claims of active Mac automation; current Windows runtime health was not inspected.

## Launch blockers and operating limits

The [current capsule proposal](/Users/pchordia/Documents/Codex/2026-08-14/lipi-worktrees/CURSOR-LIPI-INTWAVE-S07-20260909/quality/session12h/capsule-decision/capsule-membership-decision-contract.json) retains Meridian cap, Open Current tote, and Threshold Study 12×16 print, with Quiet Route jogger conditional. Membership is not owner-approved.

[Business rules](/Users/pchordia/Documents/Codex/2026-08-14/lipi-worktrees/CURSOR-LIPI-INTWAVE-S07-20260909/ops/BUSINESS_RULES.md) require a 20% worst-case all-in contribution floor and 10% defect reserve. $99 free US shipping is conditional on mixed-cart proof. Current provider costs, checkout shipping, fees, and some product costs remain unknown. Price changes have conditional authority; discounts, refunds/replacements, purchases, publication, and customer sends remain owner-controlled. No paid-ad authority is established. Historical tax posture is an owner record, not a refreshed legal determination.

Samples/inspection, exact fulfillment mapping, shipping/checkout, policy/content approval, assistive-device QA, coordinated public cutover, and actual operating receipts remain open. Existing keys: LIPI-63–69 product/economics; 70–72 samples/shipping; 73–79 storefront/checkout/launch/rollback; 80–87 measurement/organic/support/fulfillment/cycle close. Keys are references from receipts, not current Jira readback.

## First useful milestone and sequence

**Produce one genuinely purchase-ready capsule/sample decision, then validate a delivered sample.** Suggested owner: Lipi execution agent, with the business owner deciding scope and spend.

1. Reconcile Quiet Route retain/exclude and refresh exact provider variants, costs, US shipping, and fee inputs (LIPI-63–71).
2. Repair the [sample proposal](/Users/pchordia/Documents/Codex/2026-08-14/lipi-worktrees/CURSOR-LIPI-INTWAVE-S07-20260909/quality/session24h/sample-order/sample-order-approval-contract.json): all quote totals are null, and its Open Current hint says `natural` while the product contract specifies Denim Blue/Mantis M196. Do not order from that hint. Return exact identities, total, quote date, and required decision in a simple file.
3. After scoped purchase authorization, obtain the sample and record physical accept/narrow evidence (LIPI-70/72); then resolve checkout, policies, and launch approval before cutover (75/77/78/82/83).
4. After launch, prove seven real days of allowed acquisition, order/support monitoring, aggregate measurement, and owner exception handling (80–87). A later executor must demonstrate durable action receipts, replay protection, recovery, and current authority before wider autonomy.

Owner nudges should reference one unresolved decision file, explain its business consequence, and stop repeating unchanged requests. File inputs are sufficient now; a new Slack app is not a launch prerequisite.

