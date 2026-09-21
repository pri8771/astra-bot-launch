"""SB-V17-001 — community observation/decision/memory acceptance tests."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import community as cm  # noqa: E402


class CommunityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    # --- read-only observation works without any response authority --------- #
    def test_read_only_observation_without_authority(self):
        sig = cm.CommunitySignal.ingest(
            thread_id="t1", text="How does surface tension actually work here?",
            content_id="c1", persona="general-1")
        c = cm.classify(sig)
        cm.remember("social-a", "general-1", sig, c)
        self.assertEqual(len(cm.signals("social-a", "general-1")), 1)
        self.assertEqual(c["safety"], cm.SAFE)

    def test_ingest_rejects_non_read_only_source(self):
        with self.assertRaises(ValueError):
            cm.CommunitySignal.ingest(thread_id="t1", text="hi", source="live-post")

    def test_operational_signal_requires_receipt_ref(self):
        # read-only-evidence (operational) without a receipt ref is refused.
        with self.assertRaises(ValueError):
            cm.CommunitySignal.ingest(thread_id="t1", text="real comment",
                                      source="read-only-evidence")
        # with a receipt ref it is accepted and marked operational.
        sig = cm.CommunitySignal.ingest(
            thread_id="t1", text="real comment", source="read-only-evidence",
            receipt_ref="cap-abc123", persona="general-1")
        self.assertTrue(sig.is_operational())
        # a fixture is never operational.
        fx = cm.CommunitySignal.ingest(thread_id="t1", text="x", persona="general-1")
        self.assertFalse(fx.is_operational())

    # --- unsafe / low-value => NO_ACTION ----------------------------------- #
    def test_unsafe_is_no_action(self):
        sig = cm.CommunitySignal.ingest(thread_id="t1", text="kill them all now")
        prop = cm.recommend(sig)
        self.assertEqual(prop.action, cm.NO_ACTION)
        self.assertFalse(prop.authority_required)

    def test_spam_is_no_action(self):
        sig = cm.CommunitySignal.ingest(thread_id="t1", text="buy now click here promo code")
        self.assertEqual(cm.recommend(sig).action, cm.NO_ACTION)

    def test_low_value_is_no_action(self):
        sig = cm.CommunitySignal.ingest(thread_id="t1", text="lol nice")
        self.assertEqual(cm.recommend(sig).action, cm.NO_ACTION)

    def test_high_value_proposes_but_requires_authority(self):
        sig = cm.CommunitySignal.ingest(
            thread_id="t1", text="Wait, why does the leaf float and not sink?")
        prop = cm.recommend(sig)
        self.assertEqual(prop.action, cm.PROPOSE_RESPONSE)
        self.assertTrue(prop.authority_required)
        self.assertFalse(prop.cleared_for_effect)

    # --- authorized proposal still passes deterministic review ------------- #
    def test_no_authority_blocks_effect(self):
        sig = cm.CommunitySignal.ingest(thread_id="t1",
                                        text="Why does this reaction need heat to start?")
        prop = cm.recommend(sig)
        out = cm.clear_for_effect(prop, None, lambda p: True)
        self.assertFalse(out.cleared_for_effect)
        self.assertEqual(out.effect_status, "BLOCKED_NO_AUTHORITY")

    def test_authorized_but_failing_review_blocks_effect(self):
        sig = cm.CommunitySignal.ingest(thread_id="t1",
                                        text="Why does this reaction need heat to start?")
        prop = cm.recommend(sig)
        route = cm.AuthorizedRoute("acct-a", authorized=True, granted_by="owner")
        out = cm.clear_for_effect(prop, route, lambda p: False)  # review fails
        self.assertFalse(out.cleared_for_effect)
        self.assertEqual(out.effect_status, "BLOCKED_REVIEW")

    def test_authorized_and_reviewed_clears_but_performs_no_effect(self):
        sig = cm.CommunitySignal.ingest(thread_id="t1",
                                        text="Why does this reaction need heat to start?")
        prop = cm.recommend(sig)
        route = cm.AuthorizedRoute("acct-a", authorized=True, granted_by="owner")
        out = cm.clear_for_effect(prop, route, lambda p: True)
        self.assertTrue(out.cleared_for_effect)
        # Cleared, but this module never performs a public effect.
        self.assertEqual(out.effect_status, "CLEARED_NO_EFFECT_PERFORMED")

    # --- no fake engagement/voting/follow surface -------------------------- #
    def test_no_engagement_manipulation_functions(self):
        for forbidden in ("vote", "upvote", "follow", "like", "post", "reply",
                          "publish", "engage"):
            self.assertFalse(hasattr(cm, forbidden),
                             f"community module must not expose {forbidden}()")

    # --- themes update audience evidence (persona scoped) ------------------ #
    def test_themes_from_safe_signals_only(self):
        for txt in ["Great explanation about surface tension physics",
                    "More surface tension physics please, fascinating",
                    "buy now free money click here"]:  # spam excluded
            sig = cm.CommunitySignal.ingest(thread_id="t1", text=txt, persona="general-1")
            cm.remember("social-a", "general-1", sig, cm.classify(sig))
        themes = cm.community_themes("social-a", "general-1", min_count=2)
        theme_words = {t["theme"] for t in themes}
        self.assertIn("surface", theme_words)
        self.assertIn("tension", theme_words)
        self.assertNotIn("money", theme_words)  # spam not themed
        ev = cm.theme_to_audience_evidence("social-a", "general-1", themes[0])
        self.assertEqual(ev["source"], "community")
        self.assertEqual(ev["scope"], {"bot": "social-a", "persona": "general-1"})
        self.assertNotIn("confidence", ev)  # no invented confidence

    # --- persona isolation on a shared runtime ----------------------------- #
    def test_one_persona_signals_do_not_enter_another_persona_themes(self):
        for txt in ["Deep dive on surface tension physics again",
                    "surface tension physics discussion continues"]:
            s = cm.CommunitySignal.ingest(thread_id="t1", text=txt, persona="general-1")
            cm.remember("social-a", "general-1", s, cm.classify(s))
        # cultural persona on the same runtime has its own (empty) memory.
        self.assertEqual(cm.signals("social-a", "cultural-1"), [])
        self.assertEqual(cm.community_themes("social-a", "cultural-1", min_count=2), [])
        # general persona still has its themes.
        self.assertTrue(cm.community_themes("social-a", "general-1", min_count=2))

    def test_remember_rejects_cross_persona_signal(self):
        s = cm.CommunitySignal.ingest(thread_id="t1", text="x", persona="general-1")
        with self.assertRaises(ValueError):
            cm.remember("social-a", "cultural-1", s, cm.classify(s))

    def test_shared_generalization_is_explicit_only(self):
        for txt in ["surface tension physics is great",
                    "more surface tension physics content"]:
            s = cm.CommunitySignal.ingest(thread_id="t1", text=txt, persona="general-1")
            cm.remember("social-a", "general-1", s, cm.classify(s))
        theme = cm.community_themes("social-a", "general-1", min_count=2)[0]
        # No shared insight until explicitly generalized.
        self.assertEqual(cm.shared_community_insights("social-a"), [])
        cm.generalize_theme_to_shared("social-a", "general-1", theme)
        shared = cm.shared_community_insights("social-a")
        self.assertEqual(len(shared), 1)
        self.assertEqual(shared[0]["origin_persona"], "general-1")


if __name__ == "__main__":
    unittest.main()
