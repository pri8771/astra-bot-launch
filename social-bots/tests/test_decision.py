import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, research, pipeline  # noqa: E402
from runtime.state import BotState  # noqa: E402


def seed_signal(bot, n=1):
    s = research.Signal.make(
        title=f"Test signal {n} about measurement",
        summary="A real captured observation used for the hermetic test.",
        source="unit-test", url=f"https://example.org/{bot}/{n}",
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
        # social-b's primary platform (instagram, 2200) fits the ideated text.
        seed_signal("social-b")
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["chosen"]["action"], "CREATE_CANDIDATE")
        self.assertEqual(rec["outcome"], "candidate_created")
        self.assertTrue(rec["execute"]["performed"])
        self.assertTrue(rec["verify"]["verified"])
        # never authorized to publish
        self.assertFalse(rec["verify"]["publish_authorized"])
        self.assertFalse(rec["verify"]["published"])
        self.assertTrue(rec["learn"]["updated"])
        # queue exists but nothing published
        q = pipeline.publish_queue("social-b")
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
        seed_signal("social-b")
        decision.run_cycle("social-b", "social-b")
        reloaded = BotState.load("social-b")
        self.assertTrue(reloaded.data["hypotheses"],
                        "hypothesis must persist to disk after CREATE_CANDIDATE")

    def test_persona_runtime_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            decision.run_cycle("social-b", "social-a")  # social-a runs on social-a

    # ---- SB-R0A1 signal-delta consumption regressions -------------------
    def test_later_signal_processed_after_earlier_cycle(self):
        # A: signal 1 processed; B: signal 2 added later; C: next cycle processes 2.
        s1 = seed_signal("social-b", 1)
        r1 = decision.run_cycle("social-b", "social-b")
        self.assertEqual(r1["observe"]["consumed_this_cycle"], s1.id)
        r_idle = decision.run_cycle("social-b", "social-b")
        self.assertEqual(r_idle["chosen"]["action"], "NO_ACTION")
        s2 = seed_signal("social-b", 2)                    # arrives later
        r2 = decision.run_cycle("social-b", "social-b")
        self.assertEqual(r2["observe"]["consumed_this_cycle"], s2.id)
        self.assertNotEqual(s1.id, s2.id)

    def test_batched_signals_none_lost(self):
        # signals 1,2,3 all arrive before any cycle; none may be silently lost.
        ids = [seed_signal("social-b", i).id for i in (1, 2, 3)]
        consumed = []
        for _ in range(3):
            rec = decision.run_cycle("social-b", "social-b")
            consumed.append(rec["observe"]["consumed_this_cycle"])
        self.assertEqual(set(consumed), set(ids))          # each processed exactly once
        self.assertEqual(len(consumed), len(set(consumed)))  # no duplicates
        # inbox now fully drained
        self.assertEqual(decision.run_cycle("social-b", "social-b")["chosen"]["action"],
                         "NO_ACTION")

    def test_consumption_survives_restart(self):
        s1 = seed_signal("social-b", 1)
        decision.run_cycle("social-b", "social-b")         # consumes s1, persists
        # Simulate a process restart: fresh state load from disk.
        reloaded = BotState.load("social-b")
        self.assertIn(s1.id, reloaded.data["consumed_signal_ids"])
        # A new cycle after restart must not reprocess s1.
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["chosen"]["action"], "NO_ACTION")


if __name__ == "__main__":
    unittest.main()
