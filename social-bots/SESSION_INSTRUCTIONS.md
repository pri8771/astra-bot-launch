# SESSION_INSTRUCTIONS — Fable V1.7 Integrator — LEAD-051

Branch: `fable/social-bots-v23-fasttrack-20260921`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Official phase: **V0.4.x / V0.4 in progress**
Execution ceiling: **LIVE V1.7 only, then hard stop**
Role: **sole implementation/integration owner for enabled <=V1.7 runtime source**

## Lead review finding — SB-R07-041 is CHANGES_REQUIRED

Your post-LEAD-050 worker activity is real and the V1.7 scope acknowledgement is verified. Signed work through `af3fded92eaba5e68c8088737b68c6f043e40a5e` is preserved as submitted engineering evidence. Nothing in this instruction self-accepts an artifact or version.

The shared pre-dispatch gate at `12c807e970b4d7a8f92a7d5db7b7b3a3856c46d6` materially improves the raw live-callable/CLI path, but lead source review found one remaining capability bypass that must be fixed before R07-041 can be accepted:

1. `runtime.model_dispatch.classify()` exempts exact `reasoning.EngineeringStub` instances.
2. `runtime.model_dispatch.dispatch()` currently allows `ENGINEERING_STUB` and the CLI `NOT_LIVE` injected-runner seam to execute when **no dispatch scope is configured**.
3. `reasoning.EngineeringStub(fn)` accepts an arbitrary callable, and `ClaudeCodeReasoningProvider(runner=...)` accepts an arbitrary injected runner. A direct-library caller can therefore wrap a network/model-capable callable in an engineering seam and execute it without a canonical manifest simply by staying outside a production scope.
4. The current regression suite explicitly proves that an `EngineeringStub` runs outside production with no scope. Under the V1.7 negative-control contract, a caller-controlled fixture/capability seam must not be a no-grant execution capability.

### Required zero-live repair

- Make **no-scope fail closed for every arbitrary callable execution**, including exact `EngineeringStub` and injected-runner seams.
- Engineering stubs/test runners may run only under an explicit, policy-owned engineering dispatch scope with `allow_engineering_stubs=True` (or an equivalently strong non-production capability that cannot be obtained merely by omitting scope).
- Production scopes continue to refuse engineering seams.
- A raw/live callable continues to require the canonical scoped authorization manifest and durable pre-dispatch budget slot.
- Do not add an environment-variable or caller-label bypass.

Add adversarial harmless-sentinel regressions proving at minimum:
- `EngineeringStub(live_like_sentinel)` does **not** invoke with no scope;
- an injected CLI runner/wrapper does **not** invoke with no scope;
- both may execute only inside an explicitly enabled engineering scope and are recorded as engineering/non-live evidence;
- production scope refuses both;
- raw/live callable with no scope remains refused;
- existing concurrency/reentry/shared-budget tests remain green.

Run focused tests and the full suite. Make **zero** real model/provider calls. Push exact source SHA, commands/results, evidence paths, and limitations; request SUBMITTED/READY_FOR_LEAD_REVIEW only.

## Other V1.7 submissions

- `b5fd038` due-work rotation/anti-starvation: preserve as submitted engineering evidence pending independent review.
- `c4d31fee...` C05/C06/C07 final-content review binding + prospective experiment semantics: preserve as submitted engineering evidence pending independent review.
- `3da19a9c...` V1.7 producer consolidation and `af3fded...` C09 preflight/gate dossier: preserve; host/account/native-scheduler blockers remain factual.
- Continue only non-overlapping, zero-live V1.7 integration after the R07-041 seam repair. Do not expand V1.8+/V2.3/V3.0/H1–H4.

## Heartbeat and authority

Session `s-20260921T211438Z-d5589881` already emitted its one `SESSION_ONCE`; a resumed/compacted continuation of that same session must not emit a second heartbeat. A genuinely new later session emits exactly one.

No additional Claude/adaptive/product-model call, public posting/reply/message, PAYG/new spend, account mutation, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized. The V0.4 divergence batch remains blocked on fresh explicit owner authorization plus a lead-created scoped manifest.
