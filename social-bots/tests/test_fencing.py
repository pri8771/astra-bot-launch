"""SB-V03-004 — active-cycle lease fencing.

The prior flock CAS made *acquisition* single-owner, but it did not stop a worker
whose lease expired mid-cycle from committing after another worker took over.
These regressions prove the fencing-token guarantee:

- a stale takeover bumps a monotonically increasing ``generation`` (the fence
  token) and the prior owner's fence becomes permanently invalid;
- forcing the active worker's lease to expire *while it is still executing* and
  then allowing a takeover means the old owner cannot renew OR commit — no state,
  content, experiment, publish-queue entry, or success receipt;
- the takeover worker becomes the sole owner and its work commits;
- ownership/fence generation is inspectable after the race;
- reconciliation happens before the new owner performs eligible work.

Scope: single POSIX host, single filesystem (``fcntl.flock``). Cross-host or
native-Windows fencing is NOT proven here and must not be assumed.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import leasing, decision, research, pipeline, worker, paths  # noqa: E402
from runtime.state import BotState, PersonaState  # noqa: E402


def _force_stale(task_id):
    """Rewrite the on-disk lease so it is already past its TTL (as if the owner
    stalled past expiry), without deleting it — a takeover is still required to
    change ownership."""
    p = leasing.paths.leases_dir() / f"{task_id}.lease.json"
    data = json.loads(p.read_text())
    data["renewed_at"] = "2000-01-01T00:00:00+00:00"
    p.write_text(json.dumps(data))


class LeaseFencingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_generation_increments_on_takeover_and_is_inspectable(self):
        a = leasing.acquire("t", "A", ttl_seconds=0)  # immediately stale
        self.assertEqual(a.generation, 1)
        b = leasing.acquire("t", "B", ttl_seconds=300)
        self.assertEqual(b.generation, 2)
        self.assertEqual(b.took_over_from, a.lease_id)
        self.assertTrue(b.reconcile_required)
        on_disk = leasing.inspect("t")
        self.assertEqual(on_disk["generation"], 2)
        self.assertEqual(on_disk["worker_id"], "B")
        leasing.release(b)

    def test_fence_invalid_after_takeover(self):
        a = leasing.acquire("t", "A", ttl_seconds=300)
        fa = leasing.Fence(a)
        self.assertTrue(fa.valid())
        _force_stale("t")
        b = leasing.acquire("t", "B", ttl_seconds=300)  # takeover -> gen 2
        fb = leasing.Fence(b)
        self.assertFalse(fa.valid(), "old owner's fence must be invalid after takeover")
        self.assertTrue(fb.valid())
        with self.assertRaises(leasing.FenceLost):
            fa.check()
        # the old owner also cannot renew
        with self.assertRaises(leasing.LeaseError):
            leasing.renew(a)

    def test_fenced_commit_refuses_after_fence_loss(self):
        a = leasing.acquire("t", "A", ttl_seconds=300)
        fa = leasing.Fence(a)
        _force_stale("t")
        leasing.acquire("t", "B", ttl_seconds=300)  # takeover
        wrote = {"done": False}
        with self.assertRaises(leasing.FenceLost):
            fa.fenced_commit(lambda: wrote.__setitem__("done", True))
        self.assertFalse(wrote["done"], "commit body must NOT run after fence loss")

    def test_old_owner_cycle_commits_nothing_after_midcycle_takeover(self):
        # Force expiry + takeover at the exact commit boundary, then prove the
        # old owner's decision cycle writes NO durable artifact.
        bot = "social-b"
        sig = research.Signal.make("wonder", "captured evidence", "unit",
                                   "https://example.org/x", "fixture", ["n"])
        research.capture(bot, sig)
        task = worker.runtime_task_id(bot)
        a = leasing.acquire(task, "A", ttl_seconds=300)

        class TakeoverAtCommit(leasing.Fence):
            """A fence whose owner is superseded the instant it tries to commit."""
            triggered = False

            def fenced_commit(self, commit):
                if not TakeoverAtCommit.triggered:
                    TakeoverAtCommit.triggered = True
                    _force_stale(task)
                    leasing.acquire(task, "B", ttl_seconds=300)  # gen 2 takeover
                return super().fenced_commit(commit)

        with self.assertRaises(leasing.FenceLost):
            decision.run_cycle(bot, "social-b", fence=TakeoverAtCommit(a))

        # No durable side effect from the fenced-out old owner:
        exp_dir = Path(self.tmp) / "experiments" / bot
        self.assertFalse(any(exp_dir.glob("exp-*.json")) if exp_dir.exists() else False)
        self.assertEqual(pipeline.publish_queue(bot), [])
        # SB-V03-004: the decision log and last-decision are ALSO fenced — a
        # fenced-out owner writes neither.
        self.assertFalse((paths.memory_dir(bot) / "decisions.jsonl").exists())
        self.assertFalse((paths.state_dir(bot) / "last_decision.json").exists())
        # State never advanced: no runtime/persona state written, so a fresh load
        # shows the signal still unconsumed (the takeover worker will decide it).
        rt = BotState.load(bot)
        ps = PersonaState.load(bot, "social-b")
        self.assertEqual(ps.consumed_ids(), [])
        self.assertEqual(rt.data["counters"]["cycles"], 0)
        # Ownership is now the takeover worker's, inspectable after the race.
        self.assertEqual(leasing.inspect(task)["generation"], 2)
        self.assertEqual(leasing.inspect(task)["worker_id"], "B")

    def test_decision_log_and_last_decision_written_inside_fence(self):
        # SB-V03-004 repair regression. The decision log + last-decision writes
        # used to run AFTER the fenced region (outside the ownership lock), so a
        # stalled ex-owner could write those stale, later-cycle-owned records
        # after a takeover. They must now be part of the fenced closure. We probe
        # INSIDE the closure: the files must already exist by the time the
        # ownership-locked commit body returns. (Against the old ordering this
        # probe sees them absent and the test fails.)
        bot = "social-b"
        research.capture(bot, research.Signal.make(
            "wonder", "captured evidence", "unit", "https://example.org/x",
            "fixture", ["n"]))
        task = worker.runtime_task_id(bot)
        a = leasing.acquire(task, "A", ttl_seconds=300)
        seen = {}

        class ProbeFence(leasing.Fence):
            def fenced_commit(self, commit):
                def wrapped():
                    result = commit()  # runs the full durable commit body
                    seen["decisions"] = (paths.memory_dir(bot) / "decisions.jsonl").exists()
                    seen["last_decision"] = (paths.state_dir(bot) / "last_decision.json").exists()
                    return result
                return super().fenced_commit(wrapped)

        decision.run_cycle(bot, "social-b", fence=ProbeFence(a))
        self.assertTrue(seen.get("decisions"),
                        "decisions.jsonl must be written inside the fenced commit")
        self.assertTrue(seen.get("last_decision"),
                        "last_decision.json must be written inside the fenced commit")
        leasing.release(a)

    def test_stale_owner_cannot_write_decision_log_after_takeover(self):
        # Full adversarial lifecycle: A owns gen 1 and stalls right at its commit;
        # the lease expires; B takes gen 2; A resumes and attempts to commit. A
        # must write NO later cycle-owned durable record — not the decision log,
        # last-decision, state, experiments, queue, analytics or action history.
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
                    _force_stale(task)                       # A's lease expires
                    leasing.acquire(task, "B", ttl_seconds=300)  # B takes gen 2
                return super().fenced_commit(commit)         # -> FenceLost, no writes

        with self.assertRaises(leasing.FenceLost):
            decision.run_cycle(bot, "social-b", fence=TakeoverAtCommit(a))

        # Inspect every worker-owned durable surface: none carries A's cycle.
        self.assertFalse((paths.memory_dir(bot) / "decisions.jsonl").exists())
        self.assertFalse((paths.state_dir(bot) / "last_decision.json").exists())
        self.assertFalse((paths.state_dir(bot) / "bot_state.json").exists())
        self.assertFalse((paths.state_dir(bot) / "persona-social-b.json").exists())
        self.assertEqual(pipeline.publish_queue(bot), [])
        self.assertFalse((paths.memory_dir(bot) / "action_history.jsonl").exists())
        self.assertFalse((paths.analytics_dir(bot) / "events.jsonl").exists())
        exp_dir = Path(self.tmp) / "experiments" / bot
        self.assertFalse(any(exp_dir.glob("exp-*.json")) if exp_dir.exists() else False)
        # B is the sole owner after the race.
        self.assertEqual(leasing.inspect(task)["worker_id"], "B")

    def test_stale_owner_in_migration_path_leaves_no_write(self):
        # SB-V03-004 LEAD-019: a worker whose cycle would trigger the legacy
        # persona-state migration, but which loses the fence at commit, must leave
        # NO persona-state file and NO runtime migration-marker write behind — the
        # load/migration path is side-effect free; persistence is fenced only.
        import json
        bot = "social-a"
        # Seed a legacy runtime state that would trigger migration for social-a.
        legacy = {"bot": bot, "schema_version": 1,
                  "consumed_signal_ids": ["sig-old"], "hypotheses": {},
                  "counters": {"cycles": 0, "actions": 0, "no_action": 0},
                  "recovery": {"last_clean_tick": None, "in_flight": None},
                  "observation_fingerprint": None}
        sp = paths.state_dir(bot) / "bot_state.json"
        sp.write_text(json.dumps(legacy))
        before = sp.read_text()
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

        with self.assertRaises(leasing.FenceLost):
            decision.run_cycle(bot, "social-a", fence=TakeoverAtCommit(a))

        # The fenced-out owner wrote nothing: no persona file, and the runtime
        # state file is byte-for-byte unchanged (legacy intact, no marker written).
        self.assertFalse((paths.state_dir(bot) / "persona-social-a.json").exists())
        self.assertEqual(sp.read_text(), before,
                         "runtime state must be untouched after fenced-out migration cycle")
        self.assertFalse((paths.state_dir(bot) / "last_decision.json").exists())
        self.assertFalse((paths.memory_dir(bot) / "decisions.jsonl").exists())
        self.assertEqual(leasing.inspect(task)["worker_id"], "B")

    def test_worker_run_one_unit_stands_down_on_fence_loss(self):
        bot = "social-b"
        sig = research.Signal.make("wonder", "captured evidence", "unit",
                                   "https://example.org/x", "fixture", ["n"])
        research.capture(bot, sig)
        task = worker.runtime_task_id(bot)

        # Patch the Fence used inside run_one_unit so ownership is lost at commit.
        real_fence = leasing.Fence
        state = {"tripped": False}

        class TakeoverFence(real_fence):
            def fenced_commit(self, commit):
                if not state["tripped"]:
                    state["tripped"] = True
                    _force_stale(task)
                    leasing.acquire(task, "B-takeover", ttl_seconds=300)
                return super().fenced_commit(commit)

        leasing.Fence = TakeoverFence
        try:
            res = worker.run_one_unit(task, bot, "social-b", ttl_seconds=300)
        finally:
            leasing.Fence = real_fence

        self.assertEqual(res["outcome"], "fence_lost")
        self.assertFalse(res["committed"])
        # took_over_by_generation reflects the new owner (gen 2).
        self.assertEqual(res["took_over_by_generation"], 2)
        # No success artifacts; the takeover worker still owns the lease.
        self.assertEqual(pipeline.publish_queue(bot), [])
        self.assertEqual(leasing.inspect(task)["worker_id"], "B-takeover")
        # The stand-down receipt records fence loss, never candidate success.
        fin = sorted((Path(self.tmp) / "receipts" / bot).glob("*failure*.json"))[-1]
        detail = json.loads(fin.read_text())["detail"]
        self.assertEqual(detail["outcome"], "fence_lost")
        self.assertFalse(detail["candidate_succeeded"])

    def test_takeover_worker_becomes_owner_and_commits(self):
        # After the old owner is fenced out, a fresh worker on the same task runs
        # a real cycle to completion (reconciles first, then commits).
        bot = "social-b"
        sig = research.Signal.make("wonder", "captured evidence", "unit",
                                   "https://example.org/x", "fixture", ["n"])
        research.capture(bot, sig)
        task = worker.runtime_task_id(bot)
        leasing.acquire(task, "A", ttl_seconds=0)  # stale placeholder from a dead owner
        res = worker.run_one_unit(task, bot, "social-b", ttl_seconds=300)
        self.assertIn(res["outcome"], ("candidate_created",))
        self.assertTrue(res["verified"])
        self.assertEqual(res["took_over_from"] is not None, True)
        self.assertEqual(len(pipeline.publish_queue(bot)), 1)
        # A clean finish releases the lease, so it is gone from disk...
        self.assertIsNone(leasing.inspect(task))
        # ...but the finish receipt records the fence generation it committed
        # under (>= 2, i.e. it took over the dead owner's gen 1).
        fin = sorted((Path(self.tmp) / "receipts" / bot).glob("*finish*.json"))[-1]
        self.assertGreaterEqual(json.loads(fin.read_text())["detail"]["fence_generation"], 2)


if __name__ == "__main__":
    unittest.main()
