# Integration contracts — close the gap between modules and a running product

The names below describe required contracts. Check actual APIs at the pinned candidate; adapt through small reviewed adapters, not speculative renaming of active Fable code. Existing runtime.py/bin paths are identified by the previous specs; proposed new files are implementation targets, not claims of existing code.

## Shared references and schema ownership

ArtifactRef = {artifact_id, source_commit, evidence_commit?, path, sha256, schema_name, schema_version, bot, persona, environment_id, run_id}. A source commit cannot refer to itself before it exists: commit code, then attach evidence referencing it. Runtime manifests may omit evidence_commit until packaged.

Use schema_version=2 for WorkerContract/WorkerResult as required by the current canonical specialist schema. Strategy/goal types use their own declared versions; do not globally rewrite every schema version. Reject unknown widening fields and malformed/non-finite values. Add serializer compatibility tests and a deliberate migration policy for existing data. Brand scope is introduced through an explicit later mapping/migration, not by making unrelated bots share a default brand silently.

## Production authority and provider binding — NR-03/04

A production ProviderHandle is constructed only by a policy-owned factory. It binds provider implementation ID/version, permitted operation, namespace, artifact/run scope, grant ID, expiry/revocation state, per-call reservation and result destination. Every library, CLI, specialist and scheduler entrypoint reaches the same lowest dispatch gate.

A caller-provided adaptive=False, fixture=True, provenance='live', schema-valid response or arbitrary manifest directory is not authorization. Tests can use an explicit isolated factory with no operational stores/network tools. Production refuses test handles. Match the actual provider object being called, not merely SBOTS_REASONING. Recheck revocation/current authority before irreversible effects; stale local Git state cannot widen authority.

Budget ledger: atomically reserve before any external dispatch; use unique attempt IDs, shared parent+child ceilings and write-once outcomes. A dispatched call that fails or has uncertain outcome remains charged to its reservation. Reconcile after crash; never reclaim a slot simply because a receipt or slot file disappeared. One failure does not authorize automatic retry. Count development-agent, product-reasoning and reviewer calls separately under the relevant grants. Test grants in temporary roots cannot open production routes.

## Factual, voice and cultural review — NR-05/06

The generator supplies a candidate, not its own proof of truth. Every material factual claim must be independently identified and linked to captured evidence bytes/spans. The operational assessor is policy-owned; arbitrary caller-created SupportAssessment/operational flags are not accepted as authority.

Bind review = {candidate_content_sha256, claim_set_sha256, evidence_hashes, assessor_id/version, policy_version, verdict, reviewed_at}. Formatting, repair, translation or repurposing that changes material content invalidates the prior review. A required claim cannot pass merely because the text was relabeled 'framing' or 'opinion'. PARTIAL requires an explicit narrowly supported uncertainty presentation and re-review, otherwise WITHHELD. Cultural review names a real reviewer/workflow identity; a reviewer name pasted onto the candidate is not a review receipt.

A V0.6 dry run may register a prospective experiment with no measured baseline and persist evidence/review/decision learning. It cannot start a public treatment window or report audience success. Store AWAITING_PUBLICATION/AWAITING_BASELINE as appropriate. Performance conclusions need actual compatible observations.

## Durable state and version publication — NR-13

Provide a small production persistence adapter around the existing storage/fence, not an unrelated database rewrite. Contract: publish_version(namespace, expected_version, new_state, validated_fence) returns one committed version or a conflict. It never accepts a missing/expired/wrong-namespace fence for a production store.

Version data is immutable and created without overwriting an existing path. Publish one authoritative commit record under the correct lock/fence that binds prior version, next version, input/output hashes and related transaction refs. HEAD/HISTORY are derived indexes or updated/recovered against that record. Rebuild only committed indexes on restart; prepared but uncommitted payloads are not active state. Preserve prior bytes. A rollback creates a new version referencing restores_version; it does not rewrite history.

Reuse the established runtime lock scope. Avoid taking the same non-reentrant lock inside an already-fenced commit: define one transaction owner and pass its context to child writes. Fault-inject after payload creation, commit-record publication and index update. Concurrent writers at the same expected_version yield one winner; rejected/stale writers publish nothing.

## H1 — active strategy -> reasoning context — NR-14

Production caller: runtime/decision.py::run_cycle. Input: authoritative scoped strategy plus current evidence and persona. Output: ReasoningContext including strategy ref, objective and allowed priorities. Safety constraints and authority remain outside model control. Expired/missing strategy produces an explicit persona-objective fallback. Namespace mismatch fails closed.

Proof: change an accepted strategy priority and show the normal runner consumes its new ref and makes the corresponding bounded selection on fixed fixture evidence; the live counterpart must bind real provider/evidence records. Merely loading strategy.py in a test is not integration.

## H2 — validated proposal -> fenced persistent strategy — NR-15

Production caller: the cycle commit boundary. Validate proposal against the exact current strategy, real evidence refs, availability and policy. Commit the immutable revision and adoption receipt with the same ownership transaction. Replaying proposal_id does not create another revision. Stale current_version, lost fence or unresolvable evidence returns reject/hold without side effects. Unknown/insufficient evidence yields NO_CHANGE or REQUEST_MORE_EVIDENCE, not a forced strategy change.

## H3 — persistent plan -> bounded production work — NR-16

Production caller: runtime/worker.py::run_one_unit or an explicit adjacent dispatcher. Select one dependency-ready due task from the active scoped PlanDAG. Bind claim to plan version, task ID and lease generation. Persist READY -> RUNNING -> DONE/BLOCKED/FAILED with evidence. Keep DONE task IDs/input hashes across replans; changed completed inputs require an explicit invalidation/new task, not silent reuse.

Do not always select social-a because it is first in a list. Select by due time, last attempted/served time and stable ID with a documented no-starvation rule. Absent authority is BLOCKED, not successful execution. A leased task may renew its fence; that renewal is not a SESSION_ONCE heartbeat.

## H4 — planned specialist -> validated adoption — NR-17

Production dispatcher handles a bounded DELEGATE_SPECIALIST task. Build the canonical v2 contract, resolve only approved context, enforce parent+child budgets, run trusted adapters, validate returned schema/path/hash/scope and adopt through the parent fence. Child never writes parent state directly. A malformed result is retained as rejected evidence, not silently repaired into success. A late result after expiry/lease loss cannot be adopted.

The parent-private-state invariant applies before adoption and on rejection. Successful adoption may change only the explicitly authorized target records; tests compare unaffected records separately. Requiring every parent byte to remain unchanged after successful adoption would contradict useful integration.

## Specialist execution boundary — NR-18/19

Default supported mode: trusted static adapters, structured data, brokered read_context/capture_source/write_output/return_result; no generated-code execution or arbitrary shell. Every context reference is resolved under bot/persona/brand scope, not a path supplied by model text. Deny traversal, absolute paths, symlink escapes and forged cross-scope refs. Secret scanning is supplementary; the broker should never hand credential objects to the model.

A path helper is logical containment for code that uses it, not isolation from arbitrary same-process Python. For any future arbitrary-tool/code plugin, require a real OS filesystem/network boundary with negative read/write/egress tests before enabling it.

Blocking model/tool execution uses a supervised process or equivalent killable provider boundary supported on the target host. Set deadline, cancellation signal, termination grace, process-tree kill and wait/reap. Revoke result adoption before cleanup. Test a deliberately non-cooperative adapter and a child process; verify no late file/state adoption and truthful TIMED_OUT. A Future.result timeout is not proof the underlying task stopped. Do not rely on Python 3.14-only APIs when the supported runtime is older.

## Developer worker versus bot worker — NR-07/08/09

Keep two explicit invocation kinds: BOT_CYCLE and ENGINEERING_ARTIFACT. A bot's NO_ACTION can be a valid outcome but cannot prove code development. Engineering work binds an assignment ID, allowed paths/commands, base SHA, test plan, model budget, push destination and stop criteria; it must return a worktree diff/test/evidence submission or a truthful blocker.

Supported Claude headless mode and permission syntax must be verified from the installed version and current official documentation at deployment. Do not guess model IDs, force dangerous approval modes or substitute an unsupported service. Reference: https://code.claude.com/docs/en/headless . Scheduling configuration alone is not evidence; prove actual child invocation and receipt. A queued GitHub instruction does not wake ChatGPT unless a real connected review automation/event path exists. Show the executed lead turn and later worker acknowledgement, not a worker impersonating a lead review.

## Public effects and measurements — NR-10/11/12

Use exact destination/account/persona locking and minimal supported scopes. Durable effect state: PREPARED -> ATTEMPTED -> VERIFIED / FAILED / UNCERTAIN. Reserve before sending. Read back through the actual platform after submission. UNCERTAIN blocks resend until reconciliation. Do not claim universal exactly-once delivery where the platform offers no reliable idempotency key/readback; report the attainable no-blind-duplicate guarantee and unresolved uncertainty.

Observation records retain platform raw metric, unit, snapshot/delta/rate semantics, observation window, publication/experiment ref, namespace, retrieval time and provenance. Never sum snapshots as deltas. Track delayed metrics, missing denominators, deleted/private posts, pagination and timezone boundaries. A weak sample yields INCONCLUSIVE. Real engagement growth is not promised; the acceptance claim is that valid evidence changed or appropriately held strategy.
