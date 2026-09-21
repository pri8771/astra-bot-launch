"""SB-V20-002 — growth evaluator/allocation engine acceptance tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import growth_evaluator as ge  # noqa: E402


def _avail(*platforms):
    return {p: {"available": True} for p in platforms}


class GrowthEvaluatorTest(unittest.TestCase):
    def test_no_monetary_spend_authorized(self):
        out = ge.evaluate([], availability={})
        self.assertFalse(out["spend_authorized"])
        # There is no spend-authorizing function on the module.
        for forbidden in ("spend", "authorize_spend", "buy", "pay", "budget"):
            self.assertFalse(hasattr(ge, forbidden))

    def test_missing_data_not_zero(self):
        opp = ge.OpportunityInput(id="o1", platform="x", format="text",
                                  performance=None, learning_question=True)
        out = ge.evaluate([opp], availability=_avail("x"))
        # Not a growth opportunity (no measured perf), but IS a learning one.
        self.assertEqual(out["growth_opportunities"], [])
        self.assertEqual(len(out["learning_opportunities"]), 1)
        self.assertIsNone(out["learning_opportunities"][0]["performance"])

    def test_insufficient_evidence_no_recommendation(self):
        opp = ge.OpportunityInput(id="o1", platform="x", format="text",
                                  performance=None, audience_support=None,
                                  learning_question=False)
        out = ge.evaluate([opp], availability=_avail("x"))
        self.assertEqual(len(out["insufficient_evidence"]), 1)
        self.assertEqual(out["allocation"], [])

    def test_unavailable_destination_blocked(self):
        opp = ge.OpportunityInput(id="o1", platform="tiktok", format="video",
                                  performance={"value": 0.9, "samples": 20})
        out = ge.evaluate([opp], availability={"tiktok": {"available": False,
                                                          "reason": "no account"}})
        self.assertEqual(len(out["blocked"]), 1)
        self.assertEqual(out["allocation"], [])

    def test_different_evidence_different_allocation(self):
        base = [ge.OpportunityInput(id="a", platform="x", format="text",
                                    performance={"value": 0.8, "samples": 20},
                                    audience_support={"confidence": 0.8}),
                ge.OpportunityInput(id="b", platform="reddit", format="text",
                                    performance={"value": 0.2, "samples": 20},
                                    audience_support={"confidence": 0.5})]
        out1 = ge.evaluate(base, availability=_avail("x", "reddit"),
                           learning_weight=0.1)
        # Flip the performance evidence.
        flipped = [ge.OpportunityInput(id="a", platform="x", format="text",
                                       performance={"value": 0.2, "samples": 20},
                                       audience_support={"confidence": 0.5}),
                   ge.OpportunityInput(id="b", platform="reddit", format="text",
                                       performance={"value": 0.8, "samples": 20},
                                       audience_support={"confidence": 0.8})]
        out2 = ge.evaluate(flipped, availability=_avail("x", "reddit"),
                           learning_weight=0.1)
        self.assertEqual(out1["allocation"][0]["opportunity_id"], "a")
        self.assertEqual(out2["allocation"][0]["opportunity_id"], "b")

    def test_learning_can_beat_reach_when_justified(self):
        # 'known' has solid measured reach, low uncertainty, no open question.
        known = ge.OpportunityInput(id="known", platform="x", format="text",
                                    performance={"value": 0.6, "samples": 30},
                                    audience_support={"confidence": 0.7})
        # 'explore' has no measured performance but an open learning question.
        explore = ge.OpportunityInput(id="explore", platform="reddit", format="text",
                                      performance=None, learning_question=True)
        low_lw = ge.evaluate([known, explore], availability=_avail("x", "reddit"),
                             learning_weight=0.2)
        high_lw = ge.evaluate([known, explore], availability=_avail("x", "reddit"),
                              learning_weight=5.0)
        self.assertEqual(low_lw["allocation"][0]["opportunity_id"], "known")
        self.assertEqual(high_lw["allocation"][0]["opportunity_id"], "explore")

    def test_allocation_weights_sum_to_one(self):
        opps = [ge.OpportunityInput(id="a", platform="x", format="text",
                                    performance={"value": 0.5, "samples": 10},
                                    audience_support={"confidence": 0.5}),
                ge.OpportunityInput(id="b", platform="reddit", format="text",
                                    performance={"value": 0.7, "samples": 10},
                                    audience_support={"confidence": 0.6})]
        out = ge.evaluate(opps, availability=_avail("x", "reddit"))
        total = sum(a["weight"] for a in out["allocation"])
        self.assertAlmostEqual(total, 1.0, places=4)

    def test_evidence_refs_carried_through(self):
        opp = ge.OpportunityInput(id="a", platform="x", format="text",
                                  performance={"value": 0.5, "samples": 10},
                                  audience_support={"confidence": 0.5},
                                  evidence_refs=[{"experiment_id": "e-1"}])
        out = ge.evaluate([opp], availability=_avail("x"))
        self.assertEqual(out["allocation"][0]["evidence_refs"], [{"experiment_id": "e-1"}])
        self.assertEqual(out["growth_opportunities"][0]["evidence_refs"],
                         [{"experiment_id": "e-1"}])


if __name__ == "__main__":
    unittest.main()
