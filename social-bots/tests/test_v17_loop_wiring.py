"""V1.7 D2 — the V1.2–V1.6 producers wired into the ordinary decision cycle.

- V1.2 platform selection: only the credential-free account route registry can
  make a platform available; no registry => explicit exploratory drafting for
  the persona's primary platform (nothing publishable); a registry with no
  eligible route => NO_PLATFORM, nothing queued.
- V1.3 measurement semantics: per-platform history comes only from PRESENT
  derived rates of real normalized observations; MISSING is never zero.
- V1.4 audience: the persona's OWN learned hypotheses reach the reasoning
  context, the model prompt projection and the context digest.
- V1.5 experiment closeout: elapsed engine experiments close honestly —
  INCONCLUSIVE without a treatment measurement, a real effect with one.
- V1.6 lineage/novelty: variants are recorded in persona-scoped history with
  concept lineage; a near-duplicate rendering is withheld.
ENGINEERING-ONLY: temp homes, fixtures, deterministic providers, no model call.
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import (account_routes, audience, decision, experiment_engine as ee,  # noqa: E402
                     metrics, model_dispatch, paths, pipeline, reasoning, research)
from runtime import reasoning_cli, reasoning_receipt as rr  # noqa: E402
from runtime.jsonstore import read_jsonl  # noqa: E402


def seed(bot, title="Water tension demo", url="https://example.org/leaf",
         summary="A leaf floats because of surface tension."):
    research.capture(bot, research.Signal.make(
        title, summary, "unit-test", url, "fixture", ["nature"]))


def route(bot, persona, platform, *, health="verified", draft=True, publish=False,
          publish_authorized=False, route_type="API", **extra):
    r = {"schema_version": 1, "route_id": f"r-{bot}-{persona}-{platform}",
         "platform": platform, "bot": bot, "persona": persona, "route_type": route_type,
         "account_alias": f"alias-{platform}", "credential_reference_alias": "keychain:item",
         "capabilities": {"read": True, "draft": draft, "publish": publish, "reply": False,
                          "dm": False, "analytics": False},
         "publish_authorized": publish_authorized, "health_status": health,
         "last_verified_at": "2026-09-21T00:00:00Z", "verification_method": "fixture"}
    r.update(extra)
    return r


def write_registry(routes):
    path = account_routes.registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "routes": routes}), encoding="utf-8")
    return path


def _iso(dt):
    return dt.isoformat()


class _Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.env = {k: os.environ.get(k) for k in ("SBOTS_HOME", "SBOTS_REASONING",
                                                    "SBOTS_REASONING_REQUIRE_ADAPTIVE")}
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ.pop("SBOTS_REASONING", None)
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)
        reasoning.register_model_callable(None)
        model_dispatch.clear()

    def tearDown(self):
        for k, v in self.env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        reasoning.register_model_callable(None)
        model_dispatch.clear()


class PlatformSelectionTest(_Case):
    def test_no_registry_drafts_exploratory_and_unverified(self):
        seed("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["outcome"], "candidate_created")
        sel = rec["verify"]["platform_selection"]
        self.assertEqual(sel["mode"], "exploratory_unverified")
        self.assertFalse(sel["registry_present"])
        self.assertFalse(sel["publishable"])
        self.assertEqual(sel["platform"], "x")
        self.assertTrue({"reddit", "x"} <= set(sel["blocked"]), sel["blocked"])
        self.assertEqual(sel["selectable"], [])

    def test_registry_without_a_usable_route_yields_no_platform(self):
        write_registry([route("social-a", "social-a", "x", health="unhealthy")])
        seed("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["outcome"], "no_platform")
        sel = rec["verify"]["platform_selection"]
        self.assertEqual(sel["mode"], "no_platform")
        self.assertIn("x", sel["blocked"])
        self.assertFalse(rec["verify"]["queued"])
        self.assertFalse(rec["verify"]["experiment_registered"])
        self.assertEqual(pipeline.admin_publish_queue("social-a"), [])
        self.assertEqual(list(paths.experiments_dir("social-a").glob("exp-*.json")), [])
        actions = read_jsonl(paths.memory_dir("social-a") / "action_history.jsonl")
        self.assertEqual(actions[-1]["action"], "CREATE_CANDIDATE_NO_PLATFORM")

    def test_a_verified_draft_route_is_selected_with_exploratory_uncertainty(self):
        write_registry([route("social-a", "social-a", "x")])
        seed("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["outcome"], "candidate_created")
        sel = rec["verify"]["platform_selection"]
        self.assertEqual((sel["mode"], sel["platform"], sel["route_id"]),
                         ("registry_route", "x", "r-social-a-social-a-x"))
        self.assertEqual(sel["ranked"][0]["uncertainty"], "high")
        self.assertFalse(sel["any_historical_basis"])
        self.assertFalse(sel["publishable"])
        self.assertIn("reddit", sel["blocked"])

    def test_publishable_needs_an_explicit_owner_grant_on_the_route(self):
        write_registry([route("social-a", "social-a", "x", publish=True)])
        seed("social-a")
        self.assertFalse(decision.run_cycle("social-a", "social-a")
                         ["verify"]["platform_selection"]["publishable"])
        write_registry([route("social-a", "social-a", "x", publish=True,
                              publish_authorized=True)])
        seed("social-a", title="Second story", url="https://example.org/2",
             summary="Ice floats because it is less dense than water.")
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["outcome"], "candidate_created")
        self.assertTrue(rec["verify"]["platform_selection"]["publishable"])
        # The queue itself still never authorizes publication.
        self.assertFalse(all(e["publish_authorized"] for e in pipeline.admin_publish_queue("social-a")))

    def test_text_only_content_is_unsuitable_for_video_only_routes(self):
        write_registry([route("social-b", "social-b", "instagram"),
                        route("social-b", "social-b", "tiktok")])
        seed("social-b")
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "no_platform")
        sel = rec["verify"]["platform_selection"]
        self.assertEqual(sel["content_format"], "text")
        self.assertEqual(sorted(sel["unsuitable"]), ["instagram", "tiktok"])

    def test_a_poisoned_registry_fails_closed(self):
        write_registry([dict(route("social-a", "social-a", "x"), password="hunter2")])
        with self.assertRaises(account_routes.RouteRegistryError):
            account_routes.load_routes()
        seed("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["outcome"], "no_platform")
        self.assertIn("secret-like", rec["verify"]["platform_selection"]["registry_error"])

    def test_history_uses_only_present_measurements(self):
        write_registry([route("social-a", "social-a", "x")])
        window = {"window_start": "2026-09-19T00:00:00+00:00",
                  "window_end": "2026-09-21T00:00:00+00:00"}
        # PRESENT click-through rate (10/100) on x ...
        metrics.record("social-a", metrics.normalize(
            platform="x", raw_metrics={"impressions": 100, "url_link_clicks": 10},
            source="fixture", persona="social-a", content_id="c-1", **window))
        # ... and an observation whose clicks are MISSING: excluded, not zero.
        metrics.record("social-a", metrics.normalize(
            platform="x", raw_metrics={"impressions": 500}, source="fixture",
            persona="social-a", content_id="c-2", **window))
        # Another persona's measurement never counts for this persona.
        metrics.record("social-a", metrics.normalize(
            platform="x", raw_metrics={"impressions": 100, "url_link_clicks": 90},
            source="fixture", persona="cultural-primandir-atman", content_id="c-9", **window))
        self.assertEqual(decision._platform_history("social-a", "social-a"),
                         {"x": {"performance": 0.1, "samples": 1}})
        seed("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        sel = rec["verify"]["platform_selection"]
        self.assertTrue(sel["any_historical_basis"])
        top = sel["ranked"][0]
        self.assertEqual((top["platform"], top["uncertainty"]), ("x", "medium"))
        self.assertEqual(top["historical_basis"]["samples"], 1)
        self.assertAlmostEqual(top["historical_basis"]["performance"], 0.1)


class AudienceEvidenceTest(_Case):
    SEG = {"topic": "everyday-physics", "format": "did-you-notice-post"}

    def _learned(self, persona):
        hyp = audience.new_hypothesis("social-b", persona, self.SEG, "Sensory hooks earn shares.")
        audience.add_observation(hyp, audience.Observation.make(
            audience.SUPPORTS, {"content_id": "c-1", "experiment_id": "e-1"}, weight=2.0))
        audience.save("social-b", persona, hyp)
        return hyp

    def test_own_learned_evidence_reaches_reasoning_and_the_digest(self):
        mine = self._learned("social-b")
        unlearned = audience.new_hypothesis("social-b", "social-b", self.SEG, "Unproven idea.")
        audience.save("social-b", "social-b", unlearned)
        other = self._learned("cultural-primandir-utsava")     # another persona, same runtime
        seen = {}

        def capture(ctx):
            seen["ctx"] = ctx
            return reasoning.ReasoningProposal(
                alternatives=[reasoning.no_action("fixture")], recommended_action="NO_ACTION",
                uncertainties=[], provider_id="model-adaptive-v0", adaptive=True)

        os.environ["SBOTS_REASONING"] = "model"
        reasoning.register_model_callable(reasoning.EngineeringStub(capture))
        seed("social-b")
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "no_action")
        aud = seen["ctx"].state_summary["audience"]
        self.assertEqual(aud["scope"], {"bot": "social-b", "persona": "social-b"})
        self.assertEqual([h["hypothesis_id"] for h in aud["learned"]], [mine.id])
        self.assertTrue(0.0 < aud["learned"][0]["confidence"] <= 1.0)
        self.assertEqual(aud["unlearned_count"], 1)
        self.assertNotIn(other.id, json.dumps(aud))
        self.assertTrue(any("audience" in k for k in rec["orient"]["known"]))
        # Projections: the prompt context and the receipt digest both carry it.
        prompt = reasoning_cli.prompt_context(seen["ctx"])
        self.assertEqual(prompt["audience"]["learned"][0]["hypothesis_id"], mine.id)
        with_aud = rr.context_digest(rr.bounded_context(seen["ctx"]))
        bare = reasoning.ReasoningContext(
            persona=seen["ctx"].persona, objective=seen["ctx"].objective,
            top_signal=seen["ctx"].top_signal, pending_count=seen["ctx"].pending_count,
            is_duplicate=seen["ctx"].is_duplicate, draft=seen["ctx"].draft,
            state_summary={"hypotheses": seen["ctx"].state_summary["hypotheses"]})
        self.assertNotEqual(with_aud, rr.context_digest(rr.bounded_context(bare)))
        self.assertNotIn("audience", rr.bounded_context(bare))   # no evidence: unchanged shape


class ExperimentCloseoutTest(_Case):
    def _running(self, persona="social-b", started_days_ago=3):
        base = metrics.normalize(
            platform="instagram", raw_metrics={"reach": 100}, source="fixture",
            persona=persona, content_id="c-base",
            window_start="2026-09-10T00:00:00+00:00", window_end="2026-09-12T00:00:00+00:00")
        exp = ee.design("social-b", persona, hypothesis="h", baseline_observation=base,
                        intervention="publish 1 wonder post", primary_metric=metrics.REACH,
                        min_observation_hours=48, stop_criteria={"direction": "increase",
                                                                 "min_effect": 0})
        ee.start(exp, now=datetime.now(timezone.utc) - timedelta(days=started_days_ago))
        ee.register_experiment("social-b", persona, exp)
        return exp

    def test_elapsed_experiment_without_a_measurement_closes_inconclusive(self):
        exp = self._running()
        rec = decision.run_cycle("social-b", "social-b")      # no pending signals
        self.assertEqual(rec["outcome"], "no_action")
        [closed] = rec["closeout"]
        self.assertEqual((closed["experiment_id"], closed["outcome"]), (exp.id, ee.INCONCLUSIVE))
        self.assertIn("no treatment observation", closed["reason"])
        self.assertIsNone(closed["learning_ref"])
        stored = ee.load_experiment("social-b", "social-b", exp.id)
        self.assertEqual((stored.status, stored.outcome), (ee.CLOSED, ee.INCONCLUSIVE))
        self.assertEqual(decision.run_cycle("social-b", "social-b")["closeout"], [])

    def test_unelapsed_experiment_is_left_running(self):
        exp = self._running(started_days_ago=0)
        rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["closeout"], [])
        self.assertEqual(ee.load_experiment("social-b", "social-b", exp.id).status, ee.RUNNING)

    def test_elapsed_experiment_with_a_measurement_closes_with_a_real_effect(self):
        exp = self._running()
        now = datetime.now(timezone.utc)
        metrics.record("social-b", metrics.normalize(
            platform="instagram", raw_metrics={"reach": 150}, source="fixture",
            persona="social-b", content_id="c-treat", experiment_id=exp.id,
            window_start=_iso(now - timedelta(days=2, hours=1)),
            window_end=_iso(now - timedelta(hours=1))))
        rec = decision.run_cycle("social-b", "social-b")
        [closed] = rec["closeout"]
        self.assertEqual(closed["outcome"], ee.SUCCESS)
        self.assertTrue(closed["treatment_observation_id"].startswith("obs-"))
        self.assertEqual(closed["learning_ref"]["effect_size"], 50.0)
        stored = ee.load_experiment("social-b", "social-b", exp.id)
        self.assertEqual(stored.result["treatment"], 150.0)
        self.assertEqual(len(stored.learning_refs), 1)

    def test_another_personas_measurement_is_not_used(self):
        exp = self._running()
        now = datetime.now(timezone.utc)
        metrics.record("social-b", metrics.normalize(
            platform="instagram", raw_metrics={"reach": 999}, source="fixture",
            persona="cultural-primandir-utsava", content_id="c-x", experiment_id=exp.id,
            window_start=_iso(now - timedelta(days=2)), window_end=_iso(now)))
        [closed] = decision.run_cycle("social-b", "social-b")["closeout"]
        self.assertEqual(closed["outcome"], ee.INCONCLUSIVE)


class LineageAndNoveltyTest(_Case):
    def test_variants_are_recorded_with_lineage_and_near_duplicates_are_withheld(self):
        seed("social-a", url="https://example.org/first")
        first = decision.run_cycle("social-a", "social-a")
        self.assertEqual(first["outcome"], "candidate_created")
        lineage = first["verify"]["lineage"]
        self.assertEqual(lineage["platform"], "x")
        self.assertTrue(lineage["concept_id"].startswith("cc-"))
        self.assertTrue(first["verify"]["novelty"]["novel"])
        hist = read_jsonl(paths.content_dir("social-a") / "social-a" / "content_intel_history.jsonl")
        self.assertEqual([h["concept_id"] for h in hist], [lineage["concept_id"]])
        content = read_jsonl(paths.content_dir("social-a") / "content_history.jsonl")
        self.assertEqual(content[-1]["concept_id"], lineage["concept_id"])
        # Same words, different source -> different signal, near-identical rendering.
        seed("social-a", url="https://example.org/second")
        second = decision.run_cycle("social-a", "social-a")
        self.assertEqual(second["outcome"], "withheld")
        gates = {g["gate"] for g in second["execute"]["gate_failures"]}
        self.assertIn("novelty", gates)
        self.assertFalse(second["verify"]["novelty"]["novel"])
        self.assertEqual(len(pipeline.admin_publish_queue("social-a")), 1)

    def test_novelty_is_persona_scoped(self):
        seed("social-a", url="https://example.org/first")
        decision.run_cycle("social-a", "social-a")
        # The cultural persona's history is separate: same signal is novel for it
        # (it is withheld for lack of a named reviewer, not for novelty).
        rec = decision.run_cycle("social-a", "cultural-primandir-atman")
        self.assertEqual(rec["outcome"], "withheld")
        gates = {g["gate"] for g in rec["execute"]["gate_failures"]}
        self.assertNotIn("novelty", gates)


if __name__ == "__main__":
    unittest.main()
