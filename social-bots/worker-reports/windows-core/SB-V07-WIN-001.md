# Worker report — SB-V07-WIN-001 (Windows Core lane)

- **Artifact ID:** SB-V07-WIN-001 — recurring host worker execution proof
- **Lane:** Windows Core / Host (`claude/social-bots-windows-core-host`)
- **Requested status:** PARTIAL / BLOCKED (POSIX cross-process proof done;
  native-Windows/WSL scheduler proof BLOCKED — see below; nothing fabricated)
- **Starting SHA:** `fa14086da61edf21a3bce9473bcdee711ddb8f1e`

## Environment gate (per LEAD-019 instruction)

> "If your execution environment is Linux/container rather than the actual
> Windows host, mark Windows host proof BLOCKED rather than fabricating it."

Recorded host facts (`evidence/host_evidence.json`): `os.is_windows=false`,
`os.is_wsl=false`, `windows_task_scheduler_available=false`. This session runs on
a **Linux container**. Therefore the native-Windows / Windows-Task-Scheduler /
Windows→WSL recurring proofs are **BLOCKED** and are NOT claimed here.

## What IS genuinely proven on this host (real separate processes)

`bin/prove_recurring_host.py` launches `bin/run_worker.py` as **independent OS
processes** (`subprocess`, distinct PIDs), not in-process cycles. Committed
evidence: `receipts/evidence/SB-V07-recurring/SUMMARY.json` plus the real
receipts, heartbeats and lease files it produced. Recorded verdict (`all_pass:true`):

- **Two genuinely separate process invocations** — distinct PIDs `7802` and
  `7803`, both different from the parent harness PID `7800`; two distinct
  heartbeat files and two start receipts; both exited cleanly (rc 0).
- **Later independent invocation / restart-resume** — invocation 1 created a
  candidate (`CREATE_CANDIDATE`); the independent later invocation 2 resumed and
  correctly produced `NO_ACTION` (the signal was already consumed, restart-safe).
- **No-overlap** — while an external holder held the `cycle:social-b` runtime
  lease, a separate worker PROCESS was rejected and exited with the no-overlap
  code `3` (`NO-OVERLAP: task 'cycle:social-b' held by external-holder`).
- **Stale/recovery** — a separate worker process took over an already-expired
  lease and committed under fence generation ≥ 2 (`took_over_gen_ge_2: true`).

Each invocation wrote a real heartbeat (with its own pid), acquired/released a
lease under the fence, wrote start + finish receipts, and exited cleanly — the
lifecycle the artifact requires, proven by artifacts, not by a scheduler entry.

Reasoning posture for this proof is the explicit DIAGNOSTIC mode
(`SBOTS_WORKER_ALLOW_DETERMINISTIC=1`) so decisions occur and restart/resume is
observable; the production adaptive-required fail-closed posture is proven
separately (SB-V04-001, `tests/test_reasoning_contract.py`).

## Reproduce

```
cd social-bots
python3 bin/prove_recurring_host.py   # exit 0 iff all checks pass
```

## What remains BLOCKED (needs a real Windows/WSL host)

- A recurring launch via **Windows Task Scheduler** (or an already-established WSL
  user scheduler) driving these same invocations on a schedule.
- The **native-Windows strong lock** (or Windows→WSL→POSIX flock) under real
  cross-process contention on that host (see `WINDOWS_HOST_LOCKING.md`).

These require executing on an actual Windows (or Windows+WSL) machine. On this
Linux container they cannot be proven honestly, so they are reported BLOCKED.

## Interface request to lead

To close SB-V07-WIN-001 fully: provide/confirm a real Windows or Windows+WSL host.
The POSIX process-lifecycle proof here transfers directly to the WSL path (same
runtime code); only the Windows Task Scheduler wiring and, for the native path,
a real Windows lock primitive remain to be exercised there.

## Requested status

**PARTIAL — POSIX cross-process recurring proof SUBMITTED; native-Windows/WSL
scheduler + lock proof BLOCKED** pending a supported host (not fabricated).
