# Import provenance and reconciliation

Input: owner-approved conversation attachment `social_bots_delivery_plan.patch`.
Original bytes: 183820.
Original SHA-256: a200dcb3f1129fae6a4e8ded0f3472ab8a8979847a0d45eca19e06a6030e121c.
Original patch contained 19 additive delivery files. It applied cleanly to an isolated empty test repository and its validator suite passed 30 tests in this review. This does not prove application to an arbitrary dirty worker checkout.

LEAD-047 adopts the patch into canonical coordination. TASKS/GATES/RECONCILIATION preserve the supplied records with JSON whitespace normalization. The validator and its tests are imported. Prose overlapping the existing committed next-round package is routed to that material to avoid competing plans and repeated context. README, EXECUTION, IMPORT, NEXT_SESSION and validation/provenance notes are updated for the actual import and release. Original baseline/test-report wording is historical, not current status. Do not compare normalized files against the attachment's old PACKAGE_SHA256.txt as though they are identical; Git tree/blob hashes bind this adopted version.

No runtime feature code or worker branch is rewritten by the import. A separate current lead release permits Fable to change implementation source in its own branch after preserving work and checking for concurrent changes. No worker acknowledgement is fabricated.

Do not apply the downloaded patch a second time. Fetch canonical coordination and inspect the delivery directory. Merge or copy only the approved coordination changes into a clean integration worktree, preserving runtime work. If unexpected conflicts exist, preserve both versions and resolve by content/ownership; never force-reset a dirty branch.

Canonical baseline audited for this import: 2cda05b4d0144687ca842ac4fe104aa3824e6039. Fable branch observed: 72a55319cf41f9910c5d3b9623129de3ac0eea31. Cursor observed: 74a515b7f3e30c94979e0f66dc6daae66daed571. Refresh before implementing; an unpushed local change was not available for this review.
