"""SB-V14-001 — audience memory acceptance tests (persona/workspace scoped)."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import audience as au  # noqa: E402

SEG = {"topic": "science", "format": "short-video", "timezone_band": "US-eastern"}
BOT = "social-a"
P1 = "general-1"
P2 = "cultural-1"


def _obs(stance, days_ago=0, weight=1.0, cid="c-1"):
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return au.Observation.make(stance, {"content_id": cid, "experiment_id": "e-1"},
                               weight=weight, observed_at=ts)


class AudienceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def _hyp(self, statement="Claim.", persona=P1, seg=None):
        return au.new_hypothesis(BOT, persona, SEG if seg is None else seg, statement)

    def test_no_evidence_is_unlearned_not_fake(self):
        c = au.confidence(self._hyp("Short science videos land well."))
        self.assertEqual(c["status"], "unlearned")
        self.assertIsNone(c["confidence"])

    def test_repeated_support_increases_within_bounds(self):
        h = self._hyp("Hooks help.")
        vals = []
        for _ in range(5):
            au.add_observation(h, _obs(au.SUPPORTS))
            vals.append(au.confidence(h)["confidence"])
        for a, b in zip(vals, vals[1:]):
            self.assertGreaterEqual(b, a)
        self.assertLessEqual(vals[-1], 0.95)
        self.assertGreater(vals[-1], vals[0])

    def test_contrary_evidence_reduces_confidence(self):
        h = self._hyp()
        for _ in range(3):
            au.add_observation(h, _obs(au.SUPPORTS))
        before = au.confidence(h)["confidence"]
        for _ in range(3):
            au.add_observation(h, _obs(au.CONTRADICTS))
        after = au.confidence(h)["confidence"]
        self.assertLess(after, before)

    def test_old_evidence_decays(self):
        h_fresh = self._hyp("A.")
        au.add_observation(h_fresh, _obs(au.SUPPORTS, days_ago=0))
        h_old = self._hyp("A.")
        au.add_observation(h_old, _obs(au.SUPPORTS, days_ago=365))
        fresh = au.confidence(h_fresh, half_life_days=30)
        old = au.confidence(h_old, half_life_days=30)
        self.assertGreater(fresh["effective_support"], old["effective_support"])
        self.assertEqual(old["status"], "unlearned")

    # --- fork: contradiction of A is NOT support for B -------------------- #
    def test_contradiction_triggers_fork_without_borrowed_support(self):
        h = self._hyp("Morning posts do best.")
        au.add_observation(h, _obs(au.SUPPORTS, weight=1.0))
        for _ in range(3):
            au.add_observation(h, _obs(au.CONTRADICTS, weight=1.0))
        self.assertTrue(au.should_fork(h))
        fork = au.fork_hypothesis(h, "Evening posts do best.")
        self.assertEqual(fork.forked_from, h.id)
        # The fork does NOT treat A's contradiction as support for B.
        self.assertEqual(fork.supporting, [])
        self.assertEqual(au.confidence(fork)["status"], "unlearned")
        self.assertIsNone(au.confidence(fork)["confidence"])
        # The triggering contradiction is retained only as provenance.
        self.assertEqual(len(fork.origin_contradiction_refs), 3)
        # The fork inherits the parent's persona scope.
        self.assertEqual(fork.persona, h.persona)

    def test_fork_becomes_learned_only_with_its_own_support(self):
        h = self._hyp("A best.")
        for _ in range(3):
            au.add_observation(h, _obs(au.CONTRADICTS))
        fork = au.fork_hypothesis(h, "B best.")
        au.add_observation(fork, _obs(au.SUPPORTS, cid="c-B"))
        au.add_observation(fork, _obs(au.SUPPORTS, cid="c-B2"))
        self.assertEqual(au.confidence(fork)["status"], "learned")

    def test_observation_requires_refs(self):
        with self.assertRaises(ValueError):
            au.Observation.make(au.SUPPORTS, {})

    # --- segment allowlist ------------------------------------------------ #
    def test_segment_allowlist_rejects_unknown_and_sensitive(self):
        for bad in ({"religion": "x"},          # non-allowlisted dimension
                    {"race": "y"},              # non-allowlisted dimension
                    {"topic": "health"},        # allowlisted key, sensitive value
                    {"home_address": "z"},      # non-allowlisted dimension
                    {}):                         # empty
            with self.assertRaises(au.SensitiveSegmentError):
                self._hyp(seg=bad)

    def test_segment_allowlist_accepts_safe_dimensions(self):
        h = self._hyp(seg={"topic": "space", "format": "carousel", "platform": "x"})
        self.assertEqual(h.segment["platform"], "x")

    def test_open_ended_interest_dimension_removed(self):
        self.assertNotIn("audience_interest", au.ALLOWED_SEGMENT_DIMENSIONS)
        with self.assertRaises(au.SensitiveSegmentError):
            self._hyp(seg={"audience_interest": "space"})

    def test_compound_sensitive_values_rejected(self):
        # Substring matching catches compound sensitive-trait variants.
        for bad in ({"topic": "religious_interest"},
                    {"topic": "mental_health_support"},
                    {"content_theme": "political_affiliation"},
                    {"topic": "pregnancy_journey"}):
            with self.assertRaises(au.SensitiveSegmentError):
                self._hyp(seg=bad)

    def test_fork_cannot_be_rescoped_cross_persona(self):
        h = au.new_hypothesis(BOT, P1, SEG, "A best.")
        for _ in range(3):
            au.add_observation(h, _obs(au.CONTRADICTS))
        fork = au.fork_hypothesis(h, "B best.")
        # Fork stays in the source persona; there is no cross-persona re-scope.
        self.assertEqual(fork.persona, P1)
        import inspect
        self.assertNotIn("persona", inspect.signature(au.fork_hypothesis).parameters)

    def test_observation_and_inference_separated(self):
        h = self._hyp()
        au.add_observation(h, _obs(au.SUPPORTS))
        d = h.as_dict()
        self.assertIn("supporting", d)
        self.assertNotIn("confidence", d)
        self.assertIn("refs", d["supporting"][0])

    # --- confidence identifies scope + evidence refs ---------------------- #
    def test_confidence_reports_scope_and_evidence_refs(self):
        h = self._hyp(persona=P2)
        au.add_observation(h, _obs(au.SUPPORTS, cid="c-9"))
        c = au.confidence(h)
        self.assertEqual(c["scope"], {"bot": BOT, "persona": P2})
        self.assertEqual(c["evidence_refs"][0]["refs"]["content_id"], "c-9")

    # --- persona/workspace isolation -------------------------------------- #
    def test_two_personas_hold_contradictory_hypotheses_without_blending(self):
        h1 = au.new_hypothesis(BOT, P1, SEG, "Morning posts do best.")
        for _ in range(3):
            au.add_observation(h1, _obs(au.SUPPORTS))
        h2 = au.new_hypothesis(BOT, P2, SEG, "Morning posts do worst.")
        for _ in range(3):
            au.add_observation(h2, _obs(au.CONTRADICTS))
        au.save(BOT, P1, h1)
        au.save(BOT, P2, h2)
        # Each persona sees only its own; no overwrite, no blend.
        self.assertEqual([h.id for h in au.list_hypotheses(BOT, P1)], [h1.id])
        self.assertEqual([h.id for h in au.list_hypotheses(BOT, P2)], [h2.id])
        self.assertIsNone(au.load(BOT, P1, h2.id))
        self.assertIsNone(au.load(BOT, P2, h1.id))

    def test_save_rejects_cross_persona_scope(self):
        h = au.new_hypothesis(BOT, P1, SEG, "Claim.")
        with self.assertRaises(au.PersonaScopeError):
            au.save(BOT, P2, h)  # writing P1's hypothesis into P2

    def test_persist_roundtrip_scoped(self):
        h = au.new_hypothesis(BOT, P1, SEG, "Claim.")
        au.add_observation(h, _obs(au.SUPPORTS))
        au.save(BOT, P1, h)
        back = au.load(BOT, P1, h.id)
        self.assertIsNotNone(back)
        self.assertEqual(back.statement, "Claim.")
        self.assertEqual(back.persona, P1)
        self.assertEqual(len(back.supporting), 1)


if __name__ == "__main__":
    unittest.main()
