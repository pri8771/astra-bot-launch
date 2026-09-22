# Mac QA / Acceptance — SESSION_INSTRUCTIONS — LEAD-051

Branch: `claude/social-bots-mac-qa-control`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Official phase: **V0.4.x / V0.4 in progress**
Role: **independent review / acceptance only**
Execution ceiling: **LIVE V1.7 only, then hard stop**

## Status at lead review

**STALE / ACTION REQUIRED.** Fable is now materially active and has submitted current V1.7 candidate work, but this Acceptance branch still has no fresh independent post-LEAD-050 review result.

Start a fresh top-level local-Mac review session if the previous reviewer session is no longer active; a genuinely fresh session emits exactly one durable `SESSION_ONCE`. If resuming the same prior session, do not fabricate a second heartbeat. Update `CURRENT_PROGRESS.md` truthfully. Do not edit runtime/product source.

## Read first

Fetch current canonical coordination and Fable head, then read:
- `social-bots/delivery/V17_LIVE.md`
- `social-bots/delivery/V17_SCOPE.json`
- `social-bots/delivery/V17_ACCEPTANCE.md`
- `social-bots/STATE.json`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/WORK_QUEUE.md`
- latest `social-bots/AGENT_MESSAGES.md`
- Fable `social-bots/SESSION_INSTRUCTIONS.md`
- Fable current reports/evidence.

## Ordered independent review work

1. **R07-041 repaired candidate first.** Do not accept Fable `12c807e` as final R07-041. Lead review found that exact `EngineeringStub` and injected-runner seams can execute arbitrary caller-supplied callables/runners when no dispatch scope exists. Wait for the repair that makes no-scope fail closed, then independently prove with harmless sentinels:
   - EngineeringStub arbitrary sentinel does not invoke with no scope;
   - injected CLI runner/wrapper does not invoke with no scope;
   - explicit policy-owned engineering scope is required for engineering seams;
   - production scope refuses those seams;
   - raw/live callable remains manifest-gated;
   - no real model/provider call occurs.
2. Independently execute the real `SB-R07-071` multiprocess/session race against the current candidate where applicable; report host/process/round counts and exact result.
3. Independently exercise `b5fd038` due-work rotation/anti-starvation behavior, including multiple bots/due items and restart-safe deterministic selection where the implementation claims it.
4. Independently audit `c4d31fee...` C05/C06/C07 negative controls: final rendered text edited after review, wrong scope/persona/platform, replacement/symlink/late write, cultural final-text hash binding, and prospective experiment state with no fabricated baseline/outcome/confidence.
5. Audit the consolidated V1.7 producer modules and enabled dispatcher import/selection boundary. Unused V1.8+/V2.3/V3.0 routes must remain unreachable from the V1.7 dispatcher.
6. Review `af3fded...` preflight/gate dossier only as factual blocker evidence. Do not turn an ephemeral Linux host, CONNECT-403 routes, absent account registry, or absent native scheduler into operational acceptance.

For every candidate, inspect actual source/tests/receipts and record exact SHA, commands/results, environment limitations, and PASS/FAIL/CHANGES_REQUIRED reasoning. Worker-local green tests are evidence inputs, not acceptance.

## Hard authority limits

No runtime source edits. No additional Claude/adaptive/product-model call, public posting/reply/message, PAYG/new spend, account mutation, destructive action, credential exposure, fabricated evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized. The V0.4 causal-divergence gate remains blocked pending fresh explicit owner authorization and a lead-created scoped manifest; the historical canary worktree remains frozen.
