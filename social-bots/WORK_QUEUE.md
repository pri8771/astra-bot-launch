> **Latest owner assignment — 2026-09-22:** Antigravity is the next Social Bots implementation owner; target accepted LIVE V1.7. Read `social-bots/OWNER_RACE_V17_20260922.md` and `social-bots/prompts/ANTIGRAVITY_BOTS_V17_RACE_20260922.md` first. State: ASSIGNED_WAITING_FOR_WORKER, not launched. This supersedes older worker/pause routing below only; existing evidence, review holds and action grants are unchanged. No new scheduler or watcher.

# Work queue — LEAD-051 — stop at LIVE V1.7

Current official version remains **V0.4.x**. Owner execution ceiling is **LIVE V1.7 only**, not V1.8+, V2.3 or V3.0. Active contract: `delivery/V17_LIVE.md`; scope filter: `delivery/V17_SCOPE.json`; exit criteria: `delivery/V17_ACCEPTANCE.md`.

## Current lane truth

- **Fable Integrator — ACTIVE.** Worker session `s-20260921T211438Z-d5589881` ingested the V1.7-only scope and produced signed material work through `af3fded92eaba5e68c8088737b68c6f043e40a5e`.
- **Mac Acceptance — STALE / ACTION REQUIRED.** No fresh independent post-LEAD-050 reviewer result is visible.
- **Cursor/Core/Intelligence — PARKED / evidence-only.** No overlapping source work.
- **V0.4 canary — FROZEN / evidence preservation.** No further model call authorized.
- **worker-pc — outside critical path** until private-repo clone/auth is demonstrably repaired.

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
