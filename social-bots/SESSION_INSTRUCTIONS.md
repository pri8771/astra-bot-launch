# SESSION_INSTRUCTIONS — Fable V1.7 Integrator — LEAD-051 FINAL

Branch: `fable/social-bots-v23-fasttrack-20260921`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Official phase: **V0.4.x / V0.4 in progress**
Execution ceiling: **LIVE V1.7 only, then hard stop**
Role: **sole implementation/integration owner for enabled <=V1.7 runtime source**

## Lead disposition after late repair submission

Lead inspected the requested R07-041 repair at `0bca4e654923932c755c89c20a85ec79b37d0a10` after it landed during the LEAD-051 review window. The specific no-scope EngineeringStub/injected-runner capability defect found in `12c807e...` is materially repaired in source and covered by the requested harmless-sentinel regressions.

**SB-R07-041 is now SUBMITTED / READY FOR INDEPENDENT ACCEPTANCE REVIEW, not ACCEPTED.** Mac Acceptance must independently execute the pinned candidate before lead acceptance.

Preserve the following as submitted evidence pending independent review:
- `0bca4e...` — R07-041 no-scope/engineering-scope repair; worker reports 707 passed / 2 skipped, zero live calls.
- `b5fd038...` — due-work rotation/anti-starvation.
- `c4d31fee...` — C05/C06/C07 final-content binding and prospective experiment semantics.
- `3da19a9c...` — selected V1.7 producer consolidation.
- `d626eb...` — ordinary-cycle V1.2–V1.6 producer wiring.
- `af3fded...` — factual V1.7 preflight/gate dossier.
- `f0f1307...` — offline/read-only community path with reviewed reply candidates and no send path.

## Next implementation work

Continue only bounded, non-overlapping, **zero-live** V1.7 integration that does not interfere with Acceptance's pinned review. Keep operational truth explicit: fixture/offline paths are engineering proof only; they never satisfy real account/source/model/scheduler/public/measurement acceptance evidence.

Do not alter the pinned R07-041 behavior while Acceptance is reviewing it unless a new defect is found. If a defect is found, submit a new SHA and call it out explicitly rather than silently moving the review target.

Do not expand V1.8+, V2.3, V3.0 or H1–H4 future scope. Stop feature development at accepted V1.7.

Session `s-20260921T211438Z-d5589881` already emitted its one `SESSION_ONCE`; resumed/compacted work in that same session must not emit a second heartbeat.

No additional Claude/adaptive/product-model call, public posting/reply/message, PAYG/new spend, account mutation, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized. The V0.4 divergence batch remains blocked on fresh explicit owner authorization plus a lead-created scoped manifest.
