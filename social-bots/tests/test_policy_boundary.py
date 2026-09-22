"""SB-V04-003 — deterministic policy boundary around reasoning proposals.

Reasoning proposes; deterministic policy decides. An adversarial provider cannot
bypass authority/safety/effect controls, and its recommended_action cannot
override the policy's ranking. No public effect.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import reasoning, decision, research, pipeline  # noqa: E402


def seed(bot, url="https://example.org/s", prov="live-capture", tags=("a", "b")):
    research.capture(bot, research.Signal.make(
        "sig", "well-sourced current evidence", "unit-test", url, prov, list(tags)))


def _cand(action, **over):
    base = dict(action=action, rationale="adversarial", expected_value=0.9,
                expected_learning=0.9, relevance=0.9, confidence=0.9, risk=0.0,
                cost=0.0, reversibility=1.0, duplication_risk=0.0,
                payload={"signal": {"id": "s"}} if action == "CREATE_CANDIDATE" else {})
    base.update(over)
    return reasoning.Candidate(**base)


def _model(alts, recommended):
    def build(ctx):
        # Inject the REAL current signal into any CREATE_CANDIDATE payload so an
        # allowed create can actually execute through the pipeline.
        for c in alts:
            # Only for a clean create payload (leave authority-smuggling payloads
            # intact so validation still rejects them).
            if c.action == "CREATE_CANDIDATE" and set(c.payload.keys()) == {"signal"}:
                c.payload = {"signal": ctx.top_signal, "draft": ctx.draft}
        return reasoning.ReasoningProposal(
            alternatives=alts, recommended_action=recommended, uncertainties=[],
            provider_id="model-adaptive-v0", adaptive=True)
    # SB-R07-041: declared engineering stub; a raw callable is a LIVE route and
    # would be refused (no scoped manifest) before the policy boundary is reached.
    return reasoning.EngineeringStub(build)


class PolicyBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ["SBOTS_REASONING"] = "model"
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)
        reasoning.register_model_callable(None)

    def tearDown(self):
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)
        reasoning.register_model_callable(None)

    def _run(self, alts, recommended, bot="social-b"):
        reasoning.register_model_callable(_model(alts, recommended))
        seed(bot)
        return decision.run_cycle(bot, bot)

    def test_publish_action_is_blocked(self):
        rec = self._run([_cand("PUBLISH_NOW", payload={})], "PUBLISH_NOW")
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertFalse(rec["execute"]["performed"])
        self.assertEqual(pipeline.admin_publish_queue("social-b"), [])

    def test_spend_and_message_actions_blocked(self):
        for act in ("SPEND", "MESSAGE_USER", "DM_FOLLOWERS"):
            with self.subTest(act=act):
                os.environ["SBOTS_HOME"] = tempfile.mkdtemp()
                rec = self._run([_cand(act, payload={})], act)
                self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")

    def test_invalid_numeric_fields_rejected(self):
        rec = self._run([_cand("NO_ACTION", payload={}, risk=5.0)], "NO_ACTION")
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertIn("schema validation", rec["execute"]["block_reason"])

    def test_authority_smuggling_payload_blocked(self):
        rec = self._run(
            [_cand("CREATE_CANDIDATE", payload={"signal": {"id": "s"}, "publish_authorized": True})],
            "CREATE_CANDIDATE")
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertEqual(pipeline.admin_publish_queue("social-b"), [])

    def test_recommended_action_cannot_override_policy_ranking(self):
        # Provider RECOMMENDS NO_ACTION, but the highest-scoring valid alternative
        # is CREATE_CANDIDATE. Policy selects by its own ranking, not the rec.
        strong_create = _cand("CREATE_CANDIDATE")           # score high
        weak_noop = _cand("NO_ACTION", payload={}, expected_value=0.01,
                          expected_learning=0.0, relevance=0.0, confidence=1.0,
                          reversibility=1.0)
        rec = self._run([weak_noop, strong_create], "NO_ACTION")
        self.assertEqual(rec["policy"]["provider_recommended"], "NO_ACTION")
        self.assertEqual(rec["policy"]["policy_selected"], "CREATE_CANDIDATE")
        self.assertFalse(rec["policy"]["recommended_followed"])
        self.assertEqual(rec["chosen"]["action"], "CREATE_CANDIDATE")

    def test_record_distinguishes_proposal_from_allowed_action(self):
        rec = self._run([_cand("CREATE_CANDIDATE")], "CREATE_CANDIDATE")
        self.assertIn("policy", rec)
        self.assertEqual(set(rec["policy"]) >= {
            "provider_recommended", "policy_selected", "recommended_followed",
            "selection_basis", "authority_owned_by_policy"}, True)
        # public posting is never authorized by the loop even on a "created" candidate
        self.assertFalse(rec["verify"]["publish_authorized"])
        self.assertFalse(rec["verify"]["published"])

    def test_create_candidate_still_honors_review_and_authority_gates(self):
        # Even a valid CREATE proposal must pass the deterministic review/authority
        # gates; a no-authority run cannot create.
        reasoning.register_model_callable(_model([_cand("CREATE_CANDIDATE")], "CREATE_CANDIDATE"))
        seed("social-b")
        rec = decision.run_cycle("social-b", "social-b",
                                 authority=decision.Authority(can_create_candidate=False))
        self.assertEqual(rec["outcome"], "blocked_authority")
        self.assertEqual(pipeline.admin_publish_queue("social-b"), [])


if __name__ == "__main__":
    unittest.main()
