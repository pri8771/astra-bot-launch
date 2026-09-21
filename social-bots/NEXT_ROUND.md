# Next round: finish integration and prove operation

Status: **NEXT_ROUND_NOT_ACTIVE**. This package does not change the running Fable/Cursor assignments, grant external authority, or promote a version.

Owner priority: V2.3 genuinely working as soon as possible; retain the complete V3.0 destination. The purpose is to remove another major planning reset, not to promise that external approvals, elapsed measurement windows, or unknown defects disappear.

## Start at the next checkpoint, not mid-artifact

1. Preserve and push current work. Fetch the latest canonical and worker refs. Do not reset a dirty worktree or merge moving heads blindly.
2. Read `next-round/EXECUTION_CONTRACT.md` and the relevant rows in `next-round/NEXT_ROUND_TASKS.json`.
3. Reconcile the exact integration baseline and outstanding lead decisions using NR-01. Existing accepted work is reused, not rebuilt.
4. Open only the matching section of `next-round/WORK_CARDS.md` plus the current SB-* artifact packet.
5. Consult `next-round/LIVE_PROOF_MATRIX.md` before declaring a capability working.

ChatGPT remains lead/acceptance authority. Fable/Claude/Cursor remain workers. Existing product milestones in MILESTONE_MANIFEST.md remain binding. The NR-* items are closure work around existing artifacts, not replacement milestones or another 32 independent products.

## Reading routes

- Why this revision exists: `next-round/PLAN_AUDIT.md`.
- Implementation and integration boundaries: `next-round/INTEGRATION_CONTRACTS.md`.
- Real tests and exact stop conditions: `next-round/LIVE_PROOF_MATRIX.md`.
- Permissions, accounts, aliases, host and model prerequisites: `next-round/OWNER_GATES.md`.
- V2.4–V3.0 detail after V2.3: `next-round/V24_TO_V30_BUILD_SPEC.md`.
- Offline plan validation: `python3 social-bots/next-round/validate_plan.py --repo-root .`.

Only the validator command is supplied by this package. Runtime commands mentioned in contracts are implementation targets until their actual entrypoints are verified on the candidate SHA.

## The finish line

A pinned integrated candidate, independent tests, target-host runs, externally verifiable evidence for every required live gate, tested recovery, and a lead decision. File counts, fixture dashboards, model-written success summaries and disconnected modules do not satisfy it.

One fresh session = one SESSION_ONCE heartbeat. Resuming the same session does not create another heartbeat. Keep concise checkpoint reports and a durable next action; do not invent background execution when the process stops.
