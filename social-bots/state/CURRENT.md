> **Latest owner assignment — 2026-09-22:** Antigravity is active Social Bots implementation owner; target accepted LIVE V1.7. PR22 candidate (`3bad054`) and frozen Mac matrix (`1549df4`) independently verified and accepted for engineering composition. V0.4 (5-call Ollama divergence), V0.5 (review pipeline integrity), V0.6 (3-bot dry runs), and V0.7 (Apple-M5 native launchd persistent scheduler, contention/recovery) COMPLETED with live engineering evidence submitted for lead review (`ANTIGRAVITY_V07_LIVE_COMPLETION_20260922.md`). Active milestone pointer: V0.8.

# Current state — LIVE V1.7 RACE

Official version remains **V0.7.x** (V0.4–V0.7 live evidence complete and submitted, awaiting formal lead sign-off).

**Owner target: LIVE V1.7, then stop development.** No automatic V1.8/V2.3/V3.0 continuation.

- **Active implementation owner**: Antigravity on Mac (`Apple-M5-Pro-87`).
- **Verified Source**: Candidate `3bad0541fde8afb584bc6e396ea093b5d1f3c407`, tree `781fc16b1b0a982c7014ea04942437d6ada803e6`. Full unittest suite: 789 passed, 2 skipped, 0 failures, 0 errors.
- **V0.4 Empirical Divergence**: 5 local Ollama `qwen3.5:9b` calls executed sequentially on `127.0.0.1:11434`. 5 ledger slots consumed. Material divergence confirmed (`LEDGER_BOUND_MATERIAL_ENGINEERING`). Evidence in `social-bots/receipts/evidence/ANTIGRAVITY_MAC_LOCAL_DIVERGENCE_20260922/`.
- **V0.5 Review Pipeline**: 36 unit tests passed. Voice, factual claims, and cultural review gate verified.
- **V0.6 Three Adaptive Loops**: Dry runs executed for `social-a`, `social-b`, and `social-c`. Manifests in `social-bots/receipts/evidence/ANTIGRAVITY_V06_DRY_RUNS_20260922/`.
- **V0.7 Persistent Scheduler & Recovery**: Preflight attested persistent; contention/crash verified via `prove_recurring_host.py`; native `launchd` service `com.socialbots.workeronce.core` registered, fired 5 times across distinct intervals, verified clean, and uninstalled. Evidence in `social-bots/receipts/evidence/ANTIGRAVITY_MAC_LAUNCHD_V07_20260922/`.
- **Active Milestone**: **V0.8** (Platform Routes Verification for X, Instagram, TikTok, Reddit, Facebook).
- **Current Blockers / Dependencies**:
  1. X official API cost policy conflict under zero-spend constraint ($100/mo Basic tier required for read/write vs $0 budget). Must be logged as an exact blocker.
  2. Public posting / account mutations for V0.9+ canary require explicit owner canary authorization.
