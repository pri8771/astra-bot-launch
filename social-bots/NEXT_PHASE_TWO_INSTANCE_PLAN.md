# Next-phase execution plan — two Claude instances + ChatGPT lead

Owner resources:
- one Claude environment on the existing primary instance;
- one Claude environment on Windows;
- ChatGPT as artifact/acceptance lead.

## Recommendation

Run **two implementation sessions concurrently now**, one per instance.

Do not add a third implementation session during the first repair wave. The current bottleneck is cross-cutting correctness/integration, not lack of queued code. ChatGPT stays ahead by preparing acceptance/integration artifacts and reviewing each checkpoint.

A third Claude session can be added after Wave 1 when the shared state/evidence contracts are stable.

## Instance A — Windows / Core + Host

Suggested branch:
`claude/social-bots-windows-core-host`

Why Windows owns this:
- native Windows locking/fencing is currently unproven;
- actual Claude Code subscription/CLI reasoning route can be verified on a real user host;
- Windows can prove recurring worker/task-scheduler behavior that cloud sessions cannot.

### Wave A1 — Core correctness
1. Repair SB-V03-004:
   - fence decision log/latest-decision writes;
   - remove false transactionality claims;
   - prove native Windows strong lock/fence OR, if WSL already exists and is chosen, explicitly prove the supported WSL/POSIX deployment.
2. Repair SB-V03-005:
   - split RuntimeState vs PersonaState;
   - per-persona consumed signal ledger;
   - per-persona hypotheses/working/pending state;
   - shared captured evidence remains read-only.
3. Produce SB-V03-006 acceptance bundle after lead acceptance.

### Wave A2 — Adaptive reasoning + host
4. Repair SB-V04-001 and SB-V04-002:
   - production adaptive-required fail-closed posture;
   - actual bounded Claude Code CLI adapter using existing subscription if host verification succeeds;
   - fail closed if ANTHROPIC_API_KEY is present;
   - no tools/external effects in reasoning call;
   - strict REASONING_PROPOSAL_SCHEMA validation.
5. Execute V0.4 divergence/evidence bundle.
6. Implement SB-CTL-006 GitHub CI workflow.
7. Work V0.7 Windows host proof:
   - supported recurring launcher (Task Scheduler or already-available WSL scheduler);
   - two separate real invocations;
   - actual heartbeat/receipts;
   - restart/no-overlap proof.

Do not create paid API credentials.

## Instance B — Intelligence / Evidence Integrity + Growth

Suggested branch:
`claude/social-bots-intelligence-repair-v2`

### Wave B1 — Evidence foundations
1. Repair SB-V05-001:
   - trusted collector-owned live transport only;
   - public HTTP(S) destination validation / SSRF protection;
   - redirect validation;
   - extraction_status.
2. Repair SB-V05-002:
   - attributable support assessor;
   - evidence excerpt/span/hash;
   - caller-supplied stance only for fixtures;
   - fail closed operationally without assessor.
3. Repair SB-V13-001:
   - cumulative_snapshot / delta / gauge / rate semantics;
   - semantic-aware aggregation.
4. Repair SB-V14-001:
   - persona-scoped audience memory;
   - safe segment allowlist;
   - correct fork semantics.

### Wave B2 — V1.5–V2 inputs
5. Repair SB-V15-001:
   - typed normalized-observation baseline/treatment refs.
6. Repair SB-V16-001:
   - accepted ClaimSupportResult binding;
   - persona-scoped content intelligence history.
7. Repair SB-V17-001:
   - receipt-backed community evidence;
   - persona-scoped community memory/themes.
8. Repair SB-V20-002:
   - typed GrowthOpportunity construction from metrics/experiments/audience;
   - no arbitrary operational numbers.

## ChatGPT lead lane

While both sessions work:
- maintain canonical artifact statuses;
- review every submitted artifact;
- own cross-lane schemas and migrations;
- prepare merge/integration packet;
- build SB-V20-099 acceptance harness design;
- keep V2.1/V2.2/V2.3/V3 packets ready;
- track Claude performance by story point and repair count.

## Wave 2 — integration after both repair branches clear

Create an integration branch only after lead acceptance of the foundational repairs.

Integration goals:
1. merge corrected Core + Intelligence branches;
2. run full CI;
3. captured evidence -> factual support -> content/experiment -> metrics -> audience -> growth opportunity -> strategy revision;
4. prove persona isolation through entire chain;
5. implement SB-V20-001 strategy state/revision engine;
6. generate SB-V20-099 V2.0 engineering-readiness bundle.

At this point a third Claude session becomes useful:
- one Core/strategy;
- one Intelligence/integration;
- one forward lane V2.1/V2.2/V2.3.

## Wave 3 — V2.3 strategic checkpoint

After V2.0 engineering readiness:
- V2.1 immutable dynamic strategy lifecycle;
- V2.2 autonomous goal decomposition;
- V2.3 temporary specialist worker contract/lifecycle.

Windows host can also act as the first real specialist-worker execution host if it remains the proven safe host.

## Wave 4 — V3.0

Two main implementation lanes again:
- Core/portfolio orchestration + brand isolation;
- Intelligence/portfolio analytics + allocation + organizational learning.

Lead owns V3 acceptance and cross-brand contamination tests.

## Public/operational gates

Operational V1.0+/V2.0 still requires real account/public/analytics evidence where defined.

Do not weaken those gates to advance the version number.
