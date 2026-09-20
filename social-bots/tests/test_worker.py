import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import worker, leasing, receipts, research  # noqa: E402
from runtime.heartbeat import read_heartbeat  # noqa: E402


class WorkerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_two_invocations_produce_receipts_and_heartbeat(self):
        r1 = worker.run_one_unit("cycle:social-a", "social-a", "social-a")
        r2 = worker.run_one_unit("cycle:social-a", "social-a", "social-a")
        self.assertTrue(r1["lease_released"])
        self.assertTrue(r2["lease_released"])
        # two start receipts recorded
        self.assertGreaterEqual(receipts.count_invocations("social-a"), 2)
        hb = read_heartbeat(r2["worker_id"])
        self.assertEqual(hb["status"], "done")
        self.assertGreater(hb["beats"], 1)

    def test_no_overlap_second_worker_rejected(self):
        # Manually hold the lease, then a worker unit must be rejected.
        held = leasing.acquire("cycle:social-b", "holder", ttl_seconds=120)
        with self.assertRaises(leasing.LeaseHeld):
            worker.run_one_unit("cycle:social-b", "social-b", "social-b")
        leasing.release(held)

    def test_stale_lease_recovered_with_reconcile(self):
        stale = leasing.acquire("cycle:social-c", "dead-worker", ttl_seconds=0)
        res = worker.run_one_unit("cycle:social-c", "social-c", "social-c")
        self.assertEqual(res["took_over_from"], stale.lease_id)
        self.assertTrue(res["lease_released"])

    def test_restart_resume_advances_state(self):
        # First unit with a fresh signal creates a candidate; a restart (new unit)
        # sees advanced fingerprint and cleanly no-actions instead of duplicating.
        s = research.Signal.make("resume signal", "captured", "unit-test",
                                 "https://example.org/r", "fixture", ["t"])
        research.capture("social-a", s)
        r1 = worker.run_one_unit("cycle:social-a", "social-a", "social-a")
        r2 = worker.run_one_unit("cycle:social-a", "social-a", "social-a")
        self.assertEqual(r1["chosen_action"], "CREATE_CANDIDATE")
        self.assertEqual(r2["chosen_action"], "NO_ACTION")


if __name__ == "__main__":
    unittest.main()
