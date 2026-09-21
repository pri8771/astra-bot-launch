# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current lead review: `LEAD-025` (`lead-reviews/LEAD-025_2026-09-21T0158.md`). Foundational deep audits remain LEAD-015/017/019/020/023/024.

## Current verified worker/source activity

- Windows Core/Host: signed Claude commit `7e4345b041b59b9d1b1036dfea388cedf79b4d3d` repaired the LEAD-024 post-cycle finish-receipt fencing defect in source and added targeted production-read-path tests. `b2083b8f1f47c04467e38fcf62c5da274c0b8f67` regenerated V03-006 evidence from that implementation. Worker reports 127 local tests. Lead source inspection supports the V03-004 repair but finds V03-005 still incomplete because ordinary raw whole-runtime reader APIs remain callable; independent execution of the repaired branch has not yet succeeded.
- Intelligence: latest worker commit remains heartbeat seq7 `a7bdeb4c0f0d2c1a3107798327266812a9644d27` at `04:10:36Z`; no V05-001/V15-001 source repair has appeared. Seq7 does not satisfy bootstrap because seq6→7 is ~30m28s. Prior worker-local full-suite claim remains 185.
- Mac QA/control: hourly coordination cadence is accepted, but the last worker heartbeat is seq10 at `03:57:57Z`. No independent V03 repair verification report has landed. GitHub-hosted `social-bots-ci` run `35555060783` remains independently verified SUCCESS.
- V0.4 live-canary lane: no Claude worker execution commit exists; branch remains lead-only assignment evidence.
- External `worker-pc`: first Social Bots audit failed before work at private-repository visibility. LEAD-025 retried with `socialbots-v03-repair-audit-20260921-01`; it reached the Windows runner but failed at repository clone before Claude/tests, so it contributes zero acceptance evidence.

Heartbeat quality is tracked separately from implementation quality. Mac-QA coordination bootstrap is accepted; Intelligence remains bootstrap. Neither proves V0.7 recurring Social Bots runtime liveness.

## Current observations

The SP2–SP5 sample continues to support worker-first implementation with strong lead review at trust/isolation/fencing boundaries.

- SP2 bounded control work remains strong when the contract is explicit; `SB-CTL-006` CI was accepted after real GitHub-hosted execution.
- SP3 bounded engineering can pass cleanly (`SB-V03-002`), but trust/transport boundaries remain a recurring failure mode: `SB-V05-001` fixed caller-grantable trust yet independent review found the actual HTTPS constructor path invalid.
- SP4 work improves with targeted repair but still tends to satisfy behavioral examples before fully enforcing structural boundaries. V03-005 now has real production-path tests, yet the ordinary raw whole-runtime APIs remain available by convention.
- SP5 fencing improved materially after iterative adversarial review. The new V03-004 finish-receipt repair addresses a lifecycle edge missed by earlier submissions. Because it is a high-risk trust boundary, source review alone is not enough for final acceptance; independent execution remains desirable.
- Worker scheduling is currently a throughput defect on Intelligence and Mac QA: both have gone stale despite clear dependency-ready work. Heartbeat is observability and must not become foreground work.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> worker added forced FACT + VOICE failures | ACCEPTED | good bounded repair behavior |
| SB-V03-004 | 5 | PARTIAL | acquisition/final-commit repair; LEAD-019 migration defect repaired; LEAD-024 post-cycle success-receipt defect repaired at `7e4345b...` with adversarial takeover test | CHANGES_REQUIRED pending independent execution | source-level repair looks correct; single POSIX host scope remains explicit |
| SB-V03-005 | 4 | PARTIAL | state split; persona facade; production-path tests; `_reconcile` admin boundary | CHANGES_REQUIRED | ordinary raw runtime APIs (`publish_queue`, `events_for`, content history/direct readers) remain structurally callable; narrow admin/internal API repair required |
| SB-V03-006 | 3 | PREPARED | regenerated at `b2083b8...` from `7e4345b...`; worker reports 127; focused evidence says `full: OK` | BLOCKED | regenerate after final V03-005 repair and include exact full-suite output/count |
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

## LEAD-025 focused lessons

### Fencing repair quality improved, but independent execution still matters

The worker responded well to a narrow SP5 defect contract. `7e4345b...` fences completion evidence and includes the exact adversarial takeover scenario. For lifecycle/fencing artifacts, keep source inspection plus an independent execution layer before final acceptance when practical.

### Production-path tests do not automatically create a structural API boundary

V03-005 demonstrates correct scoped behavior through the chosen facade and real paths, but ordinary whole-runtime functions remain callable. The artifact contract explicitly requires an admin/internal boundary, so naming/API structure must match the policy rather than relying on comments and caller discipline.

### Evidence bundles should capture exact test output, not only an OK summary

The regenerated V03-006 bundle binds hashes and records focused suites plus `full: OK`, but does not carry a separate full-suite output/count file. Final acceptance evidence should make the 127-test claim reproducible from committed evidence rather than prose alone.

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
- admin/raw reader structural separation;
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
- Windows Core: narrow V03-005 structural reader-boundary repair, then final V03-006 regeneration;
- Intelligence: source-stalled, explicitly assigned V05 now then V15;
- Mac QA: hourly-authorized but stale; must independently execute/probe the repaired Core branch;
- dedicated local V0.4 canary: Priority Zero, still no worker activity;
- `worker-pc`: runner/control plane works, but Social Bots repository clone/auth remains broken after a second failed attempt.

Official version remains V0.3.x until artifact gates clear.
