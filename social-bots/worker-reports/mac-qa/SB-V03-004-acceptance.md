# SB-V03-004 — Independent Acceptance QA Report (Lane 3, Mac-QA / Acceptance)

- Artifact: **SB-V03-004** — Race-safe lease fencing and stale takeover (V0.3 gate)
- Lane: Mac-QA / Acceptance + Canary (Lane 3)
- Reviewer role: independent acceptance execution (no Core source edits)
- Date: 2026-09-21
- Verdict: **SB-V03-004 ACCEPT-READY** (all required scenarios PASS). Not self-marked ACCEPTED — lead audit owns final ACCEPT.

> Delivery note: this session's authorized git branch is
> `claude/social-bots-mac-qa-lane3-ordpt6`. Per session git policy the report is
> pushed there rather than directly to `claude/social-bots-mac-qa-control`; the
> lead/operator can fast-forward or cherry-pick it onto the Mac-QA control branch.
> Content is independent of push location.

## Exact Core implementation tested

The SHA named in the packet (`796d4e390bd135167e5de2ff8f586bc07ac7f370`) and the
lead-review head (`2cab7219edab5c2f3a7123fad1546f43a2fc140c`) are **not present**
in this repository's object graph (`git cat-file` = missing). The packet permits a
**"later source-equivalent Core head."** I tested the runtime carried on the
canary branch head, which contains the active-cycle fencing repair:

| Item | Value |
|---|---|
| Branch head tested | `claude/social-bots-v04-live-canary` @ `8febedb7987500b7cce1c9cc3d38e5b4be177c02` |
| `runtime/` last commit | `175f741fcedace3113191a847d6a7568d77b9cde` (2026-09-21) |
| `runtime/leasing.py` blob sha1 | `8729d42d7d60d1f40739edb52167ada0960377cd` |
| `runtime/worker.py` blob sha1 | `4d326c132b18d112de4733488b400088e457dfd9` |
| `runtime/decision.py` blob sha1 | `b1f804d500df33a2a11bf4ef8687ba9ac6662d62` |
| `runtime/isolation.py` blob sha1 | `7f3b716dfe11d57bdd0ed9f7887e6f3c817285ce` |
| `runtime/receipts.py` blob sha1 | `af7d43b0d03e274b808328a569d7088b195c3fca` |
| `runtime/state.py` blob sha1 | `45452b234be8e3cc27b274686ee87f18d28ffedc` |

## Host / filesystem scope

- OS: `Linux vm 6.18.44-fc-v37 x86_64`, single host.
- Python: `3.11.15`.
- Filesystem: single local POSIX filesystem; fencing lock is `fcntl.flock`
  (`flock_available=true` confirmed by the cross-process harness).
- **Scope limitation (as required by the packet):** single-POSIX-host, single-FS
  only. Native-Windows and cross-host/NFS fencing are **NOT** proven here and must
  not be assumed. This matches the source's own documented scope.

## Exact commands

```
cd social-bots
export PYTHONPATH="$PWD"
python3 -m unittest tests.test_fencing tests.test_leasing tests.test_concurrency \
                    tests.test_worker tests.test_decision tests.test_isolation
python3 -m unittest discover -s tests -p 'test_*.py'
python3 bin/prove_cross_process_lock.py
```

Full captured output: `SB-V03-004-evidence.txt` (this directory).

## Scenario results (mapped to the four required verifications)

### 1. Post-cycle lease expiry / takeover — stale owner cannot write a successful completion/finish receipt — **PASS**
- `tests.test_fencing.test_stale_owner_cannot_write_decision_log_after_takeover` — after A's lease expires and B takes gen 2, A's resumed commit raises `FenceLost` and writes **no** decisions.jsonl, last_decision.json, bot_state.json, persona file, publish-queue entry, action_history, or analytics events.
- `tests.test_fencing.test_fenced_commit_refuses_after_fence_loss` — the commit body never runs after fence loss.
- `tests.test_fencing.test_worker_run_one_unit_stands_down_on_fence_loss` — worker stands down.
- `tests.test_worker.test_stale_lease_recovered_with_reconcile` — takeover sets reconcile.

### 2. Active-cycle lease expiry / takeover — old owner cannot commit state/effect evidence after losing ownership — **PASS**
- `tests.test_fencing.test_old_owner_cycle_commits_nothing_after_midcycle_takeover` — expiry+takeover forced **at the commit boundary** inside `decision.run_cycle()`; old owner commits nothing; runtime cycle counter stays 0; signal remains unconsumed for the new owner.
- `tests.test_fencing.test_fence_invalid_after_takeover` — old owner's `Fence.valid()` → False, `Fence.check()` → `FenceLost`, `renew()` → `LeaseError`.
- `tests.test_fencing.test_generation_increments_on_takeover_and_is_inspectable` — monotonic `generation` fence token (1→2), `took_over_from` set, `reconcile_required` set, inspectable on disk.
- `tests.test_fencing.test_decision_log_and_last_decision_written_inside_fence` — decision log + last-decision are written **inside** the fenced closure (the SB-V03-004 repair regression), not after the ownership lock.

### 3. Migration / load — migration remains side-effect-free until the valid fenced commit — **PASS**
- `tests.test_fencing.test_stale_owner_in_migration_path_leaves_no_write` — a fenced-out owner in the legacy-migration path leaves the runtime state file **byte-for-byte unchanged** (no migration marker, no persona file).
- `tests.test_isolation.test_persona_load_is_side_effect_free_during_migration`
- `tests.test_isolation.test_run_cycle_commits_runtime_with_final_migration_marker`
- `tests.test_isolation.test_migration_recovers_when_marker_set_but_persona_file_missing`

### 4. Focused lease / fencing / concurrency suite — stale owner cannot write successful state/effect/completion evidence after takeover — **PASS**
- `tests.test_leasing` (4/4): atomic acquire rejects overlap; release only by owner; renew keeps ownership; stale takeover sets reconcile.
- `tests.test_concurrency` (5/5): concurrent fresh create → single owner; concurrent **stale** takeover → single owner; runtime-scoped locking; no lost update.
- `tests.test_fencing` (9/9).
- **Real cross-process proof** — `bin/prove_cross_process_lock.py` spawns 8 independent OS interpreters (spawn start method) contending for one lease simultaneously:
  ```json
  {"acquired_count": 1, "held_count": 7, "error_count": 0,
   "processes_spawned": 8, "single_owner_ok": true, "flock_available": true}
  ```
  Exit 0. Exactly one owner; seven `LeaseHeld` rejections; zero double-ownership.

## Test totals

| Suite | Ran | Result |
|---|---|---|
| test_fencing | 9 | OK |
| test_leasing | 4 | OK |
| test_concurrency | 5 | OK |
| test_worker | 4 | OK |
| test_decision | 10 | OK |
| test_isolation | 12 | OK |
| **Full `unittest discover`** | **115** | **OK** |
| prove_cross_process_lock.py | 8 procs | single_owner_ok=true, exit 0 |

## Acceptance-criteria coverage (from the packet)

- concurrent fresh acquisition, multiple contenders → exactly one owner — **met**.
- concurrent stale takeover, multiple contenders → exactly one owner — **met** (unit + real multi-process).
- active worker lease forced to expire mid-execution, then takeover: old owner cannot renew or commit — **met**.
- ownership/fence generation inspectable after the race — **met** (`leasing.inspect`).
- no duplicate state/effect eligibility — **met**.
- reconciliation happens before new owner performs eligible work — **met**.
- all prior lease tests pass — **met** (115/115).
- host/filesystem scope explicitly documented; no cross-host/native-Windows assumption — **met** (above).

## No-public-effect / no-spend confirmation

All verification is offline: `unittest` + a local multiprocessing harness under
temp `SBOTS_HOME` dirs. No network, no social platform, no publishing, no spend,
no credentials, no Core source edits, no destructive actions.

## Concrete defects found

**None.** All required and acceptance scenarios pass on the tested source-equivalent head.

## Verdict

**SB-V03-004 ACCEPT-READY.** Final ACCEPT is the lead's to grant; this lane does
not self-mark ACCEPTED.
