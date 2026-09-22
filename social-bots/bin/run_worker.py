#!/usr/bin/env python3
"""Run ONE bounded work unit. This is the payload a host scheduler invokes.

Usage:
    python3 bin/run_worker.py <bot> [persona_id]

Reasoning posture (SB-V04-001):
    This is the PRODUCTION V0.4 entrypoint, so it runs the adaptive-required
    posture by DEFAULT: if no adaptive reasoning provider is available the cycle
    fails closed to BLOCKED_REASONING_UNAVAILABLE and consumes no evidence (the
    signal stays pending). It never silently falls back to a deterministic
    provider. For tests/diagnostics/comparison ONLY, set
    ``SBOTS_WORKER_ALLOW_DETERMINISTIC=1`` to allow the configured non-adaptive
    provider; this is explicitly not a production V0.4 posture.

Live-route posture (SB-R07-041):
    Before any lease or cycle work, a live reasoning mode (``claude-cli`` /
    ``model``) is refused unless a canonical authorization manifest grants it.
    The Claude CLI spawn point remains the backstop for alternate callers; this
    entrypoint check is defense-in-depth for the production launcher itself.

Exit codes:
    0  unit completed (any decision, including NO_ACTION or a fail-closed block)
    3  no-overlap: another live worker holds the lease (expected, benign)
    6  live model route requested but not authorized (refused before work)
    1  unexpected failure (a failure receipt was written)
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import worker, leasing, live_route_guard, model_dispatch  # noqa: E402

EXIT_LIVE_ROUTE_REFUSED = 6


def _allow_deterministic() -> bool:
    return os.environ.get("SBOTS_WORKER_ALLOW_DETERMINISTIC", "0").strip().lower() \
        in {"1", "true", "yes", "on"}


def main() -> int:
    """Process entry. The SB-R07-041 dispatch scope ``_main`` installs is undone on
    every exit path so an in-process caller (tests) never inherits it."""
    prior_scope = model_dispatch.current_scope()
    try:
        return _main()
    finally:
        model_dispatch.set_scope(prior_scope)


def _main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    bot = sys.argv[1]
    persona = sys.argv[2] if len(sys.argv) > 2 else bot
    lane = os.environ.get("SBOTS_LANE", "windows-core")
    artifact = os.environ.get("SBOTS_ARTIFACT", "SB-RUNTIME-WORKER")
    manifest_dir = os.environ.get("SBOTS_MANIFEST_DIR") or None
    # Refuse a live model route before acquiring a lease or constructing a provider.
    route = live_route_guard.check(
        artifact=artifact,
        lane=lane,
        run_scope=f"run-worker:{bot}",
        manifest_dir=manifest_dir,
    )
    if not route.permitted:
        print(f"LIVE ROUTE REFUSED: {route.reason}", file=sys.stderr)
        return EXIT_LIVE_ROUTE_REFUSED
    # SB-R07-041 / C04: one dispatch scope for every live-capable provider this
    # process may construct; the shared gate re-authorizes and reserves a durable
    # slot before each invocation and refuses engineering seams under it.
    model_dispatch.configure(artifact, lane, f"run-worker:{bot}",
                             manifest_dir=manifest_dir,
                             home=os.environ.get("SBOTS_HOME") or None)
    # Production V0.4 default: require adaptive reasoning (fail closed). A diagnostic
    # override (None -> env-driven posture) is allowed only when explicitly opted in.
    require_adaptive = None if _allow_deterministic() else True
    # Lease keyed by RUNTIME (bot), not (bot, persona): personas on one runtime
    # share bot_state.json and must not mutate it concurrently. See
    # worker.runtime_task_id for the rationale.
    task_id = worker.runtime_task_id(bot)
    try:
        res = worker.run_one_unit(task_id, bot, persona, require_adaptive=require_adaptive)
    except leasing.LeaseHeld as held:
        print(f"NO-OVERLAP: {held}")
        return 3
    print("OK:", {k: res.get(k) for k in ("worker_id", "chosen_action", "outcome",
                                           "verified", "lease_released", "finish_receipt")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
