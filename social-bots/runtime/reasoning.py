"""Reasoning-provider seam for adaptive autonomous thinking (V0.4 / SB-R1B).

The decision engine separates two responsibilities (the "model proposes, policy
decides" boundary):

* A **reasoning provider** interprets changed evidence and *proposes* candidate
  actions with per-alternative estimates, reasoning and uncertainties. This is the
  part that should eventually be adaptive (SB-R1C) — different evidence/persona/
  state must yield materially different proposals.
* The **deterministic policy layer** (in ``decision``/``pipeline``/``leasing``)
  still owns safety, authority, publication gates, dedup, no-change detection,
  leases, scheduling, verification and reconciliation. A proposal is only a
  suggestion; the policy decides whether it is eligible to execute.

Fail-closed contract: when a reasoning route is REQUIRED (changed evidence needs
interpretation) but none is available, the provider returns ``None`` and the
engine emits ``BLOCKED_REASONING_UNAVAILABLE`` — never fabricated adaptive scores.
No SwarmAI dependency: providers are plain callables resolved from local config.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Callable, Protocol

# Bounded allowed action vocabulary (the policy layer knows how to handle each).
ACTION_VOCAB = ("NO_ACTION", "RESEARCH_MORE", "CREATE_CANDIDATE", "CONTINUE_EXPERIMENT")

# Per-candidate numeric estimate fields that must be finite and within [0, 1].
_NUMERIC_FIELDS = ("expected_value", "expected_learning", "relevance", "confidence",
                   "risk", "cost", "reversibility", "duplication_risk")

# A proposal payload may only carry inert context. It must never carry authority:
# authority is owned by the deterministic policy layer, never proposed by a model.
_ALLOWED_PAYLOAD_KEYS = {"signal", "draft", "experiment", "notes"}
_AUTHORITY_KEYS = {
    "authority", "authorized", "authorised", "can_public_post", "can_spend",
    "can_message_users", "can_create_candidate", "can_register_experiment",
    "can_update_state", "publish_authorized", "published", "grant", "grants",
    "permissions", "scopes", "token", "credential", "credentials",
}


class ReasoningContractError(Exception):
    """Raised when provider output violates the reasoning schema/contract."""


@dataclass
class Candidate:
    action: str
    rationale: str
    expected_value: float
    expected_learning: float
    relevance: float
    confidence: float
    risk: float
    cost: float
    reversibility: float
    duplication_risk: float
    payload: dict = field(default_factory=dict)

    def score(self) -> float:
        return round(
            0.9 * self.expected_value
            + 1.0 * self.expected_learning
            + 0.6 * self.relevance
            + 0.4 * self.confidence
            + 0.3 * self.reversibility
            - 0.8 * self.risk
            - 0.5 * self.cost
            - 0.7 * self.duplication_risk,
            4,
        )


def no_action(reason: str) -> Candidate:
    return Candidate("NO_ACTION", reason, expected_value=0.05, expected_learning=0.0,
                     relevance=0.0, confidence=1.0, risk=0.0, cost=0.0,
                     reversibility=1.0, duplication_risk=0.0)


@dataclass
class ReasoningContext:
    """Everything a provider needs to interpret the current situation."""
    persona: dict
    objective: str
    top_signal: dict
    pending_count: int
    is_duplicate: bool
    draft: dict
    state_summary: dict = field(default_factory=dict)


@dataclass
class ReasoningProposal:
    alternatives: list[Candidate]
    recommended_action: str
    uncertainties: list[str]
    provider_id: str
    adaptive: bool


class ReasoningProvider(Protocol):
    provider_id: str

    def available(self) -> bool: ...

    def propose(self, ctx: ReasoningContext) -> ReasoningProposal | None: ...


# --------------------------------------------------------------------------- #
# Proposal schema validation — runs BEFORE scoring/execution. A malformed or
# authority-smuggling proposal is rejected (never scored, never executed); the
# engine then fails closed. This is defense-in-depth: the deterministic policy
# layer still independently owns authority, gates, dedup, leases and scheduling.
# --------------------------------------------------------------------------- #
def _bad_number(v) -> bool:
    return not isinstance(v, (int, float)) or isinstance(v, bool) \
        or not math.isfinite(v) or v < 0.0 or v > 1.0


def validate_candidate(c) -> list[str]:
    errs: list[str] = []
    if not isinstance(c, Candidate):
        return [f"alternative is not a Candidate: {type(c).__name__}"]
    if c.action not in ACTION_VOCAB:
        errs.append(f"unsupported action {c.action!r}")
    if not isinstance(c.rationale, str) or not c.rationale.strip():
        errs.append(f"{c.action}: empty/invalid rationale")
    for f in _NUMERIC_FIELDS:
        if _bad_number(getattr(c, f, None)):
            errs.append(f"{c.action}: numeric field {f}={getattr(c, f, None)!r} out of bounds [0,1]")
    if not isinstance(c.payload, dict):
        errs.append(f"{c.action}: payload must be a dict")
    else:
        smuggled = _AUTHORITY_KEYS.intersection(c.payload.keys())
        if smuggled:
            errs.append(f"{c.action}: payload attempts to smuggle authority keys {sorted(smuggled)}")
        unknown = set(c.payload.keys()) - _ALLOWED_PAYLOAD_KEYS
        if unknown:
            errs.append(f"{c.action}: payload has unrecognized keys {sorted(unknown)}")
    # CREATE_CANDIDATE must reference a signal to act on (no phantom candidates).
    if c.action == "CREATE_CANDIDATE" and not (isinstance(c.payload, dict)
                                               and c.payload.get("signal")):
        errs.append("CREATE_CANDIDATE: payload missing 'signal'")
    return errs


def validate_proposal(proposal, ctx: ReasoningContext | None = None) -> list[str]:
    """Return a list of contract violations ([] means valid)."""
    if not isinstance(proposal, ReasoningProposal):
        return [f"proposal is not a ReasoningProposal: {type(proposal).__name__}"]
    errs: list[str] = []
    if not proposal.alternatives:
        errs.append("alternatives is empty")
    if not isinstance(proposal.provider_id, str) or not proposal.provider_id:
        errs.append("missing provider_id")
    if not isinstance(proposal.uncertainties, list):
        errs.append("uncertainties must be a list")
    actions = set()
    for c in proposal.alternatives:
        cerrs = validate_candidate(c)
        errs.extend(cerrs)
        if isinstance(c, Candidate):
            actions.add(c.action)
    # recommended action must be supported AND actually be one of the alternatives.
    if proposal.recommended_action not in ACTION_VOCAB:
        errs.append(f"recommended_action {proposal.recommended_action!r} not in vocabulary")
    elif proposal.recommended_action not in actions:
        errs.append(f"recommended_action {proposal.recommended_action!r} not among proposed alternatives")
    return errs


class _UnavailableProvider:
    """A provider that is deliberately unavailable, so the engine fails closed.

    Used when adaptive reasoning is REQUIRED but only a non-adaptive route is
    configured: we refuse to let fixed heuristic scoring masquerade as adaptive
    autonomy. ``propose`` never runs.
    """
    adaptive = False

    def __init__(self, provider_id: str, reason: str):
        self.provider_id = provider_id
        self.reason = reason

    def available(self) -> bool:
        return False

    def propose(self, ctx: ReasoningContext) -> None:
        return None


# --------------------------------------------------------------------------- #
# Baseline provider — the current deterministic heuristic. Explicitly NOT the
# adaptive V0.4 target; it is the safe default that keeps the machine runnable
# and is the thing SB-R1C replaces with a model-backed adaptive provider.
# --------------------------------------------------------------------------- #
class BaselineReasoningProvider:
    provider_id = "baseline-deterministic-v1"
    adaptive = False

    def available(self) -> bool:
        return True

    def propose(self, ctx: ReasoningContext) -> ReasoningProposal:
        dup = ctx.is_duplicate
        alts = [
            no_action("act only if a candidate clears review; otherwise wait"),
            Candidate("RESEARCH_MORE",
                      "gather more signals before committing an angle",
                      expected_value=0.2, expected_learning=0.5, relevance=0.6,
                      confidence=0.5, risk=0.1, cost=0.2, reversibility=1.0,
                      duplication_risk=0.0),
            Candidate("CREATE_CANDIDATE",
                      f"turn signal {ctx.top_signal['id']} into a reviewed, queued "
                      f"(unpublished) candidate",
                      expected_value=0.7, expected_learning=0.8, relevance=0.85,
                      confidence=0.7, risk=0.15, cost=0.3, reversibility=1.0,
                      duplication_risk=1.0 if dup else 0.0,
                      payload={"signal": ctx.top_signal, "draft": ctx.draft}),
        ]
        best = max(alts, key=lambda c: c.score())
        return ReasoningProposal(
            alternatives=alts, recommended_action=best.action,
            uncertainties=["baseline heuristic: scores are fixed, not evidence-adaptive"],
            provider_id=self.provider_id, adaptive=self.adaptive)


# --------------------------------------------------------------------------- #
# Model provider — the adaptive route. The actual model call is SB-R1C; here it
# is a fail-closed stub: with no model callable configured it is UNAVAILABLE and
# ``propose`` returns None so the engine blocks instead of faking autonomy.
# --------------------------------------------------------------------------- #
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


# Optional process-registered adaptive model callable (set by the host wiring in
# SB-R1C). Kept as a module global so no import-time model dependency exists.
_MODEL_CALLABLE: Callable[[ReasoningContext], ReasoningProposal] | None = None


def register_model_callable(fn: Callable[[ReasoningContext], ReasoningProposal] | None) -> None:
    global _MODEL_CALLABLE
    _MODEL_CALLABLE = fn


def adaptive_required() -> bool:
    """Whether this deployment REQUIRES adaptive reasoning (the V0.4 posture).

    Default False so tests/legacy/debugging may use the deterministic baseline
    explicitly. When True, a non-adaptive provider is refused: fixed heuristic
    scoring must never masquerade as adaptive autonomy. Set
    ``SBOTS_REASONING_REQUIRE_ADAPTIVE=1`` on an adaptive-contract deployment.
    """
    return os.environ.get("SBOTS_REASONING_REQUIRE_ADAPTIVE", "0").strip().lower() \
        in {"1", "true", "yes", "on"}


def resolve_provider() -> ReasoningProvider:
    """Resolve the configured provider.

    - ``SBOTS_REASONING`` selects the mode: 'baseline' (deterministic, explicitly
      NOT adaptive — for tests/legacy/debug) or 'model' (adaptive; fail-closed to
      unavailable unless a model callable was registered).
    - When ``adaptive_required()`` is True and the resolved provider is not
      adaptive, return an unavailable provider so the engine fails closed to
      BLOCKED_REASONING_UNAVAILABLE instead of running the fixed baseline and
      pretending it is adaptive autonomy.
    """
    mode = os.environ.get("SBOTS_REASONING", "baseline").strip().lower()
    provider = ModelReasoningProvider(_MODEL_CALLABLE) if mode == "model" \
        else BaselineReasoningProvider()
    if adaptive_required() and not getattr(provider, "adaptive", False):
        return _UnavailableProvider(
            provider_id=f"unavailable-adaptive-required(mode={mode})",
            reason="adaptive reasoning required but no adaptive provider is "
                   "available (configured mode is non-adaptive)")
    return provider
