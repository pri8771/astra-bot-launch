# Existing V0.4 public-capture inventory — read-only

Date: 2026-09-22

## Scope and canonical decision

- Canonical branch inspected without checkout or fetch: `origin/chatgpt/social-bots-plan-20260920@47bd5e680f364d21bdff7a070257a2b6d2d0fcf1`.
- Governing decision: `social-bots/lead-reviews/LEAD-064_2026-09-22T0845.md`.
- Current binding preparation: `coordination/astra-bot-launch/social-bots/lead-reviews/CODEX_EXECUTION_BINDING_20260922.md` and `receipts/evidence/CODEX-V04-BOUND-APPROVAL-PREPARATION-20260922/`.
- No network, collector, provider, model, credential, account, runtime, grant, scheduler, or repository write was performed.

## Result

**No already captured repository-local pair is suitable for final V0.4 E1/E2 product acceptance.**

The only retained raw public-capture pair found under the V0.4 freeze is SB-R07-042:

| Evidence | Public source | Retrieved | Bytes | Raw SHA-256 | Receipt |
|---|---|---:|---:|---|---|
| E1 | `https://example.com/` | 2026-09-21T19:37:40Z | 559 | `ff67a9d764d6a2367a187734e697f6a53217db9a21c101d410a113ca871a299d` | `cap-930c10094e914375`; collector `sbots.source-collector@1.3.0`; HTTP 200; trusted transport |
| E2 | `https://www.rfc-editor.org/rfc/rfc8259.txt` | 2026-09-21T19:37:40Z | 28,360 | `61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7` | `cap-23b5ab6d8b504a76`; collector `sbots.source-collector@1.3.0`; HTTP 200; trusted transport |

Targeted raw-byte inspection confirms E1 is the Example Domain documentation page and E2 is RFC 8259, a December 2017 JSON standard. Their raw hashes and byte counts match the receipts and prepared matrix. Copies in multiple review worktrees have the same hashes; they are copies of this one freeze, not additional captures.

The remote canonical tree contains plans, schemas, delivery-source citations and the accepted SB-V04-005 artifact packet, but the targeted receipt/hash search found no additional committed collector receipt or frozen raw public snapshot eligible to substitute for E1/E2. The prior accepted canary also remains ineligible as a matrix baseline because the canonical plan says its complete pre-invocation context/prompt was not cryptographically bound.

## Why the retained pair cannot be reused

LEAD-064 makes the suitability decision explicit:

- both captures are genuine HTTPS engineering inputs with trustworthy receipts;
- Example Domain carries essentially no meaningful changing social signal;
- RFC 8259 is a stable technical specification, not current audience/context evidence;
- divergence on them would demonstrate sensitivity to arbitrary content, not adaptive response to materially different current Social Bots evidence;
- they must be replaced by two genuine, current, materially distinct public captures relevant to the bots' research/audience/content domain;
- the replacement captures must use the accepted collector, be frozen before call 1, and receive a lead suitability judgment and pin before activation.

The newer binding packet closes source/matrix execution binding at exact source `fec97738ec0e9407415f60228f7c3938613396c3`, but it repeats that the Example/RFC snapshots remain unsuitable. Binding correctness does not change evidence suitability.

## Exact remaining frontier

The smallest next authority step is a **lead release for capture preparation**, naming or approving the public Social Bots evidence domain and allowing exactly two current, materially distinct public-source captures through the accepted collector. LEAD-064 currently says no new public-source capture is authorized, so existing authority is insufficient even for that preparation.

After capture, the lead must judge E1/E2 suitability and pin the raw bytes, receipts, URLs, ordered five-case closure, and then-current accepted source SHA/tree. Separately, the product owner must explicitly authorize the bounded maximum-five-call subscription batch before a canonical runtime grant is activated. These are distinct gates; neither is satisfied by the existing freeze, binding repair, or silence.

## Evidence inspected

- Canonical `LEAD-064_2026-09-22T0845.md`
- Canonical `V04_DIVERGENCE_ACCEPTANCE_PLAN.md`
- Binding review `CODEX_EXECUTION_BINDING_20260922.md`
- `E1.receipt.json`, `E2.receipt.json`, `PREPARED_MATRIX.json`, `FREEZE_MANIFEST.json`, `audit.json`, `checks.json`, and dormant binding metadata
- Public raw files `SB-R07-042/freeze/E1.raw` and `E2.raw`

Recommendation: **REVIEW_BLOCKED** for final V0.4 evidence preparation. Codex is the review-preparation agent, not formal acceptance authority. Request lead disposition on binding PR16 and an explicit bounded capture-preparation release. No new source was collected.
