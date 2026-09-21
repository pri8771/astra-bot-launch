"""Tests for the V2.0 engineering-acceptance harness (SB-V20-099 prep).

These prove the NON-RUNTIME harness catches the violations the acceptance plan
cares about, using fixtures only. No runtime import; nothing is executed against a
real integrated stack. When Core + Intelligence merge, the same assertions point
at real emitted records.
"""
import sys
import unittest
from pathlib import Path

_SB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SB))
from qa import v2_acceptance_harness as H  # noqa: E402


def golden_chain(persona="social-a"):
    """A complete, valid engineering trace (scenario A), fixture-labeled."""
    ev = {"id": "ev-1", "kind": "evidence_receipt", "persona": persona,
          "provenance": "fixture", "captured_at": "2026-09-20T00:00:00Z"}
    m1 = {"id": "m-1", "kind": "metric_observation", "persona": persona,
          "metric": "engagement_rate", "value": 0.12, "status": "OK",
          "evidence_refs": ["ev-1"]}
    exp = {"id": "exp-1", "kind": "experiment_result", "persona": persona,
           "result": "IMPROVED", "metric_refs": ["m-1"], "evidence_refs": ["ev-1"]}
    aud = {"id": "aud-1", "kind": "audience_hypothesis", "persona": persona,
           "confidence": 0.7, "metric_refs": ["m-1"], "evidence_refs": ["ev-1"]}
    growth = {"id": "grw-1", "kind": "growth_opportunity", "persona": persona,
              "authorized": True, "audience_refs": ["aud-1"], "experiment_refs": ["exp-1"],
              "recommendation": "increase learning on format X"}
    prop = {"id": "prop-1", "kind": "strategy_revision_proposal", "persona": persona,
            "action": "INCREASE_ALLOCATION", "confidence": 0.7,
            "allocation_delta_frac": 0.1, "growth_refs": ["grw-1"],
            "evidence_refs": ["ev-1"]}
    policy = {"id": "pol-1", "kind": "policy_decision", "persona": persona,
              "proposal_ref": "prop-1", "decision": "ACCEPT"}
    rev = {"id": "rev-1", "kind": "strategy_revision", "persona": persona,
           "proposal_ref": "prop-1", "growth_ref": "grw-1",
           "prev_version": 3, "new_version": 4}
    return [ev, m1, exp, aud, growth, prop, policy, rev]


class GoldenChainTests(unittest.TestCase):
    def test_scenario_a_full_chain_is_clean(self):
        recs = golden_chain()
        self.assertEqual(H.check_global_invariants(recs, ["social-a"]), [])
        rev = next(r for r in recs if r["kind"] == "strategy_revision")
        self.assertEqual(H.resolve_trace_chain(rev, recs), [])

    def test_valid_proposal_shape(self):
        prop = next(r for r in golden_chain() if r["kind"] == "strategy_revision_proposal")
        self.assertEqual(H.validate_proposal_shape(prop), [])


class TraceChainTests(unittest.TestCase):
    def test_dangling_ref_detected(self):
        recs = golden_chain()
        # break the growth -> audience link
        growth = next(r for r in recs if r["id"] == "grw-1")
        growth["audience_refs"] = ["aud-DOES-NOT-EXIST"]
        rev = next(r for r in recs if r["kind"] == "strategy_revision")
        viol = H.resolve_trace_chain(rev, recs)
        self.assertTrue(any("dangling ref" in v for v in viol), viol)

    def test_trace_must_reach_evidence(self):
        recs = golden_chain()
        # strip evidence refs so the chain cannot bottom out at a receipt
        for r in recs:
            r.pop("evidence_refs", None)
            r.pop("metric_refs", None)
        rev = next(r for r in recs if r["kind"] == "strategy_revision")
        viol = H.resolve_trace_chain(rev, recs)
        self.assertTrue(any("does not reach any raw evidence" in v for v in viol), viol)


class PersonaIsolationTests(unittest.TestCase):
    def test_cross_persona_reference_flagged(self):
        recs = golden_chain("social-a")
        # audience record secretly belongs to another persona
        aud = next(r for r in recs if r["id"] == "aud-1")
        aud["persona"] = "cultural-primandir-atman"
        viol = H.check_persona_isolation(recs, ["social-a", "cultural-primandir-atman"])
        self.assertTrue(any("cross-persona bleed" in v for v in viol), viol)

    def test_unknown_persona_flagged(self):
        recs = golden_chain("ghost-persona")
        viol = H.check_persona_isolation(recs, ["social-a"])
        self.assertTrue(any("unknown persona" in v for v in viol), viol)


class FixtureLabelingTests(unittest.TestCase):
    def test_operational_provenance_rejected_in_engineering(self):
        recs = golden_chain()
        recs[0]["provenance"] = "live-capture"
        viol = H.check_fixture_labeling(recs)
        self.assertTrue(any("operational" in v for v in viol), viol)

    def test_no_public_effect_flag_detected(self):
        recs = golden_chain()
        recs[-1]["published"] = True
        viol = H.check_no_public_effect(recs)
        self.assertTrue(any("published" in v for v in viol), viol)


class MissingVsZeroTests(unittest.TestCase):
    def test_missing_metric_must_be_labeled_absent(self):
        metric = {"id": "m-x", "kind": "metric_observation", "value": H.MISSING,
                  "status": "OK"}  # wrong: MISSING value but not marked absent
        viol = H.check_missing_not_zero(metric)
        self.assertTrue(viol)

    def test_missing_metric_correctly_labeled_passes(self):
        metric = {"id": "m-x", "kind": "metric_observation", "value": H.MISSING,
                  "status": "MISSING"}
        self.assertEqual(H.check_missing_not_zero(metric), [])

    def test_zero_is_a_real_value_not_missing(self):
        metric = {"id": "m-0", "kind": "metric_observation", "value": 0, "status": "OK"}
        self.assertEqual(H.check_missing_not_zero(metric), [])
        self.assertIsNot(metric["value"], H.MISSING)

    def test_experiment_inconclusive_when_metric_missing(self):
        metrics = [{"id": "m-1", "value": 0.1}, {"id": "m-2", "value": H.MISSING}]
        self.assertTrue(H.experiment_should_be_inconclusive(metrics))
        self.assertFalse(H.experiment_should_be_inconclusive([{"id": "m", "value": 0.0}]))


class StaleEvidenceTests(unittest.TestCase):
    def test_stale_without_downweight_flagged(self):
        ev = {"id": "ev-old"}
        rev = {"id": "rev-1", "stale_downweighted": False, "limitations": []}
        viol = H.check_stale_handling(ev, rev, age_days=90, freshness_days=30)
        self.assertTrue(viol)

    def test_stale_with_downweight_and_limitation_passes(self):
        ev = {"id": "ev-old"}
        rev = {"id": "rev-1", "stale_downweighted": True,
               "limitations": ["stale-source: evidence older than freshness window"]}
        self.assertEqual(H.check_stale_handling(ev, rev, age_days=90, freshness_days=30), [])

    def test_fresh_evidence_needs_nothing(self):
        ev = {"id": "ev-new"}
        rev = {"id": "rev-1", "stale_downweighted": False, "limitations": []}
        self.assertEqual(H.check_stale_handling(ev, rev, age_days=5, freshness_days=30), [])


class AuthorityBlockTests(unittest.TestCase):
    def test_unauthorized_opportunity_must_be_blocked(self):
        opp = {"id": "grw-2", "authorized": False}
        self.assertTrue(H.check_authority_block(opp, {"decision": "ACCEPT"}))
        self.assertEqual(H.check_authority_block(opp, {"decision": "BLOCKED"}), [])


class AdversarialProposalTests(unittest.TestCase):
    def test_unknown_action_rejected(self):
        p = {"id": "p", "action": "PUBLISH_EVERYWHERE", "growth_refs": ["g"],
             "evidence_refs": ["e"]}
        self.assertTrue(any("unknown strategy action" in v
                            for v in H.validate_proposal_shape(p)))

    def test_out_of_bounds_numeric_rejected(self):
        for bad in (1.5, -0.1, float("nan"), float("inf"), True, "0.5"):
            p = {"id": "p", "action": "HOLD", "confidence": bad}
            self.assertTrue(H.validate_proposal_shape(p), f"{bad!r} should be rejected")

    def test_missing_evidence_refs_rejected(self):
        p = {"id": "p", "action": "INCREASE_ALLOCATION", "growth_refs": [],
             "evidence_refs": []}
        viol = H.validate_proposal_shape(p)
        self.assertTrue(any("missing growth_refs" in v for v in viol))
        self.assertTrue(any("missing evidence_refs" in v for v in viol))

    def test_proposal_cannot_assert_authority(self):
        p = {"id": "p", "action": "HOLD", "publish_authorized": True}
        self.assertTrue(any("illegally asserts" in v
                            for v in H.validate_proposal_shape(p)))


if __name__ == "__main__":
    unittest.main()
