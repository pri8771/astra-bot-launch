"""SB-V20-002 — growth evaluator/allocation engine acceptance tests."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import growth_evaluator as ge, metrics  # noqa: E402

BOT = "social-a"
P1 = "general-1"
P2 = "cultural-1"


def _avail(*platforms):
    return {p: {"available": True} for p in platforms}


def _opp(id, platform, fmt="text", persona=P1, **kw):
    return ge.OpportunityInput(id=id, bot=BOT, persona=persona, platform=platform,
                               format=fmt, **kw)


class GrowthEvaluatorTest(unittest.TestCase):
    def test_no_monetary_spend_authorized(self):
        out = ge.evaluate([], availability={})
        self.assertFalse(out["spend_authorized"])
        for forbidden in ("spend", "authorize_spend", "buy", "pay", "budget"):
            self.assertFalse(hasattr(ge, forbidden))

    def test_opportunity_requires_scope(self):
        with self.assertRaises(ValueError):
            ge.OpportunityInput(id="o", bot="", persona="", platform="x", format="t")

    def test_missing_data_not_zero(self):
        out = ge.evaluate([_opp("o1", "x", performance=None, learning_question=True)],
                          availability=_avail("x"))
        self.assertEqual(out["growth_opportunities"], [])
        self.assertEqual(len(out["learning_opportunities"]), 1)
        self.assertIsNone(out["learning_opportunities"][0]["performance"])

    def test_insufficient_evidence_no_recommendation(self):
        out = ge.evaluate([_opp("o1", "x", performance=None, audience_support=None,
                                learning_question=False)], availability=_avail("x"))
        self.assertEqual(len(out["insufficient_evidence"]), 1)
        self.assertEqual(out["allocation"], [])

    def test_unavailable_destination_blocked(self):
        out = ge.evaluate([_opp("o1", "tiktok", "video",
                                performance={"value": 0.9, "samples": 20})],
                          availability={"tiktok": {"available": False,
                                                   "reason": "no account"}})
        self.assertEqual(len(out["blocked"]), 1)
        self.assertEqual(out["allocation"], [])
        self.assertFalse(out["blocked"][0]["operational_availability"]["available"])

    def test_different_evidence_different_allocation(self):
        base = [_opp("a", "x", performance={"value": 0.8, "samples": 20},
                     audience_support={"confidence": 0.8}),
                _opp("b", "reddit", performance={"value": 0.2, "samples": 20},
                     audience_support={"confidence": 0.5})]
        out1 = ge.evaluate(base, availability=_avail("x", "reddit"), learning_weight=0.1)
        flipped = [_opp("a", "x", performance={"value": 0.2, "samples": 20},
                        audience_support={"confidence": 0.5}),
                   _opp("b", "reddit", performance={"value": 0.8, "samples": 20},
                        audience_support={"confidence": 0.8})]
        out2 = ge.evaluate(flipped, availability=_avail("x", "reddit"), learning_weight=0.1)
        self.assertEqual(out1["allocation"][0]["opportunity_id"], "a")
        self.assertEqual(out2["allocation"][0]["opportunity_id"], "b")

    def test_learning_can_beat_reach_when_justified(self):
        known = _opp("known", "x", performance={"value": 0.6, "samples": 30},
                     audience_support={"confidence": 0.7})
        explore = _opp("explore", "reddit", performance=None, learning_question=True)
        low = ge.evaluate([known, explore], availability=_avail("x", "reddit"),
                          learning_weight=0.2)
        high = ge.evaluate([known, explore], availability=_avail("x", "reddit"),
                           learning_weight=5.0)
        self.assertEqual(low["allocation"][0]["opportunity_id"], "known")
        self.assertEqual(high["allocation"][0]["opportunity_id"], "explore")

    def test_allocation_weights_sum_to_one(self):
        opps = [_opp("a", "x", performance={"value": 0.5, "samples": 10},
                     audience_support={"confidence": 0.5}),
                _opp("b", "reddit", performance={"value": 0.7, "samples": 10},
                     audience_support={"confidence": 0.6})]
        out = ge.evaluate(opps, availability=_avail("x", "reddit"))
        self.assertAlmostEqual(sum(a["weight"] for a in out["allocation"]), 1.0, places=4)

    # --- persona scope carried through every record ------------------------ #
    def test_two_personas_distinguishable_in_records(self):
        opps = [_opp("a", "x", persona=P1,
                     performance={"value": 0.6, "samples": 10},
                     audience_support={"confidence": 0.6}),
                _opp("b", "x", persona=P2,
                     performance={"value": 0.6, "samples": 10},
                     audience_support={"confidence": 0.6})]
        out = ge.evaluate(opps, availability=_avail("x"))
        personas = {a["persona"] for a in out["allocation"]}
        self.assertEqual(personas, {P1, P2})
        self.assertTrue(all("bot" in g and "persona" in g
                            for g in out["growth_opportunities"]))

    def test_growth_opportunity_contract_fields(self):
        out = ge.evaluate([_opp("a", "x", performance={"value": 0.6, "samples": 10},
                                audience_support={"confidence": 0.6})],
                          availability=_avail("x"))
        g = out["growth_opportunities"][0]
        for key in ("opportunity_id", "bot", "persona", "opportunity_type",
                    "expected_growth_value", "expected_learning_value", "confidence",
                    "uncertainty", "required_authority", "evidence_refs",
                    "operational_availability", "cost_class"):
            self.assertIn(key, g)
        self.assertEqual(g["cost_class"], "no_spend")

    # --- typed evidence construction --------------------------------------- #
    def test_arbitrary_input_is_test_only(self):
        opp = _opp("a", "x", performance={"value": 0.9, "samples": 10},
                   audience_support={"confidence": 0.9})
        self.assertEqual(opp.provenance, ge.PROV_TEST_ONLY)
        # Under require_evidence, a test-only input cannot be a growth opportunity.
        out = ge.evaluate([opp], availability=_avail("x"), require_evidence=True)
        self.assertEqual(out["growth_opportunities"], [])

    def test_opportunity_from_evidence_is_growth_eligible(self):
        obs = metrics.normalize(platform="x", source="fixture", persona=P1,
                                content_id="c1",
                                window_start="2026-09-20T00:00:00+00:00",
                                window_end="2026-09-21T00:00:00+00:00",
                                raw_metrics={"impressions": 1000})
        opp = ge.opportunity_from_evidence(
            id="a", bot=BOT, persona=P1, platform="x", format="text",
            performance_value=0.7, samples=10, metric_observation=obs,
            audience_confidence={"confidence": 0.8, "hypothesis_id": "hyp-1",
                                 "scope": {"bot": BOT, "persona": P1}},
            now=datetime(2026, 9, 21, 1, tzinfo=timezone.utc))
        self.assertEqual(opp.provenance, ge.PROV_EVIDENCE)
        out = ge.evaluate([opp], availability=_avail("x"), require_evidence=True)
        self.assertEqual(len(out["growth_opportunities"]), 1)
        self.assertTrue(out["growth_opportunities"][0]["evidence_refs"])

    def test_stale_evidence_demoted_to_learning_not_growth(self):
        old_end = (datetime.now(timezone.utc) - timedelta(hours=100)).isoformat()
        obs = metrics.normalize(platform="x", source="fixture", persona=P1,
                                content_id="c1", window_end=old_end,
                                raw_metrics={"impressions": 1000})
        opp = ge.opportunity_from_evidence(
            id="a", bot=BOT, persona=P1, platform="x", format="text",
            performance_value=0.9, metric_observation=obs, max_age_hours=48.0)
        out = ge.evaluate([opp], availability=_avail("x"), require_evidence=True)
        self.assertEqual(out["growth_opportunities"], [])          # stale != growth
        self.assertEqual(len(out["learning_opportunities"]), 1)     # learning instead

    def test_opportunity_from_evidence_rejects_cross_persona(self):
        with self.assertRaises(ValueError):
            ge.opportunity_from_evidence(
                id="a", bot=BOT, persona=P1, platform="x", format="text",
                audience_confidence={"confidence": 0.8, "hypothesis_id": "h",
                                     "scope": {"bot": BOT, "persona": P2}})

    def test_evidence_refs_carried_through(self):
        opp = _opp("a", "x", performance={"value": 0.5, "samples": 10},
                   audience_support={"confidence": 0.5},
                   evidence_refs=[{"experiment_id": "e-1"}], provenance=ge.PROV_EVIDENCE)
        out = ge.evaluate([opp], availability=_avail("x"))
        self.assertEqual(out["allocation"][0]["evidence_refs"], [{"experiment_id": "e-1"}])
        self.assertEqual(out["growth_opportunities"][0]["evidence_refs"],
                         [{"experiment_id": "e-1"}])


if __name__ == "__main__":
    unittest.main()
