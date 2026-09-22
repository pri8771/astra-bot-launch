# Live proof matrix — V0.4 through V3.0

This is the next-round test specification, not a record of tests already passed. All existing milestone requirements remain. Numerical windows below are proposed default acceptance profiles to freeze in the lead run manifest before execution; they are not elapsed-time claims, provider entitlements or grants. Never shorten a frozen window or change a threshold after seeing a failure.

## Common packet

Every scenario records candidate source SHA, dirty-tree status, config/schema hashes, actual environment/OS/runtime, start/end times, entrypoint and safe command, test/run ID, input/output hashes, child/parent scope, grants/reservations used, external receipts, failures, result and reviewer. Never include tokens, cookies, credentials or private raw community data in Git. Logs should say tests discovered, passed, failed, errored and skipped separately.

Fixture, real network retrieval, real model call, actual target-host process execution and verified public effect are separate dimensions. A bundle can contain mixed evidence; it cannot label every stage LIVE because one HTTP request was real. No flags such as live=true or acceptance_eligible=true grant acceptance. Report capability, integration, operational evidence and lead acceptance separately.

## Version tests

| Gate | Required real-world scenario | Pass/stop criteria |
|---|---|---|
| V0.4 | Frozen E1/E2 raw source records; the five authorized persona/evidence calls through the actual provider; normal policy and persistence path | Same provider/model configuration; persona-only/evidence-only hashes isolate the intended inputs; predefined meaningful alternatives/priorities differ; no retries to fish for a pass; no public effect. Failed divergence remains open. |
| V0.5 | Actual decision-relevant sources through capture, claim assessment, formatting and required reviews | Final content hash and material claims are supported by attributable review; forged provenance, changed excerpts or missing reviewer cannot pass. Independently review at least one successful real candidate plus negative engineering cases. |
| V0.6 | A separate new-current-evidence dry run for social-a, social-b and social-c through the normal runner | Each reaches candidate creation and all required reviews, prospective experiment registration, persisted evidence/decision learning and next schedule; no audience performance invented; no publication. NO_ACTION alone does not prove create/review stages. |
| V0.7 | Native scheduling on one authorized persistent host; all bots served; crash/no-overlap test; two engineering-worker/lead cycles | At least three distinct scheduler-fired sessions with one start heartbeat each, actual child receipts and no starvation across the three bots. Include a killed worker, live-lease rejection, later takeover, fresh direction consumption, actual lead review and later implementation without owner relay. Shell loops do not qualify. |
| V0.8 | Fresh readback of each required X/Instagram/TikTok/Reddit/Facebook route and available analytics route | Exact identity, minimal scopes, support/quotas and timestamp documented. Unsupported or unavailable routes remain blockers; no invented free API entitlement or hidden browser workaround. |
| V0.9 | One explicitly authorized bounded canary per general persona | Verified destination, content, permalink/readback, duplicate/uncertain-effect handling and real observation window. Proposed observation reads at +24h and +72h, or a platform-justified frozen profile. Never invent metrics to complete a window. |
| V1.0 | Three bots run the actual scheduled pipeline over a frozen 24h profile with multiple cycles per bot | Real observations -> decisions -> authorized actions or explicit abstentions -> readback -> learning -> next work. Public action limits remain separately granted. Zero unauthorized effects; no hidden manual task relay. |
| V1.1 | Target-host outage/restart/fault exercise during a frozen 24h unattended profile | Every required failure mode produces recoverable state and no blind duplicate effects; original errors retained. Safe blocking counts as safe behavior, not successful content generation. |
| V1.2 | Real account availability/evidence changes feed platform selection | Show available-route changes alter the decision or produce NO_PLATFORM; do not publish merely to test a scorer. |
| V1.3 | Read real platform analytics and normalize/re-read them | Provenance, window and semantic compatibility preserved; missing is not zero; repeated snapshots do not inflate totals. |
| V1.4 | Persist and later retrieve evidence-backed audience hypotheses from those observations | Real support/contradiction refs affect confidence; engineering time-shift validates decay but is not months of live history. |
| V1.5 | Close a prospective experiment after its real observation window | SUCCESS/FAILURE/INCONCLUSIVE/STOPPED are honest; no deterministic requirement to succeed. Scope and measurement compatibility must hold. |
| V1.6 | Transform a real-source idea into two required platform-native candidate formats | Preserve factual support and lineage; novelty/format review on final payload; publishing separately gated. |
| V1.7 | Ingest a real authorized thread/comment read-only, draft/review a response and persist conversation state | Correct thread/account/persona binding; abuse/manipulation boundary holds. Public reply not required without its own grant. |
| V1.8 | Both cultural personas run source/reviewer/correction workflows on real source material | Real attributable cultural review and independence/disclosure treatment; no fictitious reviewer or disguised promotion. |
| V1.9 | Frozen 72h persistent-host stabilization profile; recovery from a retained backup | Receipt coverage, declared queue/availability targets, resource ceilings and supported-path defect registry pass. No unresolved critical/high supported-path correctness or authorization defects. |
| V2.0 | Compatible real measurements cause a bounded strategy revision; later observations cause hold, validation or rollback | Normal production loop writes an immutable revision and consumes it later. Inadequate data yields hold and blocks the positive-change demonstration; do not invent an effect. |
| V2.1 | Production lifecycle processes real current/stale/contradictory strategy evidence | Revision/hold/expiry/rollback is traceable; time-shift-only cases are engineering supplements. |
| V2.2 | A real owner-relevant goal becomes bounded planned work through the production dispatcher | Dependency-ready tasks actually execute; a real or clearly labeled injected blocker causes bounded replan preserving completed work. |
| V2.3 | One integrated target-host mission: real goal -> strategy -> plan -> researcher and independent reviewer/analyst -> verified adoption -> later decision | At least two distinct specialist roles with attributable real outputs; actual provider where required by the contract; hard time/worker/model limits; rejected malformed-result engineering case; no implicit publication; all prior operational gates accepted. |
| V2.4 | Real accumulated records influence production retrieval and a later decision | Demonstrate actual available history and an old/conflicted/seasonal record; synthetic aging is labeled engineering. Do not claim months of history that do not exist. |
| V2.5 | Sufficient real aggregate observations support differentiated audience segments | No person-level/sensitive profiling. Insufficient evidence yields INSUFFICIENT_DATA, not two manufactured clusters. Required sample/coverage policy is frozen before judging usefulness. |
| V2.6 | Newly captured trends feed a relevant experiment and reject an irrelevant high-volume candidate | Real timestamps/sources; persona fit over raw popularity; selected work reaches the actual plan queue. |
| V2.7 | One real idea drives platform-native sequenced work through the production scheduler | Common lineage, compatible per-platform measurement and duplicate prevention; public execution requires an applicable grant. No unsupported causal cannibalization claim. |
| V2.8 | Actual worker/platform budgets influence the work that the scheduler really selects | Reserved exploration/reliability capacity and starvation prevention are visible in receipts, not merely scorer output. |
| V2.9 | Actual telemetry plus labeled seeded defects generate bounded improvement artifacts | Findings cite evidence; proposals traverse normal independent review; no self-approval or automatic unauthorized deployment. |
| V3.0 | At least two persistent brands and multiple personas run concurrently for a frozen 24h profile | Scoped strategies/accounts/memory; shared public fact allowed; private cross-brand access denied; portfolio goals/budgets affect real work; specialists retire; organizational lesson and bounded repair proposal; recovery/restore and all predecessor gates accepted. |

## Efficient reuse

A retained run can satisfy multiple requirements only when its source/config/environment/inputs match and the exact acceptance predicate is demonstrated. Record a reuse map; never rerun a paid/live action just to fill another folder. Larger unattended windows may cover smaller ones with explicit mapping; they do not waive earlier acceptance order or data sufficiency.

## Negative controls required before scarce live calls

Attempt authorization bypass via direct library call and false fixture metadata; attempt cross-scope context access; run zero budget; corrupt/omit evidence; change final content after review; interrupt persistent commit; replay task/public attempt IDs; let a non-cooperative worker exceed its deadline. These are engineering tests and must not call real external providers or publish. Fix failures before requesting a live run.

## Final verdicts

Use PASS, FAIL, INCONCLUSIVE, BLOCKED_AUTHORIZATION, BLOCKED_HOST, BLOCKED_ACCOUNT or BLOCKED_DATA with the exact failed predicate. A review-pending packet is SUBMITTED, not ACCEPTED. No last-round pressure changes these meanings.
