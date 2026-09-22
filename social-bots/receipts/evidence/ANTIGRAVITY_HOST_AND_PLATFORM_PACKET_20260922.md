# Persistent-Host and Platform Routes Evidence Packet — 2026-09-22

**Author**: Antigravity (Social Bots Implementation Finisher)  
**Target Milestone Chain**: V0.7 (Persistent Scheduler) → V0.8 (Platform Routes) → V1.7 (Live Finish)  
**Authority Boundary**: Engineering analysis & dependency-safe preparation only. **Zero scheduler mutations, zero live account actions, zero spend, zero network/model calls.**

---

## 1. Persistent Host Assessment (V0.7 Prerequisite)

### Current Host Telemetry & Preflight State
- **Observed Host**: `Apple-M5-Pro-87` (macOS 15.6 Darwin 25.6.0 arm64)
- **Preflight Receipt**: `social-bots/receipts/evidence/CODEX_MAC_HOST_PREPARE_20260922/HOST_PREFLIGHT.json`
- **Verdict**: `INCONCLUSIVE_NEED_OWNER_CONFIRMATION`
- **Suitability for Live Scheduler**: `false` (`suitable_for_v07_live_scheduler: false`, `live_claim: false`)

### Blocking Gaps for V0.7 Acceptance
Per `delivery/V17_ACCEPTANCE.md`, milestone V0.7 requires:
1. **Persistent Host Attestation**: Owner confirmation that this host is an always-on, persistent environment (not an interactive laptop that sleeps/disconnects during scheduled intervals).
2. **Durable Deployment Path**: Dedicated repo path outside `/tmp` (as `/tmp` is wiped on reboot/purge).
3. **Scheduler Registration & Readback (`SB-R07-073`)**: Clean `launchd` registration via `scheduling/macos/install_launchd.sh` verified by `launchctl print gui/$(id -u)/com.socialbots.workeronce.<lane>`.
4. **Three Real Scheduler Firings (`SB-R07-074`)**: At least three distinct scheduled firings across ≥2 intervals, evidenced by:
   - Appends to `HEARTBEAT_LOG.jsonl`
   - Matching `"open"` and `"close"` phase entries in `$SBOTS_HOME/invocations/index.jsonl`
   - Valid exit codes (`0`, `3`, or `5`)
5. **Recovery & Lease Contention (`SB-R07-071`)**: Proof of crash recovery, stale lease takeover, and double-invocation suppression (`IgnoreNew` / `flock`).

*Strict Safety Notice*: Foreground manual runs or local CLI tests do NOT satisfy V0.7. No launchd agent has been registered or started.

---

## 2. Platform Routes Verification (V0.8 / V1.2 Prerequisite)

Per `delivery/V17_SCOPE.json`, five platform routes are strictly required: `["X", "Instagram", "TikTok", "Reddit", "Facebook"]`. None may be silently dropped.

| Platform | Route Schema / Code Status | Auth & Integration Status | Exact Blocker / Policy State |
|---|---|---|---|
| **X (Twitter)** | Implemented (`runtime/account_routes.py`, `runtime/platform_selection.py`) | API v2 client interfaces defined | **BLOCKED_COST_POLICY_CONFLICT**: X API basic tier requires paid monthly subscription. Directly conflicts with project zero-spend rule. Requires owner ruling on whether to authorize fee or approve alternative. |
| **Instagram** | Implemented & offline verified | Graph API / Threads protocol adapter | Awaiting owner credential binding outside Git. E1 live capture from Meta Threads verified. |
| **TikTok** | Implemented & offline verified | Content and display API adapters | E2 live capture from TikTok/Amplify verified. Account binding required. |
| **Reddit** | Implemented & offline verified | Script/OAuth application flow | Awaiting app client ID/secret outside Git. Read-only community endpoint verified. |
| **Facebook** | Implemented & offline verified | Meta Pages API adapter | Awaiting page access token outside Git. |

### Public Effect & Community Scope Boundary
- **V1.7 Community Surface**: Permitted read-only community observation, context ingestion, internal decision-making, and reviewed reply draft generation.
- **Out of Scope / Unauthorized**: Automated dispatch of live replies, comments, or direct messages. Live public effects require independent, explicit owner canary authorization (`G-PUBLISH` / `G-MEASURE`).

---

## 3. Evidence Integrity

- **E1 Capture**: Meta Threads live capture (Sept 16, 2026), raw SHA `2d51040128376b474391f4527c326d0d62255f61ce55da4fc0d1e334db2dc3b6`, publisher whitespace preserved byte-for-byte.
- **E2 Capture**: TikTok/Amplify live capture (Sept 14, 2026), raw SHA `72aefb0b9d06e72f08e10a12e18df6d81108ce430f0b7a5ffec941c31c410cce`.
- No simulated data or mock receipts masquerade as live evidence.
