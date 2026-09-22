# SB-V07-001 authorized-host runbook

Install `bin/worker_once.py` on a host the owner has authorized to run it on
a recurring schedule. This runbook covers install, verification, uninstall,
and triage. It does not cover writing `worker_once.py` itself (see
`social-bots/bin/worker_once.py`) or the coordination rules it follows (see
`social-bots/AUTONOMY_CONTRACT.md` and
`social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`).

## Prerequisites

- Python 3.11+ on the host, reachable as `python3` (Linux/macOS) or `python`
  (Windows).
- A git checkout of this repository with push access (the worker consumes
  lead direction from git and pushes its own receipts/artifacts as it works).
- **No `gh` CLI required.** `worker_once.py` reads lead direction and writes
  evidence through the git checkout directly; any GitHub comment transport
  elsewhere in this project is best-effort and optional, never a dependency
  for scheduling.
- **No `ANTHROPIC_API_KEY` should be set** for this scheduled path. The
  authorized-host worker package runs the bounded, deterministic-or-adaptive
  posture `worker_once.py` is invoked with; it does not require or expect a
  paid model API key in the scheduler's environment. If a key is present in
  the host environment for unrelated reasons, do not add it to the
  scheduler's environment block.
- The owner has confirmed this specific host is authorized to run recurring
  invocations (this runbook does not itself grant that authorization).

### Environment variables `worker_once.py` reads

A production worker invocation requires an available, authorized adaptive provider.
The default baseline mode is deterministic and is refused with exit code `6`
(`BLOCKED_REASONING_UNAVAILABLE`) unless the invocation explicitly opts into a
diagnostic deterministic run. Configure provider posture only after its own grant;
the scheduler package alone does not make reasoning available.

| Variable | Effect |
|---|---|
| `SBOTS_HOME` | Overrides the runtime data root (heartbeats, leases, receipts, invocation records). Defaults to the `social-bots` directory itself when unset. The systemd unit and launchd agent set it directly; Task Scheduler XML cannot carry environment variables, so the Windows installer passes the same value as `--home` instead (`-SbotsHome`, default `<RepoRoot>\social-bots`). |
| `SBOTS_REASONING` | Selects the reasoning provider mode (e.g. `baseline`, `contextual`, `model`). The default deterministic baseline cannot satisfy the production worker adaptive requirement. |
| `SBOTS_WORKER_ALLOW_DETERMINISTIC` | Diagnostics-only opt-in to a non-adaptive provider. Do not set this for a production scheduled install; `worker_once.py`'s own `--allow-deterministic` flag is the explicit, auditable way to opt in per invocation when a diagnostic run genuinely needs it. |

## Install

Each installer is idempotent: re-running it replaces a previous install of
the same task/service/agent name rather than duplicating it.

### Windows (Task Scheduler)

```powershell
cd social-bots\scheduling\windows
.\Install-WorkerOnceTask.ps1 -RepoRoot "C:\path\to\astra-bot-launch" `
                              -Lane windows-core -Branch claude/your-branch
```

This registers a task named `SocialBotsWorkerOnce` (override with
`-TaskName`) that fires every 30 minutes (override with `-IntervalMinutes`)
and runs `python.exe bin\worker_once.py --lane <lane> --branch <branch>
--repo-root <RepoRoot> --home <SbotsHome>` with the working directory set to
`<RepoRoot>\social-bots`. `MultipleInstancesPolicy` is `IgnoreNew`, so a new
firing is skipped outright while a prior invocation is still running — that
is expected under load and is not a failure.

### Linux (systemd, template unit)

```bash
cd social-bots/scheduling/linux
./install_systemd.sh --repo-root /path/to/astra-bot-launch \
                      --lane core --branch claude/your-branch
```

Installs to the calling user's `~/.config/systemd/user` by default; pass
`--system` to install to `/etc/systemd/system` instead (requires sudo). The
lane name becomes the systemd template instance:
`social-bots-worker-once@core.timer`. A `--system` install with no `User=`
override in the unit runs as root; prefer the default `--user` install
(runs as the authorized interactive/service account) unless you have a
specific reason to run system-wide.

### macOS (launchd)

```bash
cd social-bots/scheduling/macos
./install_launchd.sh --repo-root /path/to/astra-bot-launch \
                      --lane core --branch claude/your-branch
```

Installs `com.socialbots.workeronce.plist` (per-lane label suffix) to
`~/Library/LaunchAgents/` and loads it for the current user session.

## Verify a real invocation happened

An installed schedule is not evidence of anything (see
`README.md`'s honesty boundary). To confirm a worker actually ran:

1. **Heartbeat log** — `social-bots/worker-reports/<lane>/HEARTBEAT_LOG.jsonl`
   must gain exactly one new appended record per invocation. Check the
   record count before and after a scheduled firing:

   ```bash
   wc -l social-bots/worker-reports/<lane>/HEARTBEAT_LOG.jsonl
   ```

2. **Invocation receipt** — `$SBOTS_HOME/invocations/index.jsonl` (default
   `SBOTS_HOME` is the `social-bots` directory itself when unset — see
   `runtime/paths.py`) must gain two new rows per invocation: an `"open"`
   phase row written before any work, and a `"close"` phase row carrying
   that invocation's exit code and claim/work outcome. There is also one
   full receipt file per invocation at
   `$SBOTS_HOME/invocations/<invocation_id>.json`. Count `"close"` rows to
   count invocations that actually finished; an `"open"` row with no
   matching `"close"` row is the durable signature of a crashed or killed
   invocation, not evidence it completed.

   ```bash
   wc -l "$SBOTS_HOME/invocations/index.jsonl"
   grep -c '"phase": "close"' "$SBOTS_HOME/invocations/index.jsonl"
   ```

If neither file grows after a firing you expected, the process did not
actually execute the payload — go to the failure triage table below.

## Read exit codes from each scheduler's own log

The exit-code contract (`README.md`) marks `3` (no-overlap) and `5` (lead
halted) as benign. Each scheduler surfaces the raw exit code differently:

- **Windows** — Task Scheduler UI: History tab for the task, or:

  ```powershell
  Get-ScheduledTaskInfo -TaskName SocialBotsWorkerOnce
  Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 20
  ```

  Task Scheduler's own "Last Run Result" column reports the raw process exit
  code (or an HRESULT wrapping it); `0`, `3`, and `5` there are all expected,
  not evidence of failure. Task Scheduler has no built-in mapping of a
  non-zero exit to "success" — you read the number and consult the table
  yourself.

- **Linux (systemd)** — the unit here sets `SuccessExitStatus=0 3 5`, so
  systemd itself reports `3`/`5` firings as `active (exited)`, not `failed`:

  ```bash
  systemctl --user status social-bots-worker-once@<lane>.service
  journalctl --user -u social-bots-worker-once@<lane>.service -n 50
  ```

  (drop `--user` for a `--system` install).

- **macOS (launchd)** — launchd does not have a success-status allow-list;
  read the worker's own stdout/stderr logs (paths printed by the installer,
  under the log directory you gave it) and/or:

  ```bash
  launchctl print gui/$(id -u)/com.socialbots.workeronce.<lane>
  ```

  The `last exit status` launchd reports is the raw process exit code —
  `3`/`5` there are benign per the table in `README.md`, not launchd's
  concept of success.

## Uninstall / rollback

- **Windows** — `.\Uninstall-WorkerOnceTask.ps1 [-TaskName SocialBotsWorkerOnce]`
- **Linux** — `./install_systemd.sh --uninstall --lane <lane> [--user|--system]`
- **macOS** — `./install_launchd.sh --uninstall --lane <lane>`

Each uninstall is safe to run when nothing is installed (it succeeds
quietly rather than erroring).

## Failure triage

| Symptom | Likely cause | Check |
|---|---|---|
| Task/timer/agent never fires at all | Not actually registered/enabled, or host was asleep/off at the scheduled time | Windows: `Get-ScheduledTask -TaskName ...` shows `Ready`/`Enabled`; Linux: `systemctl [--user] list-timers`; macOS: `launchctl print gui/$(id -u)/<label>` shows the job loaded. Confirm `StartWhenAvailable`/`Persistent=true`/host was powered on. |
| Fires but always exits `2` | Bad arguments substituted at install time (empty `--lane`/`--branch`, wrong `--repo-root`) | Re-run the installer with correct params; inspect the resolved command line in the task/unit/plist (`schtasks /Query /XML`, `systemctl cat`, `plutil -p`). |
| Always exits `3` | Every candidate task is already leased by a live worker in this lane, or the schedule interval is shorter than a unit of work takes | This is benign per the exit-code contract. Only investigate if it persists far longer than one bounded unit should take — check `$SBOTS_HOME/leases/` for a lease that never expires. |
| Always exits `5` | Lead direction (read from git) currently halts this lane | Benign. Check `SESSION_INSTRUCTIONS.md` / the lane's coordination state for an explicit halt; this is expected until lead direction changes. |
| `python`/`python3` not found | Wrong `-PythonExe`/`--python` resolved, or Python not on PATH for the account the scheduler runs as (service/system accounts often have a different PATH than the interactive shell you tested in) | Pass an explicit absolute interpreter path at install time; re-run `Get-Command python` / `command -v python3` as the same account the scheduler uses. |
| Permission errors (can't write heartbeat/receipt/lease files, or can't push) | Scheduler running as a different user than the one with the git checkout/push credentials, or `ReadWritePaths`/`ProtectHome` on Linux excludes the repo | Confirm the scheduled task/service runs as the interactive/authorized user (never store credentials in the unit itself — see each installer); on Linux widen `ReadWritePaths=` to cover the repo checkout. |

## What this runbook does NOT prove

- It does not prove recurring liveness. One or two manually-triggered test
  firings only prove the scheduler entry works and the process can complete;
  recurring liveness requires repeated real invocations accumulating over
  time on an owner-authorized host, visible as growth in
  `HEARTBEAT_LOG.jsonl` and `$SBOTS_HOME/invocations/index.jsonl` across
  multiple scheduled cadences, not just the install session.
- It makes no acceptance claim. Per `ARTIFACT_MANAGEMENT.md`, Claude does not
  self-accept artifacts; ChatGPT lead owns acceptance of SB-V07-001 and any
  dependent V0.7 evidence artifact (e.g. SB-V07-002), based on inspecting the
  actual heartbeat/invocation evidence a host produces, not on this runbook
  existing or having been followed once.


## Mac prepare-only checkpoint — 2026-09-22

The owner selected this Mac for the first bounded local inference experiment. That selection does not attest persistent unattended hosting or authorize scheduler installation/firing. LEAD066/067 released this read-only preparation only.

Observed source: accepted `d8a211fc32802c59b07b1739bef47f9c551ed8dc`, tree `169c386c471b813585e6f441d0be88fcf1ba0158`, temporary checkout `/tmp/bots-ollama-local-20260922`. Receipt: `../receipts/evidence/CODEX_MAC_HOST_PREPARE_20260922/HOST_PREFLIGHT.json`. It records `INCONCLUSIVE_NEED_OWNER_CONFIRMATION`, `suitable_for_v07_live_scheduler=false`, `live_claim=false`.

Read-only checks: Mac installer shell syntax and plist syntax passed; 31 existing scheduling/host-preflight tests passed. `persistent_host_preflight.py` collected facts without `--owner-attested-persistent`. No installer, worker, SESSION_ONCE, scheduler registration/readback/firing, launchctl mutation or inference was executed. The collector uses Linux findmnt, so Mac filesystem types remain unknown; scheduler binary presence is not a registration or persistence check.

| Activation fact | Current disposition |
|---|---|
| First inference test host | Owner's Mac selected |
| Persistent unattended host attestation | Not supplied |
| Durable accepted checkout, runtime/report/log roots | Not selected; /tmp checkout is not a deployment |
| Worker lane and source branch | Awaiting lead assignment |
| Existing scheduler owner, label and cadence | Not inspected or approved |
| Sleep, reboot, login/logout and uptime expectations | Not supplied |
| Recurring worker/provider authority | Not granted |
| Scheduler-fired receipts | None created by this preparation |

Existing assets remain the implementation: `bin/worker_once.py`, `runtime/host_preflight.py`, `bin/persistent_host_preflight.py`, `scheduling/macos/com.socialbots.workeronce.plist`, and `scheduling/macos/install_launchd.sh`. The installer has no dry-run mode and must not be used as a preview. SB-R07-073/074 remain PLANNED.

The accepted `ollama-local` route serves the separately bound five-case divergence experiment. `reasoning.resolve_provider` does not expose that route as a scheduled-worker mode. An experiment grant must never be reused as recurring-worker authority. No new worker implementation is included in this preparation.
