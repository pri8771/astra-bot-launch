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
4. The only invocations exempt from live accounting are exact instances of the
   policy-owned non-live types: ``reasoning_receipt.ReceiptReplay`` (replays
   real receipts, calls nothing) and ``reasoning.EngineeringStub`` (declared
   engineering-only stub), plus the CLI provider's own injected-runner seam.
   Subclasses, attributes, ``adaptive=False`` labels or any other marker do NOT
   exempt. Engineering seams (stubs, injected runners) are refused under a
   production scope (``allow_engineering_stubs=False``), so a mis-wired seam
   cannot masquerade as adaptive autonomy in a scheduled run.
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
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable

from . import authorization
from .authorization import AuthorizationDenied, CallBudgetExhausted

LIVE_MODEL = "LIVE_MODEL"
RECEIPT_REPLAY = "RECEIPT_REPLAY"
ENGINEERING_STUB = "ENGINEERING_STUB"
NOT_LIVE = "NOT_LIVE"                      # the CLI provider's injected-runner seam

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

    def as_dict(self) -> dict:
        return asdict(self)


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
              allow_engineering_stubs: bool = False) -> DispatchScope:
    """Set the process-wide dispatch scope (production entrypoints call this once)."""
    scope = DispatchScope(artifact=str(artifact), lane=str(lane), run_scope=str(run_scope),
                          manifest_dir=str(manifest_dir) if manifest_dir is not None else None,
                          home=str(home) if home is not None else None,
                          allow_engineering_stubs=bool(allow_engineering_stubs))
    set_scope(scope)
    return scope


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
    from . import reasoning, reasoning_receipt          # lazy: avoids import cycles
    t = type(fn)
    if t is reasoning_receipt.ReceiptReplay:
        return RECEIPT_REPLAY
    if t is reasoning.EngineeringStub:
        return ENGINEERING_STUB
    return LIVE_MODEL


# --------------------------------------------------------------------------- #
# Reservation (used by the batch executor) and dispatch (used by every provider)
# --------------------------------------------------------------------------- #
def _reserve(scope: DispatchScope, *, context_digest: str | None, provider_id: str):
    posture = authorization.posture_violations(injected_runner=False)
    if posture:
        raise DispatchRefused("; ".join(posture))
    grant = authorization.authorize(artifact=scope.artifact, lane=scope.lane,
                                    run_scope=scope.run_scope, manifest_dir=scope.manifest_dir)
    budget = authorization.CallBudget(scope.run_scope, grant.max_calls, home=scope.home)
    slot = budget.reserve(manifest_id=grant.manifest_id, manifest_digest=grant.manifest_digest,
                          lane=grant.lane, artifact=grant.artifact,
                          context_digest=context_digest)
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
    st.token = (grant, budget, slot)
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
        if scope is not None and not scope.allow_engineering_stubs:
            st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=False,
                                     refusal=f"{_SEAM_LABEL[cls]} refused under a production "
                                             f"dispatch scope")
            raise DispatchRefused(st.last.refusal)
        st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=True,
                                 outcome="engineering_seam")
        return fn(ctx)

    # ---- LIVE_MODEL ------------------------------------------------------
    adopted = st.token
    if adopted is not None:
        st.token = None                               # single use
        grant, budget, slot = adopted
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
            grant, budget, slot = _reserve(scope, context_digest=context_digest,
                                           provider_id=provider_id)
        except AuthorizationDenied as exc:            # includes CallBudgetExhausted
            st.last = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=False,
                                     run_scope=scope.run_scope, refusal=str(exc))
            raise
        record_here = True

    st.active += 1
    rec = DispatchRecord(dispatch_class=cls, provider_id=provider_id, invoked=True,
                         slot=slot.slot, run_scope=slot.run_scope,
                         manifest_id=slot.manifest_id)
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
    posture = authorization.posture_violations(injected_runner=False)
    if posture:
        return False, "; ".join(posture)
    try:
        grant = authorization.authorize(artifact=scope.artifact, lane=scope.lane,
                                        run_scope=scope.run_scope, manifest_dir=scope.manifest_dir)
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
                                        run_scope=scope.run_scope, manifest_dir=scope.manifest_dir)
    except AuthorizationDenied:
        return {"run_scope": scope.run_scope, "authorized": False}
    return authorization.CallBudget(scope.run_scope, grant.max_calls, home=d).audit()
