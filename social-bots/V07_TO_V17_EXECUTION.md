# Social Bots execution — V0.7 through V1.7

This plan becomes active **after the V0.7 recovery contract closes**. It is deliberately decomposed into SP1/SP2 execution slices so workers do not receive broad milestone-sized assignments.

## Operating rule

- One active implementation session at a time unless ChatGPT explicitly releases independent non-overlapping slices.
- One fresh session = one SESSION_ONCE heartbeat.
- Prefer one slice per commit.
- After a slice is submitted, continue the next dependency-safe slice without waiting for owner prompt relay.
- Parent milestone artifacts in MILESTONE_MANIFEST remain the official promotion gates; the SB-S* slices are implementation units feeding those parents.
- Public effects, account auth and paid/model budgets remain explicit owner gates.

## V0.7 handoff

V0.7 is accepted only through RECOVERY_TO_V07.md and SB-R07-07A. After acceptance, the scheduler/worker infrastructure becomes the execution substrate for all later versions.

## V0.8 — real account connectivity

Goal: verified destination and analytics routes without write authority.

Sequence:
1. SB-S08-001 credentials-free account registry.
2. SB-S08-002 read-only route probes.
3. SB-S08-003 destination/persona hard lock.
4. SB-S08-004 analytics route verification.
5. SB-S08-005 lead connectivity evidence index.

LIVE checkpoint: fresh readback of actual account/profile/workspace mappings. Login/MFA/CAPTCHA is an owner gate; credentials never enter Git.

## V0.9 — controlled public canaries

Goal: exactly one bounded real public canary per general persona.

Sequence:
1. SB-S09-001 authorization compiler.
2. SB-S09-002 exactly-once public-effect wrapper.
3. SB-S09-003/004/005 one canary per persona.
4. SB-S09-006 post-window analytics/learning.

LIVE checkpoint: verified public permalink/readback plus real analytics observation window. API/browser request success alone is insufficient.

## V1.0 — autonomous three-bot operation

Goal: three bots operate real scheduled loops with real measurement and recovery.

Sequence:
1. SB-S10-001 continuous-run harness.
2. SB-S10-002 idempotency/reconciliation.
3. SB-S10-003 owner-gate instrumentation.
4. SB-S10-004 measurement-to-next-decision chains.
5. SB-S10-005 standalone dependency audit.

Acceptance window should be fixed before execution and contain multiple scheduled cycles for each bot; never keep a chat open to create the appearance of continuity.

## V1.1 — reliability hardening

Goal: supported failures degrade safely and recover without duplicate effects.

Slices:
- SB-S11-001 fault matrix;
- SB-S11-002 restart/idempotency;
- SB-S11-003 outage degradation;
- SB-S11-004 unattended live soak.

LIVE checkpoint: bounded unattended scheduler run with injected/real failures and incident receipts.

## V1.2 — multi-platform intelligence

Goal: bots choose where an idea belongs instead of blind cross-posting.

Slices:
- SB-S12-001 capability registry;
- SB-S12-002 platform scorer;
- SB-S12-003 no-platform option;
- SB-S12-004 choice-divergence acceptance.

No platform choice can create route authority that V0.8 did not verify.

## V1.3 — analytics brain

Existing normalized analytics engine is already accepted engineering; finish semantics/adapter acceptance.

Slices:
- SB-S13-001 metric semantic registry;
- SB-S13-002 real adapter conformance;
- SB-S13-003 incompatible-comparison guard.

Key rule: missing != zero; snapshot != delta; normalized values retain raw semantics.

## V1.4 — audience memory

Existing audience-memory engine is accepted engineering; finish update/decay/privacy behavior.

Slices:
- SB-S14-001 hypothesis-store conformance;
- SB-S14-002 confidence updates;
- SB-S14-003 decay/contradictions;
- SB-S14-004 privacy/isolation acceptance.

No sensitive individual profiling.

## V1.5 — autonomous experiment engine

Existing engine is close but still has the structural admin alias issue.

Slices:
- SB-S15-001 API isolation;
- SB-S15-002 measurement compatibility;
- SB-S15-003 lifecycle closeout;
- SB-S15-004 overlap/dedup.

LIVE/real evidence becomes necessary for operational experiment conclusions; fixture observations only prove engineering.

## V1.6 — content intelligence

Goal: platform-native, non-repetitive content whose factual lineage survives transformation.

Slices:
- SB-S16-001 canonical idea lineage;
- SB-S16-002 platform-native transformation;
- SB-S16-003 novelty/repetition;
- SB-S16-004 factual-lineage acceptance.

## V1.7 — community operation strategic checkpoint

Goal: safely observe and reason over community interactions, generate bounded reply candidates and learn from outcomes. Public replies remain separately authority-gated.

Slices:
- SB-S17-001 read-only community collector;
- SB-S17-002 conversation memory;
- SB-S17-003 reply authority classifier;
- SB-S17-004 safe candidate generator;
- SB-S17-005 abuse/manipulation gate;
- SB-S17-006 exact thread/destination binding;
- SB-S17-007 community learning;
- SB-S17-008 lead checkpoint index.

V1.7 can accept read-only/community-decision engineering without forcing unauthorized public replies. If a public-response acceptance case is later desired, it needs a dedicated owner authorization manifest.

## Reuse map

Use existing:
- runtime/collector.py + factcheck.py for evidence;
- runtime/metrics.py + analytics.py for analytics;
- runtime/audience.py for audience memory;
- runtime/experiment_engine.py for experiments;
- runtime/content_intelligence.py for content intelligence;
- runtime/community.py for community logic;
- AccountRoute / PublicEffectReceipt / IdeaLineage schemas already committed on canonical coordination.

Do not build parallel subsystems unless the existing one demonstrably cannot satisfy the contract.
