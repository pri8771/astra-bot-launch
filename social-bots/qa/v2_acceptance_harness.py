"""V2.0 engineering-readiness acceptance harness (SB-V20-099 prep, non-runtime).

This is a QA/control deliverable, not a runtime implementation. It encodes the
integration contract from ``V2_ENGINEERING_ACCEPTANCE.md`` as record shapes plus
pure assertion helpers, so that once Core + Intelligence are merged, the merged
runtime's emitted records can be checked against these contracts with almost no
extra wiring. It imports NO runtime module and fabricates NO integrated runtime;
it operates on record dicts (real ones later, fixtures now).

The required trace chain (V2_ENGINEERING_ACCEPTANCE.md §"Required integration path"
and §"Traceability acceptance"):

    raw evidence receipt
      -> normalized metric observation / experiment evidence
      -> audience hypothesis update
      -> experiment result (or explicit INCONCLUSIVE)
      -> growth opportunity
      -> strategy revision proposal
      -> deterministic policy validation
      -> strategy update (or NO_CHANGE) with durable revision history + evidence links

Every helper returns a list of violation strings ([] == satisfied), mirroring the
artifact validator, so tests can assert precisely.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

# --------------------------------------------------------------------------- #
# Sentinels & vocabularies
# --------------------------------------------------------------------------- #
class _Missing:
    """Distinct sentinel for a metric that is ABSENT (not the number zero).

    The 'missing vs zero' distinction (scenario C) is non-negotiable: absent
    evidence must never be silently treated as a measured zero.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "MISSING"

    def __bool__(self) -> bool:  # avoid accidental truthiness games
        return False


MISSING = _Missing()

# Provenance labels. Fixtures must never masquerade as live/operational evidence.
FIXTURE_PROVENANCE = {"fixture", "engineering-fixture", "synthetic"}
OPERATIONAL_PROVENANCE = {"live-capture", "operational", "real-account"}

EXPERIMENT_RESULTS = {"IMPROVED", "WORSE", "INCONCLUSIVE", "NO_CHANGE"}
POLICY_DECISIONS = {"ACCEPT", "NO_CHANGE", "BLOCKED", "REJECTED"}
STRATEGY_ACTIONS = {
    "INCREASE_ALLOCATION", "DECREASE_ALLOCATION", "REVERSE_ALLOCATION",
    "HOLD", "NO_CHANGE", "REQUEST_MORE_EVIDENCE",
}
# Fields on a proposal that must be finite numerics in [0,1] when present.
_UNIT_FIELDS = ("confidence", "evidence_strength", "allocation_delta_frac")

# Authority/effect flags that must never be asserted true by an engineering trace.
_PUBLIC_EFFECT_FLAGS = (
    "published", "publish_authorized", "spent", "spend_authorized",
    "message_sent", "credential_mutated",
)


def index_by_id(records: Iterable[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in records if isinstance(r, dict) and "id" in r}


# --------------------------------------------------------------------------- #
# 1. Fixture-vs-operational labeling
# --------------------------------------------------------------------------- #
def check_fixture_labeling(records: Iterable[dict]) -> list[str]:
    """Every engineering record must be labeled fixture, never operational."""
    out = []
    for r in records:
        prov = r.get("provenance")
        if prov is None:
            continue  # non-evidence records need not carry provenance
        if prov in OPERATIONAL_PROVENANCE:
            out.append(f"{r.get('id')}: provenance {prov!r} is operational; "
                       f"engineering acceptance fixtures must not claim live evidence")
        elif prov not in FIXTURE_PROVENANCE:
            out.append(f"{r.get('id')}: unknown provenance {prov!r}")
    return out


# --------------------------------------------------------------------------- #
# 2. No public/external effect (scenario F + global invariant)
# --------------------------------------------------------------------------- #
def check_no_public_effect(records: Iterable[dict]) -> list[str]:
    out = []
    for r in records:
        for flag in _PUBLIC_EFFECT_FLAGS:
            if r.get(flag) is True:
                out.append(f"{r.get('id')}: public-effect flag {flag!r} is True "
                           f"in an engineering trace (no external effect allowed)")
    return out


# --------------------------------------------------------------------------- #
# 3. Persona/workspace isolation
# --------------------------------------------------------------------------- #
def check_persona_isolation(records: Iterable[dict], personas: Iterable[str]) -> list[str]:
    """Every persona-scoped record carries a known persona; no cross-persona refs.

    A record must not reference (by *_refs) a record belonging to another persona.
    """
    recs = list(records)
    known = set(personas)
    idx = index_by_id(recs)
    out = []
    for r in recs:
        p = r.get("persona")
        if p is None:
            continue
        if p not in known:
            out.append(f"{r.get('id')}: unknown persona {p!r}")
        for key, val in r.items():
            if not key.endswith("_refs") or not isinstance(val, list):
                continue
            for ref in val:
                other = idx.get(ref)
                if other and other.get("persona") not in (None, p):
                    out.append(f"{r.get('id')} (persona {p}) references {ref} "
                               f"owned by persona {other.get('persona')} — cross-persona bleed")
    return out


# --------------------------------------------------------------------------- #
# 4. Missing-vs-zero (scenario C)
# --------------------------------------------------------------------------- #
def check_missing_not_zero(metric: dict) -> list[str]:
    """A metric observation must represent absence as MISSING, never as 0."""
    out = []
    val = metric.get("value", MISSING)
    if val is MISSING:
        # An explicitly-missing metric must be flagged missing, not carry a number.
        if metric.get("status") not in ("MISSING", "ABSENT"):
            out.append(f"{metric.get('id')}: value is MISSING but status "
                       f"{metric.get('status')!r} does not mark it absent")
    elif isinstance(val, bool) or not isinstance(val, (int, float)):
        out.append(f"{metric.get('id')}: value {val!r} is not a number or MISSING")
    return out


def experiment_should_be_inconclusive(metrics: list[dict]) -> bool:
    """True when required metrics are missing, so the experiment must not conclude."""
    return any(m.get("value", MISSING) is MISSING for m in metrics)


# --------------------------------------------------------------------------- #
# 5. Stale evidence (scenario E)
# --------------------------------------------------------------------------- #
def check_stale_handling(evidence: dict, revision: dict, *, age_days: float,
                         freshness_days: float) -> list[str]:
    """If evidence is older than the freshness policy, the revision must show it
    was downweighted/decayed AND record the stale-source limitation."""
    out = []
    if age_days > freshness_days:
        if not revision.get("stale_downweighted"):
            out.append(f"{revision.get('id')}: evidence {evidence.get('id')} is stale "
                       f"({age_days}d > {freshness_days}d) but revision did not downweight it")
        limitations = " ".join(revision.get("limitations", [])).lower()
        if "stale" not in limitations:
            out.append(f"{revision.get('id')}: stale evidence used but no stale-source "
                       f"limitation recorded")
    return out


# --------------------------------------------------------------------------- #
# 6. Authority block (scenario F)
# --------------------------------------------------------------------------- #
def check_authority_block(opportunity: dict, policy: dict) -> list[str]:
    """An unauthorized opportunity may be RECORDED but its execution must be
    BLOCKED with no public effect."""
    out = []
    if opportunity.get("authorized") is False:
        if policy.get("decision") != "BLOCKED":
            out.append(f"{opportunity.get('id')}: recommends an unauthorized action "
                       f"but policy decision is {policy.get('decision')!r}, not BLOCKED")
    return out


# --------------------------------------------------------------------------- #
# 7. Adversarial proposal shape (scenario G)
# --------------------------------------------------------------------------- #
def validate_proposal_shape(proposal: dict) -> list[str]:
    """Reject malformed numerics, unknown action, or missing evidence refs BEFORE
    any strategy mutation."""
    out = []
    action = proposal.get("action")
    if action not in STRATEGY_ACTIONS:
        out.append(f"{proposal.get('id')}: unknown strategy action {action!r}")
    for f in _UNIT_FIELDS:
        if f in proposal:
            v = proposal[f]
            if isinstance(v, bool) or not isinstance(v, (int, float)) \
                    or not math.isfinite(v) or not (0.0 <= v <= 1.0):
                out.append(f"{proposal.get('id')}: numeric {f}={v!r} out of bounds [0,1]")
    # A non-NO_CHANGE proposal must cite evidence and a growth opportunity.
    if action not in ("NO_CHANGE", "REQUEST_MORE_EVIDENCE"):
        if not proposal.get("growth_refs"):
            out.append(f"{proposal.get('id')}: missing growth_refs")
        if not proposal.get("evidence_refs"):
            out.append(f"{proposal.get('id')}: missing evidence_refs")
    # A proposal must never carry authority/effect flags itself.
    for flag in _PUBLIC_EFFECT_FLAGS:
        if proposal.get(flag) is True:
            out.append(f"{proposal.get('id')}: proposal illegally asserts {flag!r}")
    return out


# --------------------------------------------------------------------------- #
# 8. Full trace-chain resolution (Traceability acceptance)
# --------------------------------------------------------------------------- #
def resolve_trace_chain(revision: dict, records: Iterable[dict]) -> list[str]:
    """Walk strategy_revision -> growth_opportunity -> audience/experiment/metric
    -> raw evidence receipts. Every hop must resolve to a record of the expected
    kind, terminating in at least one evidence receipt with a provenance label.
    """
    idx = index_by_id(records)
    out: list[str] = []

    def need(ref: str, kinds: set[str], ctx: str) -> dict | None:
        rec = idx.get(ref)
        if rec is None:
            out.append(f"{ctx}: dangling ref {ref!r} (not in record set)")
            return None
        if rec.get("kind") not in kinds:
            out.append(f"{ctx}: ref {ref!r} is kind {rec.get('kind')!r}, expected {sorted(kinds)}")
            return None
        return rec

    if revision.get("kind") != "strategy_revision":
        return [f"{revision.get('id')}: not a strategy_revision record"]

    growth = need(revision.get("growth_ref", ""), {"growth_opportunity"},
                  f"{revision.get('id')}->growth")
    reached_evidence: set[str] = set()
    if growth:
        mids = list(growth.get("audience_refs", [])) + list(growth.get("experiment_refs", []))
        if not mids:
            out.append(f"{growth.get('id')}: growth opportunity cites no audience/experiment refs")
        for ref in mids:
            mid = need(ref, {"audience_hypothesis", "experiment_result"},
                       f"{growth.get('id')}->mid")
            if not mid:
                continue
            metric_refs = list(mid.get("metric_refs", [])) + list(mid.get("evidence_refs", []))
            for mr in metric_refs:
                leaf = need(mr, {"metric_observation", "experiment_result", "evidence_receipt"},
                            f"{mid.get('id')}->leaf")
                if not leaf:
                    continue
                for er in ([leaf["id"]] if leaf.get("kind") == "evidence_receipt"
                           else leaf.get("evidence_refs", [])):
                    ev = need(er, {"evidence_receipt"}, f"{leaf.get('id')}->evidence")
                    if ev:
                        if not ev.get("provenance"):
                            out.append(f"{ev.get('id')}: evidence receipt lacks provenance label")
                        reached_evidence.add(ev["id"])
    if not reached_evidence:
        out.append(f"{revision.get('id')}: trace does not reach any raw evidence receipt")
    return out


# --------------------------------------------------------------------------- #
# Convenience: run every applicable invariant over a full trace record set.
# --------------------------------------------------------------------------- #
def check_global_invariants(records: list[dict], personas: Iterable[str]) -> list[str]:
    out: list[str] = []
    out += check_fixture_labeling(records)
    out += check_no_public_effect(records)
    out += check_persona_isolation(records, personas)
    return out
