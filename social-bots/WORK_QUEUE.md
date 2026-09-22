> **Latest owner assignment — 2026-09-22:** Antigravity is active Social Bots implementation owner; target accepted LIVE V1.7. PR22 candidate (`3bad054`) and frozen Mac matrix (`1549df4`) independently verified and accepted for engineering composition. Dormant activation proposal prepared outside authorizations. Zero live calls executed, zero public actions, zero scheduler mutations. State: BLOCKED_OWNER_AUTHORIZATION for 5-call local divergence batch and named cultural reviewer.

# Work queue — Antigravity LIVE V1.7 RACE

Current official version remains **V0.4.x**. Owner execution ceiling is **LIVE V1.7 only**, not V1.8+, V2.3 or V3.0. Active contract: `delivery/V17_LIVE.md`; scope filter: `delivery/V17_SCOPE.json`; exit criteria: `delivery/V17_ACCEPTANCE.md`.

## Current lane truth

- **Antigravity Implementation Finisher — ACTIVE.** Working on Mac host (`Apple-M5-Pro-87`), candidate `3bad0541fde8afb584bc6e396ea093b5d1f3c407` (tree `781fc16b1b0a982c7014ea04942437d6ada803e6`). 789 unittests pass, 2 skips.
- **Mac Matrix Verification — COMPLETED & ACCEPTED FOR ENGINEERING.** PR22 and `CODEX_MAC_FINAL_MATRIX_20260922` independently reviewed and accepted (`ANTIGRAVITY_PR22_MATRIX_DISPOSITION_20260922.md`).
- **Dormant Activation Proposal — PREPARED.** `DORMANT_ACTIVATION_PROPOSAL.md` prepared outside authorizations.
- **Host & Platform Packet — PREPARED.** `ANTIGRAVITY_HOST_AND_PLATFORM_PACKET_20260922.md` documents persistent host gaps (SB-R07-073/074) and platform route status (X cost conflict vs zero-spend).
- **V0.4 Canary / Divergence — BLOCKED_OWNER_AUTHORIZATION.** 5 local Ollama calls awaiting explicit owner grant; cultural reviewer awaiting owner nomination. No execution without explicit grant.
- **Other Lanes — PARKED.** No overlapping writers.

## Immediate order

1. **Fable: repair SB-R07-041 engineering-seam capability bypass, zero live calls.** Current `12c807e` makes raw/live callable and real Claude CLI routes manifest/budget gated, but exact `EngineeringStub` and injected-runner seams can still execute arbitrary caller-supplied callables/runners when no dispatch scope exists. No-scope must fail closed. Engineering seams may execute only inside an explicit policy-owned engineering scope (`allow_engineering_stubs=True` or equivalently strong capability); production scopes refuse them.
2. Fable adds harmless-sentinel negative tests for EngineeringStub/injected-runner no-scope refusal, explicit-engineering-scope allow, production-scope refusal, raw/live manifest gating, concurrency/reentry/shared-budget preservation; run focused and full suite.
3. **Acceptance independently audits repaired R07-041** with zero real inference, then executes `SB-R07-071` multiprocess/session race against the pinned candidate.
4. Acceptance independently exercises submitted `b5fd038` due-work rotation/anti-starvation and `c4d31fee...` C05/C06/C07 negative controls: final-text edit, wrong scope/persona/platform, replacement/symlink/late write, cultural final-text hash binding, prospective experiment with no fabricated baseline/outcome/confidence.
5. Fable continues only non-overlapping zero-live V1.7 integration after the seam repair. `3da19a9c...` producer consolidation and `af3fded...` preflight/gate dossier are submitted engineering evidence, not acceptance.
6. Preserve the real-evidence critical chain: V0.4 controlled divergence only under fresh owner authorization + lead manifest; V0.5 real current-source review; V0.6 three real unpublished adaptive loops; V0.7 native scheduler on a verified persistent host; V0.8 account/route verification; bounded public canaries only with explicit authorization; then V1.1–V1.7 exact acceptance artifacts.
7. Submit final LIVE V1.7 packet and **stop feature development**. Do not advance to V1.8 or later without a new owner request.

## Submitted evidence awaiting independent review

- `12c807e...` R07-041/C04 — **CHANGES_REQUIRED** for engineering-seam no-scope bypass despite substantial raw/live gate improvement.
- `b5fd038...` scheduler due-work anti-starvation — submitted engineering evidence.
- `c4d31fee...` C05/C06/C07 final-content review binding + prospective experiments — submitted engineering evidence.
- `3da19a9c...` selected V1.7 producer consolidation — submitted engineering evidence.
- `af3fded...` read-only host/provider/account gate dossier — useful blocker evidence only.

## Operational blockers remain factual

Fable's current execution environment is an **ephemeral Linux VM**, not a verified persistent owner-controlled host with native scheduling. Its preflight records social-platform CONNECT-403 restrictions, no canonical live authorization manifest, no account registry entries and no named cultural reviewer. Those conditions block applicable operational evidence; they do not waive it.

## Authority and heartbeat

No new live product-model call, public effect, account mutation, spending, destructive action, secret exposure, main/public release or SwarmAI dependency is authorized. The prior V0.4 exactly-one canary authorization is consumed.

Canonical heartbeat policy is **ONE SESSION = ONE HEARTBEAT**. The old FAST_5M/SOAK experiment is superseded. A resumed/compacted continuation of the same session must not emit another heartbeat; V0.7 recurring liveness is proven by separate OS-scheduled bounded invocations on a real persistent host.
