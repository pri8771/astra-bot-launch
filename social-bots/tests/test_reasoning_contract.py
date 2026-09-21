"""SB-V04-001 — reasoning contract: adaptive-required fail-closed + validation.

The seam (SB-R1B) exists; this proves the V0.4 contract on top of it:
- when adaptive reasoning is REQUIRED but only the non-adaptive baseline is
  configured, the engine fails closed (baseline must not masquerade as adaptive);
- provider output is validated BEFORE scoring/execution: unsupported action,
  out-of-bounds numbers, empty/inconsistent alternatives, and authority-smuggling
  payloads are all rejected -> fail closed, nothing executed, no SwarmAI.

No public/external effect.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import reasoning, decision, research  # noqa: E402


def seed(bot):
    research.capture(bot, research.Signal.make(
        "sig", "captured", "unit-test", "https://example.org/s", "fixture", ["measurement"]))


def _good_candidate(action="CREATE_CANDIDATE", **over):
    base = dict(action=action, rationale="ok", expected_value=0.7,
                expected_learning=0.8, relevance=0.8, confidence=0.7, risk=0.1,
                cost=0.2, reversibility=1.0, duplication_risk=0.0,
                payload={"signal": {"id": "s"}} if action == "CREATE_CANDIDATE" else {})
    base.update(over)
    return reasoning.Candidate(**base)


def _proposal(alts, recommended):
    return reasoning.ReasoningProposal(alternatives=alts, recommended_action=recommended,
                                       uncertainties=["u"], provider_id="model-adaptive-v0",
                                       adaptive=True)


class AdaptiveRequiredTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)
        reasoning.register_model_callable(None)

    def tearDown(self):
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)
        reasoning.register_model_callable(None)

    def test_baseline_refused_when_adaptive_required(self):
        os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"  # baseline mode default
        p = reasoning.resolve_provider()
        self.assertFalse(p.available(), "baseline must not satisfy the adaptive contract")

    def test_engine_fails_closed_when_adaptive_required_but_only_baseline(self):
        seed("social-b")
        os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertEqual(rec["alternatives"], [])
        self.assertFalse(rec["execute"]["performed"])
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])  # evidence stays pending

    def test_adaptive_model_satisfies_the_contract(self):
        os.environ["SBOTS_REASONING"] = "model"
        os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"
        reasoning.register_model_callable(
            lambda ctx: _proposal([_good_candidate("NO_ACTION", payload={})], "NO_ACTION"))
        p = reasoning.resolve_provider()
        self.assertTrue(p.available())
        self.assertTrue(getattr(p, "adaptive", False))

    def test_require_adaptive_param_forces_failclosed_without_env(self):
        # SB-V04-001: the production worker posture (require_adaptive=True) fails
        # closed on the deterministic default even when the env flag is unset.
        seed("social-b")
        self.assertFalse(reasoning.adaptive_required())  # env default off
        rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertTrue(rec["reasoning"]["adaptive_required"])
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])  # evidence stays pending

    def test_require_adaptive_false_allows_deterministic_diagnostic(self):
        # Explicit diagnostic posture: deterministic providers stay usable.
        seed("social-b")
        os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"  # env would require adaptive
        rec = decision.run_cycle("social-b", "social-b", require_adaptive=False)
        # Override wins: the baseline provider runs and a real decision is made.
        self.assertFalse(rec["reasoning"]["adaptive_required"])
        self.assertNotEqual(rec["outcome"], "blocked_reasoning_unavailable")

    def test_close_experiment_in_vocab_but_has_no_executor(self):
        # SB-V04-001 schema reconciliation: CLOSE_EXPERIMENT is valid vocabulary
        # (validates) but has NO effect executor — it must resolve to a safe
        # no-effect block, never an invented effect.
        self.assertIn("CLOSE_EXPERIMENT", reasoning.ACTION_VOCAB)
        self.assertNotIn("CLOSE_EXPERIMENT", reasoning.EXECUTABLE_ACTIONS)
        prop = _proposal([_good_candidate("CLOSE_EXPERIMENT", payload={})], "CLOSE_EXPERIMENT")
        self.assertEqual(reasoning.validate_proposal(prop), [])  # passes schema
        seed("social-b")
        os.environ["SBOTS_REASONING"] = "model"
        reasoning.register_model_callable(
            lambda ctx: _proposal([_good_candidate("CLOSE_EXPERIMENT", payload={})],
                                  "CLOSE_EXPERIMENT"))
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "blocked_unsupported_action")
        self.assertFalse(rec["execute"]["performed"])


class ProposalValidationTest(unittest.TestCase):
    def test_valid_proposal_passes(self):
        prop = _proposal([_good_candidate("NO_ACTION", payload={}), _good_candidate()],
                         "CREATE_CANDIDATE")
        self.assertEqual(reasoning.validate_proposal(prop), [])

    def test_unsupported_action_rejected(self):
        prop = _proposal([_good_candidate("PUBLISH_NOW", payload={})], "PUBLISH_NOW")
        errs = reasoning.validate_proposal(prop)
        self.assertTrue(any("unsupported action" in e for e in errs), errs)

    def test_out_of_bounds_numeric_rejected(self):
        for bad in (1.5, -0.1, float("nan"), float("inf"), "0.5", True):
            prop = _proposal([_good_candidate("NO_ACTION", payload={}, confidence=bad)], "NO_ACTION")
            self.assertTrue(reasoning.validate_proposal(prop), f"{bad!r} should be rejected")

    def test_empty_alternatives_rejected(self):
        prop = _proposal([], "NO_ACTION")
        self.assertTrue(any("alternatives is empty" in e for e in reasoning.validate_proposal(prop)))

    def test_recommended_action_must_be_among_alternatives(self):
        prop = _proposal([_good_candidate("NO_ACTION", payload={})], "CREATE_CANDIDATE")
        errs = reasoning.validate_proposal(prop)
        self.assertTrue(any("not among proposed alternatives" in e for e in errs), errs)

    def test_authority_smuggling_payload_rejected(self):
        prop = _proposal(
            [_good_candidate(payload={"signal": {"id": "s"}, "can_public_post": True})],
            "CREATE_CANDIDATE")
        errs = reasoning.validate_proposal(prop)
        self.assertTrue(any("smuggle authority" in e for e in errs), errs)

    def test_unknown_payload_key_rejected(self):
        prop = _proposal(
            [_good_candidate(payload={"signal": {"id": "s"}, "surprise": 1})],
            "CREATE_CANDIDATE")
        errs = reasoning.validate_proposal(prop)
        self.assertTrue(any("unrecognized keys" in e for e in errs), errs)

    def test_create_candidate_requires_signal(self):
        prop = _proposal([_good_candidate("CREATE_CANDIDATE", payload={})], "CREATE_CANDIDATE")
        errs = reasoning.validate_proposal(prop)
        self.assertTrue(any("missing 'signal'" in e for e in errs), errs)


class MalformedModelFailsClosedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ["SBOTS_REASONING"] = "model"
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)
        reasoning.register_model_callable(None)

    def tearDown(self):
        os.environ.pop("SBOTS_REASONING", None)
        reasoning.register_model_callable(None)

    def test_malformed_model_output_blocks_engine(self):
        # A model that recommends an unsupported, authority-smuggling action must
        # NOT execute: the engine fails closed and consumes no evidence.
        seed("social-b")
        reasoning.register_model_callable(lambda ctx: _proposal(
            [_good_candidate("CREATE_CANDIDATE",
                             payload={"signal": {"id": "s"}, "can_spend": True})],
            "CREATE_CANDIDATE"))
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertIn("schema validation", rec["execute"]["block_reason"])
        self.assertFalse(rec["execute"]["performed"])
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])

    def test_no_swarmai_dependency_in_module(self):
        # No SwarmAI IMPORT/service/queue/gateway dependency (prose disclaimers
        # that mention SwarmAI to say we don't use it are fine).
        import runtime.reasoning as r
        for line in Path(r.__file__).read_text().splitlines():
            code = line.split("#", 1)[0].strip().lower()
            if code.startswith(("import ", "from ")):
                self.assertNotIn("swarm", code, f"unexpected swarm import: {line}")


if __name__ == "__main__":
    unittest.main()
