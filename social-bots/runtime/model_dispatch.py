"""SB-R07-041 / C04 — the ONE pre-dispatch gate for every live-capable reasoning route.

LEAD-047 reproduced four P0 defects on the previous source: a registered model
callable executed with no grant (direct-library bypass); a caller-supplied
``adaptive``/fixture label exempted an object from authorization; accounting ran
after dispatch and was private to one wrapper, so concurrent, reentrant and
multi-wrapper calls overran a one-slot budget. This module closes all of them at
the deepest boundary — the point where a callable or subprocess is invoked — so
no entrypoint, wrapper, env variable or label can route around it.

Rules
-----
1. A live invocation needs a **dispatch scope** (artifact, lane, run_scope,
   manifest dir, runtime home). Production entrypoints configure it once
   (``bin/worker_once.py``, ``bin/run_worker.py``, ``divergence_prepare``).
   With no scope configured, live dispatch is refused: direct-library callers
   cannot dispatch by accident.
2. Every live dispatch re-runs ``authorization.authorize`` (canonical scoped
   manifest, posture, expiry checked *at dispatch*) and then reserves a durable
   ``authorization.CallBudget`` slot (``O_CREAT|O_EXCL`` file) **before** the
   callable runs. Concurrency, reentry, other wrappers, other processes and a
   restart all share the same on-disk slots. A raise or a crash after the
   reservation leaves the slot consumed (``reserved_not_recorded`` = uncertain).
   A grant object is never accepted from a caller: a hand-built
   ``ExecutionGrant`` buys nothing here.
3. Reentrancy: a callable that re-enters a live dispatch on the same thread is
   refused. A second thread must win its own slot.
4. The only invocation exempt from live accounting is an exact
   ``reasoning_receipt.ReceiptReplay`` (replays validated real receipts, calls
   nothing). Engineering seams — exact ``reasoning.EngineeringStub`` and the CLI
   provider's injected-runner closure — run ONLY under the policy-owned
   ENGINEERING scope installed by ``configure_engineering()`` /
   ``engineering_scope()`` (LEAD-051): with no scope they are refused like any
   live callable (no-scope is not a capability), and under a production scope
   they are refused outright. Subclasses, attributes, ``adaptive=False`` labels
   or any other marker do NOT exempt anything.
5. The batch executor may reserve first and let the provider adopt that single
   reservation (``reserved()``), so a prepared five-call batch keeps exact
   per-case accounting without double consumption.

Residual, stated plainly: a declaration that lies in source (an
``EngineeringStub`` whose body performs a real call) is a reviewable code change,
not a runtime bypass, and is outside what a runtime gate can detect.

Every dispatch records a ``DispatchRecord`` (class: LIVE_MODEL / RECEIPT_REPLAY /
ENGINEERING_STUB / NOT_LIVE) that the decision record cites, so LIVE_MODEL and
OFFLINE evidence stay distinguishable. Nothing here performs a model call itself.
"""
from __future__ import annotations

import threading
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from . import authorization
from .authorization import AuthorizationDenied
from .authorization import (
    CallBudgetExhausted as CallBudgetExhausted,  # noqa: PLC0414 - public re-export
)

LIVE_MODEL = "LIVE_MODEL"
RECEIPT_REPLAY = "RECEIPT_REPLAY"
ENGINEERING_STUB = "ENGINEERING_STUB"
NOT_LIVE = "NOT_LIVE"                      # the CLI provider's injected-runner seam

# The ONLY artifact id under which engineering seams may run. Production
# entrypoints never configure it; a decision record citing it is never LIVE.
ENGINEERING_ARTIFACT = "ENGINEERING"
ENGINEERING_LANE = "engineering"

_SEAM_LABEL = {ENGINEERING_STUB: "engineering stub", NOT_LIVE: "injected runner"}


class DispatchRefused(AuthorizationDenied):
    """A live-capable invocation was refused before anything ran."""


@dataclass(frozen=True)
class DispatchScope:
    artifact: str
    lane: str
    run_scope: str
    manifest_dir: str | None = None
    home: str | None = None
    allow_engineering_stubs: bool = False
    execution_binding: authorization.ExecutionBinding | None = None

    def as_dict(self) -> dict:
        return asdict(self)

    @property
    def kind(self) -> str:
        return "engineering" if self.allow_engineering_stubs else "production"


@dataclass
class DispatchRecord:
    dispatch_class: str
    provider_id: str
    invoked: bool
    slot: int | None = None
    run_scope: str | None = None
    manifest_id: str | None = None
    outcome: str | None = None
    refusal: str | None = None
    scope_kind: str | None = None             # "production" | "engineering" | None
    source_sha: str | None = None
    source_tree: str | None = None
    execution_matrix_sha256: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


_lock = threading.Lock()
_SCOPE: DispatchScope | None = None
_tls = threading.local()


def _state():
    if not hasattr(_tls, "active"):
        _tls.active = 0
        _tls.token = None
        _tls.last = None
    return _tls


def configure(artifact: str, lane: str, run_scope: str, *, manifest_dir=None, home=None,
              allow_engineering_stubs: bool = False,
              execution_binding: authorization.ExecutionBinding | None = None) -> DispatchScope:
    """Set the process-wide PRODUCTION dispatch scope (entrypoints call this once).

    Engineering seams cannot be enabled here under any other artifact id: the
    only scope that runs them is the policy-owned one from
    ``configure_engineering()`` (LEAD-051), so a flag on a production scope
    cannot quietly turn stubs on.
    """
    if allow_engineering_stubs and str(artifact) != ENGINEERING_ARTIFACT:
        raise ValueError("engineering seams may only be enabled in the policy-owned "
                         "ENGINEERING scope (use model_dispatch.configure_engineering)")
    scope = DispatchScope(artifact=str(artifact), lane=str(lane), run_scope=str(run_scope),
                          manifest_dir=str(manifest_dir) if manifest_dir is not None else None,
                          home=str(home) if home is not None else None,
                          allow_engineering_stubs=bool(allow_engineering_stubs),
                          execution_binding=execution_binding)
    set_scope(scope)
    return scope


def configure_engineering(run_scope: str = "engineering-seams", *,
                          home=None) -> DispatchScope:
    """Install the policy-owned ENGINEERING scope: the only scope under which an
    ``EngineeringStub`` or an injected CLI runner may run. Unit tests and
    offline dry runs call this explicitly; production entrypoints never do.
    Live callables are still refused under it (no manifest is consulted)."""
    return configure(ENGINEERING_ARTIFACT, ENGINEERING_LANE, run_scope, home=home,
                     allow_engineering_stubs=True)


@contextmanager
def engineering_scope(run_scope: str = "engineering-seams", *, home=None):
    """``with engineering_scope():`` — ENGINEERING scope for the block, prior scope
    restored afterwards (never leaks into a later production configuration)."""
    prior = current_scope()
    configure_engineering(run_scope, home=home)
    try:
        yield current_scope()
    finally:
        set_scope(prior)


def set_scope(scope: DispatchScope | None) -> None:
    """Install (or, with ``None``, remove) the process-wide dispatch scope."""
    global _SCOPE
    if scope is not None and not isinstance(scope, DispatchScope):
        raise TypeError("set_scope expects a DispatchScope or None")
    with _lock:
        _SCOPE = scope


def clear() -> None:
    """Remove the scope and reset this thread's token/reentry state (tests)."""
    set_scope(None)
    st = _state()
    st.token = None
    st.active = 0
    st.last = None


def clear_last() -> None:
    """Forget this thread's last dispatch record (call before a new provider call)."""
    _state().last = None


def current_scope() -> DispatchScope | None:
    return _SCOPE


def last_record() -> DispatchRecord | None:
    """The most recent dispatch decision on this thread (for decision records)."""
    return _state().last


# --------------------------------------------------------------------------- #
# Classification — by EXACT policy-owned type, never by label
# --------------------------------------------------------------------------- #
def classify(fn: Any) -> str:
    """LIVE_MODEL unless ``fn`` is exactly a policy-owned non-live type."""
    from . import reasoning, reasoning_receipt  # lazy: avoids import cycles
    t = type(fn)
    if t is reasoning_receipt.ReceiptReplay:
        return RECEIPT_REPLAY
    if t is reasoning.EngineeringStub:
        return ENGINEERING_STUB
    return LIVE_MODEL


# --------------------------------------------------------------------------- #
# Reservation (used by the batch executor) and dispatch (used by every provider)
# --------------------------------------------------------------------------- #
def validate_bound_context(scope: DispatchScope, ctx: Any) -> str | None:
    if scope.artifact not in authorization.BOUND_ARTIFACTS:
        return
    if scope.execution_binding is None:
        raise DispatchRefused("execution_binding_required")
    from . import reasoning_cli, reasoning_receipt
    actual = (reasoning_receipt.context_digest(reasoning_receipt.bounded_context(ctx)),
              authorization.sha256_json(reasoning_cli.prompt_context(ctx)),
              authorization.sha256_bytes(reasoning_cli.build_prompt(ctx).encode("utf-8")))
    try:
        cases = scope.execution_binding.closure()["cases"]
        permitted = {(c["context_sha256"], c["prompt_context_sha256"], c["prompt_sha256"])
                     for c in cases}
    except (KeyError, TypeError, ValueError) as exc:
        raise DispatchRefused("execution_binding_invalid") from exc
    if actual not in permitted:
        raise DispatchRefused("dispatch_context_not_in_reviewed_matrix")
    return actual[0]


def _validate_local_provider(scope: DispatchScope | None, provider_id: str,
                             invocation=None) -> None:
    """A LOCAL grant must never authorize a hosted provider through the shared gate."""
    if scope is None or scope.execution_binding is None:
        return
    config = scope.execution_binding.closure().get("provider_config", {})
    if config.get("provider_mode") == "ollama-local":
        from . import reasoning_local
        if (config != reasoning_local.provider_config()
                or provider_id != reasoning_local.PROVIDER_ID
                or (invocation is not None and type(invocation) is not reasoning_local._LocalInvocation)):
            raise DispatchRefused("local_provider_binding_mismatch")


def _reserve(scope: DispatchScope, *, context_digest: str | None, provider_id: str):
    _validate_local_provider(scope, provider_id)
    posture = authorization.posture_violations(injected_runner=False)
    if posture:
        raise DispatchRefused("; ".join(posture))
    grant = authorization.authorize(artifact=scope.artifact, lane=scope.lane,
                                    run_scope=scope.run_scope, manifest_dir=scope.manifest_dir,
                                    execution_binding=scope.execution_binding)
    expected_contexts = None
    if scope.artifact in authorization.BOUND_ARTIFACTS:
        expected_contexts = tuple(c["context_sha256"]
                                  for c in scope.execution_binding.closure()["cases"])
    budget = authorization.CallBudget(scope.run_scope, grant.max_calls, home=scope.home)
    slot = budget.reserve(manifest_id=grant.manifest_id, manifest_digest=grant.manifest_digest,
                          lane=grant.lane, artifact=grant.artifact,
                          context_digest=context_digest, source_sha=grant.source_sha,
                          source_tree=grant.source_tree,
                          execution_matrix_sha256=grant.execution_matrix_sha256,
                          expected_contexts=expected_contexts)
    return grant, budget, slot


@contextmanager
def reserved(scope: DispatchScope, *, context_digest: str | None = None,
             provider_id: str = "batch"):
    """Reserve one live slot now; the next live dispatch on this thread adopts it.

    Yields ``(grant, budget, slot)``. The caller records the slot outcome itself
    (write-once). If no dispatch adopts the token inside the block, the token is
    dropped on exit so it can never be consumed by an unrelated later call.
    """
    st = _state()
    if st.active:
        raise DispatchRefused("cannot reserve inside an active live dispatch (reentrant)")
    grant, budget, slot = _reserve(scope, context_digest=context_digest, provider_id=provider_id)
    st.token = (grant, budget, slot, scope)
    try:
        yield grant, budget, slot
    finally:
        st.token = None


def dispatch(fn: Callable[[Any], Any], ctx: Any, *, provider_id: str, live: bool | None = None,
             scope: DispatchScope | None = None, context_digest: str | None = None) -> Any:
    """Invoke ``fn(ctx)`` through the gate. Raises ``DispatchRefused`` /
    ``CallBudgetExhausted`` BEFORE invoking when a live call is not authorized.

    ``live`` defaults to the type classification of ``fn``; a caller may only
    tighten it (``live=True`` for an injected real runner path), never loosen it.
    """
    st = _state()
    cls = classify(fn)
    if live is True and cls != LIVE_MODEL:
        cls = LIVE_MODEL                              # tightening is allowed
    if live is False and cls == LIVE_MODEL:
        # A caller-declared "not live" is exactly the label bypass LEAD-047 found.
        # It is honoured ONLY for the CLI provider's own injected-runner closure
        # (marked by the provider, never by the runner) and only as an
        # engineering seam: under a production scope it is refused below.
        cls = NOT_LIVE if getattr(fn, "__sbots_injected_runner__", False) else LIVE_MODEL

    if cls == RECEIPT_REPLAY:
        st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=True,
                                 outcome="receipt_replay")
        return fn(ctx)

    scope = scope or _SCOPE
    if cls in (ENGINEERING_STUB, NOT_LIVE):
        # LEAD-051: a seam runs ONLY under the policy-owned ENGINEERING scope.
        # No scope is not a capability; a production scope refuses outright.
        if scope is None or not scope.allow_engineering_stubs:
            where = ("no engineering dispatch scope (seams run only under "
                     "model_dispatch.configure_engineering)" if scope is None
                     else "a production dispatch scope")
            st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=False,
                                     scope_kind=scope.kind if scope else None,
                                     refusal=f"{_SEAM_LABEL[cls]} refused: {where}")
            raise DispatchRefused(st.last.refusal)
        st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=True,
                                 scope_kind=scope.kind, outcome="engineering_seam")
        return fn(ctx)

    # ---- LIVE_MODEL ------------------------------------------------------
    if scope is not None and scope.allow_engineering_stubs:
        # The ENGINEERING scope never authorizes a live callable: it consults no
        # manifest and reserves nothing. Live routes need a production scope.
        st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=False,
                                 scope_kind=scope.kind,
                                 refusal="live callable refused under the ENGINEERING scope; "
                                         "a live model route needs a production scope with "
                                         "a canonical authorization manifest")
        raise DispatchRefused(st.last.refusal)
    _validate_local_provider(scope, provider_id, fn)
    adopted = st.token
    if adopted is not None:
        st.token = None                               # single use
        _grant, budget, slot, reserved_scope = adopted
        if reserved_scope.artifact in authorization.BOUND_ARTIFACTS:
            if scope != reserved_scope:
                raise DispatchRefused("reserved_execution_scope_mismatch")
            authorization.authorize(artifact=scope.artifact, lane=scope.lane,
                                    run_scope=scope.run_scope, manifest_dir=scope.manifest_dir,
                                    execution_binding=scope.execution_binding)
            actual_context = validate_bound_context(scope, ctx)
            if actual_context != slot.context_digest:
                raise DispatchRefused("reserved_execution_context_mismatch")
        elif scope is not None and scope.artifact in authorization.BOUND_ARTIFACTS:
            raise DispatchRefused("reserved_execution_scope_mismatch")
        record_here = False
    else:
        if st.active:
            st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=False,
                                     refusal="reentrant live dispatch refused")
            raise DispatchRefused(st.last.refusal)
        if scope is None:
            st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=False,
                                     refusal="no dispatch scope configured; a live model route "
                                             "may only run through a configured entrypoint "
                                             "with a canonical authorization manifest")
            raise DispatchRefused(st.last.refusal)
        try:
            actual_context = validate_bound_context(scope, ctx)
            if actual_context is not None:
                context_digest = actual_context
            _grant, budget, slot = _reserve(scope, context_digest=context_digest,
                                           provider_id=provider_id)
        except AuthorizationDenied as exc:            # includes CallBudgetExhausted
            st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=False,
                                     run_scope=scope.run_scope, refusal=str(exc))
            raise
        record_here = True

    st.active += 1
    rec = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=True,
                         slot=slot.slot, run_scope=slot.run_scope,
                         manifest_id=slot.manifest_id, scope_kind="production",
                         source_sha=slot.source_sha, source_tree=slot.source_tree,
                         execution_matrix_sha256=slot.execution_matrix_sha256)
    st.last = rec
    try:
        value = fn(ctx)
    except BaseException as exc:
        # The OUTER invocation is the thread's last dispatch: a refusal the
        # callable met inside (e.g. its own reentrant dispatch) must not mask
        # the fact that a slot was consumed for this call.
        rec.outcome = "provider_exception"
        rec.refusal = str(exc)[:300]
        st.last = rec
        if record_here:
            _record(budget, slot, "provider_exception", {"error_type": type(exc).__name__})
        raise
    finally:
        st.active -= 1
    outcome = "proposal_received" if value is not None else "provider_unavailable"
    rec.outcome = outcome
    st.last = rec
    if record_here:
        _record(budget, slot, outcome, {"provider_id": provider_id})
    return value


def _record(budget, slot, outcome: str, detail: dict) -> None:
    try:
        budget.record_outcome(slot, outcome, detail)
    except AuthorizationDenied:
        pass                                          # write-once already recorded


def availability(scope: DispatchScope | None = None) -> tuple[bool, str]:
    """Non-consuming view: would a live dispatch be permitted right now?"""
    scope = scope or _SCOPE
    if scope is None:
        return False, "no dispatch scope configured"
    if scope.allow_engineering_stubs:
        return False, "ENGINEERING scope never authorizes a live model call"
    posture = authorization.posture_violations(injected_runner=False)
    if posture:
        return False, "; ".join(posture)
    try:
        grant = authorization.authorize(artifact=scope.artifact, lane=scope.lane,
                                        run_scope=scope.run_scope, manifest_dir=scope.manifest_dir,
                                        execution_binding=scope.execution_binding)
    except AuthorizationDenied as exc:
        return False, str(exc)
    budget = authorization.CallBudget(scope.run_scope, grant.max_calls, home=scope.home)
    if budget.remaining() < 1:
        return False, f"call budget exhausted for run_scope {scope.run_scope!r}"
    return True, f"manifest {grant.manifest_id} in force; {budget.remaining()} call(s) remaining"


def budget_audit(scope: DispatchScope | None = None) -> dict | None:
    scope = scope or _SCOPE
    if scope is None:
        return None
    d = (Path(scope.home) if scope.home else None)
    try:
        grant = authorization.authorize(artifact=scope.artifact, lane=scope.lane,
                                        run_scope=scope.run_scope, manifest_dir=scope.manifest_dir,
                                        execution_binding=scope.execution_binding)
    except AuthorizationDenied:
        return {"run_scope": scope.run_scope, "authorized": False}
    return authorization.CallBudget(scope.run_scope, grant.max_calls, home=d).audit()
