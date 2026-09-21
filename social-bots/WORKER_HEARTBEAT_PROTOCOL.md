# Worker heartbeat protocol

Purpose: allow ChatGPT lead and multiple Claude sessions to coordinate through GitHub without the owner relaying every task.

This is a state-transition heartbeat, NOT a high-frequency timer.

## Branch-local heartbeat

Each active worker lane maintains:
`social-bots/worker-reports/<lane>/HEARTBEAT.json`

Recommended lane directories:
- windows-core
- intelligence-repair
- mac-qa

Schema:
```json
{
  "schema_version": 1,
  "lane": "windows-core",
  "branch": "claude/social-bots-windows-core-host",
  "session_status": "WORKING",
  "current_artifact": "SB-V03-006",
  "started_at": "ISO-8601",
  "last_updated_at": "ISO-8601",
  "last_commit_sha": "sha-or-null",
  "canonical_seen_sha": "sha-or-null",
  "lead_message_seen": "LEAD-018",
  "next_artifact": "SB-V04-001",
  "blocker": null,
  "notes": "short factual note"
}
```

Allowed session_status:
BOOTSTRAPPING, WORKING, SUBMITTED, BLOCKED, IDLE, STOPPED.

## Update + push heartbeat
Update when starting/resuming, before a new parent artifact, after submitting an artifact, when blocked, and before idle/stop. Do not create heartbeat commits every few minutes.

Actual commits/receipts are stronger evidence than heartbeat claims.

## Pull/re-read coordination cycle
At session start and after each artifact checkpoint:
1. commit/push worker work;
2. `git pull --ff-only` own branch;
3. re-read `social-bots/SESSION_INSTRUCTIONS.md`;
4. follow the newest lead-owned file;
5. update heartbeat;
6. begin next artifact.

SESSION_INSTRUCTIONS.md is lead-owned. Workers should not rewrite it.

## Reports / blockers
Artifact reports stay under the lane worker-reports directory. SUBMITTED does not self-accept. If blocked, push exact blocker and continue another dependency-safe artifact only when instructions allow it.

Never put secrets/tokens/cookies/auth headers/private browser state/recovery codes in heartbeat.
