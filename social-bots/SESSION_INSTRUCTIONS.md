# SESSION_INSTRUCTIONS — Lane 3 / Mac Acceptance + Canary

Mode: FRESH SESSION RESET
Primary branch: `claude/social-bots-mac-qa-control`
Secondary isolated worktree branch: `claude/social-bots-v04-live-canary`

This must run on the actual local Mac with working Claude Code subscription authentication.

Read canonical:
- `social-bots/RESET_EXECUTION_20260921.md`
- `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/artifact-packets/SB-V03-004.md`
- `social-bots/artifact-packets/SB-V04-005.md`

## Start

1. Pull primary branch.
2. Set `social-bots/worker-reports/mac-qa/CURRENT_PROGRESS.md`.
3. Verify `gh auth status`.
4. Launch background reporter:

```bash
nohup python3 social-bots/bin/heartbeat_reporter.py \
  --lane ACCEPTANCE \
  --progress-file social-bots/worker-reports/mac-qa/CURRENT_PROGRESS.md \
  >/tmp/socialbots-acceptance-heartbeat.log 2>&1 &
echo $!
```

Reporter cadence:
- T0/+5/+10/+15m;
- then every 15m for 24h;
- one Issue #3 comment per heartbeat.

Update CURRENT_PROGRESS.md on every task/subtask/blocker transition.

## Mission A — close V0.3 gate FIRST

Do not edit Core runtime source.

Independently execute current final Core lifecycle behavior at implementation `796d4e390bd135167e5de2ff8f586bc07ac7f370` or a later source-equivalent branch head.

Run/probe:
1. post-cycle lease expiry/takeover: stale owner cannot write success completion receipt;
2. active-cycle lease loss/takeover: old owner cannot commit state/effect evidence;
3. migration/load stays side-effect free until fenced commit;
4. focused fencing/concurrency suite.

Report exact SHA, commands, results/test counts, host/filesystem scope, no-public-effect/no-spend confirmation.
If PASS, explicitly recommend `SB-V03-004 ACCEPT-READY`.
Push report to primary branch.

## Mission B — real V0.4 canary SECOND

After Mission A report is pushed, create/use a second isolated worktree for:
`claude/social-bots-v04-live-canary`

Do not reuse the QA checkout for canary source changes.

Execute exactly one SB-V04-005 real canary:
- real current public source;
- URL/timestamp/status/byte length/SHA-256;
- actual locally authenticated Claude Code subscription invocation through normal provider path;
- no injected/mock runner;
- no API/PAYG;
- schema validation;
- deterministic policy;
- persisted local decision;
- zero public effect.

Create required SOURCE.json / PROVIDER.json / DECISION.json / SUMMARY.json and worker report.
Commit/push canary branch and STOP canary execution for ChatGPT audit.

Then return to primary QA worktree and continue integration/CI work if dependency-safe.

No Core runtime edits, public social effects, PAYG/new spend, secrets, fake evidence, destructive actions or SwarmAI dependency.
