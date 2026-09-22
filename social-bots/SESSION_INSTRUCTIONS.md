# Mac QA / Acceptance — SESSION_INSTRUCTIONS — LEAD-051 FINAL

Branch: `claude/social-bots-mac-qa-control`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Official phase: **V0.4.x / V0.4 in progress**
Role: **independent review / acceptance only**
Execution ceiling: **LIVE V1.7 only, then hard stop**

## Status at lead review

**STALE / ACTION REQUIRED.** Fable is materially active and the requested R07-041 repair has now landed, but this Acceptance branch still has no fresh independent post-LEAD-050 review result.

Start a fresh top-level local-Mac review session if the previous reviewer session is no longer active; a genuinely fresh session emits exactly one durable `SESSION_ONCE`. If resuming the same prior session, do not fabricate a second heartbeat. Update `CURRENT_PROGRESS.md` truthfully. Do not edit runtime/product source.

## Read first

Fetch current canonical coordination and Fable head, then read `delivery/V17_LIVE.md`, `delivery/V17_SCOPE.json`, `delivery/V17_ACCEPTANCE.md`, `STATE.json`, `SESSION_ROUTER.md`, `WORK_QUEUE.md`, latest `AGENT_MESSAGES.md`, Fable `SESSION_INSTRUCTIONS.md`, and current Fable reports/evidence.

## Ordered independent review work

1. **R07-041 repaired candidate FIRST — pin `0bca4e654923932c755c89c20a85ec79b37d0a10`.** Lead source review found the prior `12c807e...` no-scope seam defect and then inspected the worker repair. Independently execute the exact pinned repaired candidate with harmless sentinels and prove:
   - `EngineeringStub(live_like_sentinel)` does not invoke with no scope;
   - injected CLI runner and wrapper-around-real-launcher do not invoke with no scope;
   - explicit policy-owned ENGINEERING scope is required for engineering seams and their records remain non-live;
   - production scope refuses engineering seams;
   - live/raw callable is refused with no scope and also refused under ENGINEERING scope;
   - production live route remains canonical-manifest + durable-budget gated;
   - concurrency/reentry/shared-budget negative controls remain green;
   - no real model/provider/subprocess/public call occurs.
   Record exact host, SHA, commands, focused/full results and limitations. Return PASS / FAIL / CHANGES_REQUIRED; do not edit source.
2. Independently execute the real `SB-R07-071` multiprocess/session race against the current compatible candidate; report process/round counts and exact result.
3. Independently exercise `b5fd038` due-work rotation/anti-starvation with multiple bots/due items and restart-safe deterministic selection where claimed.
4. Independently audit `c4d31fee...` C05/C06/C07 negative controls: final rendered text edited after review, wrong scope/persona/platform, replacement/symlink/late write, cultural final-text hash binding, and prospective experiment state with no fabricated baseline/outcome/confidence.
5. Review `d626eb...` producer wiring and `f0f1307...` community path as **engineering-only** submissions: confirm persona/account/thread/replay/duplicate/stale/injection controls, reviewed/bound reply candidate, zero effects, no send/network path, and truthful BLOCKED_DATA semantics without treating fixture rows as live completion.
6. Audit the enabled V1.7 producer/dispatcher boundary; parked V1.8+/V2.3/V3.0 routes must remain unreachable.
7. Review `af3fded...` preflight/gate dossier only as factual blocker evidence; ephemeral Linux host, CONNECT-403 routes, absent account registry, absent native scheduler/manifest/reviewer do not become operational acceptance.

Worker-local green tests are evidence inputs, not acceptance.

## Hard authority limits

No runtime source edits. No additional Claude/adaptive/product-model call, public posting/reply/message, PAYG/new spend, account mutation, destructive action, credential exposure, fabricated evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized. The V0.4 causal-divergence gate remains blocked pending fresh explicit owner authorization and a lead-created scoped manifest; the historical canary worktree remains frozen.
