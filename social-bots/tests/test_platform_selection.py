"""SB-V12-001 — platform selection intelligence acceptance tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import platform_selection as ps  # noqa: E402


def _avail(*platforms):
    return {p: {"account_available": True, "authorized": True} for p in platforms}


class PlatformSelectionTest(unittest.TestCase):
    def test_unavailable_platform_blocked_not_selectable(self):
        out = ps.select_platforms(
            persona_strategy={"x": 0.9, "tiktok": 0.9},
            content_format="video",
            availability={"x": {"account_available": True, "authorized": True},
                          "tiktok": {"account_available": False, "authorized": False,
                                     "reason": "no authorized tiktok account"}})
        self.assertIn("tiktok", out["blocked"])
        self.assertNotIn("tiktok", out["selectable"])
        blocked = next(r for r in out["ranked"] if r["platform"] == "tiktok")
        self.assertFalse(blocked["selectable"])

    def test_unsuitable_format_not_selectable(self):
        # reddit cannot carry native video.
        out = ps.select_platforms(
            persona_strategy={"reddit": 0.9, "tiktok": 0.9},
            content_format="video", availability=_avail("reddit", "tiktok"))
        self.assertIn("reddit", out["unsuitable"])
        self.assertNotIn("reddit", out["selectable"])
        self.assertIn("tiktok", out["selectable"])

    def test_no_history_yields_high_uncertainty_no_invented_prior(self):
        out = ps.select_platforms(
            persona_strategy={"x": 0.5}, content_format="text",
            availability=_avail("x"))
        r = out["ranked"][0]
        self.assertEqual(r["uncertainty"], ps.UNC_HIGH)
        self.assertIsNone(r["historical_basis"])
        self.assertFalse(out["any_historical_basis"])
        self.assertTrue(any("EXPLORATORY" in reason for reason in r["reasons"]))

    def test_history_lowers_uncertainty_and_informs_score(self):
        with_hist = ps.select_platforms(
            persona_strategy={"x": 0.5}, content_format="text",
            availability=_avail("x"),
            history={"x": {"performance": 0.9, "samples": 20}})
        r = with_hist["ranked"][0]
        self.assertEqual(r["uncertainty"], ps.UNC_LOW)
        self.assertIsNotNone(r["historical_basis"])
        self.assertEqual(r["historical_basis"]["samples"], 20)

    def test_different_formats_yield_different_rankings(self):
        strat = {"x": 0.8, "tiktok": 0.8, "reddit": 0.8}
        avail = _avail("x", "tiktok", "reddit")
        text_rank = ps.select_platforms(persona_strategy=strat,
                                        content_format="text", availability=avail)
        video_rank = ps.select_platforms(persona_strategy=strat,
                                         content_format="video", availability=avail)
        # text: x/reddit selectable, tiktok unsuitable; video: only tiktok.
        self.assertNotEqual(set(text_rank["selectable"]),
                            set(video_rank["selectable"]))
        self.assertNotIn("tiktok", text_rank["selectable"])
        self.assertEqual(video_rank["selectable"], ["tiktok"])

    def test_different_personas_yield_different_rankings(self):
        avail = _avail("x", "reddit")
        p1 = ps.select_platforms(persona_strategy={"x": 0.9, "reddit": 0.1},
                                 content_format="text", availability=avail,
                                 history={"x": {"performance": 0.5, "samples": 10},
                                          "reddit": {"performance": 0.5, "samples": 10}})
        p2 = ps.select_platforms(persona_strategy={"x": 0.1, "reddit": 0.9},
                                 content_format="text", availability=avail,
                                 history={"x": {"performance": 0.5, "samples": 10},
                                          "reddit": {"performance": 0.5, "samples": 10}})
        self.assertEqual(p1["ranked"][0]["platform"], "x")
        self.assertEqual(p2["ranked"][0]["platform"], "reddit")

    def test_learning_value_can_outrank_strategy_when_exploratory(self):
        # Two eligible platforms, equal strategy; one has strong history (low
        # uncertainty, low learning), the other none (high uncertainty, high
        # learning). With a high learning weight the unexplored one can win.
        out = ps.select_platforms(
            persona_strategy={"x": 0.5, "facebook": 0.5},
            content_format="text", availability=_avail("x", "facebook"),
            history={"x": {"performance": 0.2, "samples": 30}},  # facebook: none
            learning_weight=3.0)
        top = out["ranked"][0]["platform"]
        self.assertEqual(top, "facebook")  # learning value beat a modest known perf


if __name__ == "__main__":
    unittest.main()
