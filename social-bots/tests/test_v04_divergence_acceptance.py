"""SB-V04-004 — persona / evidence divergence acceptance suite.

This suite proves the V0.4 decision layer produces MATERIALLY DIFFERENT proposals
and decisions when — and only when — a single independent variable changes
(persona/workspace, or evidence), through the **adaptive provider path**
(``adaptive=True``).

Two layers, deliberately separated for honesty:

* ``ContextualDiagnosticTest`` — FAST DIAGNOSTIC coverage using the deterministic
  ``ContextualReasoningProvider`` (``contextual-deterministic-v1``, ``adaptive=False``).
  It is context-sensitive and useful as regression coverage, but it is honestly
  NOT adaptive and MUST NOT satisfy final V0.4 adaptive acceptance (SB-V04-001).

* ``AdaptiveReceiptDivergenceTest`` — the ACCEPTANCE layer. It exercises the real
  adaptive provider path (``ModelReasoningProvider``, ``adaptive=True``) by
  REPLAYING sanitized adaptive receipts through
  ``reasoning.register_model_callable``, holding all-but-one independent variable
  constant (proved by ``reasoning_receipt.assert_single_variable``) and asserting a
  material proposal/ranking/decision difference. It makes NO live model call and no
  network call — the one authorized live invocation is reserved for SB-V04-005.

* ``RealCanaryReceiptAcceptanceTest`` — consumes the SANITIZED REAL SB-V04-005
  receipt from ``reasoning_receipt.REAL_CANARY_RECEIPT_DIR`` when present, and
  replays it through the same adaptive path. Until the canary has run there is no
  real receipt, so it skips with a clear "awaiting real canary" message rather
  than passing on synthetic data.

Single POSIX host; no external effect; no spend.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, research, reasoning, pipeline  # noqa: E402
from runtime import reasoning_receipt as rr  # noqa: E402
from runtime.reasoning import ReasoningContext  # noqa: E402
from runtime.personas import load as load_persona  # noqa: E402


def seed(bot, title, url, tags, provenance):
    research.capture(bot, research.Signal.make(
        title, "captured evidence", "unit-test-src", url, provenance, tags))


def _alt(action, ev, el, rel, conf, risk, cost, rev, dup, refs):
    return {"action": action, "rationale": f"{action}: adaptive rationale",
            "expected_value": ev, "expected_learning": el, "relevance": rel,
            "confidence": conf, "risk": risk, "cost": cost, "reversibility": rev,
            "duplication_risk": dup, "evidence_refs": refs}


# Fixed non-persona, non-evidence variables shared by the persona-only cases.
FIXED_OBJECTIVE = "grow audience via evidence-based experiments"
SHARED_SIGNAL = {"id": "sig-shared", "title": "shared festival signal",
                 "tags": ["indian-festivals"], "provenance": "operator-supplied",
                 "url": "https://example.org/shared", "source": "op"}


def _ctx(persona_id, signal, *, objective=FIXED_OBJECTIVE, pending=1, dup=False, hyp=0):
    return ReasoningContext(
        persona=load_persona(persona_id), objective=objective, top_signal=signal,
        pending_count=pending, is_duplicate=dup, draft={"stub": True},
        state_summary={"hypotheses": hyp, "cycles": 1})


# --------------------------------------------------------------------------- #
# DIAGNOSTIC LAYER — deterministic, adaptive=False. Fast regression coverage only.
# The two historically-confounded cases are repaired here so each changes EXACTLY
# one independent variable, verified by reasoning_receipt.assert_single_variable.
# --------------------------------------------------------------------------- #
class ContextualDiagnosticTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ["SBOTS_REASONING"] = "contextual"
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)
        self.p = reasoning.ContextualReasoningProvider()

    def tearDown(self):
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)

    def test_provider_is_diagnostic_only_not_the_live_canary(self):
        prov = reasoning.resolve_provider()
        self.assertEqual(prov.provider_id, "contextual-deterministic-v1")
        self.assertFalse(getattr(prov, "adaptive", False),
                         "the diagnostic layer is NOT the SB-V04-005 adaptive canary")

    def test_persona_only_divergence_diagnostic(self):
        # REPAIRED (was confounded: it changed persona AND evidence). Now the SAME
        # signal/objective/state is proposed to three personas, varying ONLY persona.
        a = _ctx("social-a", SHARED_SIGNAL)
        b = _ctx("social-b", SHARED_SIGNAL)
        c = _ctx("cultural-primandir-atman", SHARED_SIGNAL)
        for x, y in ((a, b), (a, c), (b, c)):
            rr.assert_single_variable(rr.bounded_context(x), rr.bounded_context(y), "persona")
        props = {name: self.p.propose(ctx) for name, ctx in
                 (("a", a), ("b", b), ("cul", c))}
        # The deterministic contextual provider keys on persona KIND / source
        # requirements, so it diverges general-vs-cultural but treats two general
        # personas alike — a known limitation that is exactly why this layer is
        # diagnostic only and the adaptive layer (below) is required for the full
        # >=3-workspace acceptance.
        self.assertTrue(rr.proposal_divergence(props["a"], props["cul"])["material"])
        self.assertTrue(rr.proposal_divergence(props["b"], props["cul"])["material"])

    def test_evidence_only_divergence_diagnostic(self):
        # REPAIRED (was confounded: it changed persona AND runtime). Now the SAME
        # persona/objective/state gets two different evidence snapshots.
        strong = {"id": "s-strong", "title": "strong", "tags": ["measurement", "roi"],
                  "provenance": "live-capture", "url": "https://example.org/strong",
                  "source": "x"}
        thin = {"id": "s-thin", "title": "thin", "tags": [], "provenance": "fixture",
                "url": None, "source": ""}
        cx_s, cx_t = _ctx("social-b", strong), _ctx("social-b", thin)
        rr.assert_single_variable(rr.bounded_context(cx_s), rr.bounded_context(cx_t), "evidence")
        p_s, p_t = self.p.propose(cx_s), self.p.propose(cx_t)
        self.assertEqual(p_s.recommended_action, "CREATE_CANDIDATE")
        self.assertEqual(p_t.recommended_action, "RESEARCH_MORE")
        self.assertTrue(rr.proposal_divergence(p_s, p_t)["material"])

    def test_engine_persona_only_reaches_different_outcomes(self):
        # End-to-end diagnostic: the SAME captured signal, decided by two personas
        # on one runtime, reaches materially different terminal outcomes.
        seed("social-a", "shared festival signal", "https://example.org/shared",
             ["indian-festivals"], "operator-supplied")
        gen = decision.run_cycle("social-a", "social-a")
        cul = decision.run_cycle("social-a", "cultural-primandir-atman")
        self.assertEqual(gen["outcome"], "candidate_created")
        self.assertEqual(cul["outcome"], "withheld")  # cultural: no named reviewer
        self.assertNotEqual(gen["outcome"], cul["outcome"])

    def test_contextual_fails_closed_when_adaptive_required(self):
        os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"
        seed("social-b", "x", "https://example.org/e", ["a"], "live-capture")
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])


# --------------------------------------------------------------------------- #
# ACCEPTANCE LAYER — the ADAPTIVE provider path, driven by replayed sanitized
# receipts. adaptive=True, no live call. Isolation is enforced; divergence proved.
# --------------------------------------------------------------------------- #
ADAPTIVE_PROVIDER_ID = "claude-code-subscription-v1"


def _receipt(ctx, alternatives, recommended, kind=rr.SEAM_FIXTURE_KIND):
    return rr.build_receipt(
        bounded=rr.bounded_context(ctx), alternatives=alternatives,
        recommended_action=recommended, uncertainties=["adaptive uncertainty"],
        provider_id=ADAPTIVE_PROVIDER_ID, generated_at="2026-09-21T00:00:00Z",
        receipt_kind=kind, proposal_id=f"p-{recommended}")


class AdaptiveReceiptDivergenceTest(unittest.TestCase):
    """Persona-only and evidence-only divergence through adaptive=True replay."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ["SBOTS_REASONING"] = "model"  # adaptive route
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)

    def tearDown(self):
        reasoning.register_model_callable(None)
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)

    def _adaptive_propose(self, receipts, ctx):
        reasoning.register_model_callable(rr.replay_callable(receipts))
        provider = reasoning.resolve_provider(require_adaptive=True)
        self.assertTrue(getattr(provider, "adaptive", False),
                        "acceptance must run the adaptive provider path")
        self.assertTrue(provider.available())
        prop = provider.propose(ctx)
        self.assertIsNotNone(prop)
        # The adaptive proposal must still pass the engine's schema/authority gate.
        self.assertEqual(reasoning.validate_proposal(prop, ctx), [])
        self.assertTrue(prop.adaptive)
        self.assertEqual(prop.provider_id, ADAPTIVE_PROVIDER_ID)
        return prop

    def test_persona_only_divergence_three_workspaces_incl_primandir(self):
        # Three persona/workspace comparisons on IDENTICAL evidence/objective/state.
        contexts = {
            "social-a": _ctx("social-a", SHARED_SIGNAL),
            "social-b": _ctx("social-b", SHARED_SIGNAL),
            "cultural-primandir-atman": _ctx("cultural-primandir-atman", SHARED_SIGNAL),
        }
        # Isolation: every pair differs ONLY in persona.
        names = list(contexts)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                rr.assert_single_variable(
                    rr.bounded_context(contexts[names[i]]),
                    rr.bounded_context(contexts[names[j]]), "persona")
        refs = [SHARED_SIGNAL["id"]]
        receipts = [
            # social-a (general): confidently creates
            _receipt(contexts["social-a"], [
                _alt("NO_ACTION", 0.05, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, []),
                _alt("RESEARCH_MORE", 0.25, 0.4, 0.4, 0.6, 0.05, 0.2, 1.0, 0.0, refs),
                _alt("CREATE_CANDIDATE", 0.82, 0.7, 0.85, 0.8, 0.10, 0.3, 1.0, 0.0, refs),
            ], "CREATE_CANDIDATE"),
            # social-b (general, different voice): also creates but with materially
            # different estimates (different expected_value/relevance/confidence).
            _receipt(contexts["social-b"], [
                _alt("NO_ACTION", 0.05, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, []),
                _alt("RESEARCH_MORE", 0.30, 0.5, 0.5, 0.55, 0.05, 0.2, 1.0, 0.0, refs),
                _alt("CREATE_CANDIDATE", 0.68, 0.6, 0.70, 0.65, 0.15, 0.3, 1.0, 0.0, refs),
            ], "CREATE_CANDIDATE"),
            # cultural-primandir-atman: conservative — needs named reviewer + source,
            # so it recommends RESEARCH_MORE and ranks CREATE below research.
            _receipt(contexts["cultural-primandir-atman"], [
                _alt("NO_ACTION", 0.10, 0.0, 0.05, 1.0, 0.0, 0.0, 1.0, 0.0, []),
                _alt("RESEARCH_MORE", 0.55, 0.8, 0.65, 0.5, 0.05, 0.2, 1.0, 0.0, refs),
                _alt("CREATE_CANDIDATE", 0.25, 0.4, 0.30, 0.4, 0.45, 0.3, 1.0, 0.0, refs),
            ], "RESEARCH_MORE"),
        ]
        props = {name: self._adaptive_propose(receipts, ctx)
                 for name, ctx in contexts.items()}

        # >=3 material persona/workspace comparisons, cultural/Primandir included.
        d_ab = rr.proposal_divergence(props["social-a"], props["social-b"])
        d_ac = rr.proposal_divergence(props["social-a"], props["cultural-primandir-atman"])
        d_bc = rr.proposal_divergence(props["social-b"], props["cultural-primandir-atman"])
        self.assertTrue(d_ab["material"], d_ab)
        self.assertTrue(d_ac["material"] and d_ac["recommended_changed"], d_ac)
        self.assertTrue(d_bc["material"] and d_bc["recommended_changed"], d_bc)
        # The cultural workspace is the conservative one (does not recommend CREATE).
        self.assertEqual(props["cultural-primandir-atman"].recommended_action, "RESEARCH_MORE")

    def test_evidence_only_divergence(self):
        # Same persona/objective/state; ONLY the evidence changes.
        strong = {"id": "s-strong", "title": "strong sourced", "tags": ["measurement", "roi"],
                  "provenance": "live-capture", "url": "https://example.org/strong", "source": "x"}
        thin = {"id": "s-thin", "title": "thin unsourced", "tags": [], "provenance": "fixture",
                "url": None, "source": ""}
        cx_s, cx_t = _ctx("social-a", strong), _ctx("social-a", thin)
        rr.assert_single_variable(rr.bounded_context(cx_s), rr.bounded_context(cx_t), "evidence")
        receipts = [
            _receipt(cx_s, [
                _alt("NO_ACTION", 0.05, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, []),
                _alt("RESEARCH_MORE", 0.25, 0.4, 0.4, 0.6, 0.05, 0.2, 1.0, 0.0, ["s-strong"]),
                _alt("CREATE_CANDIDATE", 0.85, 0.7, 0.9, 0.85, 0.1, 0.3, 1.0, 0.0, ["s-strong"]),
            ], "CREATE_CANDIDATE"),
            _receipt(cx_t, [
                _alt("NO_ACTION", 0.15, 0.0, 0.05, 1.0, 0.0, 0.0, 1.0, 0.0, []),
                _alt("RESEARCH_MORE", 0.6, 0.85, 0.7, 0.5, 0.05, 0.2, 1.0, 0.0, ["s-thin"]),
                _alt("CREATE_CANDIDATE", 0.2, 0.3, 0.25, 0.4, 0.3, 0.3, 1.0, 0.0, ["s-thin"]),
            ], "RESEARCH_MORE"),
        ]
        p_s = self._adaptive_propose(receipts, cx_s)
        p_t = self._adaptive_propose(receipts, cx_t)
        d = rr.proposal_divergence(p_s, p_t)
        self.assertTrue(d["material"] and d["recommended_changed"] and d["ranking_changed"], d)
        self.assertEqual(p_s.recommended_action, "CREATE_CANDIDATE")
        self.assertEqual(p_t.recommended_action, "RESEARCH_MORE")

    def test_replay_fails_closed_when_no_receipt_matches(self):
        # Adaptive required but no receipt for this context -> BLOCKED, not faked.
        os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"
        reasoning.register_model_callable(rr.replay_callable([]))  # no receipts
        seed("social-b", "unmatched", "https://example.org/u", ["a"], "live-capture")
        rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])


class AdaptiveReplayEngineInvariantsTest(unittest.TestCase):
    """A replayed adaptive proposal flows end-to-end through the engine while every
    authority / no-public-effect / policy-boundary invariant still holds."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ["SBOTS_REASONING"] = "model"
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)

    def tearDown(self):
        reasoning.register_model_callable(None)
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)

    def _engine_ctx(self, bot, persona_id):
        persona = load_persona(persona_id)
        pending = research.unconsumed_signals(bot, set())
        sig = pending[0]
        draft = pipeline.ideate(persona, sig)
        return ReasoningContext(
            persona=persona, objective=decision._current_objective(persona),
            top_signal=sig, pending_count=len(pending),
            is_duplicate=pipeline.is_duplicate(bot, draft), draft=draft,
            state_summary={"hypotheses": 0, "cycles": 1})

    def test_replayed_create_is_queued_unpublished_with_no_public_effect(self):
        seed("social-b", "strong sourced finding", "https://example.org/strong",
             ["measurement", "roi"], "live-capture")
        ctx = self._engine_ctx("social-b", "social-b")
        refs = [ctx.top_signal["id"]]
        receipt = _receipt(ctx, [
            _alt("NO_ACTION", 0.05, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, []),
            _alt("CREATE_CANDIDATE", 0.85, 0.7, 0.9, 0.85, 0.1, 0.3, 1.0, 0.0, refs),
        ], "CREATE_CANDIDATE")
        reasoning.register_model_callable(rr.replay_callable([receipt]))

        rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        # Adaptive route actually ran: the engine resolved the adaptive
        # ModelReasoningProvider (adaptive=True) and it produced the proposal.
        self.assertTrue(rec["reasoning"]["adaptive"])
        self.assertEqual(rec["reasoning"]["provider"], "model-adaptive-v0")
        self.assertEqual(rec["outcome"], "candidate_created")
        # No public effect: queued only, never publish-authorized or published.
        self.assertFalse(rec["verify"]["publish_authorized"])
        self.assertFalse(rec["verify"]["published"])
        # Publish queue holds the candidate but with publish NOT authorized.
        q = pipeline.admin_publish_queue("social-b")
        self.assertEqual(len(q), 1)

    def test_recommended_action_is_advisory_policy_selects_by_ranking(self):
        # The receipt recommends NO_ACTION, but CREATE_CANDIDATE ranks highest; the
        # deterministic policy selects by its own ranking, not the recommendation.
        seed("social-b", "strong sourced finding", "https://example.org/strong",
             ["measurement", "roi"], "live-capture")
        ctx = self._engine_ctx("social-b", "social-b")
        refs = [ctx.top_signal["id"]]
        receipt = _receipt(ctx, [
            _alt("NO_ACTION", 0.05, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, []),
            _alt("CREATE_CANDIDATE", 0.9, 0.8, 0.9, 0.85, 0.05, 0.2, 1.0, 0.0, refs),
        ], "NO_ACTION")  # advisory recommendation deliberately != best-ranked
        reasoning.register_model_callable(rr.replay_callable([receipt]))

        rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        self.assertEqual(rec["policy"]["provider_recommended"], "NO_ACTION")
        self.assertEqual(rec["policy"]["policy_selected"], "CREATE_CANDIDATE")
        self.assertFalse(rec["policy"]["recommended_followed"])

    def test_authority_smuggling_receipt_is_refused(self):
        # A receipt that tries to smuggle publish authority cannot even be indexed.
        seed("social-b", "strong", "https://example.org/s", ["a", "b"], "live-capture")
        ctx = self._engine_ctx("social-b", "social-b")
        refs = [ctx.top_signal["id"]]
        receipt = _receipt(ctx, [
            _alt("CREATE_CANDIDATE", 0.9, 0.8, 0.9, 0.85, 0.05, 0.2, 1.0, 0.0, refs),
        ], "CREATE_CANDIDATE")
        receipt["alternatives"][0]["publish_authorized"] = True
        with self.assertRaises(rr.ReceiptError):
            rr.replay_callable([receipt])


class RealCanaryReceiptAcceptanceTest(unittest.TestCase):
    """Consume the SANITIZED REAL SB-V04-005 receipt when it exists; skip cleanly
    until the canary has run. This is the gate the lead uses for FINAL adaptive
    acceptance — Core never fabricates the receipt."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ["SBOTS_REASONING"] = "model"

    def tearDown(self):
        reasoning.register_model_callable(None)
        os.environ.pop("SBOTS_REASONING", None)

    def test_real_canary_receipts_replay_through_adaptive_path(self):
        receipts = rr.load_real_canary_receipts()
        if not receipts:
            self.skipTest(
                "awaiting SB-V04-005 real canary receipt in "
                f"{rr.REAL_CANARY_RECEIPT_DIR}; the seam + isolation are verified by "
                "AdaptiveReceiptDivergenceTest; final adaptive acceptance is gated "
                "on the real sanitized receipt")
        # When present, every real receipt must be adaptive, schema-clean, and
        # replay to a proposal that passes the engine's authority/schema gate.
        reasoning.register_model_callable(rr.replay_callable(receipts))
        for receipt in receipts:
            self.assertTrue(receipt["adaptive"])
            self.assertEqual(receipt["receipt_kind"], rr.REAL_CANARY_KIND)
            self.assertEqual(rr.validate_receipt(receipt), [])
            prop = rr.proposal_from_receipt(receipt)
            self.assertTrue(prop.adaptive)


if __name__ == "__main__":
    unittest.main()
