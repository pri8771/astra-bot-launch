from __future__ import annotations
from typing import Any, Callable
from types import SimpleNamespace
from pathlib import Path
import json

# Verbatim inspected class/method excerpts; external dependencies below are test doubles.
# Source: 72a55319cf41f9910c5d3b9623129de3ac0eea31, specialist_budget.py.
class BudgetError(Exception): pass
class ScopeMismatch(BudgetError): pass
class ProviderNotAuthorized(BudgetError): pass
class AuthorizationDenied(Exception): pass
class CallBudgetExhausted(Exception): pass
WorkerContract = Any
Deadline = Any
ReasoningContext = Any
ReasoningProposal = Any

def _require_valid(c): return c
class WorkerLedger:
    def __init__(self):
        self.calls_used = 0
        self.events = []
        self.authorization = {}
    @classmethod
    def for_contract(cls, c): return cls()
    def record_call(self, **kw):
        self.calls_used += 1
        self.events.append(kw)

def deny(**kwargs): raise AuthorizationDenied('no real grant in this isolated probe')
authorization = SimpleNamespace(authorize=deny, posture_violations=lambda **kwargs: [])
live_route_guard = SimpleNamespace(check=lambda **kw: SimpleNamespace(to_dict=lambda: {'permitted': False}))

def _ctx_scope(ctx: Any) -> tuple[str | None, str | None]:
    """Best-effort (bot, persona) of a reasoning context; None when unknown."""
    persona = getattr(ctx, "persona", None)
    if persona is None and isinstance(ctx, dict):
        persona = ctx.get("persona")
    bot = getattr(ctx, "bot", None)
    if bot is None and isinstance(ctx, dict):
        bot = ctx.get("bot")
    if isinstance(persona, dict):
        bot = bot or persona.get("bot") or persona.get("runtime")
        persona = persona.get("id") or persona.get("persona_id") or persona.get("persona")
    return (bot if isinstance(bot, str) else None, persona if isinstance(persona, str) else None)

class BudgetedProvider:
    def __init__(self, provider: Any, contract: WorkerContract, *, artifact: str, lane: str,
                 run_scope: str, manifest_dir=None, ledger: WorkerLedger | None = None,
                 deadline: Deadline | None = None):
        contract = _require_valid(contract)
        if provider is None or not callable(getattr(provider, "propose", None)):
            raise BudgetError("provider must expose propose(ctx)")
        self.contract = contract
        self.ledger = ledger or WorkerLedger.for_contract(contract)
        self.deadline = deadline
        self.provider_id = str(getattr(provider, "provider_id", type(provider).__name__))
        self.adaptive = bool(getattr(provider, "adaptive", False))
        self.grant: authorization.ExecutionGrant | None = None
        self.budget = int(contract.model_call_budget)

        # Recorded for receipts; NOT the gate (it keys on the env mode).
        route = live_route_guard.check(artifact=artifact, lane=lane, run_scope=run_scope,
                                       manifest_dir=manifest_dir)
        if self.adaptive:
            posture = authorization.posture_violations(injected_runner=False)
            if posture:
                raise ProviderNotAuthorized("; ".join(posture))
            try:
                self.grant = authorization.authorize(artifact=artifact, lane=lane,
                                                     run_scope=run_scope,
                                                     manifest_dir=manifest_dir)
            except AuthorizationDenied as exc:
                raise ProviderNotAuthorized(
                    f"adaptive provider {self.provider_id!r} refused for specialist "
                    f"{contract.worker_id}: {exc}") from exc
            self.budget = min(self.budget, int(self.grant.max_calls))
            self.ledger.authorization = {
                "required": True, "manifest_id": self.grant.manifest_id,
                "manifest_digest": self.grant.manifest_digest,
                "effective_budget": self.budget, "route": route.to_dict(),
            }
        else:
            self.ledger.authorization = {
                "required": False,
                "reason": f"provider {self.provider_id!r} is a non-adaptive fixture; "
                          f"no live call is possible",
                "effective_budget": self.budget, "route": route.to_dict(),
            }
        self._provider = provider

    # -- accounting ----------------------------------------------------------
    @property
    def calls_used(self) -> int:
        return self.ledger.calls_used

    @property
    def remaining(self) -> int:
        return max(0, self.budget - self.ledger.calls_used)

    # -- the one call path ---------------------------------------------------
    def propose(self, ctx: Any):
        bot, persona = _ctx_scope(ctx)
        if persona != self.contract.persona or (bot is not None and bot != self.contract.bot):
            raise ScopeMismatch(
                f"context scope {bot!r}/{persona!r} is not this specialist's "
                f"{self.contract.bot!r}/{self.contract.persona!r}")
        if self.deadline is not None:
            self.deadline.check()
        if self.ledger.calls_used >= self.budget:
            raise CallBudgetExhausted(
                f"specialist {self.contract.worker_id} model_call_budget {self.budget} "
                f"exhausted ({self.ledger.calls_used} used)")
        # Count BEFORE delegating: a call that raises still consumed a slot.
        try:
            out = self._provider.propose(ctx)
        except Exception as exc:                       # noqa: BLE001 - accounted, re-raised
            self.ledger.record_call(provider_id=self.provider_id, ok=False,
                                    error=f"{type(exc).__name__}: {exc}")
            raise
        self.ledger.record_call(provider_id=self.provider_id, ok=True)
        return out

    def available(self) -> bool:
        return self.remaining > 0 and bool(getattr(self._provider, "available", lambda: True)())

# Source: 74a515b7f3e30c94979e0f66dc6daae66daed571, reasoning.py.
class ModelReasoningProvider:
    provider_id = "model-adaptive-v0"
    adaptive = True

    def __init__(self, model_callable: Callable[[ReasoningContext], ReasoningProposal] | None = None):
        self._model = model_callable

    def available(self) -> bool:
        return self._model is not None

    def propose(self, ctx: ReasoningContext) -> ReasoningProposal | None:
        if self._model is None:
            return None  # fail closed: no reasoning route wired
        proposal = self._model(ctx)
        # A model that returns nothing usable is treated as unavailable, not faked.
        # Schema/authority validation of a non-empty proposal is the engine's
        # single gate (``decision`` calls ``validate_proposal`` before scoring),
        # so a truthful "failed schema validation" reason is surfaced rather than
        # being silently collapsed to "no proposal" here.
        if proposal is None or not getattr(proposal, "alternatives", None):
            return None
        return proposal

# Source: 72a55319cf41f9910c5d3b9623129de3ac0eea31, specialist_integrator.py.
class IntegrationError(Exception): pass
AdoptionReceipt = Any

def _kept_doc(adopted: AdoptionReceipt, schema: str) -> tuple[dict, dict]:
    for out in adopted.outputs:
        if out.get("schema") == schema:
            p = Path(out["kept_path"])
            try:
                doc = json.loads(p.read_bytes().decode("utf-8"))
            except (OSError, UnicodeDecodeError, ValueError) as exc:
                raise IntegrationError(f"kept output {p} unreadable: {exc}") from exc
            if not isinstance(doc, dict) or doc.get("schema") != schema:
                raise IntegrationError(f"kept output {p} is not a {schema}")
            return out, doc
    raise IntegrationError(f"adopted receipt has no {schema} output")
