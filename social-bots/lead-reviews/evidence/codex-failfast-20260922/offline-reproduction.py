"""Offline diagnostic only. Uses existing fixture inputs and in-process sentinel.
No authorization/source-identity functions are patched. No production grant created.
"""
import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
from runtime import authorization, model_dispatch, reasoning
from runtime import divergence_prepare as dp
from tests.test_v04_divergence_prepare import PERSONAS, build, default_snapshots


def iso(v):
    return v.replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def proposal():
    return reasoning.ReasoningProposal(
        alternatives=[reasoning.no_action('offline sentinel')],
        recommended_action='NO_ACTION', uncertainties=['engineering fixture'],
        provider_id='offline-sentinel', adaptive=True)


observations = []
prior_key = os.environ.pop('ANTHROPIC_API_KEY', None)
try:
    sha, tree = authorization.source_identity()
    for scenario in ('provider_unavailable', 'provider_exception', 'invalid_proposal', 'valid_identical_proposals'):
        with tempfile.TemporaryDirectory(prefix='bots-offline-failfast-') as temp:
            root = Path(temp)
            manifests = root / 'engineering-fixture-manifests'
            manifests.mkdir()
            runtime_home = root / 'isolated-runtime'
            matrix = build(run_scope='offline-failfast-' + scenario.replace('_', '-'))
            binding = dp.execution_binding(matrix)
            now = datetime.now(timezone.utc)
            manifest = dict(
                schema_version='v1', manifest_id='AUTH-OFFLINE-FAILFAST-FIXTURE',
                created_by='temporary-engineering-fixture-not-lead',
                created_at=iso(now - timedelta(minutes=1)),
                owner_authorization_ref='OFFLINE FIXTURE ONLY - no live authorization',
                artifact_scope=['SB-V04-002', 'SB-V04-004'],
                run_scope=matrix.run_scope, lane=matrix.lane,
                provider_mode='claude-cli', max_calls=5,
                expires_at=iso(now + timedelta(minutes=10)),
                retry_allowed=False, public_effect_allowed=False,
                spend_authorized=False, api_key_allowed=False,
                injected_runner_allowed=False,
                source_sha=sha, source_tree=tree,
                execution_matrix_sha256=binding.digest)
            (manifests / 'fixture.json').write_text(json.dumps(manifest))
            attempts = []

            class OfflineProvider:
                provider_id = 'offline-sentinel'
                reason = 'temporary offline provider sentinel'
                def propose(self, ctx):
                    def sentinel(actual_ctx):
                        attempts.append({'persona': actual_ctx.persona['id'],
                                         'signal': actual_ctx.top_signal['id']})
                        if len(attempts) == 1:
                            if scenario == 'provider_unavailable':
                                return None
                            if scenario == 'provider_exception':
                                raise RuntimeError('deliberate offline sentinel failure')
                            if scenario == 'invalid_proposal':
                                p = proposal()
                                p.recommended_action = 'NOT_A_VALID_ACTION'
                                return p
                        return proposal()
                    return model_dispatch.dispatch(sentinel, ctx, provider_id=self.provider_id, live=True)

            model_dispatch.clear()
            with mock.patch.object(dp.reasoning_cli, 'ClaudeCodeReasoningProvider', OfflineProvider):
                result = dp.execute_batch(
                    matrix, lane=matrix.lane, personas=PERSONAS,
                    snapshots=default_snapshots(), manifest_dir=manifests,
                    home=runtime_home)
            slots = authorization.CallBudget(matrix.run_scope, 5, home=runtime_home).slots()
            observations.append(dict(
                scenario=scenario, sentinel_attempts=len(attempts),
                attempts=attempts, ledger_slots=len(slots),
                outcomes=[{'case': x['case'], 'outcome': x['outcome']} for x in result['results']],
                exact_source_and_tree=all(s['source_sha'] == sha and s['source_tree'] == tree for s in slots),
                execution_binding=all(s['execution_matrix_sha256'] == binding.digest for s in slots),
                restored_dispatch_scope=model_dispatch.current_scope() is None))
            model_dispatch.clear()
finally:
    if prior_key is not None:
        os.environ['ANTHROPIC_API_KEY'] = prior_key

print(json.dumps(dict(
    classification='OFFLINE_ENGINEERING_DIAGNOSTIC_ONLY', source_sha=sha, source_tree=tree,
    authorization_mocked=False, source_identity_mocked=False,
    provider_transport='in-process sentinel replaces CLI constructor as in existing execution-binding tests',
    external_calls=0, scenarios=observations), indent=2))
