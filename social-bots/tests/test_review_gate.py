"""SB-R0A2 — failed required review (or platform gate) must STOP the candidate.

A withheld candidate must NOT register an experiment, enter the publish queue,
or produce a successful worker completion. It may produce a truthful WITHHELD
receipt.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, research, pipeline, worker  # noqa: E402


def seed(bot, n=1, url="https://example.org/s"):
    s = research.Signal.make(f"signal {n}", "captured evidence", "unit-test",
                             url, "fixture", ["indian-festivals"])
    research.capture(bot, s)
    return s


class ReviewGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_cultural_withheld_does_not_register_experiment_or_queue(self):
        # cultural persona has no named reviewer -> cultural review WITHHELD.
        bot = "social-a"  # cultural-primandir-atman runs on social-a
        seed(bot)
        rec = decision.run_cycle(bot, "cultural-primandir-atman")
        self.assertEqual(rec["outcome"], "withheld")
        self.assertFalse(rec["execute"]["performed"])
        self.assertFalse(rec["verify"]["experiment_registered"])
        self.assertFalse(rec["verify"]["queued"])
        self.assertFalse(rec["learn"]["updated"])
        # nothing leaked into experiment registry or publish queue
        exp_dir = Path(self.tmp) / "experiments" / bot
        self.assertFalse(any(exp_dir.glob("exp-*.json")) if exp_dir.exists() else False)
        self.assertEqual(pipeline.publish_queue(bot), [])

    def test_worker_receipt_for_withheld_is_not_success(self):
        bot = "social-a"
        seed(bot)
        res = worker.run_one_unit(f"cycle:{bot}", bot, "cultural-primandir-atman")
        self.assertEqual(res["outcome"], "withheld")
        self.assertTrue(res["withheld"])
        # find the finish receipt and confirm it does not imply candidate success
        import json
        fin = sorted((Path(self.tmp) / "receipts" / bot).glob("*finish*.json"))[-1]
        detail = json.loads(fin.read_text())["detail"]
        self.assertEqual(detail["outcome"], "withheld")
        self.assertFalse(detail["candidate_succeeded"])

    def test_over_platform_limit_candidate_is_withheld(self):
        # social-a primary platform is X (280); ideated text exceeds it -> WITHHELD,
        # never a false-positive success with within_platform_limit=false.
        bot = "social-a"
        long_sig = research.Signal.make(
            "METR RCT: experienced developers measured 19% slower with AI tools",
            "A 2026 randomized controlled trial found experienced developers were "
            "about 19% slower using AI tools despite a median 1.4-2x self-reported gain.",
            "unit-test", "https://example.org/ledger", "fixture", ["measurement"])
        research.capture(bot, long_sig)
        rec = decision.run_cycle(bot, "social-a")
        self.assertEqual(rec["outcome"], "withheld")
        self.assertFalse(rec["verify"]["within_platform_limit"])
        self.assertFalse(rec["verify"]["queued"])
        self.assertEqual(pipeline.publish_queue(bot), [])

    def test_passing_review_still_creates_candidate(self):
        # control: social-b (instagram, fits) still succeeds -> gate is not blanket-deny.
        bot = "social-b"
        seed(bot)
        rec = decision.run_cycle(bot, "social-b")
        self.assertEqual(rec["outcome"], "candidate_created")
        self.assertTrue(rec["verify"]["verified"])
        self.assertEqual(len(pipeline.publish_queue(bot)), 1)


if __name__ == "__main__":
    unittest.main()
