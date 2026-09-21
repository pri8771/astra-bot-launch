# Work queue — LEAD-038 owner execution simplification

Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed.

Primary worker contract: `CLAUDE_EXECUTION_TO_V07.md`.

Forward planning: `FORWARD_PLAN_V06_TO_V30.md`.

## Owner operating model

Claude owns the bulk of implementation.

ChatGPT lead primarily:
- maintains canonical product/architecture decisions;
- prepares downstream artifact/task decomposition;
- independently audits submissions;
- accepts/rejects artifacts;
- keeps future work unblocked.

Do not duplicate routine implementation between ChatGPT and Claude unless independent repair/review requires it.

## Heartbeat

Owner policy is now **ONE SESSION = ONE HEARTBEAT**.

The old FAST_5M / 24-hour soak is superseded.

Every fresh worker session:
1. syncs/reads canonical coordination;
2. appends exactly one real `SESSION_ONCE` heartbeat to the durable lane log;
3. optionally posts one Issue #3 visibility comment;
4. works normally with no recurring heartbeat loop.

V0.7 recurring liveness comes from repeated OS-scheduled bounded sessions, each with one heartbeat and an invocation receipt.

See `HEARTBEAT_ASSIGNMENT_PROTOCOL.md`.

## Current critical path

### V0.4

- SB-V04-001 ACCEPTED.
- SB-V04-003 ACCEPTED.
- SB-V04-005 ACCEPTED.
- SB-V04-002 BLOCKED_OWNER_AUTHORIZATION.
- SB-V04-004 BLOCKED_OWNER_AUTHORIZATION.
- SB-EVD-002 WITHHELD.

No additional model call is currently authorized.

Core may complete prepare-only matrix/hash/isolation/authorization/call-budget work with fixtures, then move to dependency-safe V0.7 host engineering.

### V0.5

- SB-V05-001 ACCEPTED.
- SB-V05-002 CHANGES_REQUIRED.
- SB-V05-003/004/005 planned.

Intelligence/evidence work may continue where dependency-safe.

### V0.6

Operational dry runs remain dependency-gated, but scaffolding/validators may be prepared without fake operational evidence.

### V0.7

SB-V07-001 is READY.

Host-worker/scheduler/session-heartbeat/invocation-receipt/no-overlap engineering is dependency-ready now without live model calls.

## Existing lanes

### Core — `claude/social-bots-windows-core-host`
Owns:
- V0.4 prepare-only divergence/authorization harness;
- then V0.7 host-worker engineering.

### Intelligence — `claude/social-bots-intelligence-repair-v2`
Owns:
- current SB-V15-001 structural repair;
- evidence/intelligence work only when released by lead.

### Acceptance — `claude/social-bots-mac-qa-control`
Owns:
- independent review;
- acceptance harnesses;
- V0.6/V0.7 validators/fault cases;
- no live model execution.

### Canary — `claude/social-bots-v04-live-canary`
Frozen for evidence preservation. No further live model calls.

## Safety

No public social effects, paid API/PAYG/new spend, secrets, destructive actions, fabricated operational evidence, engagement manipulation or SwarmAI dependency.
