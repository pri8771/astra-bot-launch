# Mac QA / Acceptance — SESSION_INSTRUCTIONS — LEAD-050

Branch: `claude/social-bots-mac-qa-control`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Official phase: **V0.4.x / V0.4 in progress**
Role: **independent review / acceptance only**
Execution ceiling: **LIVE V1.7 only, then hard stop**

## Status at lead review

**STALE / ACTION REQUIRED.** No fresh reviewer session, reviewer heartbeat, or independent result has landed after the LEAD-048 V1.7-only scope release.

Start a genuinely fresh top-level review session on the actual local Mac and emit exactly one durable `SESSION_ONCE` heartbeat. Update the lane progress report truthfully. Do not edit runtime/product source.

## Read first

Fetch current canonical coordination and read:
- `social-bots/delivery/V17_LIVE.md`
- `social-bots/delivery/V17_SCOPE.json`
- `social-bots/delivery/V17_ACCEPTANCE.md`
- `social-bots/STATE.json`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/WORK_QUEUE.md`
- `social-bots/ARTIFACT_INDEX.json`
- latest `social-bots/AGENT_MESSAGES.md`

The historical Fable branch name does not authorize V1.8+/V2.3/V3.0 work. Acceptance scope ends at LIVE V1.7.

## Ordered independent review work

1. Confirm an actual **post-LEAD-050 Fable worker commit** exists before treating the implementation lane as active. Lead-authored instruction/ack commits are not worker progress.
2. Independently execute the `SB-R07-071` real multiprocess/session race against the pinned candidate when applicable; report exact host/process/round counts and results.
3. After Fable repairs the direct/ad-hoc model-callable path, audit it with a harmless local sentinel. Prove the callable cannot execute without a valid canonical scoped authorization manifest. Zero real inference.
4. Independently stress shared budget accounting across concurrency/re-entry/wrappers and failure paths; verify reservation occurs before dispatch and crash/exception accounting fails closed.
5. Independently test heartbeat/session lease durability and crash/concurrency semantics. One review session emits one `SESSION_ONCE`; do not synthesize or backfill heartbeat evidence.
6. Audit retained-output integrity and final-content review binding against replacement/symlink/late-write/wrong-scope cases.
7. Audit prospective persona-scoped experiment persistence/read boundaries and reject ambiguous whole-runtime production readers.
8. Review read-only persistent-host/account/provider preflight evidence for V1.7. Do not perform live product-model calls, public effects, paid actions, account mutations, or deployment/release actions.

For every candidate, inspect actual source/tests/receipts and record exact source SHA, test counts, environment limitations, and PASS/FAIL/CHANGES_REQUIRED reasoning. Do not accept artifacts from worker self-report alone.

## Hard authority limits

No runtime source edits in this lane. No additional Claude/adaptive/product-model call, public posting/reply/message, PAYG/new spend, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized. The V0.4 causal-divergence gate remains blocked pending fresh explicit owner authorization; the V0.4 live-canary worktree stays frozen for evidence preservation.
