"""LEAD-066: one pinned, loopback-only Ollama proposal route.

Real local inference uses the same live authorization and durable dispatch gate
as hosted inference. No test seam, download, daemon control, tools, redirect,
proxy, retry or remote fallback exists in this provider.
"""

from __future__ import annotations

import http.client
import json

from . import authorization, model_dispatch, reasoning_cli
from .reasoning import ReasoningContext, ReasoningProposal, validate_proposal

PROVIDER_ID = "ollama-local-v1"
MAX_RESPONSE_BYTES = 1_048_576


def provider_config() -> dict:
    """Every executable option participates in the reviewed matrix binding."""
    return {
        "provider_mode": "ollama-local",
        "provider_id": PROVIDER_ID,
        "auth_route": "owner-local",
        "endpoint": "http://127.0.0.1:11434",
        "model": "qwen3.5:9b",
        "model_digest": "6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7",
        "timeout_s": 120,
        "stream": False,
        "think": False,
        "format": "json",
        "keep_alive": 0,
        "options": {"temperature": 0, "seed": 0, "num_ctx": 8192, "num_predict": 1024},
        "max_response_bytes": MAX_RESPONSE_BYTES,
        "injected_runner": False,
        "retry_allowed": False,
        "remote_fallback": False,
    }


def _request(method: str, path: str, *, payload: dict | None = None) -> dict:
    # HTTPConnection neither consults environment proxies nor follows redirects.
    # The destination is literal and immutable; no caller URL reaches transport.
    conn = http.client.HTTPConnection("127.0.0.1", 11434, timeout=120)
    try:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        conn.request(
            method, path, body=body, headers={"Content-Type": "application/json"}
        )
        response = conn.getresponse()
        if response.status != 200:
            raise ValueError("local provider HTTP response refused")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("local provider response exceeds bound")
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise TypeError("local provider response must be an object")
        return value
    finally:
        conn.close()


class _LocalInvocation:
    """Policy-owned transport capability; contains no caller-supplied callable."""

    def __call__(self, actual_ctx):
        config = provider_config()
        # Metadata read is inside the authorized, consumed attempt too.
        # An unavailable/moved/cloud-backed tag fails before generation.
        inventory = _request("GET", "/api/tags")
        models = inventory.get("models")
        if not isinstance(models, list):
            raise TypeError("local model inventory unavailable")
        matches = [
            m
            for m in models
            if isinstance(m, dict) and m.get("name") == config["model"]
        ]
        if (
            len(matches) != 1
            or matches[0].get("digest") != config["model_digest"]
            or matches[0].get("remote_host")
            or matches[0].get("remote_model")
        ):
            raise ValueError("pinned local model is unavailable or changed")
        payload = {
            key: config[key]
            for key in (
                "model",
                "stream",
                "think",
                "format",
                "keep_alive",
                "options",
            )
        }
        payload["prompt"] = reasoning_cli.build_prompt(actual_ctx)
        result = _request("POST", "/api/generate", payload=payload)
        if (
            result.get("model") != config["model"]
            or result.get("done") is not True
            or result.get("done_reason") != "stop"
            or not isinstance(result.get("response"), str)
        ):
            raise ValueError("local provider returned incomplete or mismatched output")
        proposal = reasoning_cli.parse_envelope(result["response"], actual_ctx)
        if proposal is None or validate_proposal(proposal, actual_ctx):
            raise ValueError("local provider returned invalid proposal")
        proposal.provider_id = PROVIDER_ID
        return proposal


class OllamaLocalReasoningProvider:
    provider_id = PROVIDER_ID
    adaptive = True

    def __init__(self, config: dict):
        if config != provider_config():
            raise ValueError("local provider configuration differs from pinned route")
        # Keep an independent copy; caller mutation must not change execution.
        self._config = provider_config()
        self._last_reason: str | None = None

    @property
    def reason(self) -> str | None:
        return self._last_reason

    def propose(self, ctx: ReasoningContext) -> ReasoningProposal | None:
        scope = model_dispatch.current_scope()
        if (
            scope is None
            or scope.allow_engineering_stubs
            or scope.artifact not in authorization.BOUND_ARTIFACTS
            or scope.execution_binding is None
        ):
            self._last_reason = (
                "local inference requires a bound production dispatch scope"
            )
            return None
        closure = scope.execution_binding.closure()
        if closure.get("provider_config") != self._config:
            self._last_reason = "local provider does not match reviewed configuration"
            return None

        try:
            result = model_dispatch.dispatch(
                _LocalInvocation(), ctx, provider_id=self.provider_id, live=True
            )
        except (
            authorization.AuthorizationDenied,
            OSError,
            ValueError,
            TypeError,
            http.client.HTTPException,
        ) as exc:
            self._last_reason = f"local inference refused: {type(exc).__name__}"
            return None
        self._last_reason = None
        return result
