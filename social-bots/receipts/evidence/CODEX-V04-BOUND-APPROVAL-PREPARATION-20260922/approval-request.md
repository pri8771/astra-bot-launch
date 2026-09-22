# PREPARATION ONLY — reviewable owner request for V0.4 controlled divergence

**Current authority:** `authorized=false`; owner authorization received: **no**; live calls authorized: **0**. This packet does not activate a grant, create a canonical runtime manifest, run SESSION_ONCE, or contact a model/provider/account/network/host/scheduler.

## Exact request for the product owner

> Authorize one new bounded V0.4 controlled-divergence batch of **at most 5 live adaptive Claude Code subscription calls**, with **zero new spend**, for SB-V04-002/SB-V04-004 acceptance only. Use the existing subscription-authenticated Claude Code path with `ANTHROPIC_API_KEY` absent, no injected runner, no effect tools, no account mutation, no public post/message/purchase/destructive action, and no PAYG/API fallback. Execute one fixed matrix: social-a/social-b/social-c/cultural-primandir-atman on frozen evidence E1, then social-a on materially different frozen evidence E2. Hold objective/state/policy/provider configuration constant except the declared single variable. Maximum 5 calls, no retries. On provider/schema/authorization failure, stop and preserve the failure. Authorization expires 2 hours after the lead activates the canonical manifest. This authorization is new and does not revive or modify the consumed prior one-call grant.

Approval, if given, authorizes only the bounded request above. It does not itself create the lead manifest or permit execution until the binding gap below is resolved and the lead activates a canonical manifest.

## Exact frozen inputs under review

- Accepted source requested for execution: `8c86898d1c6641adbf5c9884e1aa7ab2923b1af3`, tree `72bccc0dc5ee9eaf2919dcdfd0ac35b568719c5a`.
- Original freeze producer source: `22d6234f560e0dce26e6503d32c51058cb7ce0be`.
- Freeze: `SB-R07-042`; prepared matrix SHA-256 is in `audit.json`; every context/prompt digest is listed there and verified by current accepted code.
- E1: 559 bytes captured over trusted HTTPS from `https://example.com/`, receipt `cap-930c10094e914375`.
- E2: 28,360 bytes captured over trusted HTTPS from `https://www.rfc-editor.org/rfc/rfc8259.txt`, receipt `cap-23b5ab6d8b504a76`.

E1 and E2 are genuine public HTTPS captures with matching retained raw-byte hashes and trusted collector receipts. They are not generated engineering fixtures. They are deliberately controlled public documents rather than private/account evidence or current social/news feed content. That limitation must remain visible to the acceptance authority when judging whether they are product-representative enough.

## Fixed matrix

| Case | Persona/workspace | Evidence | Only intended changed variable |
|---|---|---|---|
| P0 | social-a | E1 | baseline |
| P1 | social-b | E1 | persona |
| P2 | social-c | E1 | persona |
| P3 | cultural-primandir-atman | E1 | persona |
| E0 | social-a | E2 | evidence |

Required comparisons are P0/P1, P0/P2, P0/P3, and P0/E0. Current verification reports all four isolated at both context-digest and prompt layers. Objective, pending count, duplicate state, prior hypotheses, policy posture, allowed actions, and provider configuration are held constant. There are exactly five calls, no retries, and fail-fast preservation of the first provider/schema/authorization failure.

## Precise activation blocker

The packet is concretely reviewable by the owner because the exact accepted source, matrix bytes, evidence hashes, prompt files, cases, limits, and safety posture are all named here. It is **not yet safe to activate through the current machine gate**:

- `PREPARED_MATRIX.json` contains per-case context/prompt/evidence hashes but no `source_sha` or `source_tree`.
- The canonical authorization-manifest schema in `runtime/authorization.py` requires artifact scope, run scope, lane, provider mode, call count, expiry, and safety booleans, but has no required `source_sha`, `source_tree`, or `prepared_matrix_sha256`/`freeze_manifest_sha256` field.

Therefore a canonical manifest could authorize the same artifact/run/lane while not machine-binding execution to the exact source and frozen bytes reviewed here. Before activation, the lead must add and enforce those bindings or provide an equivalently machine-enforced exact-source/matrix preflight. A prose source pin in this packet is not sufficient runtime enforcement.

No permission is inferred from silence. Until explicit owner approval and a bound lead manifest both exist, the verified gate remains denied.
