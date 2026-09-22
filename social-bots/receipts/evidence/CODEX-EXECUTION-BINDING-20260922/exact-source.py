#!/usr/bin/env python3
"""Engineering-only exact-source proof for LEAD-064 execution binding.

No owner grant is activated. Inputs are existing engineering fixtures and the
provider is an in-process sentinel; no model, provider, network, account, public,
host or scheduler action occurs.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

REPO = Path("/Users/pchordia/Downloads/swarm_codex/review/bots-binding-source")
SOCIAL = REPO / "social-bots"
EXPECTED_SHA = "fec97738ec0e9407415f60228f7c3938613396c3"
EXPECTED_TREE = "43e80b92d8ae559db55a41ed33329695e6fd03fc"
sys.path.insert(0, str(SOCIAL))

from runtime import authorization, divergence_prepare as dp, model_dispatch, reasoning  # noqa: E402
from tests.test_v04_divergence_prepare import (  # noqa: E402
    OBJECTIVE,
    PERSONAS,
    build,
    default_snapshots,
)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def clean_identity() -> tuple[str, str]:
    dirty = git("status", "--porcelain")
    if dirty:
        raise AssertionError(f"source not clean: {dirty}")
    actual = (git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}"))
    if actual != (EXPECTED_SHA, EXPECTED_TREE):
        raise AssertionError(f"wrong exact source: {actual}")
    if authorization.source_identity() != actual:
        raise AssertionError("authorization.source_identity disagrees with Git")
    return actual


def iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def manifest(matrix, binding, *, include_binding: bool = True) -> dict:
    now = datetime.now(timezone.utc)
    value = {
        "schema_version": "v1",
        "manifest_id": "AUTH-ENGINEERING-EXACT-SOURCE",
        "created_by": "offline-engineering-proof",
        "created_at": iso(now - timedelta(minutes=1)),
        "owner_authorization_ref": "engineering fixture only; no owner grant activation",
        "artifact_scope": ["SB-V04-002", "SB-V04-004"],
        "run_scope": matrix.run_scope,
        "lane": matrix.lane,
        "provider_mode": "claude-cli",
        "max_calls": 5,
        "expires_at": iso(now + timedelta(minutes=30)),
        "retry_allowed": False,
        "public_effect_allowed": False,
        "spend_authorized": False,
        "api_key_allowed": False,
        "injected_runner_allowed": False,
    }
    if include_binding:
        value.update(
            source_sha=EXPECTED_SHA,
            source_tree=EXPECTED_TREE,
            execution_matrix_sha256=binding.digest,
        )
    return value


def write_manifest(directory: Path, value: dict) -> None:
    directory.mkdir(parents=True)
    (directory / "engineering-only.json").write_text(
        json.dumps(value, sort_keys=True), encoding="utf-8"
    )


class OfflineProvider:
    provider_id = "offline-exact-source-sentinel"
    reason = None
    constructed = 0
    calls = 0

    def __init__(self):
        type(self).constructed += 1

    def propose(self, ctx):
        def sentinel(inner_ctx):
            type(self).calls += 1
            return reasoning.ReasoningProposal(
                alternatives=[reasoning.no_action("offline exact-source sentinel")],
                recommended_action="NO_ACTION",
                uncertainties=["engineering fixture"],
                provider_id=self.provider_id,
                adaptive=True,
            )

        return model_dispatch.dispatch(
            sentinel, ctx, provider_id=self.provider_id, live=True
        )


def exact_positive(matrix, binding) -> dict:
    with tempfile.TemporaryDirectory(prefix="bots-binding-positive-") as raw:
        root = Path(raw)
        manifests, home = root / "authorizations", root / "runtime-home"
        write_manifest(manifests, manifest(matrix, binding))
        OfflineProvider.constructed = OfflineProvider.calls = 0
        model_dispatch.clear()
        with mock.patch.object(
            dp.reasoning_cli, "ClaudeCodeReasoningProvider", OfflineProvider
        ):
            result = dp.execute_batch(
                matrix,
                lane=matrix.lane,
                personas=PERSONAS,
                snapshots=default_snapshots(),
                manifest_dir=manifests,
                home=home,
            )
        expected = (EXPECTED_SHA, EXPECTED_TREE, binding.digest)
        slots = authorization.CallBudget(matrix.run_scope, 5, home=home).slots()
        assert (OfflineProvider.constructed, OfflineProvider.calls) == (1, 5)
        assert len(result["results"]) == len(slots) == 5
        assert all(item["outcome"] == "proposal_received" for item in result["results"])
        assert all(
            (item["source_sha"], item["source_tree"], item["execution_matrix_sha256"])
            == expected
            for item in result["results"]
        )
        assert all(
            (slot["source_sha"], slot["source_tree"], slot["execution_matrix_sha256"])
            == expected
            for slot in slots
        )
        assert [slot["slot"] for slot in slots] == [1, 2, 3, 4, 5]
        report = {
            "results": len(result["results"]),
            "slots": len(slots),
            "outcomes": [slot["outcome"] for slot in slots],
            "source_sha": EXPECTED_SHA,
            "source_tree": EXPECTED_TREE,
            "execution_matrix_sha256": binding.digest,
            "provider": "offline sentinel",
        }
    assert not root.exists()
    return report


def coherent_swap_denied(matrix, binding) -> dict:
    with tempfile.TemporaryDirectory(prefix="bots-binding-swap-") as raw:
        root = Path(raw)
        manifests, home = root / "authorizations", root / "runtime-home"
        write_manifest(manifests, manifest(matrix, binding))
        changed = build(objective=OBJECTIVE + " coherent but unreviewed change")
        constructed_before = OfflineProvider.constructed
        with mock.patch.object(
            dp.reasoning_cli, "ClaudeCodeReasoningProvider", OfflineProvider
        ):
            try:
                dp.execute_batch(
                    changed,
                    lane=changed.lane,
                    personas=PERSONAS,
                    snapshots=default_snapshots(),
                    manifest_dir=manifests,
                    home=home,
                )
            except authorization.AuthorizationDenied as exc:
                reason = str(exc)
            else:
                raise AssertionError("coherent matrix swap was authorized")
        assert "execution_matrix_binding_mismatch" in reason
        assert OfflineProvider.constructed == constructed_before
        assert not (home / "call-budget").exists()
        report = {"denied": True, "reason": reason, "slots": 0, "provider_constructed": 0}
    assert not root.exists()
    return report


def omitted_binding_direct_denied(matrix, binding) -> dict:
    with tempfile.TemporaryDirectory(prefix="bots-binding-omitted-") as raw:
        root = Path(raw)
        manifests, home = root / "authorizations", root / "runtime-home"
        write_manifest(manifests, manifest(matrix, binding, include_binding=False))
        scope = model_dispatch.DispatchScope(
            "SB-V04-002",
            matrix.lane,
            matrix.run_scope,
            manifest_dir=str(manifests),
            home=str(home),
            execution_binding=binding,
        )
        calls = []
        ctx = dp._context_for(
            PERSONAS["baseline"],
            default_snapshots()["E1"],
            objective=matrix.objective,
            pending_count=matrix.held_constant["pending_count"],
            is_duplicate=matrix.held_constant["is_duplicate"],
            prior_hypotheses=matrix.held_constant["prior_hypotheses"],
            draft={},
        )
        try:
            model_dispatch.dispatch(
                lambda value: calls.append(value),
                ctx,
                provider_id="offline-direct-sentinel",
                scope=scope,
            )
        except authorization.AuthorizationDenied as exc:
            reason = str(exc)
        else:
            raise AssertionError("manifest with omitted binding dispatched")
        assert "required binding field" in reason
        assert calls == []
        assert not (home / "call-budget").exists()
        report = {"denied": True, "reason": reason, "slots": 0, "callable_calls": 0}
    assert not root.exists()
    return report


def main() -> None:
    prior_key = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        source = clean_identity()
        matrix = build()
        binding = dp.execution_binding(matrix)
        output = {
            "evidence_kind": "engineering-only-offline",
            "owner_grant_activated": False,
            "product_acceptance_evidence": False,
            "fixture_note": "existing generic engineering PERSONAS/default snapshots; not live product proof",
            "source_identity": {"sha": source[0], "tree": source[1]},
            "positive": exact_positive(matrix, binding),
            "coherent_matrix_swap": coherent_swap_denied(matrix, binding),
            "omitted_binding_direct_dispatch": omitted_binding_direct_denied(matrix, binding),
        }
        clean_identity()
        print(json.dumps(output, indent=2, sort_keys=True))
    finally:
        model_dispatch.clear()
        if prior_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = prior_key


if __name__ == "__main__":
    main()
