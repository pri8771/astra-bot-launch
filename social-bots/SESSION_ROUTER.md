# Active session router — LEAD-037

Official phase: **V0.4.x / V0.4 in progress**.
V0.3 is accepted. V0.4 is empirical-divergence authorization-blocked.

Canonical decision: `V04_DIVERGENCE_ACCEPTANCE_PLAN.md`.

## Lane 1 — Core Builder

Branch: `claude/social-bots-windows-core-host`
Status: **ACTIVE**.

Owns now:
- prepare-only V0.4 divergence matrix/hashing/isolation/authorization-gate work;
- then dependency-ready SB-V07-001 host-worker/runbook/OS-scheduler/heartbeat durability work.

Hard rule:
- **no live Claude CLI/adaptive/model call**;
- no synthetic/replayed receipt may be presented as causal adaptive evidence;
- no authorization manifest currently exists.

## Lane 2 — Intelligence Builder

Branch: `claude/social-bots-intelligence-repair-v2`
Status: **ACTIVE**.

Owns now:
- SB-V15-001 structural admin/read-boundary repair only.

Then submit and stop for lead audit.

## Lane 3 — Acceptance / QA

Branch: `claude/social-bots-mac-qa-control`
Status: **ACTIVE**.

Owns now:
- independent review of dependency-ready submissions;
- V0.7 host/heartbeat acceptance preparation;
- durable heartbeat truth checking.

Does not own:
- Core/Intelligence runtime source;
- any live model/provider execution.

## Live-canary worktree

Branch: `claude/social-bots-v04-live-canary`
Status: **FROZEN**.

Preserve evidence only.

The first chronological authorized canary is accepted for SB-V04-005. The later duplicate call exceeded authorization and remains excluded. No further model calls are authorized.

## V0.4 acceptance state

- SB-V04-001 ACCEPTED
- SB-V04-003 ACCEPTED
- SB-V04-005 ACCEPTED
- SB-V04-002 BLOCKED
- SB-V04-004 BLOCKED
- SB-EVD-002 WITHHELD

The clean future empirical matrix is five controlled provider invocations, but only after a new explicit owner authorization and lead-created authorization manifest.

## Heartbeat

Issue #3 is the human-readable feed.
`HEARTBEAT_LOG.jsonl` is authoritative for cadence proof.

Current Issue comments are active; durable reset-epoch FAST_5M proof remains zero on all three human lanes.

V0.7 host work must decouple durable logging from the optional GitHub-comment transport so a missing `gh` binary cannot prevent heartbeat evidence.

## Lead authority

Workers submit; ChatGPT lead accepts.
No worker self-promotes artifacts or versions.

## Safety

No public social effects, paid API/PAYG/new spend, destructive actions, credentials/secrets, fabricated evidence, engagement manipulation or SwarmAI dependency.
