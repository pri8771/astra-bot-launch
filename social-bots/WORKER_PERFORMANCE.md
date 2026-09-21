# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current lead review: `LEAD-026` (`lead-reviews/LEAD-026_2026-09-21T0252.md`). Foundational deep audits remain LEAD-015/017/019/020/023/024/025.

## Current verified worker/source activity

- Windows Core/Host: signed Claude commit `f73c337e66ccdd5bd09313e37f4c87b4f00df07e` structurally renamed the queue and analytics whole-runtime readers to explicit `admin_*` surfaces and added production-path bypass tests. Evidence commit `65c720b93aa973d92c2d99d378e2452b4d4e9db8` regenerated V03-006 and now commits exact verbatim full-suite output: **129 tests, OK**. Independent LEAD-026 review found one remaining V03-005 structural escape: ordinary `RuntimeState.content_history()` still reads all personas while only its docstring labels it admin, and the new bypass test checks only the old queue/analytics names.
- `SB-V03-004`: source-level repair at `7e4345b...` remains positive; no new defect was found, but independent execution required by the packet is still absent.
- Intelligence: latest worker commit remains heartbeat seq7 `a7bdeb4c0f0d2c1a3107798327266812a9644d27` at `04:10:36Z`; no V05-001/V15-001 source repair has appeared. Seq7 does not satisfy bootstrap because seq6→7 is ~30m28s. Prior worker-local full-suite claim remains 185.
- Mac QA/control: hourly coordination cadence is accepted, but the last worker heartbeat remains seq10 at `03:57:57Z`. No independent V03 repair execution report has landed. GitHub-hosted `social-bots-ci` run `35555060783` remains independently verified SUCCESS.
- V0.4 live-canary lane: no Claude worker execution commit exists; branch remains lead-only assignment evidence.
- External `worker-pc`: `socialbots-v03-repair-audit-20260921-01` failed at repository clone before Claude/tests, so it contributes zero acceptance evidence.

Heartbeat quality is tracked separately from implementation quality. Mac-QA coordination bootstrap is accepted; Intelligence remains bootstrap. Neither proves V0.7 recurring Social Bots runtime liveness.

## Current observations

The SP2–SP5 sample continues to support worker-first implementation with strong lead review at trust/isolation/fencing boundaries.

- SP2 bounded control work remains strong when the contract is explicit; `SB-CTL-006` CI was accepted after real GitHub-hosted execution.
- SP3 bounded engineering can pass cleanly (`SB-V03-002`), but trust/transport boundaries remain a recurring failure mode: `SB-V05-001` fixed caller-grantable trust yet independent review found the actual HTTPS constructor path invalid.
- SP4 isolation work responds well to narrow repair contracts but still tends to close the examples named in the review rather than proving exhaustive structural coverage. `f73c337...` correctly repaired `publish_queue` and `events_for`, but the worker's “no non-admin raw reader remains” claim escaped `RuntimeState.content_history()` because the new regression enumerated only those two names.
- SP5 fencing improved materially after iterative adversarial review. The V03-004 finish-receipt repair still looks correct in source and tests, but independent execution remains a deliberate acceptance gate for this high-risk lifecycle boundary.
- Worker scheduling remains a throughput defect on Intelligence and Mac QA: both have dependency-ready work but no fresh worker output. Heartbeat is observability and must not become foreground work.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> worker added forced FACT + VOICE failures | ACCEPTED | good bounded repair behavior |
| SB-V03-004 | 5 | PARTIAL | acquisition/final-commit repair; LEAD-019 migration defect repaired; LEAD-024 post-cycle success-receipt defect repaired at `7e4345b...` | CHANGES_REQUIRED pending independent execution | source-level repair looks correct; single POSIX host scope explicit |
| SB-V03-005 | 4 | PARTIAL | state split -> persona facade -> production-path tests -> queue/analytics admin names at `f73c337...` -> LEAD-026 found remaining ordinary `RuntimeState.content_history()` whole-runtime reader | CHANGES_REQUIRED | final narrow all-surface admin/raw-reader boundary repair required |
| SB-V03-006 | 3 | PREPARED | regenerated at `65c720b...` from `f73c337...`; exact `FULL_SUITE_OUTPUT.txt` shows 129 tests OK | BLOCKED | evidence-quality gap closed; must regenerate once more from final V03-005 SHA after predecessors accepted |
| SB-V04-001 | 3 | PARTIAL | production fail-closed posture implemented on worker branch but milestone remains dependency-gated | CHANGES_REQUIRED | real acceptance also needs canary chain |
| SB-V04-002 | 5 | PARTIAL | real Claude CLI adapter exists; injected tests prove interface but no real subscription call accepted yet | CHANGES_REQUIRED | `SB-V04-005` mandatory real proof |
| SB-V04-003 | 4 | PASS-LIKE source review | dependency unresolved | BLOCKED | deterministic authority boundary looks sound |

## Intelligence lane task results

| Artifact | SP | First submission | Independent review finding / repair cycles | Current lead disposition |
|---|---:|---|---|---|
| SB-V05-001 | 3 | PARTIAL | trust repairs closed self-registration and DNS-pinning concept; LEAD-020 found actual HTTPS path invalid; FAST TRACK repair still absent | CHANGES_REQUIRED |
| SB-V05-002 | 4 | PARTIAL | fails closed with static empty operational assessor policy; diagnostic heuristic paths do not claim operational authority | CHANGES_REQUIRED |
| SB-V13-001 | 4 | FAIL first acceptance invariant | repair added metric kinds, latest snapshot semantics, overlap-safe deltas and derivation provenance | ACCEPTED |
| SB-V14-001 | 4 | FAIL first isolation/privacy invariant | repair added bot+persona persistence, safe segment allowlist, sensitive-trait constraints | ACCEPTED |
| SB-V15-001 | 4 | PARTIAL | measurement provenance repaired; bot-wide normal experiment reader/persistence boundary remains; FAST TRACK repair absent | CHANGES_REQUIRED |
| SB-V16-001 | 4 | PARTIAL | latest repair submitted but not independently source-audited to acceptance | CHANGES_REQUIRED |
| SB-V12-001 | 3 | PASS-LIKE source review | operational availability/authority input acceptance unresolved | BLOCKED |
| SB-V17-001 | 4 | PARTIAL | latest receipt/persona-scope repair submitted but not independently accepted | CHANGES_REQUIRED |
| SB-V20-002 | 4 | PARTIAL | latest typed evidence/persona repair submitted at `feb30f4c...`; pending independent audit and V15 repair | CHANGES_REQUIRED |

## QA/control lane task results

| Artifact | SP | First submission | Independent evidence | Current lead disposition |
|---|---:|---|---|---|
| SB-CTL-012 | 3 | PASS | source reviewed; validator regressions; structural failures hard-error; V2 engineering/operational readiness separated | ACCEPTED |
| SB-CTL-006 | 2 | PASS | workflow source reviewed; read-only token; no secrets/model/deploy; GitHub-hosted run `35555060783` succeeded | ACCEPTED |
| Coordination heartbeat bootstrap | n/a | early burst/snapshot issues | later durable Mac-QA intervals accepted; Intelligence seq7 misses cadence | PASS Mac QA / FAIL-PENDING Intelligence | coordination proof only, not runtime proof |
| V2 acceptance harness prep | n/a | PASS-LIKE | non-runtime assertion layer | PREP ONLY | does not promote SB-V20-099 |
| Independent V03 repair verification | n/a | ASSIGNED / STALLED | Mac QA has not executed current repaired SHA; worker-pc clone failed | PENDING | independent execution remains absent |

## LEAD-026 focused lessons

### Exhaustive structural-boundary tests matter

The worker correctly implemented the two raw-reader examples emphasized in LEAD-025 and wrote a regression proving those old names are gone. Independent review then found another ordinary whole-runtime reader, `RuntimeState.content_history()`, that the regex/test did not enumerate. For structural isolation/security contracts, the test should derive or enumerate the complete sanctioned persona/admin surface across all stores rather than assert only a few remembered function names.

### Exact evidence capture improved

The worker immediately closed the V03-006 evidence-quality gap: `65c720b...` commits verbatim `FULL_SUITE_OUTPUT.txt` with 129 named tests and `OK`, instead of relying on prose or `full: OK`. Preserve this pattern for final acceptance regeneration.

### Fencing repair quality remains strong, but independent execution still matters

`7e4345b...` fences completion evidence and includes the exact adversarial takeover scenario. No new source defect was found in LEAD-026. Because it is a high-risk lifecycle artifact, keep independent execution as the final acceptance layer rather than silently lowering the packet bar because QA is stale.

### Stalled coordination lanes are a throughput issue

Mac QA is hourly-authorized but has produced no worker output after `03:57:57Z`. Intelligence has produced nothing after seq7 `04:10:36Z`. Lead assignments are current; the missing piece is worker execution, not more planning.

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
- complete admin/raw reader structural separation;
- migration scope;
- cross-persona import must be explicit.

### Fencing / lifecycle
- acquisition race safety is not enough;
- active-cycle ownership must be checked at commit;
- load/migration helpers must not bypass the fence with durable writes;
- completion/success evidence must not outlive ownership;
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

Do not infer worker quality from one artifact. Current evidence supports high Claude throughput when active, with adversarial lead review focused on trust, isolation, migration, lifecycle fencing, host boundaries and real-operation proof.

## Current concurrency implication

FAST TRACK primary lanes remain:
- Windows Core: final `RuntimeState.content_history()`/all-surface V03-005 raw-reader repair, then final V03-006 regeneration;
- Intelligence: source-stalled, explicitly assigned V05 now then V15;
- Mac QA: hourly-authorized but stale; must independently execute/probe current Core branch;
- dedicated local V0.4 canary: Priority Zero, still no worker activity;
- `worker-pc`: runner/control plane works, but Social Bots repository clone/auth remains broken.

Official version remains V0.3.x until artifact gates clear.
