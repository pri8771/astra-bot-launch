import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, research, pipeline  # noqa: E402
from runtime.state import BotState  # noqa: E402


def seed_signal(bot):
    s = research.Signal.make(
        title="Test signal about measurement",
        summary="A real captured observation used for the hermetic test.",
        source="unit-test", url="https://example.org/x",
        provenance="fixture", tags=["measurement", "test"])
    research.capture(bot, s)
    return s


class DecisionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_no_change_path_is_no_action_and_has_no_effect(self):
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["chosen"]["action"], "NO_ACTION")
        self.assertFalse(rec["execute"]["performed"])
        self.assertFalse(rec["observe"]["changed"])

    def test_new_evidence_creates_unpublished_candidate(self):
        seed_signal("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["chosen"]["action"], "CREATE_CANDIDATE")
        self.assertTrue(rec["execute"]["performed"])
        self.assertTrue(rec["verify"]["verified"])
        # never authorized to publish
        self.assertFalse(rec["verify"]["publish_authorized"])
        self.assertFalse(rec["verify"]["published"])
        self.assertTrue(rec["learn"]["updated"])
        # queue exists but nothing published
        q = pipeline.publish_queue("social-a")
        self.assertEqual(len(q), 1)
        self.assertFalse(q[0]["published"])

    def test_decision_records_alternatives(self):
        seed_signal("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        actions = {a["action"] for a in rec["alternatives"]}
        self.assertIn("NO_ACTION", actions)
        self.assertIn("CREATE_CANDIDATE", actions)
        self.assertIn("score", rec["chosen"])

    def test_second_cycle_same_evidence_is_no_action(self):
        seed_signal("social-a")
        decision.run_cycle("social-a", "social-a")   # consumes evidence -> fingerprint advances
        rec2 = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec2["chosen"]["action"], "NO_ACTION")

    def test_bot_isolation_no_cross_write(self):
        seed_signal("social-a")
        decision.run_cycle("social-a", "social-a")
        # social-b has no signals and no content
        b = BotState.load("social-b")
        self.assertEqual(b.content_history(), [])

    def test_learning_is_persisted_after_create(self):
        # Regression: the outer cycle save must not clobber the hypothesis written
        # during EXECUTE. Reload from disk and confirm the hypothesis survives.
        seed_signal("social-a")
        decision.run_cycle("social-a", "social-a")
        reloaded = BotState.load("social-a")
        self.assertTrue(reloaded.data["hypotheses"],
                        "hypothesis must persist to disk after CREATE_CANDIDATE")

    def test_persona_runtime_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            decision.run_cycle("social-b", "social-a")  # social-a runs on social-a


if __name__ == "__main__":
    unittest.main()
