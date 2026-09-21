"""SB-V04-004 — persona / evidence divergence acceptance suite.

Proves the V0.4 decision layer produces MATERIALLY DIFFERENT proposals and
decisions for different personas and different evidence, using the DETERMINISTIC
context-sensitive provider (``ContextualReasoningProvider``, ``adaptive=False``).

IMPORTANT SCOPE: this is ENGINEERING evidence, not the SB-V04-005 real adaptive
canary. The contextual provider is honestly ``adaptive=False`` and makes no model
call, no network call and no spend; it must never be represented as the required
real subscription-authenticated canary (that is the dedicated
``claude/social-bots-v04-live-canary`` lane only). This suite exists to accept the
*divergence* behavior deterministically, offline.

Single POSIX host; no external effect.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, research, reasoning  # noqa: E402
from runtime.reasoning import ReasoningContext  # noqa: E402


def seed(bot, title, url, tags, provenance):
    research.capture(bot, research.Signal.make(
        title, "captured evidence", "unit-test-src", url, provenance, tags))


class V04DivergenceAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ["SBOTS_REASONING"] = "contextual"   # engineering, adaptive=False
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)

    def tearDown(self):
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)

    # ---- scope guard: this is engineering evidence, not the live canary -----
    def test_provider_is_engineering_only_not_the_live_canary(self):
        p = reasoning.resolve_provider()
        self.assertEqual(p.provider_id, "contextual-deterministic-v1")
        self.assertFalse(getattr(p, "adaptive", False),
                         "the divergence suite must use the non-adaptive engineering "
                         "provider; it is NOT the SB-V04-005 live canary")

    # ---- same evidence, different personas -> materially different ----------
    def test_same_evidence_different_personas_diverge(self):
        bot = "social-a"  # hosts general social-a AND cultural-primandir-atman
        seed(bot, "shared festival signal", "https://example.org/shared",
             ["indian-festivals"], "live-capture")
        rec_gen = decision.run_cycle(bot, "social-a")
        seed(bot, "shared festival signal", "https://example.org/shared2",
             ["indian-festivals"], "live-capture")
        rec_cul = decision.run_cycle(bot, "cultural-primandir-atman")
        # General acts (candidate created); cultural is conservatively WITHHELD
        # (no named reviewer) — same class of evidence, materially different outcome.
        self.assertEqual(rec_gen["outcome"], "candidate_created")
        self.assertEqual(rec_cul["outcome"], "withheld")
        self.assertNotEqual(rec_gen["outcome"], rec_cul["outcome"])

    def test_persona_divergence_at_proposal_level(self):
        # Same signal/context to two personas -> the contextual provider yields
        # materially different alternative estimates (cultural is more conservative:
        # lower CREATE_CANDIDATE expected value and/or higher risk).
        from runtime.personas import load as load_persona
        from runtime import pipeline
        sig = research.Signal.make("s", "captured", "src", "https://e.org/x",
                                   "live-capture", ["t"]).__dict__
        prov = reasoning.ContextualReasoningProvider()

        def create_alt(persona_id):
            persona = load_persona(persona_id)
            ctx = ReasoningContext(
                persona=persona, objective="grow",
                top_signal=sig, pending_count=1, is_duplicate=False,
                draft=pipeline.ideate(persona, sig),
                state_summary={"hypotheses": 0})
            prop = prov.propose(ctx)
            return next(c for c in prop.alternatives if c.action == "CREATE_CANDIDATE")

        gen_c = create_alt("social-a")
        cul_c = create_alt("cultural-primandir-atman")
        # Materially different: the estimates are not identical, and the cultural
        # persona is the more conservative one on at least one dimension.
        self.assertNotEqual(
            (gen_c.expected_value, gen_c.risk),
            (cul_c.expected_value, cul_c.risk),
            "different personas must produce materially different CREATE estimates")
        self.assertGreaterEqual(cul_c.risk, gen_c.risk)

    # ---- same persona, different evidence -> materially different -----------
    def test_same_persona_different_evidence_diverges(self):
        # Strong, sourced, tagged live-capture evidence -> CREATE_CANDIDATE.
        seed("social-b", "strong signal", "https://example.org/strong",
             ["measurement", "roi"], "live-capture")
        strong = decision.run_cycle("social-b", "social-b")
        self.assertEqual(strong["chosen"]["action"], "CREATE_CANDIDATE")

        # Thin, untagged, low-trust fixture evidence -> RESEARCH_MORE (a different
        # runtime keeps the two evidence regimes isolated).
        seed("social-c", "thin signal", "https://example.org/thin", [], "fixture")
        thin = decision.run_cycle("social-c", "social-c")
        self.assertEqual(thin["chosen"]["action"], "RESEARCH_MORE")

        self.assertNotEqual(strong["chosen"]["action"], thin["chosen"]["action"])

    # ---- each action outcome is reachable ----------------------------------
    def test_each_action_outcome_is_reachable(self):
        # CREATE_CANDIDATE (strong/general)
        seed("social-b", "strong", "https://example.org/s", ["a", "b"], "live-capture")
        self.assertEqual(decision.run_cycle("social-b", "social-b")["chosen"]["action"],
                         "CREATE_CANDIDATE")
        # RESEARCH_MORE (thin/general)
        seed("social-c", "thin", "https://example.org/t", [], "fixture")
        self.assertEqual(decision.run_cycle("social-c", "social-c")["chosen"]["action"],
                         "RESEARCH_MORE")
        # NO_ACTION (no new evidence: the deterministic no-change path, no model call)
        second = decision.run_cycle("social-c", "social-c")  # evidence already consumed
        self.assertEqual(second["chosen"]["action"], "NO_ACTION")

    def test_context_sensitivity_is_recorded_in_uncertainties(self):
        # The provider records WHY it diverged (evidence strength/confidence/novelty),
        # so acceptance is inspectable, not opaque.
        seed("social-b", "s", "https://example.org/s", ["a"], "live-capture")
        rec = decision.run_cycle("social-b", "social-b")
        u = " ".join(rec["reasoning"].get("uncertainties", []))
        self.assertIn("evidence_strength", u)
        self.assertIn("confidence", u)


if __name__ == "__main__":
    unittest.main()
