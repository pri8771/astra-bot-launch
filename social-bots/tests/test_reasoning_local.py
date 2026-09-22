"""Offline local-provider regressions; all HTTP connections are in-process mocks."""

import json
import unittest
from dataclasses import asdict
from unittest import mock

from runtime import (
    authorization,
    model_dispatch,
    reasoning,
    reasoning_cli,
    reasoning_local,
)
from runtime import divergence_prepare as dp
from tests import test_v04_execution_binding as binding_tests
from tests.test_v04_divergence_prepare import PERSONAS, build


class LocalProviderTest(unittest.TestCase):
    _manifest = binding_tests.ExecutionBindingTest._manifest
    _write_manifest = binding_tests.ExecutionBindingTest._write_manifest
    _case_context = binding_tests.ExecutionBindingTest._case_context

    def setUp(self):
        binding_tests.ExecutionBindingTest.setUp(self)
        self.config = reasoning_local.provider_config()
        self.matrix = build(provider_config=self.config, lane="mac-local")
        self.binding = dp.execution_binding(self.matrix)
        self.transport = self.enterContext(
            mock.patch.object(reasoning_local.http.client, "HTTPConnection")
        )
        self.enterContext(
            mock.patch.object(
                authorization,
                "source_identity",
                return_value=(binding_tests.SHA, binding_tests.TREE),
            )
        )
        self.calls = []
        self.tags = {
            "models": [
                {"name": self.config["model"], "digest": self.config["model_digest"]}
            ]
        }
        self.generated = {
            "model": self.config["model"],
            "done": True,
            "done_reason": "stop",
            "response": json.dumps(
                {
                    "alternatives": [asdict(reasoning.no_action("offline fixture"))],
                    "recommended_action": "NO_ACTION",
                    "uncertainties": [],
                }
            ),
        }

        def connection(*args, **kwargs):
            conn = mock.MagicMock()

            def request(method, path, body=None, headers=None):
                self.calls.append((method, path, json.loads(body) if body else None))

            def response():
                value = (
                    self.tags if self.calls[-1][1] == "/api/tags" else self.generated
                )
                return mock.Mock(
                    status=200, read=lambda cap: json.dumps(value).encode()
                )

            conn.request.side_effect = request
            conn.getresponse.side_effect = response
            return conn

        self.transport.side_effect = connection

    def tearDown(self):
        binding_tests.ExecutionBindingTest.tearDown(self)

    def _grant(self, **updates):
        self._write_manifest(provider_mode="ollama-local", **updates)

    def _one(self):
        model_dispatch.configure(
            "SB-V04-002",
            self.matrix.lane,
            self.matrix.run_scope,
            manifest_dir=self.manifests,
            home=self.home,
            execution_binding=self.binding,
        )
        return reasoning_local.OllamaLocalReasoningProvider(self.config).propose(
            self._case_context("P0")
        )

    def _batch(self):
        return dp.execute_batch(
            self.matrix,
            lane=self.matrix.lane,
            personas=PERSONAS,
            snapshots=self.snapshots,
            manifest_dir=self.manifests,
            home=self.home,
        )

    def _slots(self):
        return authorization.CallBudget(
            self.matrix.run_scope, 5, home=self.home
        ).slots()

    def test_absent_authority_cannot_connect_or_consume(self):
        self.assertIsNone(self._one())
        self.transport.assert_not_called()
        self.assertEqual(self._slots(), [])

    def test_claude_manifest_cannot_authorize_local_inference(self):
        self._write_manifest()
        with self.assertRaises(authorization.AuthorizationDenied):
            self._batch()
        self.transport.assert_not_called()
        self.assertEqual(self._slots(), [])

    def test_local_manifest_cannot_authorize_hosted_claude(self):
        self._grant()
        model_dispatch.configure(
            "SB-V04-002",
            self.matrix.lane,
            self.matrix.run_scope,
            manifest_dir=self.manifests,
            home=self.home,
            execution_binding=self.binding,
        )
        with (
            mock.patch.object(
                reasoning_cli.shutil, "which", return_value="/fake/claude"
            ),
            mock.patch.object(reasoning_cli.subprocess, "run") as spawn,
        ):
            spawn.return_value = mock.Mock(
                returncode=0, stdout=self.generated["response"], stderr=""
            )
            proposal = reasoning_cli.ClaudeCodeReasoningProvider().propose(
                self._case_context("P0")
            )
        self.assertIsNone(proposal)
        spawn.assert_not_called()
        self.assertEqual(self._slots(), [])

    def test_direct_provider_requires_exact_reviewed_configuration(self):
        self._grant()
        # A different reviewed route cannot use this provider, even with a valid grant.
        payload = self.binding.closure()
        payload["provider_config"]["model"] = "other-model"
        self.binding = authorization.ExecutionBinding(json.dumps(payload))
        self.assertIsNone(self._one())
        self.transport.assert_not_called()

    def test_spoofed_local_label_cannot_invoke_raw_callable(self):
        self._grant()
        scope = model_dispatch.configure(
            "SB-V04-002",
            self.matrix.lane,
            self.matrix.run_scope,
            manifest_dir=self.manifests,
            home=self.home,
            execution_binding=self.binding,
        )
        sentinel = mock.Mock()
        ctx = self._case_context("P0")
        with self.assertRaises(model_dispatch.DispatchRefused):
            model_dispatch.dispatch(
                sentinel, ctx, provider_id=reasoning_local.PROVIDER_ID
            )
        self.assertEqual(self._slots(), [])
        with (
            model_dispatch.reserved(
                scope,
                context_digest=self.matrix.case("P0").context_sha256,
                provider_id=reasoning_local.PROVIDER_ID,
            ),
            self.assertRaises(model_dispatch.DispatchRefused),
        ):
            model_dispatch.dispatch(
                sentinel, ctx, provider_id=reasoning_local.PROVIDER_ID
            )
        sentinel.assert_not_called()
        self.assertEqual(len(self._slots()), 1)
        self.transport.assert_not_called()

    def test_remote_endpoint_model_and_option_overrides_refused(self):
        for field, value in [
            ("endpoint", "http://localhost:11434"),
            ("endpoint", "http://192.168.1.1:11434"),
            ("model", "remote:cloud"),
            ("retry_allowed", True),
            ("options", {"num_predict": -1}),
        ]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                reasoning_local.OllamaLocalReasoningProvider(
                    {**self.config, field: value}
                )
        self.transport.assert_not_called()

    def test_missing_or_changed_model_consumes_once_without_generation(self):
        self._grant()
        self.tags["models"][0]["digest"] = "0" * 64
        self.assertIsNone(self._one())
        self.assertEqual([x[:2] for x in self.calls], [("GET", "/api/tags")])
        self.assertEqual(len(self._slots()), 1)
        self.assertEqual(self._slots()[0]["outcome"], "provider_exception")

    def test_cloud_backed_alias_never_generates(self):
        self._grant()
        self.tags["models"][0]["remote_host"] = "https://remote.invalid"
        self.assertIsNone(self._one())
        self.assertEqual(len(self.calls), 1)

    def test_redirect_is_not_followed(self):
        self._grant()
        conn = mock.MagicMock()
        conn.getresponse.return_value.status = 302
        self.transport.side_effect = None
        self.transport.return_value = conn
        self.assertIsNone(self._one())
        self.transport.assert_called_once_with("127.0.0.1", 11434, timeout=120)
        conn.request.assert_called_once()
        conn.close.assert_called_once()
        self.assertEqual(len(self._slots()), 1)

    def test_oversized_response_is_bounded_and_not_retried(self):
        self._grant()
        conn = mock.MagicMock()
        conn.getresponse.return_value.status = 200
        conn.getresponse.return_value.read.return_value = b" " * (
            reasoning_local.MAX_RESPONSE_BYTES + 1
        )
        self.transport.side_effect = None
        self.transport.return_value = conn
        self.assertIsNone(self._one())
        conn.getresponse.return_value.read.assert_called_once_with(
            reasoning_local.MAX_RESPONSE_BYTES + 1
        )
        self.assertEqual(len(self._slots()), 1)

    def test_invalid_output_consumes_once(self):
        self._grant()
        self.generated["response"] = '{"recommended_action":"PUBLISH"}'
        self.assertIsNone(self._one())
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(len(self._slots()), 1)

    def test_bound_five_call_batch_records_local_provider_and_refuses_sixth(self):
        self._grant()
        with mock.patch.dict(
            "os.environ", {"HTTP_PROXY": "http://remote.invalid:9999"}
        ):
            result = self._batch()
        self.assertEqual(len(result["results"]), 5)
        self.assertEqual(len(self._slots()), 5)
        self.assertEqual(len(self.calls), 10)
        for item in result["results"]:
            self.assertEqual(item["outcome"], "proposal_received")
            self.assertEqual(item["proposal"].provider_id, reasoning_local.PROVIDER_ID)
        generated = [c[2] for c in self.calls if c[0] == "POST"]
        self.assertEqual(
            [p["prompt"] for p in generated], [c.prompt for c in self.matrix.cases]
        )
        self.assertTrue(all(p["options"] == self.config["options"] for p in generated))
        self.assertTrue(
            all(
                c == mock.call("127.0.0.1", 11434, timeout=120)
                for c in self.transport.call_args_list
            )
        )
        with self.assertRaises(authorization.AuthorizationDenied):
            self._batch()
        self.assertEqual(len(self.calls), 10)
        self.assertTrue(
            all(
                s["execution_matrix_sha256"] == self.binding.digest
                for s in self._slots()
            )
        )


if __name__ == "__main__":
    unittest.main()
