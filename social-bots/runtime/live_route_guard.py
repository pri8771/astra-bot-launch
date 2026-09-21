"""SB-V07-001 / SB-V04-002 — refuse a live model route on an unauthorized entrypoint.

Why this module exists
----------------------
``reasoning.resolve_provider`` picks a provider purely from ``SBOTS_REASONING``.
With ``SBOTS_REASONING=claude-cli`` it constructs ``ClaudeCodeReasoningProvider``,
which spawns the real Claude Code CLI. That path never consulted
``authorization.authorize``: the manifest requirement, the exact call budget and
the ``HARD_MAX_CALLS`` ceiling all sat on a *different* code path
(``divergence_prepare.execute_batch``) and were inert here.

So a single environment variable was enough to make a scheduled bounded worker
spawn a real model call with no manifest, no budget and no accounting — exactly
what LEAD-037/LEAD-038 say must not be possible. This module closes that gap for
every entrypoint that is not the authorized divergence batch.

What it does
------------
``check()`` inspects the configured reasoning mode. If the mode would resolve to
a genuinely live provider, it looks for an ``ExecutionGrant``. With no canonical
manifest — the current and expected state — it returns a refusal, and the caller
exits before any provider is constructed.

The result is also what makes an invocation receipt's ``live_model_call`` field
honest: it is derived from this check rather than being a hard-coded ``False``.

This is a guard, not an authorizer. It can only deny, or defer to
``authorization.authorize``, which is the single place a grant can come from.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict

from . import authorization

# Modes that resolve to a provider capable of a real, billable model call.
# 'model' is included because a host could register a live model callable via
# ``reasoning.register_model_callable``; a receipt-replay callable is not live,
# which is why ``replay_is_live`` lets a caller say so explicitly.
LIVE_MODES = ("claude-cli", "model")


@dataclass
class RouteDecision:
    """Whether this process may use a live model route, and why."""

    mode: str
    live_route_requested: bool
    permitted: bool
    reason: str
    grant_manifest_id: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def configured_mode() -> str:
    return os.environ.get("SBOTS_REASONING", "baseline").strip().lower()


def any_live_authorization(manifest_dir=None) -> tuple[bool, str]:
    """Is ANY live model call currently authorized at all? Returns ``(ok, reason)``.

    Deliberately weaker than ``check``: it does not know an artifact, lane or run
    scope, so it cannot say a *particular* batch is authorized. It answers the
    one question the spawn point itself can answer — "is there a valid, unexpired
    canonical manifest in force?" — so the real Claude CLI cannot be launched
    while the answer is no, whatever entrypoint reached it.

    The precise scope check stays in ``authorization.authorize``, which the
    divergence batch calls before this is ever reached. This is the backstop, not
    a replacement.
    """
    posture = authorization.posture_violations(injected_runner=False)
    if posture:
        return False, "; ".join(posture)
    manifests = authorization.find_manifests(manifest_dir)
    if not manifests:
        directory = manifest_dir or authorization.MANIFEST_DIR
        return False, (f"no canonical authorization manifest in {directory}; no live "
                       f"model call is authorized")
    reasons = []
    for path in manifests:
        try:
            manifest, _ = authorization.load_manifest(path)
        except authorization.AuthorizationDenied as exc:
            reasons.append(f"{path.name}: {exc}")
            continue
        errs = authorization.validate_manifest(manifest)
        if errs:
            reasons.append(f"{path.name}: " + "; ".join(errs))
            continue
        return True, f"manifest {manifest['manifest_id']} is in force"
    return False, "no valid manifest in force: " + " | ".join(reasons)


def check(*, artifact: str, lane: str, run_scope: str,
          manifest_dir=None, replay_is_live: bool = True) -> RouteDecision:
    """Decide whether a live model route is permitted for this process.

    Returns a decision; never raises. ``permitted`` is True only when the mode is
    not a live route at all, or when ``authorization.authorize`` granted one.
    """
    mode = configured_mode()
    live_requested = mode in LIVE_MODES
    if mode == "model" and not replay_is_live:
        # A registered receipt-replay callable goes through the adaptive seam but
        # calls nothing. Only a caller that knows it wired a replay may say so.
        live_requested = False

    if not live_requested:
        return RouteDecision(
            mode=mode, live_route_requested=False, permitted=True,
            reason=f"reasoning mode {mode!r} is not a live model route")

    try:
        grant = authorization.authorize(artifact=artifact, lane=lane,
                                        run_scope=run_scope,
                                        manifest_dir=manifest_dir)
    except authorization.AuthorizationDenied as exc:
        return RouteDecision(
            mode=mode, live_route_requested=True, permitted=False,
            reason=f"live reasoning mode {mode!r} requested but not authorized: {exc}")
    return RouteDecision(
        mode=mode, live_route_requested=True, permitted=True,
        reason=f"live mode {mode!r} authorized by manifest {grant.manifest_id}",
        grant_manifest_id=grant.manifest_id)
