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


@dataclass
class OpportunityInput:
    """A candidate lane: platform x format (x optional experiment).

    - ``performance``: {"value": 0..1, "samples": n} of *real, per-platform*
      normalized growth signal, or None if not measured (MISSING, not zero).
    - ``audience_support``: {"confidence": 0..1|None, "hypothesis_id": str} or None.
    - ``learning_question``: True if there is an open question worth testing
      (e.g. an INCONCLUSIVE experiment or an untried format).
    - ``evidence_refs``: refs into metrics/experiments/audience.
    """
    id: str
    platform: str
    format: str
    experiment_id: str | None = None
    performance: dict | None = None
    audience_support: dict | None = None
    learning_question: bool = False
    evidence_refs: list = field(default_factory=list)


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


def evaluate(opportunities: list[OpportunityInput], *, availability: dict,
             learning_weight: float = 1.0) -> dict:
    """Rank growth/learning opportunities and recommend an attention allocation."""
    availability = availability or {}
    growth_ops, learning_ops = [], []
    blocked, insufficient = [], []
    selectable = []  # (opp, growth_component, learning_component, uncertainty, kind)

    for opp in opportunities:
        avail = availability.get(opp.platform, {})
        if not avail.get("available"):
            blocked.append({"id": opp.id, "platform": opp.platform,
                            "status": BLOCKED,
                            "reason": avail.get("reason") or "destination unavailable",
                            "evidence_refs": opp.evidence_refs})
            continue

        if _is_insufficient(opp):
            insufficient.append({"id": opp.id, "platform": opp.platform,
                                 "format": opp.format, "status": INSUFFICIENT,
                                 "reason": "no performance, audience support or "
                                           "learning question — no recommendation",
                                 "evidence_refs": opp.evidence_refs})
            continue

        gscore = _growth_score(opp)
        lscore = _learning_score(opp)
        unc = _uncertainty(opp)
        pv = _perf_value(opp)

        entry_common = {
            "id": opp.id, "platform": opp.platform, "format": opp.format,
            "experiment_id": opp.experiment_id, "uncertainty": unc,
            "performance": pv,  # None stays None (missing != zero)
            "evidence_refs": opp.evidence_refs,
        }

        if gscore is not None:
            growth_ops.append({**entry_common, "kind": GROWTH,
                               "growth_score": gscore,
                               "reasons": [f"measured performance {pv:.2f}",
                                           f"uncertainty {unc}"]})
        if lscore > 0 and (opp.learning_question or pv is None):
            learning_ops.append({**entry_common, "kind": LEARNING,
                                 "learning_score": lscore,
                                 "reasons": [f"learning value {lscore:.2f}",
                                             f"uncertainty {unc}",
                                             "missing performance -> learning candidate"
                                             if pv is None else "open question"]})

        selectable.append((opp, gscore or 0.0, lscore, unc))

    growth_ops.sort(key=lambda o: o["growth_score"], reverse=True)
    learning_ops.sort(key=lambda o: o["learning_score"], reverse=True)

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
                "opportunity_id": opp.id, "platform": opp.platform,
                "format": opp.format, "experiment_id": opp.experiment_id,
                "weight": round(raw / total, 6), "kind": kind,
                "uncertainty": unc, "evidence_refs": opp.evidence_refs,
                "reasons": [f"growth={gcomp:.2f}", f"learning={lcomp:.2f}",
                            f"learning_weight={learning_weight:.2f}"],
            })
        allocation.sort(key=lambda a: a["weight"], reverse=True)

    return {
        "growth_opportunities": growth_ops,
        "learning_opportunities": learning_ops,
        "allocation": allocation,
        "blocked": blocked,
        "insufficient_evidence": insufficient,
        "spend_authorized": False,  # hard invariant — no monetary spend, ever
        "notes": "allocation weights are attention/effort share (sum≈1), "
                 "not monetary spend; missing performance is not treated as zero",
    }
