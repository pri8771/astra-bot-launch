# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current lead review: `LEAD-024` (`lead-reviews/LEAD-024_2026-09-21T0052.md`). Foundational deep audits remain LEAD-015/017/019/020/023.

Current verified worker/source activity:
- Windows Core/Host: `SB-V03-005` submitted at `d1e4bee3287b857c2e6fe69f344dfd122fa52c95`; `SB-V03-006` regenerated as PREPARED evidence at `0433fc85ade481e6f108b126273cc0823aa667ed`; worker reports 122 local tests. Lead source inspection found a post-cycle success-receipt fencing gap and incomplete production-reader enforcement, so V03-004/V03-005 remain CHANGES_REQUIRED and V03-006 remains BLOCKED/PREPARED.
- Intelligence: latest worker commit observed is heartbeat seq7 `a7bdeb4c0f0d2c1a3107798327266812a9644d27`; no V05-001/V15-001 source repair has been pushed since FAST TRACK activation. Seq7 does not satisfy the ~15-minute bootstrap because seq6→7 is ~30m28s. Prior worker-local full-suite claim remains 185.
- Mac QA/control: no worker-generated independent V03 verification report has landed after LEAD-023. Mac-QA hourly coordination cadence remains accepted; GitHub-hosted `social-bots-ci` run `35555060783` remains independently verified SUCCESS.
- V0.4 live-canary lane: no Claude worker execution commit exists yet; branch remains lead-only setup/assignment evidence.
- External `worker-pc`: prior Social Bots read-only audit failed before clone on private-repo credential visibility and contributes no artifact evidence. At LEAD-024 review time its single protocol slot is occupied elsewhere, so no new Social Bots dispatch is appropriate.

Heartbeat quality is tracked separately from implementation quality. Mac-QA coordination bootstrap is accepted; Intelligence remains bootstrap. Neither proves V0.7 recurring Social Bots runtime liveness.

## Current observations

The SP2–SP5 sample continues to support worker-first implementation with strong lead review at trust/isolation/fencing boundaries.

- SP2 bounded control work is strong when the contract is explicit. `SB-CTL-006` CI was accepted after real GitHub-hosted execution.
- SP3 bounded engineering can pass cleanly (`SB-V03-002`) but trust/transport boundaries remain a recurring failure mode: `SB-V05-001` fixed caller-grantable trust yet independent review found the actual HTTPS constructor path invalid.
- SP4 work improves materially after targeted repair, but isolation requires structural production-path enforcement, not only safe facade helpers. V03-005's new `persona_records()` facade is useful, yet public raw runtime readers still permit accidental bypass unless repaired.
- SP5 fencing remains high-risk. The worker successfully repaired acquisition, active-cycle commit fencing and side-effectful migration, but LEAD-024 found a later lifecycle edge: success/finish receipts are emitted after the fenced cycle returns. Acceptance must cover completion evidence as well as cycle data.
- Worker scheduling itself can become a throughput defect: Intelligence continued heartbeat activity without its assigned V05/V15 source repair. Heartbeat remains background observability and must not become the work.

This still supports Claude as the implementation workhorse. The lead should keep decomposing SP4/SP5 work into narrow contracts and independently exercise production-path trust/isolation/fencing invariants.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> worker added forced FACT + VOICE failures | ACCEPTED | good bounded repair behavior |
| SB-V03-004 | 5 | PARTIAL | acquisition/final-commit repair; LEAD-019 found side-effectful migration; `175f741...` fixed migration staging; LEAD-024 found post-cycle success/finish receipt emitted outside ownership fence | CHANGES_REQUIRED | another bounded repair required: forced post-cycle TTL expiry/takeover must prevent stale-owner success receipt; host portability remains separate V07 proof |
| SB-V03-005 | 4 | PARTIAL | RuntimeState/PersonaState split fixed primary private mutable state; `d1e4bee...` added persona reader facade + generic no-bleed tests; LEAD-024 found public raw whole-runtime readers still bypass the facade | CHANGES_REQUIRED | enforce actual production read/list paths and structurally separate admin/raw APIs |
| SB-V03-006 | 3 | PREPARED | `0433fc85...` regenerated focused/full evidence and worker reports 122 passing; new LEAD-024 defects were found afterward | BLOCKED | regenerate from final repaired SHA only after V03-004/V03-005 acceptance |
| SB-V04-001 | 3 | PARTIAL | production fail-closed posture implemented on worker branch but milestone remains dependency-gated | CHANGES_REQUIRED | real acceptance also needs canary chain |
| SB-V04-002 | 5 | PARTIAL | real Claude CLI adapter exists; injected tests prove interface but no real subscription call accepted yet | CHANGES_REQUIRED | `SB-V04-005` mandatory real proof |
| SB-V04-003 | 4 | PASS-LIKE source review | dependency unresolved | BLOCKED | deterministic authority boundary looks sound |

## Intelligence lane task results

| Artifact | SP | First submission | Independent review finding / repair cycles | Current lead disposition |
|---|---:|---|---|---|
| SB-V05-001 | 3 | PARTIAL | multiple trust repairs closed self-registration and DNS-pinning concept; LEAD-020 found actual HTTPS path invalid because `HTTPSConnection(..., server_hostname=...)` is unsupported; no repair pushed yet in FAST TRACK | CHANGES_REQUIRED |
| SB-V05-002 | 4 | PARTIAL | fails closed with static empty operational assessor policy; diagnostic keyword/heuristic paths no longer claim operational authority | CHANGES_REQUIRED |
| SB-V13-001 | 4 | FAIL first acceptance invariant | repair added metric kinds, latest snapshot semantics, known-kind-on-missing, overlap-safe deltas and derivation provenance | ACCEPTED |
| SB-V14-001 | 4 | FAIL first isolation/privacy invariant | repair added bot+persona persistence, safe segment allowlist, compound sensitive-trait rejection, same-persona forks | ACCEPTED |
| SB-V15-001 | 4 | PARTIAL | measurement provenance repaired; bot-wide experiment persistence/read API can expose another persona through normal readers; no FAST TRACK repair yet | CHANGES_REQUIRED |
| SB-V16-001 | 4 | PARTIAL | latest repair submitted but not yet independently source-audited to acceptance | CHANGES_REQUIRED |
| SB-V12-001 | 3 | PASS-LIKE source review | V13 prerequisite accepted; operational availability/authority input acceptance unresolved | BLOCKED |
| SB-V17-001 | 4 | PARTIAL | latest receipt/persona-scope repair submitted but not independently accepted | CHANGES_REQUIRED |
| SB-V20-002 | 4 | PARTIAL | latest typed evidence/persona repair submitted at `feb30f4c...`; pending independent audit and V15 repair | CHANGES_REQUIRED |

## QA/control lane task results

| Artifact | SP | First submission | Independent evidence | Current lead disposition |
|---|---:|---|---|---|
| SB-CTL-012 | 3 | PASS | source reviewed; 18 validator regressions; structural failures hard-error; V2 engineering/operational readiness separated | ACCEPTED |
| SB-CTL-006 | 2 | PASS | workflow source reviewed; read-only token; no secrets/model/deploy; GitHub-hosted run `35555060783` succeeded | ACCEPTED |
| Coordination heartbeat bootstrap | n/a | early burst/snapshot issues | later durable history includes real ~15-18m Mac-QA intervals; Intelligence seq7 misses cadence with ~30.5m interval | PASS Mac QA / FAIL-PENDING Intelligence | coordination proof only, not runtime proof |
| V2 acceptance harness prep | n/a | PASS-LIKE | 20 harness tests / 38 total reported; non-runtime assertion layer | PREP ONLY | does not promote SB-V20-099 |
| Independent V03 repair verification | n/a | ASSIGNED | Mac QA now owns post-cycle success-receipt takeover and production-reader bypass probes | PENDING | exact LEAD-024 acceptance scenarios, no Core source edits |

## LEAD-024 focused lessons

### Fencing must include completion evidence

A well-fenced decision/state commit is insufficient if the worker emits a success receipt afterward without revalidating ownership. The lease/fence contract covers durable evidence that implies successful ownership, not just business-state writes. SP5 acceptance must explicitly force takeover after the cycle commit but before the finish receipt.

### A safe persona facade is not structural isolation by itself

`persona_records()` is directionally strong, but the application still exposes ordinary public whole-runtime readers. SP4 acceptance must trace actual production call paths and either route them through persona scope or make raw access explicitly admin/private. Tests of only the facade cannot prove callers cannot bypass it.

### Heartbeat claims are independently timed

A worker note that says “completed 3x15-minute validation” is not acceptance. Intelligence seq5→6 is ~16m37s, but seq6→7 is ~30m28s, so hourly remains unauthorized. Durable timestamps, not prose, decide cadence.

### Prepared evidence must be regenerated after newly discovered defects

`SB-V03-006` at `0433fc85...` is useful evidence, but once lead review identifies correctness defects not covered by that bundle, it becomes preparation rather than acceptance proof. The final bundle must come from the repaired implementation SHA.

## Recurring defect themes

### Trust / operational provenance
- no caller self-registration of operational trust;
- fixture/untrusted evidence must never be silently upgraded;
- operational semantic authority must fail closed when unavailable;
- real network/provider paths require path-level proof.

### Persona/workspace isolation
- storage scope;
- read/list scope;
- production call-path enforcement;
- admin/raw reader separation;
- migration scope;
- cross-persona import must be explicit.

### Fencing / lifecycle
- acquisition race safety is not enough;
- active-cycle ownership must be checked at commit;
- load/migration helpers must not bypass the fence with durable writes;
- post-cycle success receipts must not outlive ownership;
- host/filesystem scope must be stated honestly.

### Dependency discipline
Workers may build additive scaffolding ahead of promotion, but downstream status stays blocked until prerequisites are accepted. `SB-V20-099` is not promoted by harness/local tests alone.

## Metrics to continue accumulating

For each SP level track:
- attempts;
- first-pass accepted;
- first-pass partial/failed;
- repair cycles;
- independent findings;
- dependency violations/early-start incidents;
- escaped defects;
- acceptance after repair;
- GitHub CI vs worker-local-only evidence;
- production-path vs fixture-only acceptance evidence;
- idle/coordination overhead that delayed dependency-ready implementation.

Do not infer worker quality from one artifact. Current evidence supports high Claude throughput with adversarial lead review focused on trust, isolation, migration, lifecycle fencing, host boundaries and real-operation proof.

## Current concurrency implication

FAST TRACK primary lanes remain:
- Windows Core implementation active on two bounded V0.3 repairs;
- Intelligence implementation active but source-stalled and explicitly re-assigned V05 now;
- Mac QA/integration active with hourly coordination heartbeat and exact independent V03 probes;
- dedicated local V0.4 canary lane ready but repository worker activity still absent.

A separate `worker-pc` capacity exists but its first Social Bots audit failed before clone on private-repo auth visibility, and its single slot is presently occupied by another control-plane task. It is not active Social Bots evidence.

Priority Zero remains the real `SB-V04-005` canary. Official version remains V0.3.x until artifact gates clear.
