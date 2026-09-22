"""SB-R1B — reasoning-provider seam + fail-closed contract."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import reasoning, decision, research, model_dispatch  # noqa: E402


def setUpModule():
    # LEAD-051: engineering stubs run only under the explicit, policy-owned
    # ENGINEERING dispatch scope; a test module declares it, production never does.
    model_dispatch.configure_engineering()


def tearDownModule():
    model_dispatch.clear()


def seed(bot):
    research.capture(bot, research.Signal.make(
        "sig", "captured", "unit-test", "https://example.org/s", "fixture", ["measurement"]))


class ReasoningTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ.pop("SBOTS_REASONING", None)
        reasoning.register_model_callable(None)

    def tearDown(self):
        os.environ.pop("SBOTS_REASONING", None)
        reasoning.register_model_callable(None)

    def test_default_provider_is_baseline(self):
        p = reasoning.resolve_provider()
        self.assertEqual(p.provider_id, "baseline-deterministic-v1")
        self.assertTrue(p.available())

    def test_model_mode_without_callable_is_unavailable(self):
        os.environ["SBOTS_REASONING"] = "model"
        p = reasoning.resolve_provider()
        self.assertFalse(p.available())
        self.assertIsNone(p.propose(reasoning.ReasoningContext(
            persona={}, objective="x", top_signal={"id": "s"}, pending_count=1,
            is_duplicate=False, draft={})))

    def test_engine_fails_closed_when_reasoning_unavailable(self):
        # Changed evidence + model mode + no model -> BLOCKED, nothing fabricated.
        seed("social-b")
        os.environ["SBOTS_REASONING"] = "model"
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertEqual(rec["alternatives"], [])
        self.assertFalse(rec["execute"]["performed"])
        # signal NOT consumed: unreasoned evidence stays pending
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])
        self.assertEqual(rec["observe"]["pending_after"], 1)

    def test_baseline_mode_still_creates_candidate(self):
        seed("social-b")
        rec = decision.run_cycle("social-b", "social-b")  # default baseline
        self.assertEqual(rec["outcome"], "candidate_created")
        self.assertFalse(rec["reasoning"]["adaptive"])
        self.assertEqual(rec["reasoning"]["provider"], "baseline-deterministic-v1")

    def test_registered_model_callable_makes_provider_available(self):
        def fake_model(ctx):
            return reasoning.ReasoningProposal(
                alternatives=[reasoning.no_action("model says wait")],
                recommended_action="NO_ACTION", uncertainties=["stub"],
                provider_id="model-adaptive-v0", adaptive=True)
        os.environ["SBOTS_REASONING"] = "model"
        # SB-R07-041: a raw callable is a LIVE route and is refused without a
        # scoped manifest; a unit test declares its stub through the policy type.
        reasoning.register_model_callable(reasoning.EngineeringStub(fake_model))
        p = reasoning.resolve_provider()
        self.assertTrue(p.available())
        seed("social-b")
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "no_action")
        self.assertTrue(rec["reasoning"]["adaptive"])


if __name__ == "__main__":
    unittest.main()
