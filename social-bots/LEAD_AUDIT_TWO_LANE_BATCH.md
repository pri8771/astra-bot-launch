# Lead audit — Core + Intelligence two-lane batch

Audit date: 2026-09-20 (America/New_York)
Lead: ChatGPT
Project: Social Bots

## Audited worker heads

- Core: `claude/social-bots-core-to-v2@874b6992fb4fff3e4832dcb8ae078828525f6a51`
- Intelligence: `claude/social-bots-intelligence-to-v2@3d249ec885706380a6a12934042ed03c1e15b831`

GitHub combined-status checks at both heads: none. Worker test counts remain local evidence and source/tests were inspected independently by the lead.

## Summary

Both worker sessions completed substantial bounded work and respected the two-lane ownership model.

The batch is useful, but it does **not** justify V1.7 or V2.0 engineering promotion yet.

Main reason: several artifacts implement good internal interfaces but still trust caller-asserted provenance/metrics/persona scope where the artifact contract requires evidence-backed behavior.

## Core verdicts

### SB-V03-003 — ACCEPTED

The missing forced fact-review and real voice-review failure regressions were added.

Verified direction:
- failure stops before experiment registration;
- failure stops before publish queue;
- worker completion is truthful non-success;
- cultural/platform gates remain fail-closed.

No new source defect found in this artifact.

### SB-V03-004 — CHANGES REQUIRED

The generation/fence design materially improves active-cycle ownership.

Good:
- same-host POSIX stale takeover is fenced;
- old lease generation cannot pass the fence after takeover;
- success side effects/state save are delayed to a fenced commit;
- adversarial expiry tests exist.

Remaining blockers:

1. `decision._commit()` writes `decisions.jsonl` and `last_decision.json` **after** `fence.fenced_commit()` returns, therefore outside the fence critical section. A worker that stalls after the fenced state/effect commit and later loses its lease can still resume and write diagnostic durable artifacts after fence loss.

2. The worker report calls the filesystem multi-write effect closure “all-or-nothing”. It is not transactional: experiment file/index, content history, queue, analytics, state etc. are multiple filesystem writes under mutual exclusion. A process/disk failure midway can leave a partial commit. This can be deferred to reliability/idempotency work, but the documentation must not claim transactionality.

3. Native Windows strong locking remains unimplemented/unproven. This is now actionable because an authorized Windows Claude environment is available.

Required repair:
- every worker-owned durable write for a cycle must be fenced, including decision log/latest decision;
- describe current guarantee as fenced mutual exclusion, not filesystem transaction;
- add native-Windows lock/fence implementation or prove an already-available POSIX/WSL deployment path on the Windows host.

### SB-V03-005 — CHANGES REQUIRED

Logical record filtering improved content/experiment/action/history separation, but private thinking/learning is still bot-wide.

Critical findings:

1. `BotState.data["hypotheses"]` is shared by every persona hosted on a runtime.
2. `consumed_signal_ids` is shared by runtime, so one persona consuming a captured signal prevents another persona workspace on the same runtime from independently considering it.
3. Core contextual reasoning uses total runtime hypothesis count when calculating novelty, so a cultural persona's learning can change the general persona's reasoning and vice versa.

This violates the intended durable persona workspace isolation.

Required architecture:
- shared read-only captured evidence may remain runtime-wide;
- each persona/workspace gets its own:
  - consumed/seen signal ledger;
  - hypotheses;
  - working state;
  - pending decisions;
  - strategy/audience-facing private memory;
- runtime-level recovery/worker/fencing state remains shared.

Preferred implementation: explicit `PersonaState` under the runtime, with physical or strongly typed logical persona scoping.

### SB-V04-001 — CHANGES REQUIRED

Good:
- provider seam exists;
- malformed/authority-smuggling proposals are rejected;
- no SwarmAI dependency.

Remaining:
- adaptive fail-closed posture is opt-in via `SBOTS_REASONING_REQUIRE_ADAPTIVE`; default runtime still permits baseline heuristics.
- no actual no-additional-spend adaptive provider is wired.
- lead schema includes CLOSE_EXPERIMENT; current action vocabulary does not.

V0.4 deployment posture must default to fail-closed when adaptive reasoning is required. Baseline/contextual providers may remain explicit test/debug modes.

### SB-V04-002 — CHANGES REQUIRED

The new contextual provider is useful deterministic contextual scoring and should be retained as a test/fallback analysis helper.

It is explicitly `adaptive=False`, therefore it does **not** satisfy the V0.4 adaptive-reasoning artifact.

Required:
- actual adaptive provider route;
- preferably existing-subscription Claude Code CLI adapter if host verification passes;
- materially different proposals from real provider output;
- fail closed on auth/quota/provider/schema failure.

### SB-V04-003 — ACCEPTED

The deterministic effect/authority boundary is well separated:
- provider recommendation is advisory;
- output schema is validated before execution;
- unsupported/authority-smuggling actions fail closed;
- public posting/spend/messaging remain outside local authority.

Future experiment actions may extend the vocabulary/executor, but the current policy boundary itself is accepted.

## Intelligence verdicts

### SB-V05-001 — CHANGES REQUIRED

The collector improves provenance, but operational “live” status is still forgeable by caller construction.

A caller can implement a custom Fetcher with `mode="live"` and return caller-provided bytes; Collector will mark it `live-capture`.

Also:
- live HTTP path currently accepts arbitrary URLs, including potentially loopback/private/link-local destinations; model/provider supplied URLs could create SSRF/local-network access.
- extraction failure leaves transport status OK; downstream evidence needs an explicit extraction validity state.

Required:
- operational-live provenance must come only from trusted collector-owned live transports, not arbitrary caller-declared fetcher mode;
- restrict operational HTTP(S) capture to safe public destinations and validate redirects/final destination;
- add extraction_status and prevent failed extraction from being used as extracted factual support.

### SB-V05-002 — CHANGES REQUIRED

The module is a good evidence-binding ledger, but it does not actually determine support.

`ClaimBinding.stance` is caller-supplied. A caller can label unrelated evidence `supports`, and the module will classify the claim SUPPORTED.

Required:
- support classification must come from an attributable support assessor/reviewer;
- store evidence excerpt/span/hash and reviewer identity/version;
- operational path fails closed when support assessor is unavailable;
- explicit caller stance may remain a test fixture/input, never operational proof.

### SB-V13-001 — CHANGES REQUIRED

Missing-vs-zero and raw metric retention are good.

Critical lead constraint was not implemented:
- metrics do not declare semantic kind: cumulative_snapshot / delta / gauge / rate;
- `aggregate_semantic()` sums all PRESENT observations;
- cumulative snapshots of 100 then 150 therefore become 250.

Required:
- raw/normalized metrics declare semantic kind;
- semantic-aware aggregation;
- cumulative snapshots are latest-value or explicitly differenced only against comparable earlier snapshots;
- no naïve cumulative summation.

### SB-V14-001 — CHANGES REQUIRED

Good evidence/decay concepts, but isolation and privacy need repair.

Findings:
1. persistence path is bot-wide `memory/<bot>/audience`; Hypothesis has no persona/workspace field.
2. sensitive-segment protection is a blacklist of exact strings; variants such as `religious_interest`, `health_interest`, etc. can bypass it.
3. `fork_hypothesis()` turns all evidence contradicting hypothesis A into positive support for arbitrary new statement B; contradiction of A does not prove B.

Required:
- persona/workspace-scoped storage and identity;
- allowlist safe segment dimensions instead of sensitive-key blacklist;
- a fork begins as a competing proposal motivated by contradictions, but does not inherit contradiction evidence as positive support unless separately assessed.

### SB-V15-001 — CHANGES REQUIRED

Lifecycle semantics are directionally good:
- observation-window gate;
- missing => INCONCLUSIVE;
- duplicate experiment detection.

But baseline/treatment are arbitrary caller dictionaries with no required normalized-observation/evidence references.

Required:
- baseline and treatment measurements bind to SB-V13 observations/evidence refs;
- semantic metric compatibility/window validation;
- learning ref traces through the actual measurement observations.

### SB-V16-001 — CHANGES REQUIRED

Repair/no-truncation behavior is good.

Findings:
- fact segments require only a non-empty `binding_ref`; the binding is not validated as an accepted SB-V05-002 ClaimSupportResult.
- `record_variant()` writes bot-wide history without persona field, conflicting with persona isolation and future V1.6 learning.

Required:
- validate factual segment binding status/reference;
- record persona/workspace scope in content-intelligence history and novelty checks.

### SB-V12-001 — ACCEPTED AS ENGINEERING MODULE

The ranking engine honestly distinguishes unavailable/unsuitable/exploratory paths and does not invent missing history.

Acceptance is for the isolated ranking module only. Operational selection remains dependent on validated account availability and corrected V13 metric inputs.

### SB-V17-001 — CHANGES REQUIRED

Read/effect separation is good and there is no public response implementation.

But:
- `source="read-only-evidence"` is caller-asserted rather than tied to a capture/platform receipt;
- community memory and themes are bot-wide rather than persona/workspace-scoped;
- theme evidence can therefore mix cultural/general community observations on one runtime.

Required:
- evidence receipt/reference required for operational read-only signal;
- persona/workspace-scoped community memory and theme aggregation.

### SB-V20-002 — CHANGES REQUIRED

The allocation math is useful, but the evaluator accepts arbitrary caller-provided `performance`, `audience_support` and opaque evidence refs.

That allows fabricated numeric inputs to drive growth recommendations.

Required:
- typed adapters/constructors from accepted NormalizedMetricObservation, ExperimentRecord and AudienceHypothesis artifacts;
- validate evidence refs and freshness;
- arbitrary raw numeric construction remains test-only;
- missing/stale/invalid evidence yields learning/no-recommendation rather than growth ranking.

## Version conclusion

Verified project version remains **V0.3.x** because V03-004 and V03-005 remain open.

Useful scaffolding now exists far ahead into V1.7/V2.0, but milestone promotion remains artifact/evidence gated.

No public effects, spend, purchases, messages or SwarmAI dependency were observed in this audit.
