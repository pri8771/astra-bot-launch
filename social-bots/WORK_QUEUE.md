# Work queue

This is the execution view of the artifact registry. Artifact-first management remains authoritative. Lead review `LEAD-014` is the current independent audit of both Claude lanes; `ARTIFACT_INDEX.json` must be reconciled to it before stale registry statuses are relied on.

## Team execution mode — target V2.0 engineering-ready

Two active worker lanes:
- **Claude Core** — `claude/social-bots-core-to-v2`
- **Claude Intelligence** — `claude/social-bots-intelligence-to-v2`

Fresh signed commits with Claude Code session metadata prove both development sessions are currently active. This is not V0.7 always-on Social Bots runtime proof.

No GitHub status checks exist at the verified lane heads; worker test counts remain local evidence. `SB-CTL-006` CI remains ready after V0.3 correctness stabilizes.

## Lead-accepted this review

- `SB-V03-003` — required-review stop gate — **SP2** — ACCEPTED.
  - Forced FACT failure and real VOICE failure both stop before experiment/queue/success/learning.
- `SB-V03-004` — active-cycle lease fencing — **SP5** — ACCEPTED for one POSIX host/local filesystem.
  - Generation fencing + atomic `Fence.fenced_commit` closes the old-owner-after-takeover defect.
- `SB-V05-001` — machine-captured source receipt collector — **SP3** — ACCEPTED as engineering artifact.
  - Fixture evidence stays fixture; operational live retrieval is not claimed.
- `SB-V03-002` remains ACCEPTED from prior review.

## Core — execute in this order

### 1. `SB-V03-005` — CHANGES_REQUIRED — SP4

Logical isolation is documented and helper filters exist, but they are optional. Raw bot-wide readers remain available, so persona-private non-shared records can still be consumed through a bypass path.

Repair contract:
- one authoritative persona-scoped read/repository boundary for private stores;
- production persona-specific reads use it;
- raw bot-wide readers are internal/admin-only or otherwise guarded;
- real production-path tests prove mixed shared-runtime stores cannot bleed across personas.

Packet: `artifact-packets/SB-V03-005.md`.

### 2. `SB-V03-006` — BLOCKED until V03-005 accepted — SP3

Regenerate the V0.3 acceptance bundle only from accepted implementation. Do not reuse superseded proof.

### 3. `SB-V04-001` — CHANGES_REQUIRED — SP3

Keep the new schema validation. Repair deployment/runtime posture:
- production changed-evidence mode intended to satisfy V0.4 requires adaptive reasoning by default;
- no adaptive provider => fail closed, evidence pending;
- baseline/contextual deterministic providers remain explicit `adaptive=false` test/diagnostic modes.

### 4. `SB-V04-002` — CHANGES_REQUIRED — SP5

`ContextualReasoningProvider` is useful but explicitly non-adaptive. It does not satisfy V0.4 real adaptive autonomy.

Next bounded work:
- preserve contextual provider as deterministic fallback/diagnostic;
- implement/verify the lead-researched no-additional-spend adaptive provider route only on an owner-authenticated target host;
- hard fail closed if `ANTHROPIC_API_KEY` is present so a paid API path cannot be selected accidentally;
- provider identity/runtime receipt must prove the adaptive path was actually invoked.

### 5. `SB-V04-003` — BLOCKED on V04-001; source review positive — SP4

Policy-boundary implementation appears aligned. Do not rework unless V04-001 repair exposes incompatibility.

### 6. `SB-CTL-006` — READY after V0.3 repair — SP2

Add GitHub Actions verification so future acceptance is not based solely on worker-local test reports.

## Intelligence — repair queue

### 1. `SB-V13-001` — CHANGES_REQUIRED — SP4 — highest priority

Current aggregation is unsafe for cumulative snapshots.

Required:
- semantic kind on metrics: cumulative_snapshot / delta / gauge / rate;
- semantic-aware aggregation;
- snapshots 100 -> 150 must not total 250;
- deltas 100 + 50 may total 150;
- snapshot-to-delta conversion only from comparable observations with explicit derivation/version metadata.

Packet updated.

### 2. `SB-V14-001` — CHANGES_REQUIRED — SP4

Audience hypotheses must be bot + persona/workspace scoped. Current bot-wide audience directory is insufficient.

Required regression: two personas sharing one runtime hold contradictory hypotheses without overwrite or read blending.

### 3. `SB-V05-002` — CHANGES_REQUIRED — SP4

Support classification is useful, but the artifact also requires identifying material factual claims in the candidate. Caller omission must not bypass review.

Add bounded claim-identification and omission-bypass tests.

### 4. `SB-V16-001` — CHANGES_REQUIRED — SP4

Content-intelligence history/novelty is bot-wide and lacks persona scope. Repair private history and duplicate/near-duplicate checks so cultural/general personas do not suppress each other.

### 5. `SB-V17-001` — CHANGES_REQUIRED — SP4

No-public-effect wall is good. Repair bot-wide community memory/theme aggregation so private community learning is persona/workspace scoped before feeding audience memory.

### 6. `SB-V20-002` — CHANGES_REQUIRED — SP4

Reconcile output to `CROSS_LANE_INTERFACES.md` after V13/V14 repair:
- bot/persona scope;
- required authority;
- operational availability;
- cost class;
- evidence refs and uncertainty;
- attention allocation only, never spend authority.

## Intelligence submissions with positive source review but dependency-blocked

- `SB-V12-001` platform selection — source review positive; BLOCKED on V13 repair.
- `SB-V15-001` experiment lifecycle — source review positive; BLOCKED on V13/V14 repair.

Do not churn these modules unless upstream interface repairs require it.

## Current milestone status

**Current version: V0.3.x.**

V0.3 still requires accepted `SB-V03-005` and regenerated/accepted `SB-V03-006` (plus manifest requirements already tracked).

V0.4 is not promoted: no accepted real adaptive provider route exists.

V1.7 is not accepted because V1.1–V1.6 acceptance chain is incomplete and V17 has a persona-scope defect.

`SB-V20-099` V2.0 engineering-readiness remains the day's target but is **not accept-ready**. `SB-V20-001` integration is not accepted/submitted and V20-002/upstream evidence semantics require repair.

Operational V2.0 remains separately BLOCKED on real account/public/measurement evidence and explicit authority.

## Persistent authority limits

No public posting, public response, customer/user messaging, purchases, paid APIs/additional spend, destructive actions, credential material, fabricated connectivity/metrics, quota evasion, engagement manipulation, or SwarmAI dependency.

## Next strategic runway after repairs

- V1.7 checkpoint acceptance.
- V2.0 strategy revision + growth evaluator integration and `SB-V20-099` engineering bundle.
- V2.1 dynamic strategy lifecycle.
- V2.2 autonomous goal decomposition.
- V2.3 temporary specialist workers.
- V3.0 multi-brand portfolio organization.
