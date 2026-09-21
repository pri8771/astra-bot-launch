# SESSION_INSTRUCTIONS — Lane 1 / Windows Core Builder

Mode: FRESH SESSION RESET — LEAD-035 STALE WAKE-UP
Branch: `claude/social-bots-windows-core-host`
Lead check: 2026-09-21T15:52:53Z

No worker-generated commit, Issue #3 heartbeat, or progress update has appeared since the reset assignment. Start the fresh session now. Heartbeat is observability only and must not delay engineering work.

Read canonical:
- `social-bots/RESET_EXECUTION_20260921.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/artifact-packets/SB-V04-004.md`

## Start

1. Pull this branch.
2. Set `social-bots/worker-reports/windows-core/CURRENT_PROGRESS.md` to a concise current status.
3. Verify `gh auth status` can access `pri8771/astra-bot-launch`.
4. Launch the heartbeat reporter in a separate background process:

PowerShell example:

```powershell
Start-Process -FilePath python -ArgumentList @(
  "social-bots/bin/heartbeat_reporter.py",
  "--lane","CORE",
  "--progress-file","social-bots/worker-reports/windows-core/CURRENT_PROGRESS.md"
) -WindowStyle Hidden
```

The reporter handles:
- T0/+5/+10/+15m;
- then every 15m for 24h;
- one human-readable Issue #3 comment per heartbeat.

Do not launch a second reporter for the same fresh session.

Update CURRENT_PROGRESS.md whenever task/subtask/test/blocker changes.

## Mission

Preserve final V03 implementation/evidence unless independent QA finds a concrete defect.

Repair only SB-V04-004:
1. persona-only divergence test: hold all non-persona variables constant;
2. evidence-only divergence test: hold all non-evidence variables constant;
3. include >=3 persona/workspace comparisons including cultural/Primandir;
4. deterministic contextual provider tests remain diagnostic only;
5. add a clean seam that consumes sanitized real SB-V04-005 adaptive receipt;
6. do not make another live model call from Core;
7. preserve adaptive-required production default and deterministic authority wall;
8. run relevant tests/full suite;
9. commit/push report and changes;
10. pull canonical instructions again and continue dependency-safe Core work only if explicitly available.

At every meaningful change, update CURRENT_PROGRESS.md. Even with no code commit, Issue #3 must show a truthful heartbeat such as "still fixing evidence-only isolation; tests not run yet".

No public effects, PAYG/new spend, secrets, fake evidence, destructive actions or SwarmAI dependency.
