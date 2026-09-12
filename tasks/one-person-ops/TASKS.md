# One Person Ops

**Goal:** Agent-facing revenue website and genuine AI/bot participation, with cumulative social follows and exposure.

**State:** priority; all entries proposed, Jira mapping pending. Read [entrypoint](../README.md), [roadmap](../../BOT_ROADMAPS.md) and [source evidence](../../CURSOR_MAC.md). These are saved facts, not fresh live checks.

**Next readiness action:** Route source/domain/storage reconciliation to the existing writer. The full shivangchordia domain is unresolved; reuse the pending question.

**Batch lanes:** Cursor Mac: source/specification and admitted OPO product work. Antigravity Windows: assigned small QA. Independent reviewer and release owner: coordinator assignment.

| Internal ID | Depends on | Acceptance / task done | Required evidence |
|---|---|---|---|
| `opo.01` | Jira admission | Reconcile source and launch contract: Source hashes, dirty assets, repository/account facts and revised Jira contracts preserved; missing domain/storage facts named. | source-manifest.json; jira-readback.json; needs-input.json |
| `opo.02` | opo.01 | Discovery and service interface: Readable discovery, versioned message/service examples and one selected demonstrator pass scoped interface checks. | artifact-manifest.json; interface-checks.md |
| `opo.03` | opo.01 | Durable communication and controls: Intake deduplicates and survives restart; authenticated controls, privacy/moderation and full adapter communication records pass checks. | restart-checks.md; synthetic-exchange.json; security-checks.md |
| `opo.04` | opo.01 | Offer and payment readiness: Concrete offer/terms, eligible payment route and fulfillment/refund handling are verified; unavailable capability remains blocked. | offer.md; redacted-payment-readiness.json |
| `opo.05` | opo.02, opo.03 | Review and qualified public launch: Exact-source review, confirmed target, anonymous discovery, labeled synthetic exchange and rollback/readback pass. | review.md; release-receipt.json; public-readback.json |
| `opo.06` | opo.05 | Outside use and business evaluation: Predeclared window evaluated from real outside-use/channel evidence; transactions, costs and uncertainty separated; next decision reviewed. | experiment.md; observations.jsonl; evaluation.md |

`opo.03` can start after 01; acceptance additionally depends on the 02 interface. `opo.05` also needs actual target confirmation and exact-source review. `opo.06` may evaluate free use, but payment actions additionally require `opo.04`. Sites skills apply if the original Sites project is selected.
