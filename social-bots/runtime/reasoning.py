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

# Bounded allowed action VOCABULARY, reconciled with REASONING_PROPOSAL_SCHEMA.md.
# A model MAY propose any of these; the deterministic policy decides eligibility.
# NOTE (SB-V04-001): being in the vocabulary does NOT imply an effect executor
# exists. CONTINUE_EXPERIMENT and CLOSE_EXPERIMENT are accepted as valid proposal
# actions but have NO executor yet, so ``decision._execute`` routes them to a safe
# ``blocked_unsupported_action`` no-effect. We deliberately do not implement
# future effect executors just because an action appears in the schema.
ACTION_VOCAB = ("NO_ACTION", "RESEARCH_MORE", "CREATE_CANDIDATE",
                "CONTINUE_EXPERIMENT", "CLOSE_EXPERIMENT")

# Actions that currently HAVE a deterministic effect executor in ``decision``.
# Everything else in ACTION_VOCAB validates but performs no effect (fail-safe).
EXECUTABLE_ACTIONS = ("NO_ACTION", "RESEARCH_MORE", "CREATE_CANDIDATE")

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
# Contextual provider (SB-V04-002) — genuinely context-sensitive deterministic
# reasoning. Unlike the fixed baseline, every estimate is COMPUTED from persona,
# evidence, current state and duplication, so different personas / evidence /
# state produce materially different alternatives AND rankings, and NO_ACTION or
# RESEARCH_MORE can genuinely win. It is honestly labeled ``adaptive = False``:
# it is transparent heuristic reasoning, not a model, so under the
# adaptive-required posture (SB-V04-001) it still fails closed rather than
# claiming model-grade autonomy. The model route below remains the adaptive one.
# --------------------------------------------------------------------------- #
_PROVENANCE_CONFIDENCE = {"live-capture": 0.85, "operator-supplied": 0.6, "fixture": 0.4}


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, round(float(x), 4)))


class ContextualReasoningProvider:
    provider_id = "contextual-deterministic-v1"
    adaptive = False

    def available(self) -> bool:
        return True

    def propose(self, ctx: ReasoningContext) -> ReasoningProposal:
        sig = ctx.top_signal
        persona = ctx.persona or {}
        tags = sig.get("tags", []) or []
        provenance = sig.get("provenance", "fixture")
        has_source = bool(sig.get("url") or sig.get("source"))
        cultural = persona.get("kind") == "cultural" or \
            persona.get("source_requirements", {}).get("cultural_review_required", False)
        strict_source = persona.get("source_requirements", {}).get("evidence_required", True)

        # --- Evidence strength & confidence, derived from the actual evidence ---
        base_conf = _PROVENANCE_CONFIDENCE.get(provenance, 0.4)
        # tag coverage: more topical tags -> more to say; saturates.
        coverage = _clamp01(0.25 + 0.2 * len(tags))
        strength = _clamp01(0.5 * coverage + 0.5 * base_conf + (0.1 if has_source else -0.2))
        confidence = _clamp01(base_conf + (0.1 if has_source else -0.15)
                              - (0.15 if cultural and not has_source else 0.0))
        # thin evidence (no source, sparse tags, low-trust provenance) -> research.
        thin = (not has_source) or len(tags) == 0 or base_conf < 0.5
        # state: an area we already have hypotheses about is less novel to learn.
        hyp = int(ctx.state_summary.get("hypotheses", 0))
        novelty = _clamp01(1.0 - 0.15 * hyp)

        # --- NO_ACTION: wins on duplicates or when acting is clearly unwarranted.
        na = no_action("duplicate or evidence too weak/irrelevant to act on")
        na.expected_value = 0.08 + (0.5 if ctx.is_duplicate else 0.0) \
            + (0.25 if (thin and cultural) else 0.0)
        na.relevance = _clamp01(0.1 + (0.6 if ctx.is_duplicate else 0.0))
        na.expected_value = _clamp01(na.expected_value)

        # --- RESEARCH_MORE: wins when evidence is thin/uncertain, esp. for strict
        #     or cultural personas that must not act on unsourced material.
        rm = Candidate(
            "RESEARCH_MORE",
            f"evidence for {sig.get('id')} is thin/uncertain "
            f"(tags={len(tags)}, provenance={provenance}, source={has_source}); "
            f"gather more before committing an angle",
            expected_value=_clamp01(0.2 + 0.3 * (1 - strength)),
            expected_learning=_clamp01(0.5 + 0.4 * (1 - confidence)
                                       + (0.15 if (cultural or strict_source) and thin else 0.0)),
            relevance=_clamp01(0.4 + 0.4 * (1 - strength)),
            confidence=_clamp01(0.5 + 0.3 * (1 - strength)),
            risk=0.05, cost=0.2, reversibility=1.0,
            duplication_risk=1.0 if ctx.is_duplicate else 0.0)

        # --- CREATE_CANDIDATE: wins on strong, novel, non-duplicate evidence for a
        #     persona that can act; cultural/strict personas need real sourcing.
        create_penalty = 0.0
        if cultural and not has_source:
            create_penalty += 0.5   # cultural without source will be withheld anyway
        if thin:
            create_penalty += 0.25
        cc = Candidate(
            "CREATE_CANDIDATE",
            f"turn signal {sig.get('id')} into a reviewed, queued (unpublished) "
            f"candidate for {persona.get('display_name', persona.get('id'))}",
            expected_value=_clamp01(0.35 + 0.5 * strength - create_penalty),
            expected_learning=_clamp01(0.4 + 0.4 * novelty),
            relevance=_clamp01(0.45 + 0.5 * strength),
            confidence=confidence,
            risk=_clamp01(0.1 + (0.3 if cultural else 0.0) + (0.2 if thin else 0.0)),
            cost=0.3, reversibility=1.0,
            duplication_risk=1.0 if ctx.is_duplicate else 0.0,
            payload={"signal": sig, "draft": ctx.draft})

        alts = [na, rm, cc]
        best = max(alts, key=lambda c: c.score())
        uncertainties = [
            f"evidence_strength={strength}", f"confidence={confidence}",
            f"novelty(vs {hyp} prior hypotheses)={novelty}",
        ]
        if thin:
            uncertainties.append("thin/low-trust evidence — bias toward RESEARCH_MORE")
        if cultural:
            uncertainties.append("cultural persona — conservative bias; needs named reviewer + source")
        return ReasoningProposal(
            alternatives=alts, recommended_action=best.action,
            uncertainties=uncertainties, provider_id=self.provider_id,
            adaptive=self.adaptive)


# --------------------------------------------------------------------------- #
# Model provider — the adaptive route. The actual model call is SB-R1C; here it
# is a fail-closed stub: with no model callable configured it is UNAVAILABLE and
# ``propose`` returns None so the engine blocks instead of faking autonomy.
# --------------------------------------------------------------------------- #
class EngineeringStub:
    """Policy-owned wrapper declaring a callable ENGINEERING-ONLY (never a model
    or network call). It is the only way a unit test may register a synthetic
    adaptive proposal source without a canonical authorization manifest — and
    even then it executes ONLY under the explicit ENGINEERING dispatch scope
    (``model_dispatch.configure_engineering`` / ``engineering_scope``), never
    with no scope and never under a production scope (LEAD-051: wrapping a
    callable in this type is not a no-grant execution capability).

    Classification is by EXACT type in ``model_dispatch.classify`` — a subclass,
    an ``adaptive=False`` attribute or any other label changes nothing.
    """

    def __init__(self, fn: Callable[[ReasoningContext], ReasoningProposal | None],
                 *, label: str = "engineering-stub"):
        if not callable(fn):
            raise TypeError("EngineeringStub needs a callable")
        self._fn = fn
        self.label = label

    def __call__(self, ctx: ReasoningContext) -> ReasoningProposal | None:
        return self._fn(ctx)


class ModelReasoningProvider:
    """Adaptive provider over a process-registered callable.

    SB-R07-041 (LEAD-047 P0): the callable is NEVER invoked directly. Every
    ``propose`` goes through ``model_dispatch.dispatch``, which refuses a live
    callable without a configured dispatch scope + canonical scoped manifest,
    reserves a durable call slot BEFORE invoking, refuses reentry, and records the
    outcome. Direct-library callers, env variables and labels cannot bypass it:
    only exact policy-owned non-live types (receipt replay, engineering stub) run
    without a grant, and those are classified in the decision record.
    """
    provider_id = "model-adaptive-v0"
    adaptive = True

    def __init__(self, model_callable: Callable[[ReasoningContext], ReasoningProposal] | None = None):
        self._model = model_callable
        self._last_reason: str | None = None

    @property
    def reason(self) -> str | None:
        return self._last_reason

    def available(self) -> bool:
        from . import model_dispatch
        if self._model is None:
            self._last_reason = "no reasoning route wired"
            return False
        cls = model_dispatch.classify(self._model)
        if cls == model_dispatch.LIVE_MODEL:
            ok, reason = model_dispatch.availability()
            self._last_reason = None if ok else f"live model call not authorized: {reason}"
            return ok
        scope = model_dispatch.current_scope()
        if cls == model_dispatch.ENGINEERING_STUB and (
                scope is None or not scope.allow_engineering_stubs):
            # LEAD-051: a stub runs only under the policy-owned ENGINEERING scope.
            self._last_reason = ("engineering stub refused: no engineering dispatch scope"
                                 if scope is None else
                                 "engineering stub refused under a production dispatch scope")
            return False
        self._last_reason = None
        return True

    def propose(self, ctx: ReasoningContext) -> ReasoningProposal | None:
        from . import model_dispatch
        if self._model is None:
            self._last_reason = "no reasoning route wired"
            return None  # fail closed: no reasoning route wired
        try:
            proposal = model_dispatch.dispatch(self._model, ctx, provider_id=self.provider_id)
        except model_dispatch.AuthorizationDenied as exc:
            # Usually refused BEFORE any invocation (no scope / no manifest /
            # exhausted / stale / reentrant / posture) — no slot consumed. If the
            # callable itself raised a refusal after being dispatched (e.g. it
            # re-entered the gate), the slot IS consumed and the ledger says so.
            rec = model_dispatch.last_record()
            if rec is not None and rec.invoked:
                self._last_reason = f"provider exception after dispatch: {exc}"
            else:
                self._last_reason = f"live model call refused: {exc}"
            return None
        except Exception as exc:                      # noqa: BLE001 - slot already consumed
            self._last_reason = f"provider exception: {type(exc).__name__}"
            return None
        self._last_reason = None
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

# Optional model id for the SB-V04-002 Claude Code CLI provider (mode
# 'claude-cli'); None lets the CLI use its configured default model.
_CLI_MODEL: str | None = os.environ.get("SBOTS_REASONING_CLI_MODEL") or None


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


def resolve_provider(require_adaptive: bool | None = None) -> ReasoningProvider:
    """Resolve the configured provider.

    - ``SBOTS_REASONING`` selects the mode: 'baseline'/'contextual' (deterministic,
      explicitly NOT adaptive — for tests/diagnostics/debug) or 'model' (adaptive;
      fail-closed to unavailable unless a model callable was registered).
    - ``require_adaptive`` overrides the adaptive-required posture for this call:
      None (default) uses the env-driven ``adaptive_required()``; the production
      worker passes True so a V0.4 production run cannot silently fall back to a
      deterministic provider. When the effective requirement is True and the
      resolved provider is not adaptive, an unavailable provider is returned so
      the engine fails closed to BLOCKED_REASONING_UNAVAILABLE instead of running
      the fixed baseline and pretending it is adaptive autonomy.
    """
    require = adaptive_required() if require_adaptive is None else bool(require_adaptive)
    mode = os.environ.get("SBOTS_REASONING", "baseline").strip().lower()
    if mode == "model":
        provider = ModelReasoningProvider(_MODEL_CALLABLE)
    elif mode == "claude-cli":
        # SB-V04-002 real adaptive route: bounded, effect-free Claude Code CLI
        # subprocess on the existing subscription. Lazy import avoids a cycle.
        from .reasoning_cli import ClaudeCodeReasoningProvider
        provider = ClaudeCodeReasoningProvider(model=_CLI_MODEL)
    elif mode == "contextual":
        provider = ContextualReasoningProvider()   # context-sensitive, adaptive=False
    else:
        provider = BaselineReasoningProvider()
    if require and not getattr(provider, "adaptive", False):
        return _UnavailableProvider(
            provider_id=f"unavailable-adaptive-required(mode={mode})",
            reason="adaptive reasoning required but no adaptive provider is "
                   "available (configured mode is non-adaptive)")
    return provider
