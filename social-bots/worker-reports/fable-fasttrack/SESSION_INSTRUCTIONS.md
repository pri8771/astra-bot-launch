# Fable Integrator — SESSION_INSTRUCTIONS — LEAD-050

Branch: `fable/social-bots-v23-fasttrack-20260921`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Official phase: **V0.4.x / V0.4 in progress**
Execution ceiling: **LIVE V1.7 only, then hard stop**

## Status at lead review

**STALE / ACTION REQUIRED — LEAD-048 LIVE V1.7 scope has not yet been acknowledged by a fresh worker session.**

The historical branch name does not authorize V2.3/V3.0 continuation. Preserve all existing code and signed evidence, including material checkpoint `a204ad0827748a4e9661f1945b8e025d53d0ae09`, but do not execute later-roadmap work.

## Read before editing

Fetch current canonical coordination and read:
- `social-bots/delivery/V17_LIVE.md`
- `social-bots/delivery/V17_SCOPE.json`
- `social-bots/delivery/V17_ACCEPTANCE.md`
- `social-bots/STATE.json`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/WORK_QUEUE.md`
- `social-bots/MILESTONE_MANIFEST.md`
- `social-bots/ARTIFACT_INDEX.json`
- latest `social-bots/AGENT_MESSAGES.md`

Start a genuinely fresh top-level worker session, emit exactly one durable `SESSION_ONCE` heartbeat for that session, and update `CURRENT_PROGRESS.md` truthfully. A lead commit/comment is not worker acknowledgement.

## Sole implementation scope

Fable remains the sole implementation/integration owner through **LIVE V1.7 only**. Hard stop after V1.7. Do **not** continue into V1.8+, V2.3, V3.0, or H1–H4 roadmap work. Existing later scaffolding may be preserved but must not be advanced or counted as acceptance.

Execute the current zero-live repair/integration order against the actual candidate modules:

1. **Direct/ad-hoc model-callable authorization** — every live-capable provider/callable path must fail closed at the actual dispatch boundary without a valid canonical scoped authorization manifest. Use harmless local sentinels only; zero real model calls.
2. **Capability/fixture bypass hardening** — production must not trust caller-supplied fixture/adaptive/capability labels to bypass authorization.
3. **Shared durable pre-dispatch budget accounting** — reserve atomically before dispatch across concurrency, re-entry, wrappers/processes and restart; exceptions/crashes consume or remain uncertain; enforce expiry/revocation at dispatch.
4. **Heartbeat/session lease durability** — preserve one-session/one-heartbeat semantics and prove crash/concurrency behavior without synthetic operational evidence.
5. **Retained-output integrity + final-content review** — verify canonical path/type and exact bytes/hash actually consumed, including wrong-scope, replacement, symlink and late-write cases; bind review to the final retained content.
6. **Prospective persona-scoped experiment persistence/read boundary** — no ambiguous whole-runtime production readers.
7. **Read-only preflight** for the real persistent host/account/provider chain required by V1.7. Do not perform live product-model calls, public effects, paid actions, account mutations, or release actions without separate explicit owner authorization.

Run focused regressions and the full current suite after each coherent repair wave. Produce signed reports with exact commit SHA, exact test discovery/pass/fail/error/skip counts, and known limitations. Worker-local success never self-accepts an artifact or version.

## Handoff

QA/Acceptance is independent review-only. Cursor/Core/Intelligence are parked from overlapping source edits. When a coherent candidate is pushed, stop and wait for independent acceptance feedback before broadening work.

## Hard authority limits

No additional Claude/adaptive/product-model call, public posting/reply/message, PAYG/new spend, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized. The prior exactly-one live canary authorization is consumed. V0.4 causal-divergence evidence remains owner-authorization blocked; do not synthesize or replay evidence to satisfy it.
