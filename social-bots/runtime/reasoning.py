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

import os
from dataclasses import dataclass, field
from typing import Callable, Protocol


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
        if proposal is None or not proposal.alternatives:
            return None
        return proposal


# Optional process-registered adaptive model callable (set by the host wiring in
# SB-R1C). Kept as a module global so no import-time model dependency exists.
_MODEL_CALLABLE: Callable[[ReasoningContext], ReasoningProposal] | None = None


def register_model_callable(fn: Callable[[ReasoningContext], ReasoningProposal] | None) -> None:
    global _MODEL_CALLABLE
    _MODEL_CALLABLE = fn


def resolve_provider() -> ReasoningProvider:
    """Resolve the configured provider. Default 'baseline'; 'model' is fail-closed
    unless a model callable was registered. ``SBOTS_REASONING`` selects the mode."""
    mode = os.environ.get("SBOTS_REASONING", "baseline").strip().lower()
    if mode == "model":
        return ModelReasoningProvider(_MODEL_CALLABLE)
    return BaselineReasoningProvider()
