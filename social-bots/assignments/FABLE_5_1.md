# Assignment — Fable 5.1 — LEAD-045 review hold

Role: senior implementation architect + non-conflicting V2.3 engineering worker.

## Current state

The currently released new-files-only batch is complete. Fresh engineering submissions exist for **SB-S20-001** and **SB-S23-001..SB-S23-008** on `fable/social-bots-v23-fasttrack-20260921`.

Lead has reviewed material source/evidence and classified the batch as **submitted engineering evidence**, not operational acceptance. `SB-S23-008` remains fixture-class evidence and requires an independent Acceptance rerun.

## Current instruction — PAUSE NEW SOURCE WORK

1. Preserve the submitted source, worker reports, fixture evidence, hashes, and test results.
2. Do **not** begin another implementation slice until a new explicit lead release is committed.
3. Do not edit Cursor-owned existing recovery/runtime files.
4. If a fresh session is started only to read/review coordination, emit exactly one durable `SESSION_ONCE` heartbeat and do not manufacture progress.
5. You may respond to a concrete lead review question with read-only analysis, but do not turn that into unassigned source changes.

## Review queue

Acceptance is assigned to independently rerun/audit `SB-S23-008` after the immediate R07 gates. Lead has pinned the integration predicates in `../next-round/BASELINE.json`.

`SB-S20-000` remains blocked until `SB-R07-041` is accepted. Downstream V2.0–V2.3 integration cannot skip that dependency.

## Evidence classification

Worker-local green tests and fixtures are ENGINEERING evidence only. They never promote operational V2.0–V2.3 by themselves.

## Hard gates

No unauthorized live model call, public/account effect, new spend/PAYG, destructive action, credential exposure, engagement manipulation, or SwarmAI dependency.

Workers submit. ChatGPT lead accepts.
