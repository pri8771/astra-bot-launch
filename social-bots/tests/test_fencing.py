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
from runtime import leasing, decision, research, pipeline, worker  # noqa: E402
from runtime.state import BotState  # noqa: E402


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
        # State never advanced: no bot_state written, so a fresh load shows the
        # signal still unconsumed (the takeover worker will decide on it).
        st = BotState.load(bot)
        self.assertEqual(st.consumed_ids(), [])
        self.assertEqual(st.data["counters"]["cycles"], 0)
        # Ownership is now the takeover worker's, inspectable after the race.
        self.assertEqual(leasing.inspect(task)["generation"], 2)
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
