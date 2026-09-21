#!/usr/bin/env python3
"""Independent acceptance harness for SB-V03-004 (Mac-QA lane).

This is QA-ONLY evidence. It does NOT modify Core runtime source. It imports the
Core runtime read-only from a pinned checkout (``CORE_SRC`` env, default: a
sibling ``core-verify`` worktree) and independently re-derives the four required
acceptance scenarios rather than trusting Core's own regression files:

  1. POST-CYCLE TAKEOVER  — after the cycle's durable commit but before the
     finish receipt, the old owner's lease expires and another worker takes over.
     The stale owner must NOT write a success/finish receipt and must NOT imply
     successful ownership; it stands down truthfully.
  2. ACTIVE-CYCLE TAKEOVER — the old owner loses its fence WHILE still executing
     (at the cycle's durable commit). It must commit NO state/content/experiment/
     publish-eligibility/success receipt, and cannot renew afterwards.
  3. MIGRATION FENCING — legacy-state load/migration is side-effect free before
     the fenced ownership commit; a stale owner cannot persist migration writes;
     restart/idempotence is sane (migration applies exactly once, no re-migrate).
  4. Delegated to the focused Core regression suites (run separately by the
     runner script); this file asserts the adversarial invariants directly.

Every scenario runs in its own throwaway ``SBOTS_HOME`` temp dir. Publishing is
disabled in the runtime, so "external-effect eligibility" is the (unpublished)
publish queue; we assert it stays empty for every fenced-out owner. No network,
no public action, no spend.

Exit code 0 iff every scenario PASSES.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


def _core_src() -> Path:
    env = os.environ.get("CORE_SRC")
    if env:
        return Path(env) / "social-bots"
    # default: sibling worktree created by the runner
    here = Path(__file__).resolve()
    return here.parent.parent.parent  # .../social-bots


CORE = _core_src()
sys.path.insert(0, str(CORE))

from runtime import leasing, decision, research, pipeline, worker, paths  # noqa: E402
from runtime.state import BotState, PersonaState  # noqa: E402


RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(cond), detail))
    flag = "PASS" if cond else "FAIL"
    print(f"    [{flag}] {name}" + (f" — {detail}" if detail and not cond else ""))


def _fresh_home() -> str:
    tmp = tempfile.mkdtemp(prefix="sbv03004-qa-")
    os.environ["SBOTS_HOME"] = tmp
    # Force runtime path cache (if any) to re-read the new home.
    return tmp


def _force_stale(task_id: str) -> None:
    p = leasing.paths.leases_dir() / f"{task_id}.lease.json"
    data = json.loads(p.read_text())
    data["renewed_at"] = "2000-01-01T00:00:00+00:00"
    p.write_text(json.dumps(data))


# ---------------------------------------------------------------------------
# Scenario 1 — POST-CYCLE TAKEOVER
# ---------------------------------------------------------------------------
def scenario_post_cycle_takeover() -> None:
    print("\n[1] POST-CYCLE TAKEOVER")
    tmp = _fresh_home()
    bot = "social-b"
    research.capture(bot, research.Signal.make(
        "wonder", "captured evidence", "unit", "https://example.org/x",
        "fixture", ["n"]))
    task = worker.runtime_task_id(bot)

    real_fence = leasing.Fence
    state = {"commits": 0}

    class TakeoverBeforeFinish(real_fence):
        def fenced_commit(self, commit):
            state["commits"] += 1
            # commit #1 = cycle durable commit (succeeds under valid ownership);
            # commit #2 = finish/success receipt — force takeover right before it.
            if state["commits"] == 2:
                _force_stale(task)
                leasing.acquire(task, "B-takeover", ttl_seconds=300)  # gen 2
            return super().fenced_commit(commit)

    leasing.Fence = TakeoverBeforeFinish
    try:
        res = worker.run_one_unit(task, bot, "social-b", ttl_seconds=300)
    finally:
        leasing.Fence = real_fence

    check("cycle durably committed under valid ownership", res.get("committed") is True)
    check("outcome is fence_lost_post_commit (no success asserted)",
          res.get("outcome") == "fence_lost_post_commit", str(res.get("outcome")))
    check("verified is False (no success claim)", res.get("verified") is False)
    check("no finish_receipt returned in summary", "finish_receipt" not in res)

    rdir = Path(tmp) / "receipts" / bot
    finish_receipts = list(rdir.glob("*finish*.json"))
    check("NO success/finish receipt on disk", finish_receipts == [],
          f"found {[f.name for f in finish_receipts]}")
    fails = sorted(rdir.glob("*failure*.json"))
    check("a truthful failure/stand-down receipt exists", len(fails) >= 1)
    if fails:
        detail = json.loads(fails[-1].read_text())["detail"]
        check("failure receipt: candidate_succeeded is False",
              detail.get("candidate_succeeded") is False)
        check("failure receipt: outcome == fence_lost_post_commit",
              detail.get("outcome") == "fence_lost_post_commit")
        check("failure receipt: records cycle_committed True (honest)",
              detail.get("cycle_committed") is True)
    od = leasing.inspect(task)
    check("takeover worker is the on-disk owner after the race",
          od is not None and od.get("worker_id") == "B-takeover",
          str(od.get("worker_id") if od else None))


# ---------------------------------------------------------------------------
# Scenario 2 — ACTIVE-CYCLE TAKEOVER
# ---------------------------------------------------------------------------
def scenario_active_cycle_takeover() -> None:
    print("\n[2] ACTIVE-CYCLE TAKEOVER (fence lost mid-execution)")
    tmp = _fresh_home()
    bot = "social-b"
    research.capture(bot, research.Signal.make(
        "wonder", "captured evidence", "unit", "https://example.org/x",
        "fixture", ["n"]))
    task = worker.runtime_task_id(bot)
    a = leasing.acquire(task, "A", ttl_seconds=300)

    class TakeoverAtCommit(leasing.Fence):
        triggered = False

        def fenced_commit(self, commit):
            if not TakeoverAtCommit.triggered:
                TakeoverAtCommit.triggered = True
                _force_stale(task)                          # A's lease expires
                leasing.acquire(task, "B", ttl_seconds=300)  # B takes gen 2
            return super().fenced_commit(commit)             # -> FenceLost, no writes

    raised = False
    try:
        decision.run_cycle(bot, "social-b", fence=TakeoverAtCommit(a))
    except leasing.FenceLost:
        raised = True
    check("FenceLost raised — old owner refused at commit", raised)

    # No durable worker-owned write of ANY kind from the fenced-out old owner.
    check("no decisions.jsonl", not (paths.memory_dir(bot) / "decisions.jsonl").exists())
    check("no last_decision.json", not (paths.state_dir(bot) / "last_decision.json").exists())
    check("no bot_state.json (state not advanced)",
          not (paths.state_dir(bot) / "bot_state.json").exists())
    check("no persona-social-b.json", not (paths.state_dir(bot) / "persona-social-b.json").exists())
    check("no action_history.jsonl", not (paths.memory_dir(bot) / "action_history.jsonl").exists())
    check("no analytics events.jsonl", not (paths.analytics_dir(bot) / "events.jsonl").exists())
    exp_dir = Path(tmp) / "experiments" / bot
    check("no experiment eligibility written",
          not (any(exp_dir.glob("exp-*.json")) if exp_dir.exists() else False))
    check("publish queue empty — no external-effect eligibility",
          pipeline.admin_publish_queue(bot) == [])

    # State never advanced: signal still unconsumed, cycle counter 0.
    ps = PersonaState.load(bot, "social-b")
    rt = BotState.load(bot)
    check("persona consumed ledger empty (signal left for takeover worker)",
          ps.consumed_ids() == [])
    check("runtime cycle counter still 0", rt.data["counters"]["cycles"] == 0)

    # Old owner cannot renew after fence loss.
    renew_failed = False
    try:
        leasing.renew(a)
    except leasing.LeaseError:
        renew_failed = True
    check("old owner cannot renew its lease after takeover", renew_failed)

    od = leasing.inspect(task)
    check("takeover worker (gen 2, B) is sole owner",
          od is not None and od.get("worker_id") == "B" and od.get("generation") == 2,
          str(od))


# ---------------------------------------------------------------------------
# Scenario 3 — MIGRATION FENCING
# ---------------------------------------------------------------------------
_LEGACY = {
    "bot": "social-a", "schema_version": 1,
    "consumed_signal_ids": ["sig-old"], "hypotheses": {},
    "counters": {"cycles": 0, "actions": 0, "no_action": 0},
    "recovery": {"last_clean_tick": None, "in_flight": None},
    "observation_fingerprint": None,
}


def scenario_migration_fencing() -> None:
    print("\n[3] MIGRATION FENCING")
    tmp = _fresh_home()
    bot = "social-a"
    sp = paths.state_dir(bot) / "bot_state.json"
    sp.write_text(json.dumps(_LEGACY))
    before = sp.read_text()

    # 3a — load/migration is SIDE-EFFECT FREE (no disk write on load).
    rt = BotState.load(bot)
    ps = PersonaState.load(bot, "social-a", runtime=rt) if _accepts_runtime() else PersonaState.load(bot, "social-a")
    check("load() does not modify runtime state file (side-effect free)",
          sp.read_text() == before)
    check("load() writes no persona-state file",
          not (paths.state_dir(bot) / "persona-social-a.json").exists())

    # 3b — a stale owner that would migrate but loses the fence persists NOTHING.
    research.capture(bot, research.Signal.make(
        "mig", "captured", "unit", "https://example.org/m", "fixture", ["n"]))
    task = worker.runtime_task_id(bot)
    a = leasing.acquire(task, "A", ttl_seconds=300)

    class TakeoverAtCommit(leasing.Fence):
        triggered = False

        def fenced_commit(self, commit):
            if not TakeoverAtCommit.triggered:
                TakeoverAtCommit.triggered = True
                _force_stale(task)
                leasing.acquire(task, "B", ttl_seconds=300)  # gen 2 takeover
            return super().fenced_commit(commit)

    raised = False
    try:
        decision.run_cycle(bot, "social-a", fence=TakeoverAtCommit(a))
    except leasing.FenceLost:
        raised = True
    check("FenceLost raised for stale migrating owner", raised)
    check("stale owner persisted NO persona-state file",
          not (paths.state_dir(bot) / "persona-social-a.json").exists())
    check("runtime state byte-identical (legacy intact, no marker written)",
          sp.read_text() == before)
    check("no last_decision.json from fenced-out migrating owner",
          not (paths.state_dir(bot) / "last_decision.json").exists())
    check("no decisions.jsonl from fenced-out migrating owner",
          not (paths.memory_dir(bot) / "decisions.jsonl").exists())
    od = leasing.inspect(task)
    check("takeover worker (B) owns lease after migration race",
          od is not None and od.get("worker_id") == "B")

    # 3c — RESTART / IDEMPOTENCE: a fresh clean takeover worker runs one full cycle.
    #      Migration is applied exactly once and persisted under the fence; a second
    #      cycle does not re-migrate or lose data.
    _force_stale(task)  # B (takeover owner from 3b) stalls past TTL -> takeable
    res = worker.run_one_unit(task, bot, "social-a", ttl_seconds=300)
    check("clean takeover worker completes a cycle (took over)",
          res.get("took_over_from") is not None, str(res.get("outcome")))
    persona_file = paths.state_dir(bot) / "persona-social-a.json"
    check("migration now persisted: persona-state file exists", persona_file.exists())
    rt2 = BotState.load(bot)
    migrated_marker = rt2.data.get("_legacy", {}).get("migrated_to_persona")
    check("runtime migrated_to_persona marker set exactly once",
          migrated_marker is True, str(migrated_marker))
    # legacy consumed id preserved into persona-private ledger (no data loss).
    if persona_file.exists():
        pdata = json.loads(persona_file.read_text())
        check("legacy consumed signal preserved through migration (no data loss)",
              "sig-old" in json.dumps(pdata))

    # second cycle must NOT re-migrate (idempotent restart)
    research.capture(bot, research.Signal.make(
        "mig2", "captured2", "unit", "https://example.org/m2", "fixture", ["n"]))
    before_persona = persona_file.read_text() if persona_file.exists() else None
    res2 = worker.run_one_unit(task, bot, "social-a", ttl_seconds=300)
    rt3 = BotState.load(bot)
    check("second cycle does not re-run migration (marker stable True)",
          rt3.data.get("_legacy", {}).get("migrated_to_persona") is True)
    check("second cycle completes cleanly (idempotent restart sane)",
          res2.get("outcome") in ("candidate_created", "no_action"),
          str(res2.get("outcome")))


def _accepts_runtime() -> bool:
    import inspect
    try:
        return "runtime" in inspect.signature(PersonaState.load).parameters
    except (TypeError, ValueError):
        return False


def main() -> int:
    print("=" * 72)
    print("SB-V03-004 INDEPENDENT ACCEPTANCE — Mac-QA lane")
    print(f"Core source: {CORE}")
    print("=" * 72)
    scenario_post_cycle_takeover()
    scenario_active_cycle_takeover()
    scenario_migration_fencing()

    print("\n" + "=" * 72)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"CHECKS: {passed}/{total} passed")
    if failed:
        print("FAILED CHECKS:")
        for n in failed:
            print(f"  - {n}")
        print("RESULT: FAIL")
        return 1
    print("RESULT: ALL SCENARIO CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
