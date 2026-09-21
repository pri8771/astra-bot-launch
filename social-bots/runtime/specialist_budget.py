"""SB-S23-007 — specialist worker budget and child-spawn guard.

Enforces a specialist's time / model-call / effect budgets and forbids recursive
worker spawning **by wrapper, not by adapter discipline**
(``V20_TO_V23_IMPLEMENTATION_SPEC.md`` §5 S23-007 row, §5.3).

Pieces
------
``WorkerLedger``
    Per-worker deterministic accounting: ``calls_used``, ``effect_attempts`` and
    an event list. Adapters copy these counts into ``WorkerResult`` so the
    integrator (SB-S23-006) sees the truth, not a self-report.
``Deadline``
    Monotonic wall-clock budget from ``contract.time_budget_s``; ``check()``
    raises ``DeadlineExceeded``. Injectable clock; tests never sleep.
``BudgetedProvider``
    The ONLY way a specialist may hold a reasoning provider. Construction:
      * a deterministic fixture provider (``adaptive`` false) needs no manifest
        and never counts as a live call;
      * an adaptive provider object is a live route **whatever**
        ``SBOTS_REASONING`` says, so it must pass ``authorization.authorize``
        (canonical manifest covering artifact/lane/run_scope, posture clean).
        Without a manifest construction raises ``ProviderNotAuthorized`` and the
        wrapped provider is never touched. This is deliberately stricter than
        ``live_route_guard.check``, whose decision keys on the env mode: a
        directly-injected live provider must not slip past an env that says
        ``baseline`` (the SB-R07-041 bypass class).
    ``propose()`` refuses a context for another persona, enforces the deadline,
    counts the call BEFORE delegating (a raise still counts) and raises
    ``authorization.CallBudgetExhausted`` at the budget. For an adaptive provider
    the effective budget is ``min(contract.model_call_budget, grant.max_calls)``.
``SpawnGuard``
    ``assert_no_child`` / ``assert_tool_allowed`` / ``depth_of`` / ``assert_depth``:
    a specialist can never request ``spawn_specialist`` (or any tool outside its
    allowlist), and a contract whose ``parent_run_id`` is itself a worker id
    (depth > 1) is refused. Defense in depth over ``validate_contract``.
``EffectGuard``
    ``attempt()`` is the only way a specialist could "try" an external effect. It
    always denies (``external_effect_budget`` is fixed at 0 by type) and records
    the attempt in the ledger so ``WorkerResult.effect_attempts`` is truthful and
    ``validate_result`` rejects the result.

No subprocess, no network, no ``reasoning_cli`` import: a provider is only ever
called through ``propose``; this module cannot itself spawn anything.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable

from . import authorization, live_route_guard
from .authorization import AuthorizationDenied, CallBudgetExhausted
from .jsonstore import now_iso
from .specialist_contract import WorkerContract, validate_contract

SPAWN_TOOLS: frozenset[str] = frozenset({"spawn_specialist", "spawn_worker", "create_worker",
                                         "delegate_specialist"})
_WORKER_ID_RE = re.compile(r"^w-[0-9a-f]{12}$")


class BudgetError(Exception):
    """Base for guard refusals."""


class DeadlineExceeded(BudgetError):
    pass


class ProviderNotAuthorized(BudgetError):
    """An adaptive provider was offered without a valid canonical grant."""


class ChildSpawnDenied(BudgetError):
    pass


class ToolDenied(BudgetError):
    pass


class EffectDenied(BudgetError):
    pass


class ScopeMismatch(BudgetError):
    """A reasoning context for a different persona/bot than the contract."""


def _require_valid(contract: Any) -> WorkerContract:
    errs = validate_contract(contract)
    if errs:
        raise BudgetError("invalid contract: " + "; ".join(errs))
    return contract


# --------------------------------------------------------------------------- #
# Ledger
# --------------------------------------------------------------------------- #
@dataclass
class WorkerLedger:
    worker_id: str
    calls_used: int = 0
    effect_attempts: int = 0
    events: list = field(default_factory=list)
    authorization: dict = field(default_factory=dict)

    @classmethod
    def for_contract(cls, contract: WorkerContract) -> "WorkerLedger":
        return cls(worker_id=_require_valid(contract).worker_id)

    def record_call(self, *, provider_id: str, ok: bool, error: str | None = None) -> None:
        self.calls_used += 1
        self.events.append({"kind": "model_call", "provider_id": provider_id, "ok": ok,
                            "error": error, "n": self.calls_used, "at": now_iso()})

    def record_effect_attempt(self, effect_kind: str) -> None:
        self.effect_attempts += 1
        self.events.append({"kind": "effect_attempt", "effect": effect_kind,
                            "denied": True, "n": self.effect_attempts, "at": now_iso()})

    def as_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Deadline
# --------------------------------------------------------------------------- #
class Deadline:
    def __init__(self, contract: WorkerContract | None = None, *, budget_s: float | None = None,
                 clock: Callable[[], float] = time.monotonic):
        if budget_s is None:
            if contract is None:
                raise BudgetError("Deadline needs a contract or an explicit budget_s")
            budget_s = float(_require_valid(contract).time_budget_s)
        self.budget_s = float(budget_s)
        self._clock = clock
        self.started = clock()

    def elapsed_s(self) -> float:
        return max(0.0, self._clock() - self.started)

    def remaining_s(self) -> float:
        return max(0.0, self.budget_s - self.elapsed_s())

    def expired(self) -> bool:
        return self.budget_s <= 0 or self.elapsed_s() >= self.budget_s

    def check(self) -> None:
        if self.expired():
            raise DeadlineExceeded(
                f"time budget {self.budget_s:.3f}s exceeded (elapsed {self.elapsed_s():.3f}s)")


# --------------------------------------------------------------------------- #
# Spawn / tool guard
# --------------------------------------------------------------------------- #
class SpawnGuard:
    @staticmethod
    def depth_of(contract: WorkerContract) -> int:
        """1 for a specialist spawned by a persistent bot run; 2 if its parent is
        itself a specialist worker id (which is never allowed)."""
        parent = getattr(contract, "parent_run_id", "") or ""
        return 2 if _WORKER_ID_RE.match(parent) else 1

    @staticmethod
    def assert_depth(contract: WorkerContract) -> None:
        if SpawnGuard.depth_of(contract) != 1:
            raise ChildSpawnDenied(
                f"contract {contract.worker_id} has a specialist as parent "
                f"({contract.parent_run_id}); specialists may not spawn specialists")

    @staticmethod
    def assert_no_child(contract: WorkerContract, requested_tool: str) -> None:
        if requested_tool in SPAWN_TOOLS:
            raise ChildSpawnDenied(
                f"specialist {contract.worker_id} requested {requested_tool!r}; "
                f"a specialist may not create child workers")

    @staticmethod
    def assert_tool_allowed(contract: WorkerContract, requested_tool: str) -> None:
        SpawnGuard.assert_no_child(contract, requested_tool)
        if requested_tool in contract.denied_tools or requested_tool not in contract.allowed_tools:
            raise ToolDenied(
                f"tool {requested_tool!r} is not in the {contract.role!r} specialist's "
                f"allowlist {sorted(contract.allowed_tools)}")


# --------------------------------------------------------------------------- #
# Effect guard
# --------------------------------------------------------------------------- #
class EffectGuard:
    @staticmethod
    def attempt(contract: WorkerContract, effect_kind: str, *, ledger: WorkerLedger) -> None:
        """Record and DENY an external-effect attempt. Never returns normally."""
        if not isinstance(effect_kind, str) or not effect_kind:
            effect_kind = "unspecified"
        ledger.record_effect_attempt(effect_kind)
        raise EffectDenied(
            f"specialist {contract.worker_id} attempted external effect {effect_kind!r}; "
            f"external_effect_budget is 0 (attempt #{ledger.effect_attempts} recorded)")


# --------------------------------------------------------------------------- #
# Budgeted provider
# --------------------------------------------------------------------------- #
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
