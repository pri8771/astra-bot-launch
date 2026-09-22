"""Offline fail-fast regressions through real authorization and durable accounting."""

import unittest
from unittest import mock

from runtime import authorization, model_dispatch
from runtime import divergence_prepare as dp
from tests import test_v04_execution_binding as binding_tests
from tests.test_v04_divergence_prepare import PERSONAS


class BatchFailFastTest(unittest.TestCase):
    _manifest = binding_tests.ExecutionBindingTest._manifest
    _write_manifest = binding_tests.ExecutionBindingTest._write_manifest

    def setUp(self):
        binding_tests.ExecutionBindingTest.setUp(self)
        self._write_manifest()
        self.enterContext(
            mock.patch.object(
                authorization,
                "source_identity",
                return_value=(binding_tests.SHA, binding_tests.TREE),
            )
        )

    def tearDown(self):
        binding_tests.ExecutionBindingTest.tearDown(self)

    def _run(self, failure=None, failure_at=0):
        calls = []

        class OfflineProvider:
            provider_id = "offline-sentinel"
            reason = "offline unavailable fixture"

            def propose(self, context):
                def sentinel(inner_context):
                    index = len(calls)
                    calls.append(inner_context)
                    if index == failure_at:
                        if failure == "provider_unavailable":
                            return None
                        if failure == "provider_exception":
                            raise RuntimeError("offline fixture failure")
                        if failure == "invalid_proposal":
                            proposal = binding_tests._proposal()
                            proposal.recommended_action = "INVALID_ACTION"
                            return proposal
                    return binding_tests._proposal()

                return model_dispatch.dispatch(
                    sentinel, context, provider_id=self.provider_id, live=True
                )

        with mock.patch.object(
            dp.reasoning_cli, "ClaudeCodeReasoningProvider", OfflineProvider
        ):
            result = dp.execute_batch(
                self.matrix,
                lane=self.matrix.lane,
                personas=PERSONAS,
                snapshots=self.snapshots,
                manifest_dir=self.manifests,
                home=self.home,
            )
        slots = authorization.CallBudget(
            self.matrix.run_scope, 5, home=self.home
        ).slots()
        self.assertIsNone(model_dispatch.current_scope())
        return result, calls, slots

    def _assert_stopped(self, failure, index):
        result, calls, slots = self._run(failure, index)
        ids = [case.case_id for case in self.matrix.cases]
        self.assertEqual(len(calls), index + 1)
        self.assertEqual(len(slots), index + 1)
        self.assertEqual([item["case"] for item in result["results"]], ids[: index + 1])
        self.assertEqual(
            [item["outcome"] for item in result["results"]],
            ["proposal_received"] * index + [failure],
        )
        self.assertEqual(
            result["batch_stop"],
            {
                "case": ids[index],
                "outcome": failure,
                "unattempted_cases": ids[index + 1 :],
            },
        )
        self.assertEqual(slots[-1]["outcome"], failure)

    def test_first_unavailable_stops_after_one_slot(self):
        self._assert_stopped("provider_unavailable", 0)

    def test_first_exception_stops_after_one_slot(self):
        self._assert_stopped("provider_exception", 0)

    def test_first_invalid_stops_after_one_slot(self):
        self._assert_stopped("invalid_proposal", 0)

    def test_middle_failure_preserves_successes_and_unattempted_slots(self):
        self._assert_stopped("provider_exception", 2)

    def test_valid_batch_preserves_all_five_results(self):
        result, calls, slots = self._run()
        self.assertEqual(len(calls), 5)
        self.assertEqual(len(slots), 5)
        self.assertEqual(
            [item["case"] for item in result["results"]],
            [case.case_id for case in self.matrix.cases],
        )
        self.assertTrue(
            all(item["outcome"] == "proposal_received" for item in result["results"])
        )
        self.assertTrue(all(item["proposal"] is not None for item in result["results"]))
        self.assertNotIn("batch_stop", result)
