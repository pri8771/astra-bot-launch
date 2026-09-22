# Social Bots target architecture at V3.0

## Control plane
Artifact graph, version gates, owner authorization manifests, policy, budgets, acceptance and audit.

## Evidence plane
Collectors -> CaptureReceipt/EvidenceRef -> factual/cultural support -> analytics/community observations.

## Memory plane
Persona state -> audience/experiment memory -> StrategyState -> OrganizationalMemory, each scope-isolated and versioned.

## Decision plane
ReasoningProvider proposes -> deterministic policy validates -> strategy/goal planner creates bounded artifacts/actions.

## Action plane
AccountRoute -> authorization manifest -> exactly-once effect wrapper -> external readback -> analytics observation.

## Worker plane
OS-scheduled persistent worker sessions plus temporary least-authority specialist workers.

## Portfolio plane
Brand contracts, shared-public knowledge allowlist, portfolio goals, resource budgets/allocation and organizational self-evaluation.

## Deployment shape

Preferred default through V3.0: self-hosted on one owner-controlled persistent host with durable local storage and OS scheduling, because the expected workload does not justify distributed infrastructure by default.

Add complexity only from measured need:
- SQLite WAL/index adapter if JSON/file-store contention appears.
- Separate process pools when specialist concurrency demands it.
- Postgres only if multi-host/write-concurrency or operational evidence demonstrates SQLite/file storage is inadequate.
- Remote workers remain optional capacity, never project authority.

## Model strategy

Reasoning remains behind a provider interface.

Use:
- deterministic code for policy, authority, scheduling, verification, math, dedup and state transitions;
- reasoning models for interpretation, synthesis, ranking, drafting and review;
- explicit per-run/provider budgets;
- fail closed when required adaptive reasoning is unavailable;
- no implicit PAYG fallback.

V3.0 must not depend on one particular model provider for correctness of authority/safety.
