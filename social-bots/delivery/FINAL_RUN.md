# FINAL RUN — LEAD-047 integration and evidence campaign

**Released for implementation now. ChatGPT is lead; Fable is the integrator/worker.** This is the current campaign assignment, not another proposed roadmap. It supersedes LEAD-045/046's Fable pause and LEAD-043's new-files-only restriction. It does not supersede owner authority or any required real-world acceptance gate.

## Goal and finish line

Finish the known recovery/security/integration gaps and get **V2.3 genuinely working first**, then continue the existing V3.0 roadmap without another kickoff. Do not treat the already-submitted specialist library, green fixture bundle or a later version number as working V2.3. No unspecified future integration phase may remain.

Current official version remains V0.4.x. Prior live-call authority is consumed. This release authorizes code repair, tests, integration and necessary preparation—not extra product model calls, public effects, spending, account bypass or main/public release. Owner's necessary existing-account/verified Unsubscriber-alias setup allowance remains separate and accurately scoped in OWNER_GATES.md.

## Start once; preserve what exists

1. Fetch canonical `chatgpt/social-bots-plan-20260920` and worker refs. Read this file **from the fetched canonical ref**, not an older local assignment. Read the new lead review and `reviews/LEAD047_AUDIT.md`.
2. Continue on `fable/social-bots-v23-fasttrack-20260921` or its clean dedicated integration worktree. Preserve uncommitted work and any just-pushed code. Reviewed branch head was 72a55319cf41f9910c5d3b9623129de3ac0eea31; material checkpoint a204ad0827748a4e9661f1945b8e025d53d0ae09. These are minimum audit baselines, not permission to reset a newer head.
3. Check Cursor/QA changes. Fable now owns shared recovery/runtime integration. Cursor and legacy implementation lanes are parked; do not discard new material work or edit the same uncommitted paths concurrently. Update the ownership/report before work. No fake worker acknowledgement.
4. Use prior available project memory for intent only; current Git and explicit owner instructions control truth. Exactly one SESSION_ONCE heartbeat for a genuinely fresh top-level session; no second heartbeat for a resumed session or context compaction. Lower-model subtasks use bounded task receipts, not an invented heartbeat loop.
5. Run the delivery validator/tests and the actual baseline suite. Record exact discovered/pass/fail/error/skip counts. The lead ran planning tests and narrow source-excerpt probes, not your full checkout; do not repeat those as independent runtime acceptance.

## One queue and one baseline

Use C01–C31 in TASKS.json and the existing SB-* feature packets. The previous next-round NR-* work is supporting detail, not a second implementation queue. Read only the current card with `python3 social-bots/delivery/validate_delivery.py --card C04`, then the relevant contract section. Keep a compact WORKER_PROGRESS.json with source ref, task, tests, evidence, blocker and next runnable action.

C01 reconciles schema/status/build predicates. Lead approves the architectural corrections R01–R10 in RECONCILIATION.json: preserve actual historical evidence, separate rehearsal from LIVE, align specialist schema v2, retain operational predecessor requirements, and register production hooks. Propose any new product/authority change instead of silently weakening it. Workers may prepare canonical status deltas from actual prior lead decisions, but cannot create a new ACCEPTED decision.

## First execution order — repair before expansion

A. Reproduce the six sentinel scenarios in `reviews/LEAD047_PROBES.json` against the **actual current modules**. The archived excerpt harness reproduces historical defects; its success is not a safety test. Repair R07-041/direct callable dispatch, false fixture exemptions, shared durable pre-dispatch budgets (concurrency, reentry, exceptions, new wrappers and restart), and retained-output hash verification. Add real-module regressions with external dispatch blocked.

B. Add required cleanup/finalization and hard deadline supervision; scope the sandbox honestly. Repair crash-consistent strategy publication and final-content review binding. Preserve S23 and strategy-store work; do not rewrite the system for novelty.

C. Consolidate the needed Intelligence producers on the same candidate, preserving stronger recovery source. Implement the missing S20/S21 strategy/revision/lifecycle and S22 planner pieces. The S23 fixture track is not the whole V2.3 product.

D. Wire **all H1–H4** into ordinary production entrypoints. Strategy affects reasoning; approved revision persists under the real fence; planned tasks drive the real dispatcher; actual bounded specialists return validated results that affect later parent work. Also separate DEVELOPMENT_ARTIFACT dispatch from BOT_CYCLE. A logged assignment or NO_ACTION bot cycle is not code-worker proof.

E. Run one integrated rehearsal with network/model/public routes unavailable, then independently review the pinned candidate. Add failure injection, reentry/races, wrong scope, tampered files, corrupt/torn receipts, cancellation, non-cooperative timeout, restart and missing-data cases. A separate demo-only wiring script does not satisfy the normal entrypoint requirement.

F. Perform actual host/account/provider preflight; assemble one exact gate dossier. Execute each live scenario only when the applicable grants and predecessors truly exist. Prioritize closing operational V0.4–V2.3; after that continue V2.4–V3.0 and final multi-brand proof.

## Do not get stuck on our former administrative deadlock

After candidate C04 negative tests pass, Fable is explicitly released to consolidate and build against provisional submitted modules in **isolated offline tests** without waiting for a sleeping Cursor/QA session. This does not accept R07-041 or permit its operational use. Safe code prerequisites may be present and independently testable before the corresponding LIVE milestone is accepted. Prepare readiness evidence separately from operational evidence. Do not toggle a LIVE artifact to ACCEPTED to unlock a build.

Review may be delegated to a separate fresh reviewer context/worktree using the existing authorized development environment. Return exact reviewer source and command evidence; don't invent independence. ChatGPT still accepts. If live review/grant is pending, continue other released safe implementation. If only external/data gates remain, checkpoint with exact missing actions; do not pretend an idle chat is running in the background.

## Completion contract

Work in small artifact-prefixed commits and push recoverable checkpoints. Use lower-cost already-available subagents only for bounded independent mechanical tasks; reserve stronger reasoning for integration/security/concurrency. No paid fallback or excessive parallel fanout.

By the next review, return a pinned combined candidate, actual full-suite result, repaired-defect regressions, ordinary-entrypoint integration trace, tested target-host capability/restore where permitted, and the minimal remaining external gate dossier. Continue safe build work through the existing V3.0 contracts, but never let cosmetic V3 scaffolding delay V2.3 integration.

For operational promotion, all original milestone tests still apply. A justified HOLD is safe but does not close a required positive measured strategy-change case. Insufficient audiences, missing history, unavailable platforms and elapsed windows cannot be fabricated. Freeze live test inputs, budgets and thresholds before execution; no retry-until-pass.

Terminal report: exact source/evidence SHAs, defects fixed/open, component/integrated/LIVE scopes, tests including skips, genuine accounts/host/provider evidence, remaining gate IDs, and next executable action. Use READY_FOR_LEAD_REVIEW or an explicit BLOCKED_* state. Never self-accept or claim V2.3/V3.0 from fixture success.
