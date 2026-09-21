"""Growth evaluator and allocation engine (SB-V20-002).

Turn real analytics / experiment / audience evidence into bounded
recommendations about where to spend *attention and learning effort* — never
money.

Guarantees
----------
- **No monetary spend is ever authorized.** Allocation weights are attention/
  effort shares that sum to 1.0. `spend_authorized` is always False and there is
  no spend API.
- **Missing data does not become zero.** A missing performance metric is kept as
  `None`; it never scores as "zero growth". A missing-performance opportunity is
  simply not a *growth* candidate — it may still be a *learning* candidate.
- **No recommendation when evidence is insufficient.** An opportunity with no
  performance, no learning question and no audience support is INSUFFICIENT and
  excluded from allocation.
- **Learning value can beat short-term reach** when justified (configurable
  `learning_weight`).
- Unavailable destinations are BLOCKED and excluded from allocation.
- Every ranked item carries reasons, evidence refs and uncertainty.

SB-V20-002 repair (INTELLIGENCE_WAVE1 §8 + LEAD-014)
--------------------------------------------------
- Every ``OpportunityInput`` carries a persistent bot + persona/workspace scope,
  and every opportunity/allocation record echoes it, so two personas on one
  runtime stay distinguishable.
- Outputs are typed ``GrowthOpportunity`` records aligned with
  ``CROSS_LANE_INTERFACES.md`` §7 (opportunity_type, expected_growth_value,
  expected_learning_value, confidence, uncertainty[], required_authority,
  evidence_refs[], operational_availability, cost_class) — Core's
  strategy-revision interface can consume them without inventing
  authority/cost/scope.
- A GROWTH opportunity may only be built from typed accepted evidence
  (``opportunity_from_evidence``). An arbitrary numeric ``OpportunityInput`` is
  ``provenance="test-only"``; under ``require_evidence=True`` it can never become
  a growth opportunity. Invalid/stale evidence demotes to learning / no
  recommendation — never growth optimization.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

# Per-opportunity outcome classes.
GROWTH = "growth"
LEARNING = "learning"
BLOCKED = "blocked"
INSUFFICIENT = "insufficient_evidence"

# Uncertainty levels and their learning value.
UNC_HIGH = "high"
UNC_MEDIUM = "medium"
UNC_LOW = "low"
_UNC_VALUE = {UNC_HIGH: 1.0, UNC_MEDIUM: 0.6, UNC_LOW: 0.2}

# Provenance of an OpportunityInput.
PROV_EVIDENCE = "evidence"      # built from typed accepted records
PROV_TEST_ONLY = "test-only"    # arbitrary numbers (tests/dev only)


@dataclass
class OpportunityInput:
    """A candidate lane: platform x format (x optional experiment).

    - ``bot`` / ``persona``: persistent scope (required).
    - ``performance``: {"value": 0..1, "samples": n} of *real, per-platform*
      normalized growth signal, or None if not measured (MISSING, not zero).
    - ``audience_support``: {"confidence": 0..1|None, "hypothesis_id": str} or None.
    - ``learning_question``: True if there is an open question worth testing.
    - ``required_authority`` / ``cost_class``: carried, never invented.
    - ``provenance``: ``evidence`` (typed accepted records) or ``test-only``.
    - ``evidence_refs``: refs into metrics/experiments/audience.
    """
    id: str
    bot: str
    persona: str
    platform: str
    format: str
    experiment_id: str | None = None
    performance: dict | None = None
    audience_support: dict | None = None
    learning_question: bool = False
    required_authority: str = "none"     # attention/learning needs no public authority
    cost_class: str = "no_spend"         # this artifact never authorizes spend
    provenance: str = PROV_TEST_ONLY
    evidence_refs: list = field(default_factory=list)

    def __post_init__(self):
        if not self.bot or not self.persona:
            raise ValueError("OpportunityInput requires a bot and persona scope")


@dataclass
class GrowthOpportunity:
    """Typed output aligned with CROSS_LANE_INTERFACES.md §7."""
    opportunity_id: str
    bot: str
    persona: str
    opportunity_type: str                # growth | learning
    platform: str
    format: str
    experiment_id: str | None
    expected_growth_value: float | None
    expected_learning_value: float | None
    confidence: float | None
    uncertainty: list                    # [level, *flags]
    required_authority: str
    evidence_refs: list
    operational_availability: dict
    cost_class: str
    provenance: str
    reasons: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def _scope_of(record, kind: str) -> tuple:
    """Extract (bot, persona) from a typed upstream record for scope checks."""
    if record is None:
        return (None, None)
    if kind == "metric":            # metrics.NormalizedObservation
        return (getattr(record, "bot", None) or getattr(record, "account_alias", None),
                getattr(record, "persona", None))
    if kind == "experiment":        # SB-V15 to_learning_ref dict
        return (record.get("bot"), record.get("persona"))
    if kind == "audience":          # SB-V14 confidence() dict
        sc = record.get("scope", {})
        return (sc.get("bot"), sc.get("persona"))
    return (None, None)


def opportunity_from_evidence(*, id: str, bot: str, persona: str, platform: str,
                              format: str, performance_value: float | None = None,
                              samples: int = 1, metric_observation=None,
                              experiment_learning_ref: dict | None = None,
                              audience_confidence: dict | None = None,
                              learning_question: bool = False,
                              required_authority: str = "none",
                              cost_class: str = "no_spend",
                              max_age_hours: float = 48.0, now=None) -> OpportunityInput:
    """Construct an evidence-backed OpportunityInput from typed accepted records.

    Validates that every provided upstream record shares the (bot, persona) scope,
    and demotes stale/missing metric evidence to a learning signal (never growth).
    Only inputs built here carry ``provenance="evidence"`` and are eligible to
    become GROWTH opportunities under ``require_evidence=True``.
    """
    # 1. Persona/workspace scope must be consistent across all evidence.
    for rec, kind in ((metric_observation, "metric"),
                      (experiment_learning_ref, "experiment"),
                      (audience_confidence, "audience")):
        rb, rp = _scope_of(rec, kind)
        if rp is not None and rp != persona:
            raise ValueError(
                f"{kind} evidence persona {rp!r} != opportunity persona {persona!r}")

    evidence_refs: list = []
    uncertainty_flags: list = []

    # 2. Performance from a metric observation, honouring freshness.
    performance = None
    if metric_observation is not None:
        from . import metrics  # local import; no cycle
        evidence_refs.append({"metric_observation_id":
                              getattr(metric_observation, "observation_id", None)})
        stale = metrics.is_stale(metric_observation, max_age_hours=max_age_hours, now=now)
        if stale:
            uncertainty_flags.append("stale-metric-evidence")
            learning_question = True   # stale => learning, not growth
        elif performance_value is not None:
            performance = {"value": performance_value, "samples": samples}
    elif performance_value is not None:
        # A performance value with no backing observation is not growth-eligible.
        uncertainty_flags.append("performance-without-observation")
        learning_question = True

    # 3. Experiment learning ref.
    experiment_id = None
    if experiment_learning_ref is not None:
        experiment_id = experiment_learning_ref.get("experiment_id")
        evidence_refs.append({"experiment_id": experiment_id,
                              "baseline_observation_id":
                              experiment_learning_ref.get("baseline_observation_id"),
                              "treatment_observation_id":
                              experiment_learning_ref.get("treatment_observation_id")})

    # 4. Audience support.
    audience_support = None
    if audience_confidence is not None:
        audience_support = {"confidence": audience_confidence.get("confidence"),
                            "hypothesis_id": audience_confidence.get("hypothesis_id")}
        evidence_refs.append({"audience_hypothesis_id":
                              audience_confidence.get("hypothesis_id")})

    opp = OpportunityInput(
        id=id, bot=bot, persona=persona, platform=platform, format=format,
        experiment_id=experiment_id, performance=performance,
        audience_support=audience_support, learning_question=learning_question,
        required_authority=required_authority, cost_class=cost_class,
        provenance=PROV_EVIDENCE, evidence_refs=evidence_refs)
    # Stash flags for the evaluator to surface in uncertainty[].
    opp.__dict__["_uncertainty_flags"] = uncertainty_flags
    return opp


def _uncertainty(opp: OpportunityInput) -> str:
    perf = opp.performance
    if not perf or not isinstance(perf.get("value"), (int, float)):
        return UNC_HIGH
    samples = perf.get("samples", 0)
    base = UNC_LOW if samples >= 5 else UNC_MEDIUM
    # Missing audience corroboration nudges uncertainty up one level.
    if not opp.audience_support or opp.audience_support.get("confidence") is None:
        base = UNC_MEDIUM if base == UNC_LOW else UNC_HIGH
    return base


def _perf_value(opp: OpportunityInput) -> float | None:
    perf = opp.performance
    if not perf or not isinstance(perf.get("value"), (int, float)):
        return None  # MISSING — never coerced to 0.0
    return max(0.0, min(1.0, float(perf["value"])))


def _growth_score(opp: OpportunityInput) -> float | None:
    pv = _perf_value(opp)
    if pv is None:
        return None
    conf = None
    if opp.audience_support:
        conf = opp.audience_support.get("confidence")
    if isinstance(conf, (int, float)):
        return round(pv * (0.5 + 0.5 * max(0.0, min(1.0, conf))), 6)
    return round(pv, 6)


def _learning_score(opp: OpportunityInput) -> float:
    unc = _uncertainty(opp)
    base = _UNC_VALUE[unc]
    # An explicit open question (or missing perf) is where learning pays off.
    active = opp.learning_question or _perf_value(opp) is None
    return round(base * (1.0 if active else 0.3), 6)


def _is_insufficient(opp: OpportunityInput) -> bool:
    no_perf = _perf_value(opp) is None
    no_audience = (not opp.audience_support
                   or opp.audience_support.get("confidence") is None)
    return no_perf and no_audience and not opp.learning_question


def _availability_of(availability: dict, platform: str) -> dict:
    a = availability.get(platform, {})
    return {"platform": platform, "available": bool(a.get("available")),
            "reason": a.get("reason")}


def evaluate(opportunities: list[OpportunityInput], *, availability: dict,
             learning_weight: float = 1.0, require_evidence: bool = False) -> dict:
    """Rank growth/learning opportunities and recommend an attention allocation.

    ``require_evidence=True`` (operational mode) forbids a GROWTH opportunity from
    a ``test-only`` input — arbitrary numbers may only ever be learning/no-rec.
    Every emitted record carries the (bot, persona) scope and the cross-lane
    GrowthOpportunity contract.
    """
    availability = availability or {}
    growth_ops, learning_ops = [], []
    blocked, insufficient = [], []
    selectable = []  # (opp, growth_component, learning_component, uncertainty)

    for opp in opportunities:
        op_avail = _availability_of(availability, opp.platform)
        if not op_avail["available"]:
            blocked.append({"opportunity_id": opp.id, "bot": opp.bot,
                            "persona": opp.persona, "platform": opp.platform,
                            "status": BLOCKED,
                            "reason": op_avail["reason"] or "destination unavailable",
                            "operational_availability": op_avail,
                            "evidence_refs": opp.evidence_refs})
            continue

        if _is_insufficient(opp):
            insufficient.append({"opportunity_id": opp.id, "bot": opp.bot,
                                 "persona": opp.persona, "platform": opp.platform,
                                 "format": opp.format, "status": INSUFFICIENT,
                                 "reason": "no performance, audience support or "
                                           "learning question — no recommendation",
                                 "evidence_refs": opp.evidence_refs})
            continue

        gscore = _growth_score(opp)
        # Test-only inputs may never be growth optimization under require_evidence.
        if require_evidence and opp.provenance != PROV_EVIDENCE:
            gscore = None
        lscore = _learning_score(opp)
        unc_level = _uncertainty(opp)
        pv = _perf_value(opp)
        conf = (opp.audience_support or {}).get("confidence")
        flags = list(opp.__dict__.get("_uncertainty_flags", []))
        if require_evidence and opp.provenance != PROV_EVIDENCE:
            flags.append("test-only-input-not-growth-eligible")
        uncertainty = [unc_level] + flags

        def _mk(kind, growth_v, learning_v, reasons):
            return GrowthOpportunity(
                opportunity_id=opp.id, bot=opp.bot, persona=opp.persona,
                opportunity_type=kind, platform=opp.platform, format=opp.format,
                experiment_id=opp.experiment_id, expected_growth_value=growth_v,
                expected_learning_value=learning_v, confidence=conf,
                uncertainty=uncertainty, required_authority=opp.required_authority,
                evidence_refs=opp.evidence_refs, operational_availability=op_avail,
                cost_class=opp.cost_class, provenance=opp.provenance,
                reasons=reasons).as_dict()

        if gscore is not None:
            growth_ops.append({**_mk(GROWTH, gscore, lscore,
                                     [f"measured performance {pv:.2f}",
                                      f"uncertainty {unc_level}"]),
                               "growth_score": gscore, "performance": pv})
        if lscore > 0 and (opp.learning_question or pv is None):
            learning_ops.append({**_mk(LEARNING, gscore, lscore,
                                       [f"learning value {lscore:.2f}",
                                        f"uncertainty {unc_level}",
                                        "missing/stale performance -> learning candidate"
                                        if pv is None else "open question"]),
                                 "learning_score": lscore, "performance": pv})

        selectable.append((opp, gscore or 0.0, lscore, unc_level))

    growth_ops.sort(key=lambda o: (-o["growth_score"], o["opportunity_id"]))
    learning_ops.sort(key=lambda o: (-o["learning_score"], o["opportunity_id"]))

    # Allocation: blend growth + weighted learning across selectable lanes.
    weights = []
    for opp, gcomp, lcomp, unc in selectable:
        raw = gcomp + max(0.0, learning_weight) * lcomp
        weights.append((opp, raw, gcomp, lcomp, unc))
    total = sum(w for _, w, _, _, _ in weights)

    allocation = []
    if total > 0:
        for opp, raw, gcomp, lcomp, unc in weights:
            if raw <= 0:
                continue
            kind = LEARNING if (learning_weight * lcomp) > gcomp else GROWTH
            allocation.append({
                "opportunity_id": opp.id, "bot": opp.bot, "persona": opp.persona,
                "platform": opp.platform, "format": opp.format,
                "experiment_id": opp.experiment_id,
                "weight": round(raw / total, 6), "opportunity_type": kind,
                "uncertainty": unc, "required_authority": opp.required_authority,
                "cost_class": opp.cost_class, "provenance": opp.provenance,
                "operational_availability": _availability_of(availability, opp.platform),
                "evidence_refs": opp.evidence_refs,
                "reasons": [f"growth={gcomp:.2f}", f"learning={lcomp:.2f}",
                            f"learning_weight={learning_weight:.2f}"],
            })
        allocation.sort(key=lambda a: (-a["weight"], a["opportunity_id"]))

    return {
        "growth_opportunities": growth_ops,
        "learning_opportunities": learning_ops,
        "allocation": allocation,
        "blocked": blocked,
        "insufficient_evidence": insufficient,
        "spend_authorized": False,  # hard invariant — no monetary spend, ever
        "require_evidence": require_evidence,
        "notes": "allocation weights are attention/effort share (sum≈1), "
                 "not monetary spend; missing/stale performance is not treated as "
                 "zero; growth requires evidence-provenance under require_evidence",
    }
