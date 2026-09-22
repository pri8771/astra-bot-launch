# Master execution plan — Social Bots V0.4 through V3.0

This is the lead-side dependency and execution plan. It does not change current milestone status or authorize any live model/public/account action.

## Operating model

- Claude is the primary implementation worker.
- ChatGPT lead stays ahead on contracts, artifact decomposition, acceptance criteria, independent review and next-work release.
- One fresh worker session emits exactly one durable SESSION_ONCE heartbeat.
- Repository truth and accepted artifacts determine promotion.
- If one artifact is authority-blocked, workers pull dependency-safe engineering/prep work instead of idling.

## Critical path

V0.4 empirical divergence
→ V0.5 evidence integrity
→ V0.6 three real zero-public dry runs
→ V0.7 OS-scheduled worker/lead autonomy
→ V0.8 verified real account connectivity
→ V0.9 explicitly authorized public canaries + real measurement
→ V1.0 continuous three-bot operation
→ V1.1 reliability
→ V1.2 platform intelligence
→ V1.3 analytics semantics
→ V1.4 audience memory
→ V1.5 experiments
→ V1.6 content intelligence
→ V1.7 community operation
→ V1.8 cultural personas operational
→ V1.9 stabilization
→ V2.0 growth engine
→ V2.1 dynamic strategy
→ V2.2 goal decomposition
→ V2.3 bounded specialist workers
→ V2.4 institutional memory
→ V2.5 non-sensitive audience segmentation
→ V2.6 trend intelligence
→ V2.7 cross-platform strategy
→ V2.8 growth allocation
→ V2.9 bounded self-evaluation
→ V3.0 autonomous multi-brand media organization.

## Parallel preparation lanes

### Core/runtime
Worker-once, schedulers, leases/fencing, task claim, strategy state, planners, specialist-worker lifecycle, portfolio plane.

### Intelligence/evidence
Collectors, factual support, analytics semantics, audience memory, experiments, content intelligence, community intelligence, trends, allocation, drift detection.

### Connectivity
Credentials-free account registry, route verification, readback, analytics routes, exact destination locking.

### Acceptance/QA
Mechanical validators, fault injection, independent candidate review, crash/restart tests, public-effect readback, operational bundles.

### Lead/control
Artifact graph, schemas, owner-gate manifests, acceptance evidence review, version promotion, cross-lane conflict prevention.

## Pull-next rule

A worker chooses the next task by:
1. reading canonical STATE/ARTIFACT_INDEX/WORK_QUEUE/SESSION_ROUTER;
2. filtering artifacts owned by its lane whose dependencies are accepted;
3. excluding anything requiring an owner gate that is not currently authorized;
4. preferring current critical-path work;
5. if critical path is externally blocked, taking the earliest dependency-safe prep/engineering artifact;
6. never self-accepting.

## Owner-only gates

Only these classes should stop for owner action:
- fresh authorization for bounded live model/adaptive call batches when no valid manifest exists;
- real public posting/reply/message action;
- account login/MFA/passkey/CAPTCHA/consent or credential connection;
- new spend/PAYG/purchase;
- destructive/correction action with external impact when not already authorized.

Ordinary implementation, tests, fixtures, validators, docs, scheduling adapters and read-only analysis should continue without owner relay.

## Evidence hierarchy

1. real external/public/account readback or host execution receipts;
2. independent acceptance execution against pinned source;
3. committed test outputs/CI;
4. worker self-reported tests;
5. fixtures/synthetic engineering checks;
6. prose claims.

A lower tier cannot substitute for a higher tier when the packet explicitly requires operational proof.

## Planning corrections made

The product roadmap already contained V1.8/V1.9 and V2.4–V2.9, but the milestone manifest previously jumped V1.7→V2.0 and V2.3→V3.0. The manifest is now aligned so operational promotion cannot skip those roadmap stages.

V2.0 engineering may still be prepared early, but operational V2.0 requires V1.9 stabilization. V3.0 engineering may be prepared early, but V3.0 acceptance requires the V2.9 self-evaluation checkpoint.
