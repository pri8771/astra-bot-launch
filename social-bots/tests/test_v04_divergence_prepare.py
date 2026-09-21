"""SB-V04-002/004 — prepare-only divergence matrix: hashing, isolation, reporting.

ENGINEERING-ONLY. Every snapshot here is a labeled fixture and every receipt is a
``synthetic-seam-fixture``. Nothing in this file is causal live-model evidence,
and no test makes or authorizes an adaptive provider call. Empirical
SB-V04-002/SB-V04-004 acceptance remains owner-authorization-blocked.
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import authorization, divergence_prepare as dp  # noqa: E402
from runtime import reasoning_receipt as rr  # noqa: E402

PERSONAS = {
    "baseline": {"id": "social-a", "kind": "general", "display_name": "The Ledger"},
    "variant_b": {"id": "social-b", "kind": "general", "display_name": "Tidepool"},
    "variant_c": {"id": "social-c", "kind": "general", "display_name": "Switchboard"},
    "cultural": {"id": "cultural-primandir-atman", "kind": "cultural",
                 "display_name": "Sadhana Notes"},
}

OBJECTIVE = "grow a durable, factually sound audience without publishing anything unreviewed"


def signal(sid, title, summary, tags, url="https://example.invalid/x"):
    return {"id": sid, "title": title, "summary": summary, "source": "engineering-fixture",
            "url": url, "captured_at": "2026-09-21T00:00:00Z", "provenance": "fixture",
            "tags": list(tags)}


def snapshot(sid, sig, raw, *, label=dp.ENGINEERING_FIXTURE):
    return dp.EvidenceSnapshot.from_bytes(
        sid, sig, raw, {"kind": "engineering-fixture", "byte_length": len(raw)},
        provenance_label=label, captured_at="2026-09-21T00:00:00Z")


def default_snapshots():
    return {
        "E1": snapshot("E1", signal("sig-e1", "Ledger tooling release",
                                    "A reconciliation report command shipped.",
                                    ["accounting", "tooling"]), b"E1-bytes"),
        "E2": snapshot("E2", signal("sig-e2", "Transit fare-equity dataset",
                                    "A machine-readable fare-equity dataset was published.",
                                    ["transit", "open-data"],
                                    url="https://example.invalid/y"), b"E2-bytes"),
    }


def build(**overrides):
    kwargs = dict(personas=PERSONAS, snapshots=default_snapshots(), objective=OBJECTIVE,
                  run_scope="v04-divergence-test", lane="windows-core")
    kwargs.update(overrides)
    return dp.build_matrix(**kwargs)


class MatrixShapeTest(unittest.TestCase):
    def test_matrix_is_the_five_planned_cases(self):
        """The matrix is exactly the plan's P0/P1/P2/P3/E0, in that order."""
        matrix = build()
        self.assertEqual([c.case_id for c in matrix.cases],
                         ["P0", "P1", "P2", "P3", "E0"])
        self.assertEqual([c.persona_id for c in matrix.cases],
                         ["social-a", "social-b", "social-c",
                          "cultural-primandir-atman", "social-a"])
        self.assertEqual([c.evidence_id for c in matrix.cases],
                         ["E1", "E1", "E1", "E1", "E2"])

    def test_one_cultural_workspace_is_included(self):
        """The plan requires a cultural/Primandir workspace among the persona variants."""
        matrix = build()
        self.assertEqual(matrix.case("P3").bounded_context["persona"]["kind"], "cultural")

    def test_held_constant_fields_are_identical_across_every_case(self):
        """Objective, pending count, duplication and prior hypotheses never vary."""
        matrix = build(pending_count=2, prior_hypotheses=3)
        for name in ("objective", "pending_count", "is_duplicate", "prior_hypotheses"):
            values = {json.dumps(c.bounded_context[name], sort_keys=True)
                      for c in matrix.cases}
            self.assertEqual(len(values), 1, f"{name} varied across cases: {values}")

    def test_missing_persona_slot_or_snapshot_is_refused(self):
        """An incomplete matrix is an error, not a silently smaller batch."""
        with self.assertRaises(dp.MatrixError):
            build(personas={k: v for k, v in PERSONAS.items() if k != "cultural"})
        with self.assertRaises(dp.MatrixError):
            build(snapshots={"E1": default_snapshots()["E1"]})


class HashingTest(unittest.TestCase):
    def test_every_case_emits_all_five_required_digests(self):
        """Context, prompt, prompt-context, evidence bytes and evidence receipt."""
        for case in build().cases:
            for name in ("context_sha256", "prompt_sha256", "prompt_context_sha256",
                         "evidence_bytes_sha256", "evidence_receipt_sha256"):
                value = getattr(case, name)
                self.assertTrue(value.startswith("sha256:"), (case.case_id, name, value))
                self.assertEqual(len(value), len("sha256:") + 64)

    def test_context_digests_are_distinct_per_case(self):
        """Five identical contexts would make some of the five calls redundant."""
        digests = [c.context_sha256 for c in build().cases]
        self.assertEqual(len(set(digests)), 5)

    def test_evidence_digests_track_the_snapshot_not_the_persona(self):
        """P0-P3 share E1's bytes/receipt digests; only E0 differs."""
        matrix = build()
        e1 = {matrix.case(c).evidence_bytes_sha256 for c in ("P0", "P1", "P2", "P3")}
        self.assertEqual(len(e1), 1)
        self.assertNotIn(matrix.case("E0").evidence_bytes_sha256, e1)

    def test_prompt_digest_is_over_the_exact_production_prompt(self):
        """The recorded prompt digest must hash the real prompt text, byte for byte."""
        from runtime import reasoning_cli
        from runtime.reasoning import ReasoningContext
        snaps = default_snapshots()
        ctx = ReasoningContext(persona=PERSONAS["baseline"], objective=OBJECTIVE,
                               top_signal=snaps["E1"].signal, pending_count=0,
                               is_duplicate=False, draft={},
                               state_summary={"hypotheses": 0})
        matrix = build(snapshots=snaps)
        self.assertEqual(matrix.case("P0").prompt, reasoning_cli.build_prompt(ctx))

    def test_provider_config_is_one_configuration_for_the_whole_batch(self):
        """A per-case provider difference would confound any observed divergence."""
        matrix = build()
        self.assertEqual(matrix.provider_config["provider_mode"], "claude-cli")
        self.assertFalse(matrix.provider_config["retry_allowed"])
        self.assertTrue(matrix.provider_config["anthropic_api_key_expected_absent"])


class IsolationTest(unittest.TestCase):
    def test_all_required_comparisons_are_single_variable(self):
        """P0|P1, P0|P2, P0|P3 vary persona alone; P0|E0 varies evidence alone."""
        report = dp.isolation_report(build())
        self.assertTrue(report["all_isolated"])
        self.assertEqual([c["comparison"] for c in report["comparisons"]],
                         ["P0|P1", "P0|P2", "P0|P3", "P0|E0"])
        for comparison in report["comparisons"]:
            self.assertTrue(comparison["digest_layer"]["ok"], comparison)
            self.assertTrue(comparison["prompt_layer"]["ok"], comparison)

    def test_confounded_persona_variant_is_rejected(self):
        """If a 'persona-only' case also changed objective, the matrix must not build."""
        matrix = build()
        matrix.case("P1").bounded_context["objective"] = "a different objective"
        with self.assertRaises(dp.MatrixError) as ctx:
            dp.verify_isolation(matrix)
        self.assertIn("isolation violated", str(ctx.exception))

    def test_prompt_layer_catches_an_evidence_change_the_digest_layer_cannot_see(self):
        """The digest projection omits the signal summary; the prompt layer must not.

        This is the hole the two-layer check exists for: a 'persona-only' variant
        whose evidence summary was quietly altered would still reach the model
        with different evidence text, so any observed divergence would not be
        attributable to persona alone.
        """
        matrix = build()
        p1 = matrix.case("P1")
        # Change ONLY the summary, which bounded_context (the digest layer) drops.
        p1.prompt_context = copy.deepcopy(p1.prompt_context)
        p1.prompt_context["signal"]["summary"] = "a quietly different evidence summary"
        report = dp.isolation_report(matrix)
        comparison = next(c for c in report["comparisons"] if c["comparison"] == "P0|P1")
        self.assertTrue(comparison["digest_layer"]["ok"],
                        "digest layer is blind to a summary-only change, as expected")
        self.assertFalse(comparison["prompt_layer"]["ok"])
        self.assertEqual(comparison["prompt_layer"]["differing_keys"], ["persona", "signal"])
        self.assertFalse(report["all_isolated"])

    def test_evidence_change_invisible_to_the_digest_layer_fails_the_build(self):
        """E2 differing from E1 only in summary makes P0|E0 non-isolated, so build fails."""
        snaps = default_snapshots()
        e1_sig = snaps["E1"].signal
        near_duplicate = dict(e1_sig, summary="only the summary differs")
        snaps["E2"] = snapshot("E2", near_duplicate, b"E2-bytes")
        with self.assertRaises(dp.MatrixError):
            build(snapshots=snaps)


class ProvenanceTest(unittest.TestCase):
    def test_fixture_snapshots_mark_the_matrix_engineering_only(self):
        """Fixtures can exercise the machinery but can never be acceptance evidence."""
        matrix = build()
        self.assertFalse(matrix.acceptance_eligible)
        self.assertEqual(len(matrix.engineering_only_reasons), 2)
        self.assertTrue(all("engineering-fixture" in r
                            for r in matrix.engineering_only_reasons))

    def test_live_capture_snapshots_clear_the_engineering_only_flag(self):
        """Only real captures make a prepared matrix acceptance-eligible in principle."""
        snaps = default_snapshots()
        for sid in ("E1", "E2"):
            snaps[sid].provenance_label = dp.LIVE_CAPTURE
        matrix = build(snapshots=snaps)
        self.assertTrue(matrix.acceptance_eligible)
        self.assertEqual(matrix.engineering_only_reasons, [])


class WrittenArtifactTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.matrix = build()

    def test_prepared_artifact_is_immutable(self):
        """A prepared matrix is written once; rewriting it is refused."""
        path = self.tmp / "PREPARED_MATRIX.json"
        dp.write_prepared(self.matrix, path)
        with self.assertRaises(dp.MatrixError):
            dp.write_prepared(self.matrix, path)

    def test_round_trip_verification_recomputes_every_digest(self):
        """verify_written re-derives digests from content instead of trusting them."""
        path = self.tmp / "PREPARED_MATRIX.json"
        prompts = self.tmp / "prompts"
        dp.write_prepared(self.matrix, path)
        dp.write_prompts(self.matrix, prompts)
        result = dp.verify_written(path, prompts)
        self.assertTrue(result["verified"])
        self.assertTrue(result["prompt_bytes_verified"])
        self.assertEqual(result["digest_errors"], [])

    def test_tampered_artifact_fails_verification(self):
        """Editing a written context without fixing its digest is detected."""
        path = self.tmp / "PREPARED_MATRIX.json"
        dp.write_prepared(self.matrix, path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][0]["bounded_context"]["objective"] = "tampered"
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = dp.verify_written(path)
        self.assertFalse(result["verified"])
        self.assertTrue(any("context_sha256" in e for e in result["digest_errors"]))

    def test_prompt_files_are_written_once_with_their_digests(self):
        """Each case's exact prompt is preserved next to a digest manifest."""
        prompts = self.tmp / "prompts"
        dp.write_prompts(self.matrix, prompts)
        digests = json.loads((prompts / "PROMPT_DIGESTS.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(digests), ["E0", "P0", "P1", "P2", "P3"])
        with self.assertRaises(dp.MatrixError):
            dp.write_prompts(self.matrix, prompts)


def receipt_for(case, *, recommended="RESEARCH_MORE", bump=0.0):
    """A SYNTHETIC SEAM FIXTURE receipt bound to a prepared case's context digest."""
    signal_id = case.bounded_context["signal"]["id"]

    def alt(action, base):
        return {"action": action, "rationale": f"{action} fixture rationale",
                "expected_value": min(1.0, base + bump), "expected_learning": base,
                "relevance": base, "confidence": 0.6, "risk": 0.1, "cost": 0.2,
                "reversibility": 1.0, "duplication_risk": 0.0,
                "evidence_refs": [signal_id]}

    return rr.build_receipt(
        bounded=case.bounded_context,
        alternatives=[alt("NO_ACTION", 0.1), alt("RESEARCH_MORE", 0.5),
                      alt("CREATE_CANDIDATE", 0.4)],
        recommended_action=recommended, uncertainties=["engineering fixture"],
        provider_id="synthetic-seam-fixture-provider", generated_at="2026-09-21T00:00:00Z",
        receipt_kind=rr.SEAM_FIXTURE_KIND, proposal_id=f"fixture-{case.case_id}")


class DivergenceReportTest(unittest.TestCase):
    def setUp(self):
        self.matrix = build()

    def test_missing_receipts_are_reported_as_not_material(self):
        """A comparison with no receipt is never silently counted as divergent."""
        report = dp.divergence_report(self.matrix, {})
        self.assertFalse(report["all_comparisons_material"])
        self.assertTrue(all(not c["material"] for c in report["comparisons"]))
        self.assertEqual(len(report["errors"]), 5)

    def test_identical_proposals_are_reported_as_not_material(self):
        """No-retry at the reporting layer: a null result is recorded, not rerun."""
        receipts = {c.case_id: receipt_for(c) for c in self.matrix.cases}
        report = dp.divergence_report(self.matrix, receipts)
        self.assertEqual(report["errors"], [])
        self.assertFalse(report["all_comparisons_material"])
        for comparison in report["comparisons"]:
            self.assertIn("identical", comparison["reason"])

    def test_differing_proposals_are_reported_as_material(self):
        """Changed recommendation/ranking/estimates all count as material divergence."""
        receipts = {}
        for index, case in enumerate(self.matrix.cases):
            receipts[case.case_id] = receipt_for(
                case, recommended="CREATE_CANDIDATE" if index else "RESEARCH_MORE",
                bump=0.05 * index)
        report = dp.divergence_report(self.matrix, receipts)
        self.assertEqual(report["errors"], [])
        self.assertTrue(report["all_comparisons_material"])

    def test_a_receipt_bound_to_another_context_is_rejected(self):
        """A receipt must bind to its own case's context digest, or it is invalid."""
        receipts = {c.case_id: receipt_for(c) for c in self.matrix.cases}
        receipts["P1"] = receipt_for(self.matrix.case("P2"))
        report = dp.divergence_report(self.matrix, receipts)
        self.assertTrue(any("does not bind" in e for e in report["errors"]))

    def test_synthetic_receipts_are_never_acceptance_evidence(self):
        """Even fully material divergence from seam fixtures cannot be acceptance evidence."""
        receipts = {}
        for index, case in enumerate(self.matrix.cases):
            receipts[case.case_id] = receipt_for(
                case, recommended="CREATE_CANDIDATE" if index else "RESEARCH_MORE",
                bump=0.05 * index)
        report = dp.divergence_report(self.matrix, receipts)
        self.assertTrue(report["all_comparisons_material"])
        self.assertFalse(report["all_receipts_real_adaptive"])
        self.assertFalse(report["acceptance_evidence_eligible"])
        self.assertIn("ChatGPT lead", report["acceptance_authority"])


class ExecutionGateTest(unittest.TestCase):
    """The prepare-only boundary: execution must fail closed before any spawn."""

    def setUp(self):
        self.matrix = build()
        self.tmp = Path(tempfile.mkdtemp())
        self.empty_manifests = self.tmp / "authorizations"
        self.empty_manifests.mkdir()

    def test_execute_batch_fails_closed_without_a_manifest(self):
        """With no canonical manifest, execution is denied before a provider exists."""
        with self.assertRaises(authorization.AuthorizationDenied):
            dp.execute_batch(self.matrix, lane="windows-core",
                             personas=PERSONAS, snapshots=default_snapshots(),
                             manifest_dir=self.empty_manifests, home=self.tmp)

    def test_denied_execution_consumes_no_call_budget(self):
        """Failing closed must happen before any slot is reserved."""
        with self.assertRaises(authorization.AuthorizationDenied):
            dp.execute_batch(self.matrix, lane="windows-core",
                             personas=PERSONAS, snapshots=default_snapshots(),
                             manifest_dir=self.empty_manifests, home=self.tmp)
        budget = authorization.CallBudget(self.matrix.run_scope, 5, home=self.tmp)
        self.assertEqual(budget.consumed(), 0)

    def test_injected_provider_cannot_bypass_the_gate(self):
        """Supplying a fake provider does not make execution authorized."""
        calls = []

        def factory():
            calls.append(1)
            raise AssertionError("provider must never be constructed while denied")

        with self.assertRaises(authorization.AuthorizationDenied):
            dp.execute_batch(self.matrix, lane="windows-core", personas=PERSONAS,
                             snapshots=default_snapshots(), provider_factory=factory,
                             manifest_dir=self.empty_manifests, home=self.tmp)
        self.assertEqual(calls, [])

    def test_prepare_only_status_states_the_blocked_truth(self):
        """The prepare-only verdict must not imply V0.4 empirical acceptance."""
        status = dp.prepare_only_status(self.matrix, lane="windows-core",
                                        manifest_dir=self.empty_manifests, home=self.tmp)
        self.assertFalse(status["live_execution_permitted"])
        self.assertFalse(status["live_execution_performed"])
        self.assertIn("BLOCKED_OWNER_AUTHORIZATION", status["empirical_acceptance_state"])
        self.assertEqual(status["planned_call_count"], 5)
        self.assertTrue(status["isolation"]["all_isolated"])


class ExecutionMechanicsTest(unittest.TestCase):
    """ENGINEERING-ONLY: the below-the-gate loop, driven by an injected provider.

    These exercise reserve-before-spawn, truthful outcome recording and no-retry
    without any provider call. They are not evidence that a batch may run: every
    public path into this code still goes through the denied gate above.
    """

    def setUp(self):
        self.matrix = build()
        self.tmp = Path(tempfile.mkdtemp())
        self.grant = authorization.ExecutionGrant(
            manifest_id="AUTH-FIXTURE-0001", manifest_path="(fixture)",
            manifest_digest="sha256:fixture", created_by="test-fixture",
            owner_authorization_ref="engineering fixture", artifact="SB-V04-002",
            lane="windows-core", run_scope=self.matrix.run_scope,
            provider_mode="claude-cli", max_calls=5, expires_at="2099-01-01T00:00:00Z",
            granted_at="2026-09-21T00:00:00Z")
        self.budget = authorization.CallBudget(self.matrix.run_scope, 5, home=self.tmp)

    def _run(self, provider, case_id="P0"):
        case = self.matrix.case(case_id)
        return dp._execute_one_case(
            case, provider, self.budget, grant=self.grant, draft={},
            persona=PERSONAS[case.persona_slot], objective=self.matrix.objective,
            snapshot_signal=default_snapshots()[case.evidence_id].signal,
            pending_count=0, is_duplicate=False, prior_hypotheses=0)

    def test_slot_is_reserved_before_the_provider_is_called(self):
        """Atomic pre-spawn accounting: the budget moves before propose() runs."""
        observed = {}

        class Provider:
            reason = None

            def propose(_self, ctx):
                observed["consumed_during_call"] = self.budget.consumed()
                return None

        self._run(Provider())
        self.assertEqual(observed["consumed_during_call"], 1)

    def test_unavailable_provider_consumes_its_slot_and_is_recorded_truthfully(self):
        """A failed call is an outcome, not a cue to retry."""
        class Provider:
            reason = "fixture: unavailable"

            def propose(self, ctx):
                return None

        result = self._run(Provider())
        self.assertEqual(result["outcome"], "provider_unavailable")
        self.assertEqual(self.budget.consumed(), 1)
        self.assertEqual(self.budget.audit()["outcomes"],
                         [{"slot": 1, "outcome": "provider_unavailable"}])

    def test_provider_exception_consumes_its_slot(self):
        """A crashing provider cannot silently hand its slot back."""
        class Provider:
            reason = None

            def propose(self, ctx):
                raise RuntimeError("fixture failure")

        result = self._run(Provider())
        self.assertEqual(result["outcome"], "provider_exception")
        self.assertEqual(self.budget.remaining(), 4)

    def test_schema_invalid_proposal_is_rejected_and_recorded(self):
        """A malformed proposal never becomes a result; its slot is still spent."""
        from runtime.reasoning import Candidate, ReasoningProposal

        class Provider:
            reason = None

            def propose(self, ctx):
                bad = Candidate("NO_ACTION", "fixture", 5.0, 0.1, 0.1, 0.1, 0.1, 0.1,
                                1.0, 0.0)
                return ReasoningProposal([bad], "NO_ACTION", [], "fixture", True)

        result = self._run(Provider())
        self.assertEqual(result["outcome"], "invalid_proposal")
        self.assertEqual(self.budget.remaining(), 4)

    def test_budget_exhaustion_stops_before_a_sixth_call(self):
        """The sixth invocation is refused by the budget, not attempted."""
        class Provider:
            reason = "fixture"

            def propose(self, ctx):
                return None

        provider = Provider()
        for _ in range(5):
            self._run(provider)
        with self.assertRaises(authorization.CallBudgetExhausted):
            self._run(provider)


if __name__ == "__main__":
    unittest.main()
