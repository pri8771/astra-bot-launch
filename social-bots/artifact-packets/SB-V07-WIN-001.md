# Artifact packet — SB-V07-WIN-001

Artifact: Native Windows host/runtime compatibility and recurring-worker proof
Milestone: V0.7
Lane: Windows Core/Host
Story points: 5

## Goal

Use the actual Windows Claude environment to prove the supported Windows host path, rather than assuming Linux-only worker behavior.

## Phase 1 — environment readback

Record safe metadata only:
- Windows version/build;
- Python version;
- Claude Code version;
- repo path;
- whether WSL is already available;
- whether ANTHROPIC_API_KEY is present (record boolean only, never value);
- current user-level Task Scheduler availability.

No credentials/tokens in Git.

## Phase 2 — locking decision

Preferred:
- if native Windows is the target, implement/test a strong process lock/fence using Windows-supported primitives.
- if an already-installed WSL environment is deliberately chosen as the supported worker runtime, document and prove that exact WSL/POSIX path instead of claiming native Windows.

Acceptance:
- cross-process single-owner acquisition;
- stale takeover one owner;
- active-cycle fence loss prevents old commit;
- process crash releases lock;
- no unsupported fallback silently treated as strong fencing.

## Phase 3 — Claude adaptive-provider host proof

Read CLAUDE_REASONING_ROUTE_RESEARCH.md.

Prove:
- existing Claude Code subscription auth works;
- ANTHROPIC_API_KEY absent for the test;
- bounded non-interactive JSON invocation succeeds;
- provider/auth/quota failure is fail-closed;
- no tools/external side effects;
- no API PAYG credentials created.

## Phase 4 — recurring worker proof

Install/use a user-authorized no-additional-spend recurring launcher.

Produce at least two genuinely separate invocations with:
- invocation receipt;
- process heartbeat;
- lease/fence;
- bounded work or truthful NO_ACTION;
- clean exit;
- later independent invocation.

Scheduler configuration alone is not proof.

No public social action.
