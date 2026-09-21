"""SB-V04-002 — context-sensitive proposal generation.

The ContextualReasoningProvider replaces fixed heuristic scoring: every estimate
is derived from persona + evidence + state, so proposals and rankings differ
materially across personas and across evidence, and NO_ACTION / RESEARCH_MORE can
genuinely win. It is honestly deterministic (adaptive=False), so under the
adaptive-required posture (SB-V04-001) it still fails closed. No SwarmAI.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import reasoning, decision, research  # noqa: E402
from runtime.reasoning import ReasoningContext, ContextualReasoningProvider  # noqa: E402
from runtime.personas import load as load_persona  # noqa: E402


def _ctx(persona_id, sig, dup=False, hyp=0, pending=1):
    return ReasoningContext(
        persona=load_persona(persona_id), objective="grow",
        top_signal=sig, pending_count=pending, is_duplicate=dup, draft={"x": 1},
        state_summary={"hypotheses": hyp, "cycles": 1})


STRONG = {"id": "s-strong", "tags": ["a", "b", "c"], "provenance": "live-capture",
          "url": "https://example.org/e", "source": "x"}
THIN = {"id": "s-thin", "tags": [], "provenance": "fixture", "url": None, "source": ""}


class ContextualDivergenceTest(unittest.TestCase):
    def setUp(self):
        self.p = ContextualReasoningProvider()

    def _reco(self, ctx):
        return self.p.propose(ctx).recommended_action

    def test_three_persona_divergence_on_same_evidence(self):
        # Same unsourced/operator evidence -> different personas rank differently.
        sig = {"id": "s", "tags": ["festival"], "provenance": "operator-supplied",
               "url": None, "source": ""}
        general = self._reco(_ctx("social-b", sig))
        cultural = self._reco(_ctx("cultural-primandir-atman", sig))
        # cultural persona (needs named reviewer + source) is conservative here.
        self.assertEqual(cultural, "RESEARCH_MORE")
        # a general persona and a cultural persona do not produce identical
        # proposals on this evidence.
        self.assertNotEqual(
            {c.action: c.score() for c in self.p.propose(_ctx("social-b", sig)).alternatives},
            {c.action: c.score() for c in self.p.propose(_ctx("cultural-primandir-atman", sig)).alternatives})
        # and a THIRD persona on strong sourced evidence acts.
        self.assertEqual(self._reco(_ctx("social-a", STRONG)), "CREATE_CANDIDATE")

    def test_same_persona_different_evidence_changes_ranking(self):
        strong = self._reco(_ctx("social-b", STRONG))
        thin = self._reco(_ctx("social-b", THIN))
        self.assertEqual(strong, "CREATE_CANDIDATE")
        self.assertEqual(thin, "RESEARCH_MORE")
        self.assertNotEqual(strong, thin)

    def test_no_action_can_win(self):
        # duplicate + thin evidence: acting is unwarranted -> NO_ACTION wins.
        self.assertEqual(self._reco(_ctx("social-b", THIN, dup=True)), "NO_ACTION")

    def test_research_more_can_win(self):
        self.assertEqual(self._reco(_ctx("social-b", THIN)), "RESEARCH_MORE")

    def test_state_affects_estimates(self):
        # More prior hypotheses lowers the novelty (expected_learning) of a new
        # candidate, so the CREATE estimate is materially different.
        few = self.p.propose(_ctx("social-b", STRONG, hyp=0))
        many = self.p.propose(_ctx("social-b", STRONG, hyp=5))
        cc_few = next(c for c in few.alternatives if c.action == "CREATE_CANDIDATE")
        cc_many = next(c for c in many.alternatives if c.action == "CREATE_CANDIDATE")
        self.assertGreater(cc_few.expected_learning, cc_many.expected_learning)

    def test_output_passes_schema_validation(self):
        for ctx in (_ctx("social-b", STRONG), _ctx("social-b", THIN),
                    _ctx("cultural-primandir-atman", STRONG)):
            self.assertEqual(reasoning.validate_proposal(self.p.propose(ctx), ctx), [])


class ContextualEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ["SBOTS_REASONING"] = "contextual"
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)

    def tearDown(self):
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)

    def test_engine_uses_contextual_and_creates_on_strong_evidence(self):
        research.capture("social-b", research.Signal.make(
            "strong finding", "well-sourced current evidence", "unit-test",
            "https://example.org/strong", "live-capture", ["a", "b", "c"]))
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["reasoning"]["provider"], "contextual-deterministic-v1")
        self.assertEqual(rec["outcome"], "candidate_created")

    def test_engine_research_more_on_thin_evidence_no_effect(self):
        # A thin fixture signal -> RESEARCH_MORE wins -> no experiment/queue.
        research.capture("social-b", research.Signal.make(
            "vague", "", "unit-test", None, "fixture", []))
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["chosen"]["action"], "RESEARCH_MORE")
        self.assertEqual(rec["outcome"], "research_more")
        from runtime import pipeline
        self.assertEqual(pipeline.admin_publish_queue("social-b"), [])

    def test_contextual_fails_closed_when_adaptive_required(self):
        os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"
        research.capture("social-b", research.Signal.make(
            "x", "y", "unit-test", "https://example.org/e", "live-capture", ["a"]))
        rec = decision.run_cycle("social-b", "social-b")
        # contextual is deterministic, not the adaptive model route -> blocked.
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])


if __name__ == "__main__":
    unittest.main()
