# Antigravity — V0.4 to V0.7 Live Engineering Completion Report

**Date:** 2026-09-22  
**Author:** Antigravity (Social Bots Implementation Finisher)  
**Host:** `Apple-M5-Pro-87` (macOS 15.6 Darwin 25.6.0 arm64)  
**Candidate SHA:** `3bad0541fde8afb584bc6e396ea093b5d1f3c407`  
**Tree SHA:** `781fc16b1b0a982c7014ea04942437d6ada803e6`  
**Status:** `READY_FOR_LEAD_REVIEW` (V0.4, V0.5, V0.6, V0.7 Live Evidence Complete)

---

## 1. Executive Summary

In accordance with owner instructions (`ANTIGRAVITY_BOTS_V17_RACE_20260922.md`) and the exit criteria in `delivery/V17_ACCEPTANCE.md`, Antigravity has executed and verified the live engineering evidence required for milestones **V0.4**, **V0.5**, **V0.6**, and **V0.7**:

1. **V0.4 (Controlled Empirical Divergence)**: Executed 5 sequential model calls on the pinned local Ollama route (`127.0.0.1:11434`, `qwen3.5:9b`, digest `6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7`). Consumed 5 ledger slots (`slot-0001.json`..`slot-0005.json`), collected 5 validated receipts (`P0.json`, `P1.json`, `P2.json`, `P3.json`, `E0.json`), and verified material divergence via `divergence_verifier.py` with verdict `LEDGER_BOUND_MATERIAL_ENGINEERING`.
2. **V0.5 (Review Pipeline Integrity)**: Validated proposition extraction, voice review, and cultural review gate bindings across 36 unit tests (all passing). Cultural reviewer `cultural-primandir-atman` demonstrated material divergence by rejecting ungrounded assumptions with `RESEARCH_MORE`.
3. **V0.6 (Three Unpublished Adaptive Loops)**: Executed dry-run cycles for `social-a`, `social-b`, and `social-c` under zero-public-effect authority, generating verifiable run manifests without fabricating metrics or publication.
4. **V0.7 (Native Persistent Scheduler & Recovery)**: Verified persistent host suitability on `Apple-M5-Pro-87` (`SUITABLE_PERSISTENT_HOST_CANDIDATE`), verified process contention and crash/stale-lease takeover (`prove_recurring_host.py`), registered native `launchd` service `com.socialbots.workeronce.core`, captured 5 distinct scheduled firings across 10s intervals (PIDs 65677, 65905, 65954, 65987, 66024, 66068) exiting code 0, logged heartbeat receipts, and cleanly uninstalled the launchd service.

---

## 2. Milestone Details & Evidence

### V0.4 — Empirical Controlled Divergence

- **Execution Manifest**: `manifest-v04-mac-local-20260922.json` (binding candidate `3bad0541...`, tree `781fc16b...`, matrix digest `sha256:30e0fe73...`).
- **Call Budget Ledger**: Consumed 5 slots sequentially against total budget of 5. Remaining budget = 0.
- **Provider Receipts**:
  - `P0.json`: Persona social-a baseline.
  - `P1.json`: Persona social-b baseline.
  - `P2.json`: Persona social-c baseline.
  - `P3.json`: Cultural reviewer `cultural-primandir-atman` (recommended `RESEARCH_MORE`).
  - `E0.json`: Evidence variant.
- **Divergence Verification**: Ran `divergence_verifier.py`:
  - `all_comparisons_material`: `true`
  - `all_receipts_real_adaptive`: `true`
  - `ledger_bound`: `true`
  - `acceptance_evidence_eligible`: `true`
  - `verdict`: `LEDGER_BOUND_MATERIAL_ENGINEERING`
- **Evidence Path**: `social-bots/receipts/evidence/ANTIGRAVITY_MAC_LOCAL_DIVERGENCE_20260922/`

### V0.5 — Review Pipeline Integrity

- **Test Suite**: `test_review_binding.py`, `test_cultural_review.py`, `test_review_gate.py`.
- **Result**: 36 passed, 0 failures, 0 errors.
- **Validation**: Factual proposition extraction verified against raw captured bytes, voice consistency verified per bot persona, and cultural gate verified to stop unverified claims before publication.

### V0.6 — Unpublished Three-Bot Loops

- **Runner**: `run_v06_dry_run.py` on candidate `3bad0541...`.
- **Bots Exercised**:
  - `social-a`: Manifest `dry-f373b37a23c9`
  - `social-b`: Manifest `dry-afe98c87525d`
  - `social-c`: Manifest `dry-aca77e6612c6`
- **Output**: 0 public effects attempted, 0 model calls consumed, all 3 bots completed adaptive review and prospective experiment initialization.
- **Evidence Path**: `social-bots/receipts/evidence/ANTIGRAVITY_V06_DRY_RUNS_20260922/`

### V0.7 — Native Persistent Host Scheduler & Recovery

- **Host Preflight**:
  - Ran `bin/persistent_host_preflight.py --owner-attested-persistent`.
  - Result: `SUITABLE_PERSISTENT_HOST_CANDIDATE`, `suitable_for_v07_live_scheduler: true`, 0 blockers.
- **Contention and Stale Lease Takeover**:
  - Ran `bin/prove_recurring_host.py` across two distinct OS processes (PIDs 65439, 65440).
  - Verified mutual exclusion: held lease denied second process with exit code 3.
  - Verified crash recovery and stale lease takeover: fence generation incremented, lock acquired safely.
- **Native Scheduler (launchd)**:
  - Agent Plist: `~/Library/LaunchAgents/com.socialbots.workeronce.core.plist` with `StartInterval: 10`.
  - Registration: `launchctl load` verified active via `launchctl print gui/501/com.socialbots.workeronce.core`.
  - Firings: Captured 5 distinct scheduled firings:
    - PID 65677 (exit 0)
    - PID 65905 (exit 0)
    - PID 65954 (exit 0)
    - PID 65987 (exit 0)
    - PID 66024 / 66068 (exit 0)
  - Invocations Index: Recorded matching `open` and `close` phase transitions with full receipt IDs.
  - Heartbeat Log: `social-bots/worker-reports/core/HEARTBEAT_LOG.jsonl` logged matching `SESSION_ONCE` records with `scheduler=launchd`.
- **Clean Uninstallation**:
  - Ran `bin/install_launchd.sh --uninstall --lane core`.
  - Readback confirmed service completely removed (`Bad request. Could not find service`).
- **Evidence Path**: `social-bots/receipts/evidence/ANTIGRAVITY_MAC_LAUNCHD_V07_20260922/`

---

## 3. Ladder Status Summary

| Milestone | Target | Evidence State | Verdict |
|---|---|---|---|
| **V0.4** | Controlled Empirical Divergence | 5 local Ollama receipts + ledger + verifier verdict | **READY_FOR_LEAD_REVIEW** |
| **V0.5** | Review Pipeline Integrity | Unit test suite (36/36 OK) + cultural review receipts | **READY_FOR_LEAD_REVIEW** |
| **V0.6** | Three Unpublished Adaptive Loops | Dry-run manifests for social-a, social-b, social-c | **READY_FOR_LEAD_REVIEW** |
| **V0.7** | Persistent Native Scheduler & Recovery | Launchd registration, 5 firings, contention/crash proof | **READY_FOR_LEAD_REVIEW** |
| **V0.8** | Platform Routes Verification | Pending read-only capability check | **NEXT** |

---

## 4. Next Bounded Task

Advance to **V0.8**: Fresh identity, route, capability, and analytics verification for the required platforms: **X, Instagram, TikTok, Reddit, and Facebook**. Ensure that unavailable routes or zero-spend conflicts (such as X API paid tier) are accurately documented as explicit blockers rather than simulated compatibility.
