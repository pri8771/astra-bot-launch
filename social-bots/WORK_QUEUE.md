# Work queue

This is the execution view of the artifact registry. `ARTIFACT_INDEX.json` is the durable machine-readable artifact state; `artifact-packets/` contains bounded execution contracts.

Lead acceptance is evidence-gated. Claude submissions and local test claims do not self-close artifacts.

## Team execution mode — target V2.0 engineering-ready

Lead plan:
- `EXECUTION_TO_V2_TODAY.md`
- `TEAM_LANES.md`
- `STRATEGIC_CHECKPOINTS.md`

Two worker lanes:
- **Claude Core** — branch `claude/social-bots-core-to-v2`
- **Claude Intelligence** — branch `claude/social-bots-intelligence-to-v2`

Workers do not directly own canonical artifact/state files. They submit source/tests/evidence; ChatGPT lead reconciles canonical acceptance.

### Claude Core — current chain
1. Repair `SB-V03-003`.
2. Repair `SB-V03-004`.
3. Repair `SB-V03-005`.
4. Produce `SB-V03-006`.
5. Repair/complete `SB-V04-001`.
6. Implement `SB-V04-002` / `SB-V04-003` / V0.4 acceptance.
7. Continue worker/reliability artifacts and `SB-V20-001` as dependencies clear.

### Claude Intelligence — safe parallel chain
1. `SB-V05-001` — READY: machine-captured source collector.
2. `SB-V13-001` — READY: normalized analytics brain.
3. Continue `SB-V05-002`, `SB-V14-001`, `SB-V15-001`, `SB-V16-001`, `SB-V17-001`, `SB-V20-002` as dependencies clear.
4. Do not present fixtures as operational evidence and do not edit Core-owned runtime files without lead reassignment.

Today's lead target is `SB-V20-099` V2.0 engineering readiness. Operational V2.0 remains separately evidence-gated.

## Current gate — V0.3.x correctness

Implementation reviewed: PR #2 head `2cab7219edab5c2f3a7123fad1546f43a2fc140c`.

### ACCEPTED

- `SB-R0A1` -> `SB-V03-002` — signal-delta consumption correctness — **SP3**.
  - Lead inspected per-signal consumed ledger and later/batch/restart regressions.
  - No new work unless a later defect reopens the artifact.

### CHANGES REQUIRED — execute in this order

1. `SB-R0A2` -> `SB-V03-003` — required-review stop gate — **SP2**.
   - Current code gate is directionally correct.
   - Add the packet-required forced fact-review failure regression.
   - Add the packet-required forced voice-review failure regression.
   - Prove both stop before experiment registration / publish queue and produce truthful non-success state.
   - Packet: `artifact-packets/SB-V03-003.md`.

2. `SB-R0B1` -> `SB-V03-004` — active-cycle lease fencing + stale takeover — **SP5**.
   - `flock` now serializes simultaneous acquisition/takeover on one POSIX host.
   - Remaining blocker: lease can expire while `decision.run_cycle()` is still executing; another worker can take over while the old worker retains the ability to commit.
   - Add real lifecycle fencing/renewal so an old owner cannot commit after fence loss.
   - Add an adversarial forced-expiry-while-running regression.
   - Do not paper over this with a larger TTL.
   - Explicitly document host/filesystem scope; native-Windows/cross-host strong fencing is not currently proven.
   - Packet: `artifact-packets/SB-V03-004.md`.

3. `SB-R0B2` -> `SB-V03-005` — shared-runtime persona concurrency/workspace isolation — **SP4**.
   - Runtime task key `cycle:<bot>` is directionally correct while a valid lease is held.
   - Acceptance depends on `SB-V03-004` lifecycle fencing.
   - Reconcile architecture claim vs code: docs say persona experiment/content/memory namespaces are isolated, but current `paths.py` and decision/pipeline storage are bot-scoped.
   - Either implement true persona-private non-shared namespaces or explicitly choose logical shared-store isolation and prove every read/filter path prevents cross-persona contamination.
   - Packet: `artifact-packets/SB-V03-005.md`.

4. `SB-R0B3` -> `SB-V03-006` — V0.3 adversarial acceptance bundle — **SP3**.
   - Status: BLOCKED until `SB-V03-003`, `SB-V03-004`, and `SB-V03-005` are lead-accepted.
   - Regenerate evidence from the accepted implementation; do not reuse superseded buggy proof as current acceptance.
   - Packet: `artifact-packets/SB-V03-006.md`.

## Worker evidence / heartbeat

`SB-EVD-001` remains CHANGES REQUIRED.

Verified latest committed in-session heartbeat:
- `heartbeat_at=2026-09-20T23:24:34+00:00`
- `status=done`
- `host_alias=local`
- worker `w-vm-2114-3ba847`

This proves another bounded invocation only. It does **not** prove recurring/always-on host liveness.

No GitHub Actions workflow run exists for PR #2 head `2cab7219`; Claude's reported `38 passing` remains worker-local evidence.

## V0.4 — Core integration locked until V0.3 acceptance bundle

Claude Core must not materially advance shared V0.4 integration source while V0.3 repair artifacts are under review.

Claude Intelligence may prebuild explicitly independent artifacts marked READY in ARTIFACT_INDEX.json when they do not touch Core-owned files or claim early milestone promotion.

Prepared next artifacts once dependencies clear:
- `SB-R1B` -> `SB-V04-001` — reasoning-provider interface + fail-closed contract — **SP3** — packet: `artifact-packets/SB-V04-001.md`.
- `SB-R1C` -> `SB-V04-002` — adaptive alternative generation/scoring — **SP5**.
- `SB-R1D` -> `SB-V04-003` — deterministic policy boundary — **SP4**.
- `SB-R1E` -> `SB-V04-004` — persona/evidence-divergence acceptance suite — **SP3**.

Safe independent work while current source is under lead audit:
- exact-source reuse reconciliation;
- read-only future artifact design/readback;
- architecture risk analysis;
- test/acceptance preparation that does not alter reviewed runtime source.

## Later prepared backlog

### V0.5
- `SB-R2A` -> `SB-V05-001` — machine-captured source receipt collector — **SP3** — packet prepared.
- `SB-R2B` -> `SB-V05-002` — claim-to-source factual support review — **SP4**.
- `SB-R2C` — platform-native formatter/repair loop — **SP3**.
- `SB-R2D` — cultural-review evidence binding — **SP2**.

### V0.6
- `SB-R3A` — three real general-persona dry runs — **SP3**.
- `SB-R3B` — independent reviewer receipt pipeline — **SP2**.
- `SB-R3C` — dry-run evidence validator — **SP2**.

### V0.7
- `SB-R4A` -> `SB-V07-001` — authorized-host worker packaging/config — **SP3**.
- `SB-R4B` -> `SB-V07-002` — recurring host execution + heartbeat proof — **SP4**.
- `SB-R4C` — ChatGPT-direction consumption/ack loop — **SP3**.
- `SB-R4D` — crash/restart/no-overlap host acceptance — **SP4**.

### V0.8 preparation

Lead research `SB-ACC-008` is accepted. Account/browser artifacts remain externally gated; no login, key creation, account connection, spend, or posting is authorized by this queue.

## Persistent authority limits

No public posting, public deployment, customer/user messaging, purchases, paid APIs, additional spend, destructive actions, credential material, fake connectivity/metrics, quota evasion, or engagement manipulation without explicit owner authorization.

Social Bots remains fully independent of SwarmAI.


## Strategic checkpoint backlog

### V1.7
Required engineering chain:
- `SB-V11-001/002` reliability.
- `SB-V12-001/002` platform selection.
- `SB-V13-001/002` analytics.
- `SB-V14-001/002` audience memory.
- `SB-V15-001/002` experiment engine.
- `SB-V16-001/002` content intelligence.
- `SB-V17-001/002/003` community checkpoint.

### V2.0 today's target
- `SB-V20-001` strategy revision engine — Core.
- `SB-V20-002` growth evaluator/allocation — Intelligence.
- `SB-V20-003` measured-evidence strategy-change acceptance — lead integration.
- `SB-V20-099` engineering-readiness bundle — lead acceptance target.
- `SB-V20-004` operational acceptance remains BLOCKED until real public/account/measurement evidence is authorized and observed.

### V2.3 next strategic checkpoint
- `SB-V21-001` dynamic strategy lifecycle.
- `SB-V22-001` goal decomposition.
- `SB-V23-001/002/003` temporary specialist workers.

### V3.0
- `SB-V30-001..005` portfolio/multi-brand organization.
