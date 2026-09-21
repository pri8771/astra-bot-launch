# Active session router — LEAD-036

Canonical plan: `RESET_EXECUTION_20260921.md`.
Lead review: `LEAD-036` at 2026-09-21T17:10:00Z.
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted. V0.4 is not complete.

## Lane 1 — Windows Core Builder

Branch: `claude/social-bots-windows-core-host`
Machine assignment: Windows
Status: **ACTIVE / SUBMITTED**.

Owns:
- non-live SB-V04-004 acceptance/test seam work only;
- later dependency-safe Core work after lead assignment.

Current truth:
- deterministic persona/evidence isolated comparisons are repaired;
- SB-V04-001 and SB-V04-003 are accepted;
- SB-V04-002/SB-V04-004 still lack required real adaptive causal-divergence evidence;
- owner's one-call live-model authorization is consumed.

Hard rule: **no further Claude CLI/adaptive model call**. Do not substitute replay/fixtures for causal adaptive-divergence proof.

## Lane 2 — Mac Intelligence Builder

Branch: `claude/social-bots-intelligence-repair-v2`
Machine assignment: Mac
Status: **ACTIVE / SUBMITTED**.

Owns:
1. SB-V15-001 narrow structural admin/read-boundary repair now;
2. later Intelligence audits/repairs only after lead release.

Current truth:
- SB-V05-001 is accepted at `a462bd6`;
- V15 persona partitioning is materially improved at `2052955`, but ordinary `load` / `load_all` names still expose whole-runtime reads.

Next: remove/private/rename ambiguous aliases, preserve explicit `admin_*` readers, add production-surface isolation regression, run tests, submit, stop for lead audit.

## Lane 3 — Acceptance / QA

Primary branch: `claude/social-bots-mac-qa-control`
Machine assignment in reset plan: actual local Mac
Status: **ACTIVE / SUBMITTED**.

Current truth:
- independent SB-V03-004 acceptance at `72e380b` is accepted;
- V0.3 is closed;
- actual acceptance execution ran on Linux CCR/POSIX rather than the reset-plan physical Mac, so the lifecycle guarantee is scoped to single POSIX host/filesystem;
- live canary execution is complete and frozen.

Owns next:
- non-overlapping QA/CI/V2 acceptance integration;
- durable prospective heartbeat reporting;
- no Core/Intelligence runtime source edits.

Hard rule: **no further Claude CLI/adaptive model call**.

## Live-canary worktree

Branch: `claude/social-bots-v04-live-canary`
Status: **FROZEN — EVIDENCE PRESERVATION ONLY**.

The first chronological real canary (~16:15Z, on the Acceptance-side isolated branch) consumed the owner's exactly-one call authorization and is accepted as SB-V04-005 evidence. A second call (~16:53Z) later occurred on the dedicated branch; it exceeded authorization and is excluded from acceptance evidence.

No additional canary/provider/model execution is authorized.

## Remote worker-pc

External optional verifier only; not on critical path.
Do not redispatch Social Bots until private-repo clone/auth to `pri8771/astra-bot-launch` is demonstrably repaired.

## Heartbeat / visibility

Issue #3 is the human-readable feed, but durable `HEARTBEAT_LOG.jsonl` is authoritative for the reset soak.

At LEAD-036, all three human lanes have active Issue comments but **zero verified reset-epoch FAST_5M intervals in durable logs**. No backfill. Heartbeat does not block engineering.

## Lead authority

ChatGPT owns artifact acceptance, canonical reconciliation and next assignments. No worker self-accepts a milestone.

## Safety

No public social effects, paid API/PAYG/new spend, destructive actions, credentials/secrets, fabricated evidence, engagement manipulation or SwarmAI dependency.
