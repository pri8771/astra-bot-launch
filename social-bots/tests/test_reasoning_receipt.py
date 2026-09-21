"""SB-V04-004 — unit tests for the sanitized adaptive-receipt seam.

These verify the seam MACHINERY only (load / validate / reject authority / reject
fabricated evidence / digest binding / single-variable isolation / divergence
detection / fail-closed replay). Fixtures here are ``synthetic-seam-fixture`` and
are NEVER represented as the real SB-V04-005 canary receipt.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import reasoning, reasoning_receipt as rr  # noqa: E402
from runtime.reasoning import ReasoningContext  # noqa: E402
from runtime.personas import load as load_persona  # noqa: E402


def make_ctx(persona_id, signal, *, objective="grow", pending=1, dup=False,
             hyp=0, draft=None):
    return ReasoningContext(
        persona=load_persona(persona_id), objective=objective, top_signal=signal,
        pending_count=pending, is_duplicate=dup, draft=draft or {"x": 1},
        state_summary={"hypotheses": hyp, "cycles": 1})


def alt(action, ev, el, rel, conf, risk, cost, rev, dup, refs):
    return {"action": action, "rationale": f"{action} rationale",
            "expected_value": ev, "expected_learning": el, "relevance": rel,
            "confidence": conf, "risk": risk, "cost": cost, "reversibility": rev,
            "duplication_risk": dup, "evidence_refs": refs}


def receipt_for(ctx, *, alternatives, recommended, provider_id="claude-code-subscription-v1",
                kind=rr.SEAM_FIXTURE_KIND, uncertainties=("u1",)):
    bounded = rr.bounded_context(ctx)
    return rr.build_receipt(
        bounded=bounded, alternatives=alternatives, recommended_action=recommended,
        uncertainties=list(uncertainties), provider_id=provider_id,
        generated_at="2026-09-21T00:00:00Z", receipt_kind=kind,
        proposal_id="p-test")


SIG = {"id": "sig-1", "title": "t", "tags": ["a", "b"], "provenance": "live-capture",
       "url": "https://example.org/e", "source": "x"}


def strong_alts(refs=("sig-1",)):
    return [
        alt("NO_ACTION", 0.05, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, []),
        alt("RESEARCH_MORE", 0.2, 0.5, 0.5, 0.6, 0.05, 0.2, 1.0, 0.0, list(refs)),
        alt("CREATE_CANDIDATE", 0.8, 0.7, 0.85, 0.8, 0.1, 0.3, 1.0, 0.0, list(refs)),
    ]


class ReceiptValidationTest(unittest.TestCase):
    def test_valid_receipt_passes(self):
        r = receipt_for(make_ctx("social-a", SIG),
                        alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        self.assertEqual(rr.validate_receipt(r), [])

    def test_reconstructed_proposal_passes_engine_schema(self):
        ctx = make_ctx("social-a", SIG)
        r = receipt_for(ctx, alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        prop = rr.proposal_from_receipt(r, ctx)
        self.assertTrue(prop.adaptive)
        self.assertEqual(reasoning.validate_proposal(prop, ctx), [])

    def test_adaptive_false_rejected(self):
        r = receipt_for(make_ctx("social-a", SIG),
                        alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        r["adaptive"] = False
        self.assertTrue(any("adaptive must be True" in e for e in rr.validate_receipt(r)))

    def test_authority_smuggling_rejected(self):
        r = receipt_for(make_ctx("social-a", SIG),
                        alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        r["alternatives"][2]["publish_authorized"] = True
        errs = rr.validate_receipt(r)
        self.assertTrue(any("authority" in e for e in errs), errs)

    def test_fabricated_evidence_ref_rejected(self):
        r = receipt_for(make_ctx("social-a", SIG),
                        alternatives=strong_alts(refs=("sig-1", "sig-DOES-NOT-EXIST")),
                        recommended="CREATE_CANDIDATE")
        errs = rr.validate_receipt(r)
        self.assertTrue(any("non-context evidence refs" in e for e in errs), errs)

    def test_out_of_range_estimate_rejected(self):
        bad = strong_alts()
        bad[2]["expected_value"] = 1.7
        r = receipt_for(make_ctx("social-a", SIG),
                        alternatives=bad, recommended="CREATE_CANDIDATE")
        self.assertTrue(any("out of bounds" in e for e in rr.validate_receipt(r)), )

    def test_recommended_not_among_alts_rejected(self):
        r = receipt_for(make_ctx("social-a", SIG),
                        alternatives=strong_alts(), recommended="CLOSE_EXPERIMENT")
        self.assertTrue(any("not among alternatives" in e for e in rr.validate_receipt(r)))

    def test_tampered_context_digest_rejected(self):
        r = receipt_for(make_ctx("social-a", SIG),
                        alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        r["context"]["objective"] = "TAMPERED"
        self.assertTrue(any("context_digest" in e for e in rr.validate_receipt(r)))

    def test_proposal_from_invalid_receipt_raises(self):
        r = receipt_for(make_ctx("social-a", SIG),
                        alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        r["adaptive"] = False
        with self.assertRaises(rr.ReceiptError):
            rr.proposal_from_receipt(r, make_ctx("social-a", SIG))


class IsolationHelperTest(unittest.TestCase):
    def test_single_variable_persona_only(self):
        a = rr.bounded_context(make_ctx("social-a", SIG))
        b = rr.bounded_context(make_ctx("cultural-primandir-atman", SIG))
        self.assertEqual(rr.differing_variables(a, b), {"persona"})
        rr.assert_single_variable(a, b, "persona")  # no raise

    def test_single_variable_evidence_only(self):
        other = dict(SIG, id="sig-2", tags=["c"], provenance="fixture", url=None, source="")
        a = rr.bounded_context(make_ctx("social-a", SIG))
        b = rr.bounded_context(make_ctx("social-a", other))
        self.assertEqual(rr.differing_variables(a, b), {"evidence"})
        rr.assert_single_variable(a, b, "evidence")

    def test_confounded_change_detected(self):
        other = dict(SIG, id="sig-2")
        a = rr.bounded_context(make_ctx("social-a", SIG))
        b = rr.bounded_context(make_ctx("cultural-primandir-atman", other))  # 2 vars
        self.assertEqual(rr.differing_variables(a, b), {"persona", "evidence"})
        with self.assertRaises(rr.ReceiptError):
            rr.assert_single_variable(a, b, "persona")


class DivergenceHelperTest(unittest.TestCase):
    def test_recommended_and_ranking_divergence_is_material(self):
        ctx = make_ctx("social-a", SIG)
        pa = rr.proposal_from_receipt(
            receipt_for(ctx, alternatives=strong_alts(), recommended="CREATE_CANDIDATE"), ctx)
        thin_alts = [
            alt("NO_ACTION", 0.05, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, []),
            alt("RESEARCH_MORE", 0.6, 0.9, 0.7, 0.5, 0.05, 0.2, 1.0, 0.0, ["sig-1"]),
            alt("CREATE_CANDIDATE", 0.2, 0.3, 0.3, 0.4, 0.4, 0.3, 1.0, 0.0, ["sig-1"]),
        ]
        pb = rr.proposal_from_receipt(
            receipt_for(ctx, alternatives=thin_alts, recommended="RESEARCH_MORE"), ctx)
        d = rr.proposal_divergence(pa, pb)
        self.assertTrue(d["material"])
        self.assertTrue(d["recommended_changed"])
        self.assertTrue(d["ranking_changed"])

    def test_identical_proposals_not_material(self):
        ctx = make_ctx("social-a", SIG)
        r = receipt_for(ctx, alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        pa = rr.proposal_from_receipt(r, ctx)
        pb = rr.proposal_from_receipt(r, ctx)
        self.assertFalse(rr.proposal_divergence(pa, pb)["material"])


class ReplayCallableTest(unittest.TestCase):
    def test_replay_returns_proposal_on_match_and_none_otherwise(self):
        ctx = make_ctx("social-a", SIG)
        r = receipt_for(ctx, alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        call = rr.replay_callable([r])
        prop = call(ctx)
        self.assertIsNotNone(prop)
        self.assertTrue(prop.adaptive)
        # A context with no matching receipt fails closed (None).
        self.assertIsNone(call(make_ctx("social-c", dict(SIG, id="other"))))

    def test_replay_refuses_to_index_invalid_receipt(self):
        ctx = make_ctx("social-a", SIG)
        r = receipt_for(ctx, alternatives=strong_alts(), recommended="CREATE_CANDIDATE")
        r["adaptive"] = False
        with self.assertRaises(rr.ReceiptError):
            rr.replay_callable([r])


class DiskLoadTest(unittest.TestCase):
    def test_load_receipt_roundtrip_and_kind_filter(self):
        ctx = make_ctx("social-a", SIG)
        real = receipt_for(ctx, alternatives=strong_alts(),
                           recommended="CREATE_CANDIDATE", kind=rr.REAL_CANARY_KIND)
        fixture = receipt_for(ctx, alternatives=strong_alts(),
                              recommended="CREATE_CANDIDATE", kind=rr.SEAM_FIXTURE_KIND)
        d = Path(tempfile.mkdtemp())
        (d / "real.json").write_text(json.dumps(real))
        (d / "fixture.json").write_text(json.dumps(fixture))
        loaded = rr.load_real_canary_receipts(d)
        self.assertEqual(len(loaded), 1)  # only the real-canary one
        self.assertEqual(loaded[0]["receipt_kind"], rr.REAL_CANARY_KIND)

    def test_missing_dir_returns_empty(self):
        self.assertEqual(rr.load_real_canary_receipts(Path(tempfile.mkdtemp()) / "nope"), [])


if __name__ == "__main__":
    unittest.main()
