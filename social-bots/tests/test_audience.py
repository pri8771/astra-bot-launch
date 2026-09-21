"""SB-V14-001 — audience memory acceptance tests."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import audience as au  # noqa: E402

SEG = {"topic": "science", "format": "short-video", "timezone_band": "US-eastern"}


def _obs(stance, days_ago=0, weight=1.0, cid="c-1"):
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return au.Observation.make(stance, {"content_id": cid, "experiment_id": "e-1"},
                               weight=weight, observed_at=ts)


class AudienceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_no_evidence_is_unlearned_not_fake(self):
        h = au.new_hypothesis(SEG, "Short science videos land well.")
        c = au.confidence(h)
        self.assertEqual(c["status"], "unlearned")
        self.assertIsNone(c["confidence"])

    def test_repeated_support_increases_within_bounds(self):
        h = au.new_hypothesis(SEG, "Hooks help.")
        vals = []
        for _ in range(5):
            au.add_observation(h, _obs(au.SUPPORTS))
            vals.append(au.confidence(h)["confidence"])
        # Monotonic non-decreasing, and never exceeds the upper bound.
        for a, b in zip(vals, vals[1:]):
            self.assertGreaterEqual(b, a)
        self.assertLessEqual(vals[-1], 0.95)
        self.assertGreater(vals[-1], vals[0])

    def test_contrary_evidence_reduces_confidence(self):
        h = au.new_hypothesis(SEG, "Claim.")
        for _ in range(3):
            au.add_observation(h, _obs(au.SUPPORTS))
        before = au.confidence(h)["confidence"]
        for _ in range(3):
            au.add_observation(h, _obs(au.CONTRADICTS))
        after = au.confidence(h)["confidence"]
        self.assertLess(after, before)

    def test_old_evidence_decays(self):
        h_fresh = au.new_hypothesis(SEG, "A.")
        au.add_observation(h_fresh, _obs(au.SUPPORTS, days_ago=0))
        h_old = au.new_hypothesis(SEG, "A.")
        au.add_observation(h_old, _obs(au.SUPPORTS, days_ago=365))
        fresh = au.confidence(h_fresh, half_life_days=30)
        old = au.confidence(h_old, half_life_days=30)
        self.assertGreater(fresh["effective_support"], old["effective_support"])
        # A single support decayed over a year falls below the learning epsilon.
        self.assertEqual(old["status"], "unlearned")

    def test_contradiction_triggers_fork(self):
        h = au.new_hypothesis(SEG, "Morning posts do best.")
        au.add_observation(h, _obs(au.SUPPORTS, weight=1.0))
        for _ in range(3):
            au.add_observation(h, _obs(au.CONTRADICTS, weight=1.0))
        self.assertTrue(au.should_fork(h))
        fork = au.fork_hypothesis(h, "Evening posts do best.")
        self.assertEqual(fork.forked_from, h.id)
        # The parent's contradicting evidence supports the fork.
        self.assertEqual(len(fork.supporting), 3)
        self.assertGreater(au.confidence(fork)["confidence"], 0.5)

    def test_observation_requires_refs(self):
        with self.assertRaises(ValueError):
            au.Observation.make(au.SUPPORTS, {})  # no refs => no fake learning

    def test_sensitive_segment_rejected(self):
        for bad in ({"religion": "x"}, {"topic": "health"}, {"race": "y"}):
            with self.assertRaises(au.SensitiveSegmentError):
                au.new_hypothesis(bad, "targeted")

    def test_observation_and_inference_separated(self):
        h = au.new_hypothesis(SEG, "Claim.")
        au.add_observation(h, _obs(au.SUPPORTS))
        # Stored data holds raw observations; no confidence number is persisted.
        d = h.as_dict()
        self.assertIn("supporting", d)
        self.assertNotIn("confidence", d)
        self.assertIn("refs", d["supporting"][0])

    def test_persist_roundtrip(self):
        h = au.new_hypothesis(SEG, "Claim.")
        au.add_observation(h, _obs(au.SUPPORTS))
        au.save("social-a", h)
        back = au.load("social-a", h.id)
        self.assertIsNotNone(back)
        self.assertEqual(back.statement, "Claim.")
        self.assertEqual(len(back.supporting), 1)


if __name__ == "__main__":
    unittest.main()
