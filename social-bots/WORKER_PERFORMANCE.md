# Claude worker performance

Purpose: measure Claude Code implementation reliability by story-pointed artifact packet and task type. Story points reflect complexity/uncertainty, not time. No worker submission self-accepts.

Current lead review: `LEAD-034` (`lead-reviews/LEAD-034_2026-09-21T1055.md`). Foundational deep audits remain LEAD-015/017/019/020/023/024/025/026/027/028; LEAD-029–034 are primarily liveness/evidence/capacity reconciliation reviews unless noted otherwise.

## Current verified worker/source activity

- Windows Core/Host: final V03 source remains `796d4e390bd135167e5de2ff8f586bc07ac7f370` with evidence `436787b0a63fdae0e89c224a54054607e32b5187` (**130 tests, OK**). Latest worker-generated signed implementation commit remains `76e96dde4677346fd5b40c8cba4988f6e4c64fee`; no corrected `SB-V04-004` worker submission has appeared.
- `SB-V03-005`: **ACCEPTED in LEAD-027** after multiple narrow repair cycles and exhaustive six-store persona/admin boundary hardening.
- `SB-V03-004`: source-level repair still looks correct; it remains CHANGES_REQUIRED solely because the packet requires independent lifecycle execution and neither Mac QA nor worker-pc has returned valid execution evidence.
- `SB-V04-004`: first worker attempt remains **CHANGES_REQUIRED**. Its named persona/evidence comparisons do not isolate the intended causal variable, and its provider is explicitly `adaptive=false`.
- Intelligence: latest worker activity remains heartbeat seq7 at `04:10:36Z`; no V05-001/V15-001 source repair. Historical hourly authorization remains false.
- Mac QA/control: historical coordination bootstrap is accepted, but the last worker heartbeat remains seq10 at `03:57:57Z`. No independent V03-004 execution report has landed.
- V0.4 live-canary lane: no Claude worker execution commit exists and no durable heartbeat log exists.
- External `worker-pc`: LEAD-034 re-dispatched a read-only V03 lifecycle audit after unrelated capacity cleared. Task `socialbots-v03-audit-retry-20260921-1052` / Actions run `35615370153` again failed at **repository clone** before Claude/tests. Zero acceptance evidence; repeated clone/auth failure is now a stable infrastructure defect, not a transient task failure.

Heartbeat quality is tracked separately from implementation quality. For the temporary 2026-09-21 soak, **none of the four active Claude lanes has yet produced a durable `FAST_5M` T0**. Historical heartbeat records are not relabeled and no backfill counts.

## Core lane task results

| Artifact | SP | First submission | Lead findings / repair cycles | Current lead disposition | Notes |
|---|---:|---|---|---|---|
| SB-V03-002 | 3 | PASS | 0 repair cycles | ACCEPTED | per-signal consumed ledger; later/batch/restart regressions |
| SB-V03-003 | 2 | PARTIAL | 1 lead gap -> forced FACT + VOICE failures | ACCEPTED | bounded repair behaved well |
| SB-V03-004 | 5 | PARTIAL | acquisition/final-commit repair -> migration repair -> post-cycle success-receipt repair | CHANGES_REQUIRED pending independent execution | source-level implementation stable; independent run still missing |
| SB-V03-005 | 4 | PARTIAL | state split -> persona facade -> production paths -> admin naming -> all-store guard | ACCEPTED | SP4 needed repeated adversarial boundary review |
| SB-V03-006 | 3 | PREPARED | final regeneration `436787b...` from `796d4e3...`; exact full suite 130 tests OK | BLOCKED / final prepared | waits on V03-004 + final V03 reconciliation |
| SB-V04-001 | 3 | PARTIAL | production fail-closed/adaptive-required posture improved | CHANGES_REQUIRED / source-positive | integrated adaptive evidence still open |
| SB-V04-002 | 5 | PARTIAL | Claude CLI adapter exists; injected tests engineering-only | CHANGES_REQUIRED | real `SB-V04-005` mandatory |
| SB-V04-003 | 4 | PASS-LIKE source review | dependency unresolved | BLOCKED | deterministic authority boundary promising |
| SB-V04-004 | 3 | FAIL acceptance design | `76e96dd` suite is confounded and uses `adaptive=false` contextual provider | CHANGES_REQUIRED / repair assigned | no corrected worker submission through LEAD-034 |

## Intelligence lane task results

| Artifact | SP | First submission | Independent review finding / repair cycles | Current lead disposition |
|---|---:|---|---|---|
| SB-V05-001 | 3 | PARTIAL | trust repairs improved; actual HTTPS constructor/path still invalid | CHANGES_REQUIRED |
| SB-V05-002 | 4 | PARTIAL | fail-closed assessor posture improved; still depends on trusted live/adaptive semantic evidence | CHANGES_REQUIRED |
| SB-V13-001 | 4 | FAIL first acceptance invariant | repaired metric kinds/latest-snapshot/overlap-safe deltas/provenance | ACCEPTED |
| SB-V14-001 | 4 | FAIL first isolation/privacy invariant | repaired bot+persona persistence and sensitive-segment controls | ACCEPTED |
| SB-V15-001 | 4 | PARTIAL | measurement provenance repaired; bot-wide normal experiment boundary remains | CHANGES_REQUIRED |
| SB-V16-001 | 4 | PARTIAL | latest repair submitted but not independently accepted | CHANGES_REQUIRED |
| SB-V12-001 | 3 | PASS-LIKE source review | operational availability/authority acceptance unresolved | BLOCKED |
| SB-V17-001 | 4 | PARTIAL | latest receipt/persona-scope repair submitted but not independently accepted | CHANGES_REQUIRED |
| SB-V20-002 | 4 | PARTIAL | typed evidence/persona repair submitted; pending V15 + independent audit | CHANGES_REQUIRED |

## QA/control and external verification results

| Work | Result | Independent evidence | Current lead disposition |
|---|---|---|---|
| SB-CTL-012 artifact validator | PASS | source reviewed; dependency/readiness hard errors | ACCEPTED |
| SB-CTL-006 CI | PASS | real GitHub-hosted run `35555060783` succeeded | ACCEPTED |
| Historical Mac-QA coordination heartbeat | PASS | durable ~15–17m sequence accepted | historical hourly authorized |
| Intelligence historical heartbeat | FAIL-PENDING | seq6→7 ~30m28s | hourly unauthorized |
| 2026-09-21 temporary heartbeat soak | NOT STARTED | zero durable `FAST_5M` T0 records on all four lanes | unproven, non-blocking |
| Independent SB-V03-004 Mac-QA lifecycle run | STALLED | no current report | PENDING / V0.3 gate |
| worker-pc Social Bots audit retry | FAIL | Actions `35615370153`; `Repository clone failed.` before Claude/tests | ZERO EVIDENCE; clone/auth repair required |
| V0.4 real canary | NOT STARTED | no worker-generated provider/source/decision receipt | Priority Zero |

## Current lessons

### Green tests are not artifact acceptance

The V04-004 submission showed that a suite can be entirely green while still failing the intended acceptance invariant because variables are confounded. Experimental design must be independently inspected.

### SP4/SP5 work needs adversarial review

Persona boundaries and lease/fencing work repeatedly converged only after independent review found lifecycle or structural bypasses. Continue decomposing implementation for Claude while preserving final integration acceptance.

### Trust and provenance require production-path proof

Fixtures and caller assertions cannot establish operational evidence. Real network/provider paths need path-level proof and collector-owned/provider-owned provenance.

### External worker infrastructure is not useful until repository access is real

`worker-pc` itself is online and proven on another private repository, but Social Bots tasks have repeatedly failed before Claude because `pri8771/astra-bot-launch` cannot be cloned. Do not keep consuming capacity with identical retries; fix clone/auth first.

### Heartbeat is observability, not delivery

Historical coordination heartbeats do not prove V0.7 runtime liveness, and today's temporary soak does not count until real durable `FAST_5M` entries exist. Heartbeat must run beside useful work, never instead of it.

## Metrics to continue accumulating

For each SP level track attempts, first-pass acceptance, repair cycles, independent findings, dependency violations, escaped defects, final acceptance, GitHub-CI vs worker-local evidence, production-path vs fixture-only evidence, coordination idle time, and external-worker infrastructure failures.

## Current concurrency implication

FAST TRACK lanes:
- Windows Core: V03 stable; repair V04-004 acceptance design while independent V03 gate runs;
- Intelligence: stale; V05 now then V15;
- Mac QA: stale; independent V03-004 gate now, then QA/integration;
- dedicated local V0.4 canary: Priority Zero, still no worker activity;
- `worker-pc`: no more Social Bots dispatch until clone/auth is demonstrably repaired.

Official version remains V0.3.x until artifact gates clear.
