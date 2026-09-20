import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import leasing  # noqa: E402


class LeasingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_atomic_acquire_rejects_overlap(self):
        a = leasing.acquire("t1", "worker-A")
        with self.assertRaises(leasing.LeaseHeld):
            leasing.acquire("t1", "worker-B")
        self.assertTrue(leasing.release(a))

    def test_release_only_by_owner(self):
        a = leasing.acquire("t2", "worker-A")
        # Fake a different lease id trying to release.
        fake = leasing.Lease(**{**a.__dict__, "lease_id": "other"})
        self.assertFalse(leasing.release(fake))
        self.assertTrue(leasing.release(a))

    def test_stale_takeover_sets_reconcile(self):
        a = leasing.acquire("t3", "worker-A", ttl_seconds=0)  # immediately stale
        b = leasing.acquire("t3", "worker-B", ttl_seconds=120)
        self.assertTrue(b.reconcile_required)
        self.assertEqual(b.took_over_from, a.lease_id)
        # A can no longer renew — it lost the lease.
        with self.assertRaises(leasing.LeaseError):
            leasing.renew(a)
        self.assertTrue(leasing.release(b))

    def test_renew_keeps_ownership(self):
        a = leasing.acquire("t4", "worker-A", ttl_seconds=120)
        leasing.renew(a)
        # still held against a second worker
        with self.assertRaises(leasing.LeaseHeld):
            leasing.acquire("t4", "worker-B")
        leasing.release(a)


if __name__ == "__main__":
    unittest.main()
