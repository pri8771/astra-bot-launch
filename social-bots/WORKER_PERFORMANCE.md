# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current lead review: `LEAD-023` (`lead-reviews/LEAD-023_2026-09-21T0006.md`). Foundational deep audits remain LEAD-015/017/019/020.

Current verified worker/source activity:
- Windows Core/Host: V03-004 migration re-repair submitted at `175f741fcedace3113191a847d6a7568d77b9cde`; worker reports 115 local tests. Lead source inspection is positive; canonical acceptance remains CHANGES_REQUIRED until independent Mac-QA execution/report.
- Intelligence: last worker commit observed for this review is timed heartbeat seq6 `c27882546940536dd16c172ebd277664396c7cea`; no new V05-001/V15-001 source repair has been pushed since FAST TRACK activation. Prior worker-local full-suite claim remains 185.
- Mac QA/control: durable heartbeat validation progressed through seq10 `d0972adc15917ff9fca3edf48e1cd740ec61b66a`; multiple real ~15-18 minute intervals are present and lead authorized hourly coordination cadence. GitHub-hosted `social-bots-ci` run `35555060783` remains independently verified SUCCESS.
- V0.4 live-canary lane: no Claude worker execution commit exists yet; branch remains lead-only setup/authorization.
- External `worker-pc` read-only V03 audit attempt failed before clone on private-repo credential/visibility handling; it contributes no artifact evidence.

Heartbeat quality is tracked separately from implementation quality. Mac-QA coordination bootstrap is accepted; Intelligence remains bootstrap. Neither proves V0.7 recurring Social Bots runtime liveness.

## Current observations

The SP2–SP5 sample continues to support worker-first implementation with strong lead review at trust/isolation/fencing boundaries.

- SP2 bounded control work is strong when the contract is explicit. `SB-CTL-006` CI was accepted after real GitHub-hosted execution.
- SP3 bounded engineering can pass cleanly (`SB-V03-002`) but trust/transport boundaries remain a recurring failure mode: `SB-V05-001` fixed caller-grantable trust yet independent review found the actual HTTPS constructor path invalid.
- SP4 work improves materially after targeted repair. `SB-V13-001` and `SB-V14-001` are accepted; `SB-V15-001` still shows why production read/list isolation must be tested, not just record shape.
- SP5 fencing is still high-risk but the latest V03-004 repair is encouraging: the worker converted legacy migration to side-effect-free staging and routes durable migration writes through the fence. Independent QA is intentionally assigned before canonical acceptance changes.
- Worker scheduling itself can become a throughput defect: both Windows and Intelligence spent time on heartbeat-test waits after FAST TRACK explicitly made heartbeat background observability. Lead assignments now explicitly prohibit foreground heartbeat-only idling.

This still supports Claude as the implementation workhorse. The lead should keep decomposing SP4/SP5 work into narrow contracts and independently exercise production-path trust/isolation/fencing invariants.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> worker added forced FACT + VOICE failures | ACCEPTED | good bounded repair behavior |
| SB-V03-004 | 5 | PARTIAL | generation/final commit repair, then LEAD-019 found side-effectful migration; `175f741...` stages migration in memory and fences all durable writes | CHANGES_REQUIRED pending independent QA | lead source review positive; Mac QA must execute/review current branch before status promotion; host portability remains separate V07 proof |
| SB-V03-005 | 4 | PARTIAL | RuntimeState/PersonaState split fixed primary private mutable state; production dedup read scoped, but authoritative persona-scoped production readers remain incomplete | CHANGES_REQUIRED | immediate Core task; preserve V03-004 repair |
| SB-V03-006 | 3 | BLOCKED | depends on accepted V03-004/V03-005 | BLOCKED | regenerate fresh only after repair/verification |
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
| SB-V15-001 | 4 | PARTIAL | measurement provenance repaired; bot-wide experiment persistence/read API can expose another persona through normal readers | CHANGES_REQUIRED |
| SB-V16-001 | 4 | PARTIAL | latest repair submitted but not yet independently source-audited to acceptance | CHANGES_REQUIRED |
| SB-V12-001 | 3 | PASS-LIKE source review | V13 prerequisite accepted; operational availability/authority input acceptance unresolved | BLOCKED |
| SB-V17-001 | 4 | PARTIAL | latest receipt/persona-scope repair submitted but not independently accepted | CHANGES_REQUIRED |
| SB-V20-002 | 4 | PARTIAL | latest typed evidence/persona repair submitted at `feb30f4c...`; pending independent audit and V15 repair | CHANGES_REQUIRED |

## QA/control lane task results

| Artifact | SP | First submission | Independent evidence | Current lead disposition |
|---|---:|---|---|---|
| SB-CTL-012 | 3 | PASS | source reviewed; 18 validator regressions; structural failures hard-error; V2 engineering/operational readiness separated | ACCEPTED |
| SB-CTL-006 | 2 | PASS | workflow source reviewed; read-only token; no secrets/model/deploy; GitHub-hosted run `35555060783` succeeded | ACCEPTED |
| Coordination heartbeat bootstrap | n/a | early burst/snapshot issues | later durable history includes several real ~15-18m intervals; Mac QA hourly authorized | PASS for Mac QA / Intelligence still bootstrap | coordination proof only, not runtime proof |
| V2 acceptance harness prep | n/a | PASS-LIKE | 20 harness tests / 38 total reported; non-runtime assertion layer | PREP ONLY | does not promote SB-V20-099 |
| Independent V03-004 repair verification | n/a | ASSIGNED | Mac QA now owns non-source-changing verification of `175f741...` | PENDING | replaces failed worker-pc audit evidence path for this checkpoint |

## LEAD-023 focused lessons

### Heartbeat must not become the work

Timed coordination proof is useful, but FAST TRACK explicitly makes it background observability. A foreground `sleep` validation loop is acceptable for a one-time mechanism test, not as an ongoing reason to pause dependency-ready source work. Worker instructions now require recording due heartbeats and continuing implementation/QA immediately.

### Fencing review must include load/migration paths

Moving the main commit under a lease fence is insufficient if a load helper mutates disk before the final ownership check. The V03-004 repair at `175f741...` is stronger because migration is staged in memory and only persisted by the fenced commit. Independent execution is still required before canonical acceptance changes.

### Test the actual trusted transport constructor

Security architecture can look correct while the operational path is unusable. `SB-V05-001` still needs a regression that reaches the real HTTPS connection-construction path rather than only overridden/stubbed helpers.

### Persona isolation must cover readers, not only records

Adding a persona field or separate mutable state is insufficient if normal persistence/list/read APIs stay bot-wide. Every SP4+ private workspace store must expose an authoritative persona-scoped production boundary and mixed-persona regressions through that boundary.

### Independent CI/QA improves evidence quality

`SB-CTL-006` remains the first independently verified GitHub-hosted control. Mac QA is now additionally used as a non-overlapping independent verifier of difficult Core fencing repairs before lead promotion.

## Recurring defect themes

### Trust / operational provenance
- no caller self-registration of operational trust;
- fixture/untrusted evidence must never be silently upgraded;
- operational semantic authority must fail closed when unavailable;
- real network/provider paths require path-level proof.

### Persona/workspace isolation
- storage scope;
- read/list scope;
- migration scope;
- cross-persona import must be explicit.

### Fencing / migration
- acquisition race safety is not enough;
- active-cycle ownership must be checked at commit;
- load/migration helpers must not bypass the fence with durable writes;
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

Do not infer worker quality from one artifact. Current evidence supports high Claude throughput with adversarial lead review focused on trust, isolation, migration, host boundaries and real-operation proof.

## Current concurrency implication

FAST TRACK primary lanes remain:
- Windows Core implementation active;
- Intelligence implementation active;
- Mac QA/integration active with hourly coordination heartbeat;
- dedicated local V0.4 canary lane ready but repository worker activity not yet detected.

A separate `worker-pc` capacity exists but its first read-only audit failed before clone on private-repo auth visibility. It is not active acceptance evidence and must not overlap source ownership if re-enabled.

Priority Zero remains the real `SB-V04-005` canary. Official version remains V0.3.x until artifact gates clear.
