# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current lead review: `LEAD-020` (`lead-reviews/LEAD-020_2026-09-20T2251.md`). Foundational deep audits remain LEAD-015/017/019.

Current verified worker/source activity:
- Windows Core/Host: standby at implementation head `5318065aad6e38de1e3313ad984d09451a2dfcb7`.
- Intelligence: signed repair progress through `feb30f4c3fd00ae1fa0bb115a92bdb767ae9f67d`; latest worker reports 185 local tests.
- Mac QA/control: signed progress through `ede387e256be19d6aaaf1e6c96151d7218221d33`; GitHub-hosted `social-bots-ci` run `35555060783` independently verified SUCCESS.

Heartbeat quality is tracked separately from implementation quality. Neither target Mac lane has passed the 3x approximately-15-minute durable heartbeat bootstrap; burst submission heartbeats and snapshot-only sequence advancement do not count.

## Current observations

The SP2–SP5 sample continues to support worker-first implementation with strong lead review at trust/isolation boundaries.

- SP2 bounded control work is strong when the contract is explicit. `SB-CTL-006` CI was accepted after real GitHub-hosted execution.
- SP3 bounded engineering can pass cleanly (`SB-V03-002`) but trust/transport boundaries remain a recurring failure mode: `SB-V05-001` fixed caller-grantable trust yet independent review found the actual HTTPS connection constructor is invalid for stdlib `HTTPSConnection`.
- SP4 work has improved substantially after targeted repair. `SB-V13-001` and `SB-V14-001` both closed earlier semantic/privacy findings and are accepted. `SB-V15-001` fixed measurement provenance but still exposes bot-wide production experiment readers, showing cross-cutting isolation must be tested at the actual read API, not just the record model.
- SP5 fencing remains the highest-risk Core area. `SB-V03-004` is still CHANGES_REQUIRED under LEAD-019 because legacy migration can durably write before the final ownership fence.

This still supports Claude as the implementation workhorse. The lead should keep decomposing SP4/SP5 work into narrow contracts and independently test production-path trust/isolation/fencing invariants.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> worker added forced FACT + VOICE failures | ACCEPTED | good bounded repair behavior |
| SB-V03-004 | 5 | PARTIAL | generation fencing and final fenced commit improved; LEAD-019 found side-effectful legacy migration durable writes before the final fence | CHANGES_REQUIRED | host portability is separate V07 proof; migration ownership defect remains V03 correctness |
| SB-V03-005 | 4 | PARTIAL | RuntimeState/PersonaState split fixed primary private mutable state; authoritative persona-scoped production reads + crash-safe migration still required | CHANGES_REQUIRED | do not regress state split |
| SB-V03-006 | 3 | BLOCKED | depends on accepted V03-004/V03-005 | BLOCKED | regenerate only after repair |
| SB-V04-001 | 3 | PARTIAL | production fail-closed posture implemented on worker branch but milestone still dependency-gated | CHANGES_REQUIRED | real acceptance also needs canary chain |
| SB-V04-002 | 5 | PARTIAL | real Claude CLI adapter exists; injected tests prove interface but no real subscription call accepted yet | CHANGES_REQUIRED | `SB-V04-005` is mandatory real proof |
| SB-V04-003 | 4 | PASS-LIKE source review | dependency unresolved | BLOCKED | deterministic authority boundary looks sound |

## Intelligence lane task results

| Artifact | SP | First submission | Independent review finding / repair cycles | Current lead disposition |
|---|---:|---|---|---|
| SB-V05-001 | 3 | PARTIAL | multiple trust repairs closed self-registration and DNS pinning concept; LEAD-020 found actual HTTPS live path invalid because `HTTPSConnection(..., server_hostname=...)` is unsupported | CHANGES_REQUIRED |
| SB-V05-002 | 4 | PARTIAL | now fails closed with static empty operational assessor policy; diagnostic keyword/heuristic paths no longer claim operational authority | CHANGES_REQUIRED | accepted adaptive semantic provider + working trusted live evidence still required |
| SB-V13-001 | 4 | FAIL first acceptance invariant | repair added metric kinds, latest snapshot semantics, known-kind-on-missing, overlap-safe deltas and derivation provenance | ACCEPTED | strong repair cycle; fixture-labelled engineering evidence only |
| SB-V14-001 | 4 | FAIL first isolation/privacy invariant | repair added bot+persona persistence, safe segment allowlist, compound sensitive-trait rejection, same-persona forks | ACCEPTED | strong repair cycle; production private memory boundary now explicit |
| SB-V15-001 | 4 | PARTIAL | measurement provenance repaired; remaining bot-wide experiment persistence/read API can expose another persona through normal readers | CHANGES_REQUIRED | next repair: authoritative bot+persona readers/writers |
| SB-V16-001 | 4 | PARTIAL | latest repair submitted but not yet independently source-audited to acceptance in LEAD-020 | CHANGES_REQUIRED |
| SB-V12-001 | 3 | PASS-LIKE source review | V13 prerequisite now accepted, but operational availability inputs remain acceptance-gated | BLOCKED |
| SB-V17-001 | 4 | PARTIAL | latest receipt/persona-scope repair submitted but not independently accepted yet | CHANGES_REQUIRED |
| SB-V20-002 | 4 | PARTIAL | latest typed evidence/persona repair submitted at `feb30f4c...`; pending independent source audit and V15 dependency repair | CHANGES_REQUIRED |

## QA/control lane task results

| Artifact | SP | First submission | Independent evidence | Current lead disposition |
|---|---:|---|---|---|
| SB-CTL-012 | 3 | PASS | source reviewed; 18 validator regressions; structural failures hard-error; V2 engineering/operational readiness separated | ACCEPTED |
| SB-CTL-006 | 2 | PASS | workflow source reviewed; read-only token; no secrets/model/deploy; GitHub-hosted run `35555060783` succeeded | ACCEPTED |
| V2 acceptance harness prep | n/a | PASS-LIKE | 20 harness tests / 38 total reported; non-runtime assertion layer | PREP ONLY | does not promote SB-V20-099 |

## LEAD-020 focused lessons

### Heartbeat evidence must be append-only and time-real

A worker snapshot saying sequence 4 is not four heartbeats if the durable history contains only sequence 0. Likewise four submission updates in seven minutes do not prove a 15-minute recurring loop. Future bootstrap acceptance must inspect `HEARTBEAT_LOG.jsonl` timestamps and reject backfilled/burst evidence.

### Test the actual trusted transport constructor

Security architecture can look correct while the real operational path is unusable. `SB-V05-001` now has a strong static trust model and pinning concept, but its HTTPS constructor call is invalid. At least one test must exercise the production transport-construction path rather than only overridden/stubbed helpers.

### Persona isolation must cover readers, not only records

Adding a `persona` field is insufficient if normal persistence/list/read APIs stay bot-wide. Every SP4+ artifact that stores private workspace state must expose an authoritative persona-scoped production boundary and mixed-persona regression tests through that boundary.

### Independent CI meaningfully improves evidence quality

`SB-CTL-006` is the first independently verified GitHub-hosted Social Bots CI control. Worker-local suites remain useful, but hosted CI now gives a stronger baseline for branches that consume the workflow.

## Recurring defect themes

### Trust / operational provenance
- no caller self-registration of operational trust;
- fixture/untrusted evidence must never be silently upgraded;
- operational semantic authority must fail closed when unavailable;
- real network/provider paths require at least one path-level acceptance proof.

### Persona/workspace isolation
- storage scope;
- read/list scope;
- migration scope;
- cross-persona import must be explicit, not an accidental helper parameter.

### Dependency discipline
Workers may build additive scaffolding ahead of promotion, but downstream status stays blocked until prerequisites are accepted. `SB-V20-099` is not promoted by a harness or local tests alone.

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
- production-path vs fixture-only acceptance evidence.

Do not infer worker quality from one artifact. Current evidence supports high Claude throughput with adversarial lead review focused on trust, isolation, migration, host boundaries and real-operation proof.

## Current concurrency implication

Keep the current ceiling:
- Intelligence repair implementation active;
- Mac QA/control heartbeat validation active;
- Windows Core/Host standby by owner/lead.

Do not start a fourth worker. Priority Zero after valid Mac QA heartbeat bootstrap is the real V0.4 canary.
