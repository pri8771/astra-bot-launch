# Six missions from current evidence to unattended operation

This is an implementation plan, not a running platform. It extends qualified product routes through small common contracts. OPO, WHB and CommerceLint remain first priority. BidetFit and Guru use the next suitable release lanes; Lipi proceeds through its product/provider decisions. Existing Windows release work continues on its current assignments and authority.

## Reuse and source placement

The control baseline is `pri8771/astra-bot-launch@3833a1b392b140f0a4f79ac4ba00e39dcad383fb`. Mission evidence records fresh source refs. CommerceLint and BidetFit have existing deterministic operators; adapt them without starting a second scheduler. WHB has substantive retained Buffer/operator code whose first-account selection, non-atomic history, synthetic scheduling status and absent destination verification need repair. OPO is preserved site source, not an adopted commerce runtime. Guru references are editorial assets. Lipi's local readiness contracts are reuse candidates, not store/provider acceptance.

Shared prototypes named in CLAUDE_MAC.md are historical source pointers, not files verified in this control checkout. Do not fetch the old Mac. SH-01 consumes available portable focused returns or records a bounded source gap. Future shared implementation home is proposed `pri8771/astra-bot-launch/runtime/autonomy/` with small versioned contracts and adapters; SH-01 can bind a verified existing equivalent home with a reviewed path amendment. This planning assignment writes only `planning/autonomy-complete/`. Future implementation paths in task cards confer no present write ownership.

Shared code exposes ledger/claim/effect/input interfaces. Product repositories retain their code, native release routes and mission data. No new full Kai/Pri roadmap: optional owner-input adapters accept sanitized direction IDs; private mail, conversation history, credentials, personal preferences and assistant runtimes stay outside the control repository. File input is sufficient. i9 and Digital Temple are excluded.

## Minimum runtime topology

One authoritative ledger/effect broker owns each conflicting scope. Initial Windows qualification uses one local service process and local transactional storage; remote workers call that service rather than mounting its database. Existing cloud operators remain their mission owners until a recorded fenced handoff; they can report receipts without transferring effect authority. Shared claim membership is mandatory only when a mission adopts shared autonomous execution. This avoids a second scheduler alongside CommerceLint/BidetFit workflows.

SQLite on a local disk is a proposed low-complexity implementation for the initial service. Use transactions and uniqueness constraints for events/actions, a schema version and online-consistent backups. Do not put a WAL database on SMB or allow independent host copies to act as simultaneous authorities. SQLite supports one write transaction and WAL requires same-host access; busy errors get bounded deterministic retry, never a fail-open claim. These are storage constraints, not proof of distributed effect safety. [SQLite WAL](https://www.sqlite.org/wal.html), [transactions](https://www.sqlite.org/lang_transaction.html), checked 2026-09-12.

The effect broker alone holds publication/payment mutation credentials. Workers have proposal/read capabilities and receive short-lived action grants bound to mission, resource, operation, exact payload digest, current charter/direction, source/spec hash, budget reservation and fencing token. Direct worker credentials that bypass the broker would invalidate fencing. If a provider cannot enforce fences, serialize dispatch at the broker; revoke/disable the old route and reconcile all in-flight effects before takeover. Never promise exactly-once network delivery. The target is no duplicate business effect through idempotency or explicit reconciliation and fail-closed uncertainty.

## Persistent records and proposed interfaces

All IDs are namespaced by mission. Timestamps are UTC; monotonic clocks enforce local timeout, hub time enforces leases. Persist observed time separately from provider event time. Store original revisions append-only; summaries can be materialized and rebuilt.

| Record | Required fields and invariant |
| --- | --- |
| Charter/capability | mission, revision, issuer, resource/account, allowed effect, grant source/expiry, secret reference, monetary currency/cap, model/tool/time caps, stop state; missing monetary cap cannot authorize spending |
| Task/admission | internal ID, nullable Jira key, spec/source hashes, path/action claims, dependency evidence, current native readback hash, reviewer route; revision mismatch invalidates execution admission |
| Event/observation | event ID, source/account, source version, payload digest, observed/provider times, trust class, synthetic flag, data-scope reference; unique source+event+revision |
| Job/attempt | job ID, state, dependency/input refs, next_check_at, evidence version, decision fingerprint, host/worker, attempt ID, claim epoch/expiry, timeout; state transitions compare expected revision |
| Decision/experiment | original mission/charter, evidence IDs, hypothesis, alternative, intervention, source hash, comparison/baseline, metric/denominator, window/exposure, stop/success criteria, resource reservations, result/confounders/next decision; never rewrite old criteria |
| Effect/receipt | action ID, idempotency key, intent digest, resource/account, attempt and fence, grant revision, reservation, preimage, dispatch state/time, provider ID, receiving-system readback and evidence hash; a timeout is unknown effect |
| Direction/question | issuer/mission, direction revision, supersedes, question ID, minimum missing item, affected jobs, response evidence, seen/applied/needs-input/superseded state; silence never resolves it |
| Review/outbox | immutable operation ID, payload/spec hash, actual author/reviewer route, verdict, allowed fields, writer scope, preimage/readback, bounded repair count; a queued projection is not Jira acceptance |
| Usage/incident | actual model/provider/effort/host/tool counters, costs or null reason, reserved/max amounts, attempt time, incident fingerprint/severity, alert receipt/ack; elapsed experiment windows are not worklogs |

Proposed API operations: `append_observation`, `admit_task`, `claim(expected_revision)`, `renew(owner,epoch)`, `propose_decision(evidence_version)`, `reserve_budget`, `prepare_effect`, `dispatch_effect`, `verify_effect`, `reconcile_effect`, `record_direction`, `answer_question`, `append_outbox`, `ack_projection`, `checkpoint`, `restore_dry_run`. Each validates mission/resource scope and schema version. Read/proposal tools cannot call mutations by providing a different tool name. Integrations implement typed methods, not free-form shell commands supplied by external content.

## Deterministic selection and decision loop

1. A webhook/file change/qualified scheduled collector appends deduplicated observations. Validate provider signatures where available, reject replay and isolate untrusted content. Read collectors have explicit page/byte/time limits.
2. Ordinary code selects due jobs whose inputs changed or evaluation window/exception is due. Persist `next_check_at`, evidence version and decision fingerprint. Unchanged input and not-due decisions make zero inference calls. A missing-input job has no inference timer; a validated answer or material change wakes it.
3. Validate admission, owner stop/direction, dependency receipts, required inputs, capability and remaining budget. Block only dependent jobs. A deterministic action such as a known refresh need not use a model. A reasoning decision receives bounded sanitized context and returns a schema-validated proposal, never authority.
4. Record an experiment before its action through the designated Jira writer, preserving the current release packet's already-admitted work. New unrecorded experiments wait for native readback; independent preparation and permitted read-only observation continue during writer outage.
5. Claim task and action scope atomically, reserve cost/call budget, freeze source/payload/review hashes, recheck latest direction immediately before dispatch. Persist intent before the effect. Do not hold a database transaction open across network I/O.
6. Execute through the account-bound adapter, then read the actual destination. Provider acceptance, scheduled status, public visibility, customer delivery and measured business result are separate states. Failed verification produces pending/unknown/failed with evidence, not success.
7. Collect the declared window cheaply. Evaluate supported, not supported, inconclusive or invalidated. Record confounders and choose adopt/continue/amend/revert/stop or a new finite experiment. At least two completed eligible cycles per mission must demonstrate next-decision selection without another launch prompt; Lipi also retains the actual seven-day operations requirement. Waiting cannot be accelerated with fixtures.

The experiment graph is cyclic in operation through **new versioned experiment instances**, while the implementation task graph is acyclic. Zero demand is a valid observation; revenue, qualified outside agents and audience growth require actual evidence.

## Effects, uncertainty and owner changes

Before dispatch, an action is `prepared`; once a request may have left the process it is `dispatching/unknown` until destination reconciliation. A crash between remote success and local receipt never permits a blind retry. Query by provider idempotency key/client reference and expected account/payload/time range; confirm one match, confirmed absence, or unresolved ambiguity. Only confirmed absence under a provider-qualified protocol permits reattempt. Unsupported lookup creates an owner/reviewer exception and blocks that effect class. Retain budget reservation for unknown charged effects until reconciled.

Owner direction is validated at intake, job start and before each effect. Persist recorded/seen/applied separately; acknowledge the exact revision the worker consumed. Pause prevents new effects at a safe boundary; an order already submitted must be reconciled and is not assumed canceled. Amend active experiments with a dated revision. Questions are deduplicated by mission+missing fact+scope; reuse valid prior grants/answers. No approval by silence or generic nudge.

See PERMISSIONS_AND_INPUTS.md for exact effect gate records and release-worker interfaces. Ordinary previously granted categories do not require fresh generic permission. Concrete missing accounts, identifiers, quote ceilings or platform approvals do remain gates. Outgoing messages during this planning assignment are not authorized and are not sent.

## Windows lifecycle and later R730 handoff

SH-11 qualifies a Windows-native finite runner: create child suspended, assign it to a Job Object before resuming, disallow unsupported breakaway and inherited job handles, set process/memory/time caps and kill-on-close, then verify grandchildren terminate on timeout, owner stop and supervisor death. Handle assignment failure by refusing to resume. PID-only termination is insufficient. Scheduled/service startup and credentials must work without an active RDP session; a UI-only route remains explicitly desktop-dependent. [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects), checked 2026-09-12.

The runner restarts from durable state, verifies storage/source/schema, reconciles unknown effects and acquires a new epoch before running. Proposed qualification objectives are recovery within 15 minutes on available hardware and zero loss of acknowledged intents; these are test targets, not achieved service levels. An offline backup can lose later observations, so restore enters reconciliation mode and must not replay effects until destination checks cover the backup gap. Alerts cover inaccessible storage, unknown effect, stale receipt, unauthorized attempt, exhausted limit and failed restore. No alert repetition without a material state change or an explicitly agreed reminder.

SH-16 is a later independent migration gate. Qualify R730's existing storage/container/backup/secret facilities through the authorized official Unraid application route if an app is needed. No purchase or installation is performed by this plan. Transfer source/schema/config templates and sanitized hashes; provision credentials through approved host-local mechanisms. Drain/fence one mission on Windows or its current cloud owner, disable its old mutation route, reconcile in-flight effects, take consistent backup, restore on R730, validate epoch and run one allowed cycle. Restore/takeback follows the same fence/receipt protocol. A hub outage stops dependent effects; it does not grant Windows a new authority just because a heartbeat expired. Keep one active effect owner and retain host-local worktrees. No mobile-Mac runtime dependency, new network exposure, or i9 work is assumed.

## Review and completion boundary

Per-task checks and shared fault matrix feed exact-source independently attributable review. Record actual reviewer/model/effort/provider, reviewed source/spec/artifact hashes, commands run versus inspected, limitations and verdict. Same-model independent review must be labeled as such; it is not distinct-model approval where a product contract requires that. Two targeted repairs maximum unless a stricter task contract applies; unresolved findings keep the task incomplete and independent work eligible.

Planning completes when coverage, graph, inputs, estimates and outbox are actionable and reviewed. Implementation, deployment, autonomous operation, approved store launch, elapsed fulfillment and business validation remain separate unclaimed states. The task cards give future executors concrete acceptance instead of treating this plan as runtime evidence.
