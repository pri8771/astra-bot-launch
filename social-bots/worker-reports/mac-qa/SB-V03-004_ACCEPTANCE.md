# SB-V03-004 — Independent Acceptance Report (Mac-QA lane)

**Artifact:** SB-V03-004 — Race-safe lease fencing and stale takeover
**Milestone:** V0.3
**Lane:** Mac QA / Integration Control (independent acceptance — no Core ownership)
**Session:** Mac Lane 1, fresh session, heartbeat epoch T0 @ 2026-09-21T16:53:27Z
**Verdict:** **SB-V03-004 ACCEPT-READY** (lead reconciliation still required; this lane does NOT self-mark ACCEPTED)

---

## 1. Implementation under test (exact SHA)

- **Pinned Core implementation SHA:** `796d4e390bd135167e5de2ff8f586bc07ac7f370`
  (`SB-V03-005: structural admin boundary for content_history + all-surface bypass guard (LEAD-026)`)
- **Source-equivalence to a later Core head:** the current core head is
  `74a357d` (`windows-core: SB-V04-004 submitted`). `git diff` between the pinned
  SHA and `74a357d` is **empty** for every fencing-relevant file:
  `social-bots/runtime/leasing.py`, `runtime/worker.py`, `runtime/decision.py`,
  `runtime/state.py`, `tests/test_fencing.py`, `tests/test_concurrency.py`.
  Acceptance therefore holds for the pinned SHA and for the later source-equivalent
  Core head.
- **Verified against:** isolated **read-only** git worktree checked out at the
  pinned SHA. **No Core runtime source was edited by this lane.** All QA artifacts
  live under `social-bots/qa/acceptance/` and `social-bots/worker-reports/mac-qa/`.

## 2. Host / filesystem scope (documented truthfully)

- **Actual execution host:** Linux CCR container (`Linux 6.18.44 x86_64`),
  **not** a physical Mac. Recorded honestly per no-fabrication rule.
- **Python:** 3.11.15
- **Filesystem:** ext2/ext3 (single local filesystem).
- **Fencing primitive:** POSIX `fcntl.flock` present → `FLOCK_AVAILABLE = True`,
  i.e. the strong CAS path is exercised.
- **Guarantee scope:** single POSIX host, single filesystem. Cross-host and
  native-Windows fencing are **NOT** proven here and must not be assumed
  (matches the module's own scope note).

## 3. Method

Two independent evidence tracks:

1. **Independent QA harness** — `social-bots/qa/acceptance/sbv03_004_independent_acceptance.py`
   (QA-authored, imports Core runtime read-only from the pinned checkout). It
   re-derives the adversarial scenarios directly rather than trusting Core's own
   regression files; 37 explicit invariant checks.
2. **Core regression suites** re-run at the pinned SHA as a cross-check.

## 4. Exact commands

```
# isolated read-only worktree at the pinned SHA
git worktree add --detach <scratch>/core-verify 796d4e390bd135167e5de2ff8f586bc07ac7f370

# independent QA harness (37 invariant checks)
CORE_SRC=<scratch>/core-verify \
  python3 social-bots/qa/acceptance/sbv03_004_independent_acceptance.py

# focused Core regressions (run from the pinned worktree's social-bots/)
python3 -m unittest tests.test_leasing
python3 -m unittest tests.test_fencing
python3 -m unittest tests.test_concurrency
python3 -m unittest tests.test_worker
python3 -m unittest tests.test_decision
python3 -m unittest tests.test_isolation_decisions
python3 -m unittest discover -s tests            # full suite
```

## 5. Scenario results

### Scenario 1 — POST-CYCLE TAKEOVER — **PASS**
Force lease expiry + takeover *after* the cycle's durable commit but *before* the
finish/success receipt.
- Stale owner **cannot** write a success/finish receipt — no `*finish*.json` on
  disk; summary carries no `finish_receipt`.
- Stale owner **cannot imply successful ownership** — outcome is
  `fence_lost_post_commit`, `verified=False`; the only receipt is a truthful
  `failure` receipt with `candidate_succeeded=False`, `cycle_committed=True`.
- Takeover worker (`B-takeover`) is the sole on-disk owner after the race.
- Evidence: independent harness [1] (10/10 checks) + Core
  `test_stale_owner_cannot_write_success_finish_receipt_after_takeover`.

### Scenario 2 — ACTIVE-CYCLE TAKEOVER — **PASS**
Force lease expiry + takeover *while the original owner is still executing*
(at the cycle's fenced durable commit).
- `leasing.FenceLost` raised; old owner **commits no state** — no
  `decisions.jsonl`, `last_decision.json`, `bot_state.json`, persona-state file,
  `action_history.jsonl`, or analytics `events.jsonl`.
- **No effect eligibility** — experiments dir empty; publish queue empty.
- **No misleading successful evidence** — no success receipt; state never advanced
  (persona consumed ledger empty, runtime cycle counter 0).
- Old owner **cannot renew** after takeover (`leasing.LeaseError`).
- Takeover worker `B` (generation 2) is the sole owner; generation inspectable.
- Evidence: independent harness [2] (13/13 checks) + Core
  `test_old_owner_cycle_commits_nothing_after_midcycle_takeover`,
  `test_stale_owner_cannot_write_decision_log_after_takeover`,
  `test_worker_run_one_unit_stands_down_on_fence_loss`.

### Scenario 3 — MIGRATION FENCING — **PASS**
- **Load/migration is side-effect free before the fenced ownership commit:**
  loading legacy runtime state + staging a persona migration writes nothing —
  `bot_state.json` byte-identical after load, no persona-state file created.
- **Stale ownership cannot persist migration writes:** a stale owner that would
  migrate but loses the fence at commit persists no persona-state file and leaves
  the runtime state byte-for-byte unchanged (legacy intact, no migrated-marker).
- **Restart / idempotence sane:** a clean takeover worker completes a cycle,
  persists the migration exactly once (persona file present, runtime
  `migrated_to_persona=True`), preserves the legacy consumed signal (no data
  loss); a second cycle does **not** re-migrate and completes cleanly.
- Evidence: independent harness [3] (14/14 checks) + Core
  `test_stale_owner_in_migration_path_leaves_no_write`.

### Scenario 4 — FOCUSED CONCURRENCY / FENCING SUITE — **PASS**
Core regressions at the pinned SHA (test counts / output):

| Suite | Tests | Result |
|-------|------:|--------|
| `tests.test_leasing` | 4 | OK |
| `tests.test_fencing` | 10 | OK |
| `tests.test_concurrency` | 5 | OK |
| `tests.test_worker` | 4 | OK |
| `tests.test_decision` | 10 | OK |
| `tests.test_isolation_decisions` | 3 | OK |
| **Focused subtotal** | **36** | **OK** |
| Full suite (`unittest discover -s tests`) | 130 | OK |

Concurrency highlights (in `test_concurrency`): 40 rounds × 6 contenders for both
concurrent fresh-create and concurrent stale-takeover each yield **exactly one
owner** with all losers receiving an explicit non-owner (`LeaseHeld`) result; the
shared-runtime test proves no lost update across two personas over 25 rounds.

## 6. Independent harness summary

```
CHECKS: 37/37 passed
RESULT: ALL SCENARIO CHECKS PASS
```

Full transcripts:
- `social-bots/worker-reports/mac-qa/evidence/independent_acceptance_run.txt`
- `social-bots/worker-reports/mac-qa/evidence/regression_suites_run.txt`

## 7. Required-property coverage (from the SB-V03-004 packet)

- exactly one owner on fresh acquisition — **PASS** (test_concurrency)
- exactly one owner on stale takeover — **PASS** (test_concurrency)
- losing contender gets explicit non-owner result — **PASS** (`LeaseHeld`)
- active-cycle expiry → old owner cannot renew or commit — **PASS** (Scenario 2)
- no duplicate state / effect eligibility — **PASS** (Scenarios 2 & 3)
- reconciliation before new eligible effects — **PASS** (`reconcile_required`
  set on takeover; worker reconciles before work; test_worker
  `test_stale_lease_recovered_with_reconcile`)
- receipts identify lease/fence generation — **PASS** (start/finish/failure
  receipts carry `fence_generation`)
- lease validity covers the whole work unit, not just acquisition — **PASS**
  (`Fence` gates every durable commit)
- correct across restart — **PASS** (Scenario 3c; test_worker
  `test_restart_resume_advances_state`)
- ownership/fence generation inspectable after race — **PASS** (`leasing.inspect`)

## 8. Safety confirmation

- **No Core runtime source modifications** by this lane (verified read-only worktree).
- **No public/social actions.** Publishing is disabled in the runtime; the only
  external-effect surface (unpublished publish queue) was asserted empty for every
  fenced-out owner.
- **No paid API / no new spend.** No network calls; decision cycles ran on the
  default heuristic posture (no adaptive provider invoked); `ANTHROPIC_API_KEY`
  not used.
- **No secrets, no fabricated evidence, no destructive actions, no SwarmAI dependency.**

## 9. Verdict

All four required scenarios and all packet required-properties pass on the pinned
Core implementation `796d4e3` (source-equivalent to core head `74a357d`).

**SB-V03-004 ACCEPT-READY.**

This lane does **not** self-mark ACCEPTED. Handing off to ChatGPT lead for
reconciliation and canonical artifact-state update.
