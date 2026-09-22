# Scheduling assets (SB-V07-001)

Host-scheduler packaging for `social-bots/bin/worker_once.py`: OS-native task
definitions plus installers for Windows Task Scheduler, Linux systemd (user or
system), and macOS launchd. See `RUNBOOK.md` for the authorized-host install
and verification procedure.

## One invocation, one session

`worker_once.py` is a bounded CLI, never a daemon. Each scheduled firing is one
OS process that:

1. emits exactly one durable `SESSION_ONCE` heartbeat;
2. reads current lead direction from git (no owner relay required);
3. claims at most one task (lease/fence protected — overlapping invocations
   are safe, but every installer here still sets a single-instance policy so
   runs do not stack);
4. runs one bounded unit of work;
5. writes an invocation receipt;
6. exits.

The scheduler's only job is to start that process on a cadence and leave it
alone. It does not hold state, retry loops, or long-lived connections.

## Exit-code contract

| Code | Meaning | Scheduler should treat as |
|------|---------|----------------------------|
| `0` | Unit completed | success |
| `3` | No-overlap: every candidate task already leased by a live worker | benign, expected — not a failure |
| `5` | Lead direction halted this lane | benign, expected — not a failure |
| `6` | Required adaptive reasoning is unavailable | blocked; inspect the invocation receipt and authorized provider posture |
| `1` | Unexpected failure (a receipt was written) | failure |
| `2` | Bad usage (bad arguments) | failure — check the invocation, not the worker logic |

Every installer here maps `3` and `5` into "success" in the native scheduler's
own success/failure accounting where that scheduler supports it (systemd's
`SuccessExitStatus=`); where the scheduler has no such concept (Task
Scheduler, launchd) the runbook explains how to read the process exit code
from that scheduler's own log instead of relying on a green/red status.

## Honesty boundary

**Installing a scheduler entry is not evidence that a worker ran.** A task
definition, timer, or plist can be registered, enabled, and still never fire,
fire and fail before writing anything, or fire against a host that later goes
offline. None of that is visible from the installer output alone.

The only evidence that a worker actually ran is:

- a new record appended to
  `social-bots/worker-reports/<lane>/HEARTBEAT_LOG.jsonl` (the durable
  `SESSION_ONCE` heartbeat — see `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`), and
- a new record appended to `$SBOTS_HOME/invocations/index.jsonl` (the
  invocation receipt written by the live `worker_once.py` process).

Both are written by the worker process itself, never by the scheduler. See
`social-bots/AUTONOMY_CONTRACT.md` ("Heartbeat proves liveness only when
updated by the actual worker process. Scheduler configuration alone is not
evidence.") for the rule this packaging follows. Nothing in this directory —
including a successful install script run — should ever be cited as proof of
a completed invocation. `RUNBOOK.md` explains exactly what to inspect instead.

## Layout

- `windows/` — Task Scheduler v1.2 task definition + PowerShell install/uninstall.
- `linux/` — systemd template unit + timer + shell installer (user or system).
- `macos/` — launchd plist + shell installer.
- `RUNBOOK.md` — prerequisites, install/verify/uninstall steps, failure triage.
