# Social Bots — Astra coordination proposal, 2026-09-22

Status: **READY_FOR_LEAD_REVIEW / PROPOSAL_ONLY**. This note requests formal lead disposition; it does not accept an artifact, promote a version, release a held task, or authorize live execution.

## Owner direction and canonical ladder

The current owner directive is: **"My goal is to reach 2.7 on each, I'll be happy with 2.3."** For Social Bots, record **V2.3 as the floor and V2.7 as the target**, superseding the earlier V1.3/V1.7 ceilings while retaining every required predecessor and separate action grant. Codex is coordinating and finishing implementation directly; no Fable dispatch is authorized.

The canonical ladder already defines both versions in `social-bots/delivery/GATES.json`:

- **V2.3 — Integrated specialists and parent reasoning**, `SB-V23-001..003`: ordinary production H1–H4 execution; bounded researcher and reviewer/analyst tasks; safe adoption and rejection; accepted output consumed by later parent reasoning. Real provider calls require their own applicable grants.
- **V2.7 — Cross-platform strategy**, `SB-V27-001..004`: reuse the CanonicalIdea store; create supported platform-native reviewed drafts with common idea/claim lineage, real route constraints, sequencing and duplication controls. Publication remains separately authorized.

Sequential operational predecessors remain required. `VERSION_EXIT_MATRIX.md` and `LATER_VERSION_CONTRACTS.md` preserve the positive measured strategy-change requirement; a HOLD-only or fixture-only run cannot replace it. Official product phase remains **V0.4.x / V0.4 in progress**.

## Current Git and existing verdict

Read-only remote checks during this pass observed:

- canonical `chatgpt/social-bots-plan-20260920`: `7451465a74bd06a2676efd7a04cd0f60a86463c5`;
- PR16 `codex/bots-execution-binding-20260922`: `fec97738ec0e9407415f60228f7c3938613396c3`, tree `43e80b92d8ae559db55a41ed33329695e6fd03fc`;
- PR17 `codex/bots-capture-prep-20260922`: `da53159704e3e1dfefb8d7e4d2518fdc889317fb`, tree `32a7e6c18f2fea4e6f6f32b5d7ae65af56f18e6d`.

Canonical `social-bots/lead-reviews/LEAD-065_2026-09-22T0934.md` formally **ACCEPTS PR16 ENGINEERING at that exact SHA/tree**. Its still-open draft PR and absent GitHub review do not erase the native verdict. Do not request duplicate engineering acceptance or infer any live/model approval from that verdict.

PR17 is an open draft with no GitHub comments/reviews/checks observed. Its local worktree was clean. The pending disposition is **capture suitability and the next preparation release**, not PR16 engineering acceptance.

## Exact PR17 capture integrity readback

Evidence directory: `social-bots/receipts/evidence/CODEX_CURRENT_CAPTURE_20260922/`.

Both captures were retrieved at `2026-09-22T11:28:42+00:00` through the recorded accepted collector path, collector version `1.3.0`. The retained receipts report HTTP 200, `status: ok`, trusted `live-capture`, non-partial content, and extraction `not_attempted`.

| Input | Source / publication | Receipt | Bytes | Raw SHA-256 | Receipt-file SHA-256 |
|---|---|---|---:|---|---|
| E1 | Meta Reels India audience evidence; raw publication timestamp `2026-06-04T06:56:43+00:00` | `cap-7920a4414afe4fe4` | 345208 | `adf1d1b5f7006431bf3806479d8a227a4152cf5472a879865f9606586bdc069d` | `d4aa9f7fc89bd06edd995d1a4c30a4ba121aa0abd6cbf6d73cf4c3fc7e63088e` |
| E2 | TikTok/Amplify creator-led content series; visible publication date `2026-09-14` | `cap-9701ad2cb45c4b19` | 74480 | `72aefb0b9d06e72f08e10a12e18df6d81108ce430f0b7a5ffec941c31c410cce` | `08755929630fa107a781343046b8cb469cf98a2bb4313f716d4946f6c420ae00` |

Recorded source URLs:

- E1: https://about.fb.com/news/2026/06/reels-is-shaping-indias-video-first-future-across-gen-z-women-bharat/
- E2: https://newsroom.tiktok.com/tiktok-and-amplify-launch-new-creator-led-content-series-for-brands?lang=en-AU

This pass independently recomputed raw and receipt-file SHA-256 values and byte counts; all match `CAPTURE_INDEX.json` and the receipts. Retained HTML independently contains the stated source titles and publication dates. No new capture or external content retrieval was performed.

`CODEX_PR17_CAPTURE_INTEGRITY_RECOMMENDATION_20260922.md` already recommends acceptance of capture-package integrity at candidate `033b973351a9e7d1b2204f9037f901bac1810140`; the present PR17 head adds that review record. Neither that recommendation nor this byte-integrity readback accepts normalized factual analysis or final V0.4 suitability. **E1's June publication age, decision relevance, and appropriateness for a September controlled comparison need an explicit lead judgment.** Trusted capture provenance does not itself prove current relevance.

The Example Domain/RFC8259 pair remains retained engineering evidence and explicitly unsuitable for final product acceptance under LEAD064/065.

## Held work and unapproved gates

- LEAD065 released exactly two capture candidates; that preparation is complete. It did **not** release final P0/P1/P2/P3/E0 matrix rebuilding, dormant owner-request replacement, or manifest activation.
- LEAD063 bounded reasoning-unavailable retry policy remains specified but implementation **HELD**, explicitly reaffirmed by LEAD065. No source change is proposed under that held item.
- Canonical `SB-R07-073` (native scheduler installation/readback) and `SB-R07-074` (three real scheduler-fired receipts) remain **PLANNED**, with empty evidence arrays. Host preflight/tests or direct invocations do not satisfy them.
- No new model/provider, account/mailbox, public/application, host/scheduler, spend, main-merge or deployment grant has been approved in this pass. No new scheduler, SESSION_ONCE, Fable handoff, source edit, or live action occurred.

The consolidated owner request must retain separate, concrete grants: a maximum-five-call/no-retry/zero-spend Claude Code subscription divergence batch after exact source/tree/matrix pinning and lead activation; designated persistent-host and existing-scheduler facts plus any later explicit host/scheduler authority; exact supported account/credential aliases and owner consent; content-hash/account/persona public-canary approvals and external readback; bounded analytics windows; attributable cultural review; separate generation/reviewer/specialist budgets; actual lead-write transport; and scoped backup/recovery drills. Prior conditional account-setup allowances are historical context, not inferred current execution grants. The dormant five-call request is not authorization and its superseded source must not be activated unchanged.

## Requested lead disposition and next bounded action

1. Reconcile native target metadata to the current owner's V2.3 floor/V2.7 target, preserving official V0.4.x status and required live predecessors.
2. Issue an exact PR17/E1/E2 suitability verdict: accept the pair as final divergence inputs, explicitly considering E1's June recency, or specify the narrow replacement-source criterion. Do not repeat either capture without a new applicable release.
3. If suitable, explicitly release **prepare-only** rebuilding/freezing of P0/P1/P2/P3/E0 on an accepted PR16 descendant, with zero provider calls. The resulting source SHA/tree and complete matrix digest must then be reviewed before replacing the dormant owner request.
4. Keep retry implementation held unless the lead separately releases the already-specified bounded repair. Identify any additional dependency-safe engineering task through its native card and ownership boundary.

After this disposition, Codex can perform only the next released bounded task. Owner grants and lead activation remain distinct prerequisites for live execution. No self-acceptance is requested or recorded.
