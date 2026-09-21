# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current lead review: `LEAD-027` (`lead-reviews/LEAD-027_2026-09-21T0354.md`). Foundational deep audits remain LEAD-015/017/019/020/023/024/025/026.

## Current verified worker/source activity

- Windows Core/Host: signed implementation `796d4e390bd135167e5de2ff8f586bc07ac7f370` closes the final SB-V03-005 structural raw-reader escape. Evidence commit `436787b0a63fdae0e89c224a54054607e32b5187` regenerates V03-006 and commits exact full-suite output: **130 tests, OK**. Later worker heartbeat `1fed0684...` waits for lead audit.
- `SB-V03-005`: **ACCEPTED in LEAD-027** after multiple narrow repair cycles. The worker ultimately converted the remembered-example fixes into an exhaustive six-store persona/admin boundary and added a structural guard designed to fail if bare whole-runtime reader names return.
- `SB-V03-004`: source-level repair still looks correct; no new defect found. It remains CHANGES_REQUIRED solely because the packet requires independent lifecycle execution and Mac QA has not returned it.
- Intelligence: latest worker commit remains heartbeat seq7 `a7bdeb4c0f0d2c1a3107798327266812a9644d27` at `04:10:36Z`; no V05-001/V15-001 source repair. Hourly remains unauthorized.
- Mac QA/control: hourly coordination cadence is accepted, but the last worker heartbeat remains seq10 at `03:57:57Z`. No independent V03-004 execution report has landed; this lane is now the V0.3 gating executor.
- V0.4 live-canary lane: no Claude worker execution commit exists; branch remains lead-only assignment evidence.
- External `worker-pc`: latest Social Bots audit reached the real Windows runner but failed at repository clone before Claude/tests. Zero acceptance evidence; do not redispatch until access is fixed.

Heartbeat quality is tracked separately from implementation quality. Mac-QA coordination bootstrap is accepted; Intelligence remains bootstrap. Neither proves V0.7 recurring Social Bots runtime liveness.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> forced FACT + VOICE failures | ACCEPTED | bounded repair behaved well |
| SB-V03-004 | 5 | PARTIAL | acquisition/final-commit repair -> migration repair -> post-cycle success-receipt repair | CHANGES_REQUIRED pending independent execution | source-level implementation is stable; single POSIX host scope explicit |
| SB-V03-005 | 4 | PARTIAL | state split -> persona facade -> production paths -> queue/analytics admin names -> LEAD-026 found content_history escape -> `796d4e3` exhaustive six-store/admin repair | **ACCEPTED** | strong example of SP4 needing adversarial/exhaustive boundary review before convergence |
| SB-V03-006 | 3 | PREPARED | final regeneration `436787b...` from `796d4e3...`; exact `FULL_SUITE_OUTPUT.txt` shows 130 tests OK | BLOCKED / final prepared | waits on V03-004 independent acceptance and final lead reconciliation, not another known source repair |
| SB-V04-001 | 3 | PARTIAL | production fail-closed posture exists; needs fresh current-branch audit after V03 closure | CHANGES_REQUIRED | Core now assigned dependency-safe reconciliation/tests |
| SB-V04-002 | 5 | PARTIAL | Claude CLI adapter exists; injected tests are engineering-only; no real subscription run accepted | CHANGES_REQUIRED | `SB-V04-005` mandatory live proof |
| SB-V04-003 | 4 | PASS-LIKE source review | dependency unresolved | BLOCKED | deterministic authority boundary remains promising |

## Intelligence lane task results

| Artifact | SP | First submission | Independent review finding / repair cycles | Current lead disposition |
|---|---:|---|---|---|
| SB-V05-001 | 3 | PARTIAL | trust repairs closed self-registration/DNS concept; LEAD-020 found actual HTTPS constructor path invalid; FAST TRACK repair still absent | CHANGES_REQUIRED |
| SB-V05-002 | 4 | PARTIAL | static/fail-closed assessor posture improved; still dependent on working trusted live evidence/adaptive semantic path | CHANGES_REQUIRED |
| SB-V13-001 | 4 | FAIL first acceptance invariant | repaired metric kinds, latest-snapshot semantics, overlap-safe deltas, provenance | ACCEPTED |
| SB-V14-001 | 4 | FAIL first isolation/privacy invariant | repaired bot+persona persistence and sensitive-segment controls | ACCEPTED |
| SB-V15-001 | 4 | PARTIAL | measurement provenance repaired; bot-wide normal experiment persistence/read boundary remains | CHANGES_REQUIRED |
| SB-V16-001 | 4 | PARTIAL | latest repair submitted but not independently accepted | CHANGES_REQUIRED |
| SB-V12-001 | 3 | PASS-LIKE source review | operational availability/authority acceptance unresolved | BLOCKED |
| SB-V17-001 | 4 | PARTIAL | latest receipt/persona-scope repair submitted but not independently accepted | CHANGES_REQUIRED |
| SB-V20-002 | 4 | PARTIAL | typed evidence/persona repair submitted; pending V15 repair + independent audit | CHANGES_REQUIRED |

## QA/control lane task results

| Artifact | SP | First submission | Independent evidence | Current lead disposition |
|---|---:|---|---|---|
| SB-CTL-012 | 3 | PASS | source reviewed; structural graph failures hard-error; V2 engineering/operational distinction retained | ACCEPTED |
| SB-CTL-006 | 2 | PASS | read-only workflow + real GitHub-hosted run `35555060783` succeeded | ACCEPTED |
| Coordination heartbeat bootstrap | n/a | early burst/snapshot issues | later durable Mac-QA intervals accepted; Intelligence seq7 misses cadence | PASS Mac QA / FAIL-PENDING Intelligence | coordination proof only |
| V2 acceptance harness prep | n/a | PASS-LIKE | non-runtime assertion layer | PREP ONLY | cannot promote SB-V20-099 |
| Independent SB-V03-004 lifecycle execution | n/a | ASSIGNED / STALLED | Mac QA has not run the current repaired SHA; worker-pc clone failed | **PENDING / V0.3 GATE** | exact command/result required before V03-004 acceptance |

## LEAD-027 lessons

### SP4 isolation converged after exhaustive contract testing

SB-V03-005 took several repair cycles because each earlier iteration fixed the specifically named escape while leaving another ordinary whole-runtime reader. The final `796d4e3` repair is materially better because the regression encodes the whole contract: all six persona-private stores must have sanctioned persona readers, raw enumeration must be explicit admin/internal, and bare reader names are structurally prohibited. This is the preferred pattern for future trust/isolation work.

### Exact evidence capture is now good

`436787b...` preserves the improved evidence discipline: verbatim full-suite output is committed and shows 130 named tests with `OK`, rather than relying on prose. Preserve this pattern.

### Independent execution is a real gate, not ceremony

V03-004 is not being withheld for another known source defect. It is withheld because lifecycle fencing is high-risk and the packet explicitly requires a separate executor to run the adversarial takeover cases. Do not silently lower this bar because QA is stale.

### Worker inactivity is now the main throughput defect outside Core

Core is producing and converging. Intelligence has dependency-ready V05/V15 work but no worker source progress since seq7. Mac QA is hourly-authorized but has not returned the gating independent run. The live-canary lane has no worker execution at all. Lead planning is not the missing input.

## Recurring defect themes

### Trust / operational provenance
- no caller self-registration of operational trust;
- fixtures/untrusted evidence cannot be upgraded to operational evidence;
- real network/provider paths need path-level proof.

### Persona/workspace isolation
- scope storage and read/list surfaces;
- enforce production call paths structurally;
- make complete admin/raw-reader separation machine-testable;
- cross-persona imports must be explicit.

### Fencing / lifecycle
- acquisition safety is insufficient;
- ownership must cover active work and completion evidence;
- migration helpers cannot durably bypass the fence;
- host/filesystem scope must be honest.

### Dependency discipline
Workers may build additive scaffolding ahead of promotion, but status remains dependency/evidence gated. `SB-V20-099` is not promoted by local tests/harness alone.

## Metrics to continue accumulating

For each SP level track attempts, first-pass acceptance, repair cycles, independent findings, dependency violations, escaped defects, final acceptance, GitHub-CI vs worker-local evidence, production-path vs fixture-only evidence, and coordination idle time.

## Current concurrency implication

FAST TRACK lanes:
- Windows Core: V03 implementation stable; use capacity on V04 reconciliation/tests while independent V03 gate runs;
- Intelligence: stale; V05 now then V15;
- Mac QA: stale but hourly-authorized; must run the independent V03-004 gate now;
- dedicated local V0.4 canary: Priority Zero, still no worker activity;
- `worker-pc`: runner/control plane works but Social Bots repo clone/auth remains broken.

Official version remains V0.3.x until artifact gates clear.
