# Mac-QA — Current Progress

Session: Mac Lane 1 — Independent V0.3 Acceptance (fresh session, heartbeat epoch T0 @ 2026-09-21T16:53:27Z, FAST_5M continuous).

- Task: Independent acceptance of SB-V03-004 (race-safe lease fencing + stale takeover). **COMPLETE — verdict SB-V03-004 ACCEPT-READY.**
- Implementation under test: Core SHA `796d4e390bd135167e5de2ff8f586bc07ac7f370` (source-equivalent to current core head `74a357d` for all lease/fence/worker/decision/test files — empty diff).
- Method: isolated read-only git worktree at the pinned SHA; independent QA harness (37/37 invariant checks pass) + Core regression re-run (focused 36 tests OK, full suite 130 OK). NO Core runtime source edits.
- Scenario results: POST-CYCLE TAKEOVER PASS; ACTIVE-CYCLE TAKEOVER PASS; MIGRATION FENCING PASS; FOCUSED CONCURRENCY/FENCING SUITE PASS.
- Report: `social-bots/worker-reports/mac-qa/SB-V03-004_ACCEPTANCE.md`. Evidence: `.../mac-qa/evidence/`. Harness: `social-bots/qa/acceptance/sbv03_004_independent_acceptance.py`.
- Blocker: none.
- Next: push QA report + evidence; stop new implementation work; continue 5-min heartbeats; wait for ChatGPT lead reconciliation. Do NOT self-mark ACCEPTED.
- Host/fs scope: Linux CCR container (POSIX fcntl.flock, ext filesystem); single-host/single-fs guarantee only. No public effect, no spend.
