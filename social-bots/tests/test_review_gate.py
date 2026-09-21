"""SB-R0A2 — failed required review (or platform gate) must STOP the candidate.

A withheld candidate must NOT register an experiment, enter the publish queue,
or produce a successful worker completion. It may produce a truthful WITHHELD
receipt.
"""
import json
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

    def _assert_no_downstream_effect(self, bot, rec, failed_gate_check):
        """Every failure mode must produce the SAME truthful stop: withheld,
        no experiment file, no publish-queue entry, no learning, and a
        gate_failures record naming the failed review check."""
        self.assertEqual(rec["outcome"], "withheld")
        self.assertFalse(rec["execute"]["performed"])
        self.assertFalse(rec["verify"]["experiment_registered"])
        self.assertFalse(rec["verify"]["queued"])
        self.assertFalse(rec["verify"]["published"])
        self.assertFalse(rec["verify"]["publish_authorized"])
        self.assertFalse(rec["verify"]["review_passed"])
        self.assertFalse(rec["learn"]["updated"])
        # the specific review check that failed is truthfully recorded
        review_failures = [g for g in rec["execute"]["gate_failures"]
                           if g["gate"] == "review"]
        self.assertTrue(review_failures, "expected a review gate failure record")
        failed_checks = {c["check"] for g in review_failures for c in g["checks"]}
        self.assertIn(failed_gate_check, failed_checks)
        # nothing leaked into the experiment registry
        exp_dir = Path(self.tmp) / "experiments" / bot
        self.assertFalse(any(exp_dir.glob("exp-*.json")) if exp_dir.exists() else False)
        idx = exp_dir / "index.jsonl"
        self.assertFalse(idx.exists() and idx.read_text().strip())
        # nothing leaked into the publish queue
        self.assertEqual(pipeline.publish_queue(bot), [])

    def test_forced_fact_review_failure_blocks_experiment_and_queue(self):
        # Acceptance test 2: a general candidate whose FACT review fails must be
        # blocked before any experiment registration or publish-queue entry.
        # Fault injection: the natural pipeline always coalesces a source ref, so
        # we force fact_check to fail to prove the deterministic gate STOPS the
        # candidate. review()'s aggregation and the gate run for real.
        bot = "social-b"  # general persona; only the fact check will fail
        seed(bot, url="https://example.org/wonder")
        orig_fact = pipeline.fact_check
        pipeline.fact_check = lambda persona, candidate: {
            "check": "fact", "passed": False,
            "reason": "forced: claim not traceable to a reputable source (fault injection)"}
        try:
            rec = decision.run_cycle(bot, "social-b")
        finally:
            pipeline.fact_check = orig_fact
        self._assert_no_downstream_effect(bot, rec, "fact")

    def test_forced_voice_review_failure_blocks_experiment_and_queue(self):
        # Acceptance test 3: a VOICE-review failure must be blocked before any
        # experiment registration or publish-queue entry. This uses the REAL
        # voice_review: the signal text contains a persona banned move ("snark"),
        # so the actual voice check fails end-to-end (no monkeypatch).
        bot = "social-b"  # banned_moves include "snark"
        sig = research.Signal.make(
            "A quiet look at tide pools",
            "This wonder note leans on snark instead of curiosity to bait a reaction.",
            "unit-test", "https://example.org/tidepools", "fixture", ["nature"])
        research.capture(bot, sig)
        rec = decision.run_cycle(bot, "social-b")
        # confirm the real voice check is what failed
        self.assertFalse(rec["verify"]["review_passed"])
        self._assert_no_downstream_effect(bot, rec, "voice")

    def test_worker_receipt_for_forced_voice_failure_is_not_success(self):
        # Acceptance test 4 across the general/voice path: the worker finish
        # receipt must record the withheld state, never candidate success.
        bot = "social-b"
        sig = research.Signal.make(
            "A quiet look at tide pools",
            "This wonder note leans on snark instead of curiosity to bait a reaction.",
            "unit-test", "https://example.org/tidepools", "fixture", ["nature"])
        research.capture(bot, sig)
        res = worker.run_one_unit(f"cycle:{bot}", bot, "social-b")
        self.assertEqual(res["outcome"], "withheld")
        self.assertTrue(res["withheld"])
        fin = sorted((Path(self.tmp) / "receipts" / bot).glob("*finish*.json"))[-1]
        detail = json.loads(fin.read_text())["detail"]
        self.assertEqual(detail["outcome"], "withheld")
        self.assertFalse(detail["candidate_succeeded"])
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
