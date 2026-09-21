# SESSION_INSTRUCTIONS — Lane 2 / Mac Intelligence Builder

Mode: FRESH SESSION RESET — LEAD-035 STALE WAKE-UP
Branch: `claude/social-bots-intelligence-repair-v2`
Lead check: 2026-09-21T15:52:53Z

No worker-generated commit, Issue #3 heartbeat, or progress update has appeared since the reset assignment. Start useful work now. Heartbeat is observability only and must run in parallel rather than delay V05/V15 implementation.

Read canonical:
- `social-bots/RESET_EXECUTION_20260921.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `social-bots/SESSION_ROUTER.md`

## Start

1. Pull this branch.
2. Set `social-bots/worker-reports/intelligence-repair/CURRENT_PROGRESS.md`.
3. Verify `gh auth status`.
4. Launch in background:

```bash
nohup python3 social-bots/bin/heartbeat_reporter.py \
  --lane INTELLIGENCE \
  --progress-file social-bots/worker-reports/intelligence-repair/CURRENT_PROGRESS.md \
  >/tmp/socialbots-intelligence-heartbeat.log 2>&1 &
echo $!
```

Reporter cadence:
- T0/+5/+10/+15m;
- then every 15m for 24h;
- one Issue #3 comment each heartbeat.

Update CURRENT_PROGRESS.md whenever work changes.

## Mission

Accepted/frozen:
- SB-V13-001
- SB-V14-001

Priority 1 — SB-V05-001:
- connect to validated/pinned public IP;
- preserve original hostname for TLS SNI/certificate verification;
- no hostname re-resolution after validation;
- correct Host header;
- redirects fail closed unless each hop is revalidated/pinned;
- preserve SSRF/trust/extraction/fixture-vs-operational controls;
- add production-path regression catching invalid HTTPS constructor/API use;
- run tests, commit/push, report exact limitations.

Priority 2 — SB-V15-001:
- authoritative bot+persona experiment save/load/list/read APIs;
- normal persona flows cannot enumerate another persona's experiments;
- whole-runtime access explicit admin/internal only;
- mixed-persona production-path regressions;
- preserve normalized observation provenance and INCONCLUSIVE behavior.

After both submit, stop expansion and wait/pull for lead audit.

Do not edit Core runtime.
No public effects, PAYG/new spend, secrets, fake metrics/evidence, destructive actions or SwarmAI dependency.
