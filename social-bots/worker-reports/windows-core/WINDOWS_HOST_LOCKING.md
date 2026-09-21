# Worker report — Windows host locking / supported host path (Wave1 #1)

- **Parent artifact:** SB-V03-004 (host-locking sub-deliverable)
- **Lane:** Windows Core / Host (`claude/social-bots-windows-core-host`)
- **Requested status:** SUBMITTED (not self-accepted)
- **Starting SHA:** `fa14086da61edf21a3bce9473bcdee711ddb8f1e`

## IMPORTANT environment reality (must be read first)

This "Windows Core / Host" worker session is **not executing on a Windows
physical machine or inside WSL**. It is executing in a **Linux remote-execution
container**. Recorded, non-fabricated host facts
(`evidence/host_evidence.json`, secrets as booleans only):

| Fact | Value |
|---|---|
| `os.system` | `Linux` |
| `os.is_windows` | `false` |
| `os.is_wsl` | `false` |
| `os.release` | `6.18.44-fc-v37` |
| `python.version` | `3.11.15` |
| `git` | `git version 2.43.0` |
| `claude` CLI | `2.1.278 (Claude Code)`, on PATH |
| `fcntl.flock` available | `true` (strong path = `posix-flock`) |
| Windows Task Scheduler (`schtasks`) | `false` (not a Windows host) |
| POSIX `crontab` | `false` |
| `systemd --user` (`systemctl`) | `true` |
| `ANTHROPIC_API_KEY` present | **`false`** (boolean only; value never read/printed) |
| `CLAUDE_CODE_OAUTH_TOKEN` present | `false` |

Per the hard limits (no fake operational evidence), I will **not** claim a
native-Windows locking primitive or a literal WSL runtime that this host cannot
demonstrate. Doing so would be fabricated evidence.

## Supported host path chosen — as observed

The packet offered Option A (native Windows strong lock) or Option B (WSL →
POSIX flock/fence). On this host neither the native-Windows API surface nor a
Windows→WSL boundary exists to exercise. What genuinely exists and is the
strongest available path here is the **single-POSIX-host `fcntl.flock`** path,
which is exactly the Option B *runtime* (POSIX flock/fence) — just reached
directly on Linux rather than via a Windows→WSL hop.

Decision recorded for the lead:
- **Supported/proven path on this instance:** Linux/POSIX host, `fcntl.flock`
  compare-and-swap lease + monotonic fencing token (`runtime/leasing.py`,
  `FLOCK_AVAILABLE=True`).
- **Native-Windows strong locking:** NOT proven here — no Windows host available
  in this environment. A real native-Windows primitive (e.g. `LockFileEx` /
  `msvcrt.locking`, or a named-mutex CAS) must be implemented and proven on an
  actual Windows host before the deployment may assert native-Windows fencing.
  `runtime/leasing.py` already carries a non-POSIX fallback and flags it as
  best-effort (`FLOCK_AVAILABLE=False`), which the deployment must treat as the
  weak path until a real Windows primitive is proven.
- **Windows→WSL→POSIX:** architecturally the recommended Windows deployment
  shape (Windows physical machine → WSL → this same POSIX flock/fence code), and
  the POSIX half is proven here; the Windows→WSL boundary itself still needs
  proof on a real Windows+WSL machine.

## What IS proven here (genuine, cross-process)

`bin/prove_cross_process_lock.py` spawns 8 **independent OS processes**
(`multiprocessing` 'spawn' start method → fresh interpreters, not threads) that
contend for the same lease (`cycle:social-a`) simultaneously via a barrier.
Recorded verdict (`evidence/cross_process_lock.json`):

```json
{
  "acquired_count": 1,
  "held_count": 7,
  "error_count": 0,
  "flock_available": true,
  "processes_spawned": 8,
  "single_owner_ok": true,
  "start_method": "spawn (independent interpreters)"
}
```

Exactly one process acquired the lease; the other seven were correctly rejected
with `LeaseHeld`; zero errors. This is real cross-**process** exclusivity (the
unit tests only prove cross-thread), on the `fcntl.flock` strong path. Combined
with the SB-V03-004 fencing-token guarantee (obsolete owner commits nothing),
this is the supported single-host durability guarantee.

## Reproduce

```
cd social-bots
python3 bin/host_evidence.py              # host facts (booleans for secrets)
python3 bin/prove_cross_process_lock.py   # exit 0 iff single-owner invariant holds
```

## Known limits

- Single POSIX host, single local filesystem. No cross-host distributed lock.
- Native-Windows and Windows→WSL boundary locking are explicitly **unproven** on
  this Linux container and are not claimed. This is an environment blocker for
  the native-Windows Option A, reported rather than faked.

## Requested status

**SUBMITTED** — and flagged for lead decision: the Windows lane is currently
running on a Linux container. If genuine native-Windows / Windows-Task-Scheduler
evidence is required, this artifact needs to be run on a real Windows host.
