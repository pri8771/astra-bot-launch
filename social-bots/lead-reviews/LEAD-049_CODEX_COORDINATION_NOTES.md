# LEAD-049 — repository-native notes for one Codex coordinator

Type: owner-requested documentation and routing handoff. NOT runtime acceptance, a new model grant, an implementation takeover, or a milestone/scope change.

The owner requested that all relevant notes be saved in Git so Codex can manage Social Bots, Jobs and Swarm in one conversation. Added `coordination/codex/START.md`, machine-readable PROJECTS.json, per-project dossiers, owner decision history, operating/heartbeat handoff rules, compact session record and a reusable prompt. Root AGENTS.md routes explicitly requested multi-project work there. Added a Social Bots-specific Codex handoff pointer.

## Verified source baselines

- Bots: canonical 982fbce3406e24f186d9b68d0fadeb9bf7058ca6; worker head 347de2b5c91c774670c3b884cc542c88fa6eabfa. Read root agent rules and LIVE V1.7 scope. No material runtime progress inferred from lead assignment delivery.
- Jobs: main 5610f43276c7886bbdb1d1d038473101566a19c3. Read native V17_LEAD_HANDOFF and FABLE_V17_LIVE. Candidate branch/ref is recorded separately, not treated as accepted main or assumed active worker.
- Swarm: coordination 817821d0bab6c68ae1b92671b115f8be98590ebc; app ab958d7a4b4d6198b143e7e79ecf69ff367cb10e. Read native AGENTS, SESSION_START, EXECUTION_CONTROL and worker status/heartbeat. Reported Fable takeover/OPS-CI-01/next R27a is a worker snapshot, not an independent checkpoint pass. Status/heartbeat paths are under docs/coordination, not root.

## Decisions preserved

All three native contracts currently cap development at genuinely LIVE V1.7. No V1.8+ auto-continuation. Same numeric target does not merge definitions or prerequisites.

Bots uses SESSION_ONCE. Jobs and Swarm each use one owned local five-minute worker heartbeat. The coordinator must not unify those rules, create duplicate watchers or turn a timer into false model activity. No automation was changed or started.

ChatGPT remains artifact acceptance authority. Codex coordinates status, reviews, readiness and safe execution; Fable's implementation ownership remains until an actual permitted clean handoff. No worker ACK or active process was fabricated. A safe coordinator action must not add another writer.

Runtime data, secrets, approval ledgers, model/public/application/mailbox permissions and source trees remain separate. Social Bots remains independent of Swarm. The common hub is only notes and navigation, not another runtime or second product registry.

## Scope of this write

Only this Social Bots repository's documentation/routing is changed. Jobs/Swarm source and coordination were read, not rewritten. Existing artifact statuses, milestone manifests, model/public grants and native queues remain unchanged. No full runtime suite, live model call, public effect, account creation, scheduler install or main merge occurred. The prior delivery patch and detailed plans are already in Git and referenced, not reapplied or copied as another queue.

Codex's first actual session must fetch current refs again, inspect submitted evidence/real ownership, produce one compact three-project table, and execute the smallest already-permitted nonconflicting action. Future exact status belongs to fresh project evidence, not these pinned snapshots.
