# Work queue — LEAD-037

Lead review: `LEAD-037`.
Official phase: **V0.4.x / V0.4 in progress**. V0.3 is accepted and closed. V0.4 is not complete.

## Architectural decision

SB-V04-002 and SB-V04-004 are **BLOCKED on fresh explicit owner authorization for empirical adaptive-divergence execution**.

Core engineering has repaired the single-variable design and receipt seam, but replay/synthetic receipts cannot prove live model causality. No additional Claude CLI/adaptive/model call is authorized.

Canonical execution design: `V04_DIVERGENCE_ACCEPTANCE_PLAN.md`.

## Lane 1 — CORE / `claude/social-bots-windows-core-host`

Status: **ACTIVE — NO-LIVE-CALL PREP, THEN V0.7 HOST WORK**.

Priority A:
1. Do not execute any live model/provider call.
2. Build the prepare-only five-context divergence matrix:
   - social-a / E1;
   - social-b / same E1;
   - social-c / same E1;
   - cultural Primandir / same E1;
   - social-a / E2.
3. Emit complete bounded context JSON, context SHA-256 and exact prompt SHA-256 per case.
4. Assert only persona differs across the first four contexts and only evidence differs for social-a E1 vs E2.
5. Add fail-closed authorization-manifest + exact call-budget enforcement. No authorization manifest exists now; live execution must therefore stop before spawning Claude.
6. Add no-retry semantics and engineering-only fixture tests.
7. Submit and stop for lead/QA audit of this prep.

Priority B after A submission:
- **SB-V07-001 is READY.**
- Build authorized-host worker/runbook and OS-level scheduling package with one-task claim, invocation receipts, crash-safe/no-overlap primitives and heartbeat durability.
- Heartbeat logging must work even when `gh` is unavailable; comment posting is optional transport, durable local/repo log is the evidence source.
- Tests must not invoke a live model.

## Lane 2 — INTELLIGENCE / `claude/social-bots-intelligence-repair-v2`

Status: **ACTIVE — NARROW REPAIR**.

1. Repair **SB-V15-001** only.
2. Remove/private/rename ordinary whole-runtime `load(bot,id)` and `load_all(bot)` aliases.
3. Preserve explicit admin-only whole-runtime readers.
4. Add regression proving normal production experiment APIs cannot enumerate another persona.
5. Run focused/full tests, push report and stop for lead audit.

Do not expand into V16/V17/V20-002 until lead review.

## Lane 3 — ACCEPTANCE / QA / `claude/social-bots-mac-qa-control`

Status: **ACTIVE — REVIEW + V0.7 PREP**.

1. No model calls.
2. Independently review new Core and Intelligence submissions when they land.
3. Prepare V0.7 host/heartbeat acceptance checks and fault cases without editing Core/Intelligence runtime source.
4. Validate that durable heartbeat logging is transport-independent and that missed intervals are never backfilled.

## Live-canary lane

`claude/social-bots-v04-live-canary`

Status: **FROZEN — EVIDENCE PRESERVATION ONLY**.

No further adaptive/model execution.

## V0.4 critical path

1. SB-V04-002 — BLOCKED on owner-authorized empirical divergence batch.
2. SB-V04-004 — BLOCKED on same batch.
3. SB-EVD-002 — WITHHELD until both are ACCEPTED.
4. V0.4 stays in progress.

No downstream engineering changes this milestone truth.

## Heartbeat truth

Issue #3 contains active progress comments, including Acceptance FAST_5M comments through approximately 17:16Z.

The protocol defines durable `HEARTBEAT_LOG.jsonl` entries as authoritative. Current worker branches still contain no reset-epoch FAST_5M durable records.

**Verified durable reset soak: 0 FAST_5M intervals on Core, Intelligence and Acceptance.**

Do not backfill. This does not block useful work.

## Safety / authority

No public social effects, paid API/PAYG/new spend, destructive actions, credentials/secrets, fabricated evidence, engagement manipulation or SwarmAI dependency.
