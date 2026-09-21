# Cross-cutting delivery contracts

Use the corresponding detailed section of `../next-round/INTEGRATION_CONTRACTS.md` when implementing. The requirements below adopt the supplied patch and add the observed LEAD-047 source defects. FINAL_RUN.md controls current ownership and release; no contract grants public/model/spend authority.

## K1. Three execution kinds

DEVELOPMENT_ARTIFACT implements a repository artifact and submits code/tests. BOT_CYCLE operates a social persona. SPECIALIST performs a bounded parent task. Use a typed assignment binding artifact/task ID, kind, coordination/source SHA, scope, allowed paths/tools, inputs/expected outputs, grant/budget refs and deadline. The deterministic dispatcher chooses a reviewed entrypoint. Never execute arbitrary shell from GitHub comments or retrieved text. The actual job must change when its assignment changes, not only the heartbeat caption.

## K2. Actual execution authority

Effective authority is the intersection of owner grant, lead assignment, host policy, account/provider capability, budget and runtime state. Verify at the deepest library/call/spawn boundary. An arbitrary callable or self-reported adaptive=False/fixture=True is not a trusted offline fixture. Production fixture exemptions must not be available to caller-created objects. Disabling network in an engineering harness is useful negative control, not a product model grant.

Atomically reserve a durable shared parent+child slot before dispatch. Exceptions and crash-uncertainty retain the charge; new wrapper instances and reentry cannot reset usage. Recheck expiry/revocation/scope at execution, not only construction. The supplied implementation currently records its in-memory call after dispatch; fix the implementation, not just its comment. No hidden key/PAYG/alternate-account fallback. Verify actual installed model IDs/effort/subagent support; do not invent compatibility.

## K3. Claim-specific evidence

Keep ENGINEERING/LIVE plus scopes OFFLINE_FIXTURE, LIVE_SOURCE, REAL_PROCESS, NATIVE_SCHEDULER, LIVE_MODEL, LIVE_ACCOUNT, LIVE_PUBLIC_EFFECT, LIVE_ANALYTICS. One real HTTP request cannot make all stages LIVE. Bind inputs, final outputs, code/config/schema hashes, environment, invocation origin, actual timestamps, grants/usage and reviewer. Hashes bind bytes; they do not prove honest provenance by themselves. Preserve first failures and uncertainty. A validator's PASS never self-promotes an artifact.

## K4. Crash-consistent persistence

Reuse the current store behind an explicit publication transaction. Production mutations require the right live fence/scope/expected version; fence=None is allowed only in isolated engineering storage. Create immutable version bytes without overwrite; publish an authoritative commit record/CAS, then recoverable indexes. Do not hold a state lock during remote reasoning. Reconcile orphaned prepared versions, torn logs and pointer/history interruptions. Never treat file replacement alone as a multi-file transaction. Test simultaneous writers, stale takeover, interrupted commit and rollback-as-new-version. A SIGKILL experiment is not proof against hardware power loss. Avoid nested non-reentrant fences.

## K5. Final content review

Bind exact rendered content hash, material-claim set, source byte hashes/spans, reviewer event/identity/version and policy. A changed fact, quantity, qualifier, date, actor or negation invalidates the review. Caller labels such as framing/creative cannot exempt known factual prose. PARTIAL material support is not an unconditional pass: withhold or explicitly qualify then re-review. A configured cultural-reviewer name is not an actual review event; automated checks must not claim human endorsement. Retrieved source instructions cannot change account destination, tools, authority or success criteria.

## K6. Honest experiments

Unpublished dry runs may create DRAFT/WAITING_BASELINE experiments and persist research/review lessons; baseline_ref, outcome and publication_ref remain null until actual data exists. Never borrow another persona's baseline or coerce missing into zero. Real windows start from verified publication. Keep snapshot/delta/rate semantics, source, denominator, exposure and compatible time windows. Inconclusive evidence yields HOLD/INCONCLUSIVE; it does not satisfy a still-required positive measured-change demonstration.

## K7. Production integration H1–H4

H1 resolves the current scoped strategy into the real reasoning context with explicit fallback when absent/expired. H2 validates proposal/evidence/current-version then publishes the immutable revision through the production fence. H3 selects and executes an actual due dependency-ready planner task with stable fairness among all three bots. H4 dispatches an actual bounded specialist and uses its validated adopted result in the parent's subsequent plan/decision. Every hook is required for integrated V2.3; a helper-only demonstration is insufficient. Rejection cannot mutate protected parent state; successful adoption may mutate only its approved write set.

## K8. Specialist boundary and integrity

WorkerContract/WorkerResult are canonical schema v2; other records retain their own versions. Trusted adapter orchestration is not arbitrary-code sandboxing. Use a killable supervision boundary for operational blocking model/tool work, process-tree cleanup and late-result revocation. Thread future cancellation does not stop a running task. Untrusted code/shell remains unavailable unless an OS filesystem/network boundary has actually been installed and negatively tested.

Resolve context by approved scope rather than model-supplied paths. Deny symlink/traversal/race escapes and unexpected output types/sizes. Copy validated outputs to parent-owned immutable storage before retiring scratch. Verify hashes again when consuming retained bytes; the current _kept_doc path omits this check. Reconcile ledger counts independently of adapter-returned counts. Cleanup/lease release needs a finalization path even when validation, receipt writing or filesystem I/O fails.

## K9. Account and public effects

Verify exact current identity/persona/destination, supported route, scopes, limits, credential alias and readback. Unsupported/stale is not connected. Use durable stable effect ID and intent/reservation before an allowed attempt. Missing readback becomes UNCERTAIN; reconcile before any resend. Do not claim exactly-once public delivery if the provider lacks sufficient support. Posting/reply/DM/correction/deletion/setup/spend are distinct capabilities. Preserve the user's necessary account/Unsubscriber-alias setup allowance only after actual mechanism and ownership verification; it does not authorize posting or model calls.

## K10. Later scopes and reuse

Use explicit brand/bot/persona mapping when introducing brands; do not silently merge legacy identity stores. Version and test migration/rollback with retained hashes. Persona-private, brand-private, shared-public and portfolio state remain separate. Sharing is allowlisted, attributable and revocable, including caches/indexes. No credentials or unnecessary raw community personal data in Git. Reuse the V1.6 idea store at V2.7 and existing budgets/planners/specialists at V3.0 rather than build competing infrastructure.
