"""Audience memory (SB-V14-001).

Evidence-backed audience *hypotheses* that evolve only with measured results,
scoped to a specific bot runtime AND persona/workspace.

Key rules
---------
- **Persona/workspace scoped.** Every hypothesis carries a persistent
  ``bot`` + ``persona`` scope. Private audience memory is stored under
  ``memory/<bot>/audience/<persona>/`` and the save/load/list APIs reject or
  exclude another persona's hypotheses. Two personas on one runtime can hold
  contradictory hypotheses without overwriting or blending them.
- **Observation vs inference are separate.** Observations are stored raw facts
  (with refs to the content/experiment/metric that produced them). Confidence is
  an inference *derived* from those observations on read — never a stored,
  hand-edited number. Every confidence result identifies the persona/workspace
  scope and the evidence refs it used.
- **No metrics => no fake learning.** A hypothesis with no (non-decayed)
  evidence is ``unlearned`` with confidence ``None``.
- **Repeated support raises confidence within bounds; contrary evidence lowers
  it.** Confidence is a bounded evidence ratio with a neutral prior.
- **Old evidence decays** (exponential half-life), so stale support fades.
- **Contradictions reduce confidence or fork** a competing hypothesis — but a
  contradiction of A is NOT positive evidence for an arbitrary alternative B.
- **Safe segment dimensions are an allowlist**, not a sensitive-attribute
  blacklist: a segment key must be a known content/context dimension.
"""
from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

from . import paths
from .jsonstore import write_json, read_json, now_iso

# Stances an observation can take toward a hypothesis.
SUPPORTS = "supports"
CONTRADICTS = "contradicts"

# Confidence model constants.
_PRIOR = 0.5
_PRIOR_STRENGTH = 1.0
_CONF_MIN, _CONF_MAX = 0.05, 0.95
_DEFAULT_HALF_LIFE_DAYS = 30.0
_EPSILON = 0.01  # below this total effective weight -> "unlearned"

# Fork when contradicting effective weight materially exceeds supporting.
_FORK_RATIO = 1.5

# Allowlist of safe segment dimensions. A segment describes content/context
# affinity only. Anything not on this list (including any sensitive-person
# attribute) is rejected — an allowlist, not a blacklist. Deliberately no
# open-ended "interest" dimension: a free-form interest field is a vector for
# sensitive-trait inference (e.g. religious_interest / health_interest).
ALLOWED_SEGMENT_DIMENSIONS = {
    "topic", "format", "platform", "timezone_band", "language",
    "content_theme", "posting_time", "series", "campaign", "funnel_stage",
    "content_length", "hook_style", "cadence",
}

# Sensitive-person trait roots. Matched as substrings against tokenized values so
# compound variants (religious_interest, mental_health, political_affiliation,
# medical-condition, ...) are caught, not just exact strings.
SENSITIVE_TRAIT_ROOTS = (
    "race", "ethnic", "religio", "faith", "health", "medic", "diagnos",
    "disab", "sexual", "sexuality", "orientation", "gender_identity", "lgbt",
    "politic", "immigrat", "citizen", "genetic", "biometric",
    "geolocation", "precise_location", "home_address", "minor", "children",
    "criminal", "financial_account", "union_member", "pregnan", "mental",
)

# Retained for compatibility/reference (exact sensitive dimension names).
SENSITIVE_ATTRS = {
    "race", "ethnicity", "religion", "religious", "health", "medical",
    "diagnosis", "disability", "sexual_orientation", "sexuality", "gender_identity",
    "political", "political_affiliation", "immigration", "citizenship", "genetic",
    "biometric", "precise_location", "home_address", "minor", "minors", "children",
    "criminal_record", "financial_account", "union_membership",
}


def _names_sensitive_trait(text: str) -> bool:
    """True if any token/substring of ``text`` names a sensitive-trait root."""
    low = str(text).strip().lower()
    return any(root in low for root in SENSITIVE_TRAIT_ROOTS)


class SensitiveSegmentError(ValueError):
    """Raised when a segment uses a non-allowlisted or sensitive dimension."""


class PersonaScopeError(ValueError):
    """Raised when an audience-memory op crosses a persona/workspace boundary."""


def validate_segment(segment: dict) -> dict:
    """Validate a segment against the allowlist of safe content/context dimensions.

    A segment key MUST be a known content/context dimension
    (:data:`ALLOWED_SEGMENT_DIMENSIONS`). This is an allowlist, so a sensitive or
    unknown dimension is rejected by default rather than requiring the blacklist
    to enumerate it. As defense-in-depth a value naming a sensitive attribute is
    also rejected.
    """
    if not isinstance(segment, dict):
        raise SensitiveSegmentError("segment must be a mapping of context keys")
    if not segment:
        raise SensitiveSegmentError("segment must name at least one safe dimension")
    for key, val in segment.items():
        k = str(key).strip().lower()
        if k not in ALLOWED_SEGMENT_DIMENSIONS:
            raise SensitiveSegmentError(
                f"segment dimension {key!r} is not in the safe allowlist "
                f"{sorted(ALLOWED_SEGMENT_DIMENSIONS)}")
        # Defense-in-depth: reject a value (or key) that names a sensitive trait,
        # matched by substring so compound variants cannot slip through.
        if _names_sensitive_trait(key) or _names_sensitive_trait(val):
            raise SensitiveSegmentError(
                f"segment names a sensitive-person trait: {key!r}={val!r}")
    return segment


@dataclass(frozen=True)
class Observation:
    """A raw measured fact bearing on a hypothesis. Immutable once recorded."""
    id: str
    stance: str
    weight: float          # base evidence weight (e.g. effect size); >= 0
    observed_at: str
    refs: dict             # {content_id, experiment_id, observation_id, metric, ...}
    note: str = ""

    @staticmethod
    def make(stance: str, refs: dict, *, weight: float = 1.0,
             observed_at: str | None = None, note: str = "") -> "Observation":
        if stance not in (SUPPORTS, CONTRADICTS):
            raise ValueError(f"bad stance {stance!r}")
        if weight < 0:
            raise ValueError("observation weight must be >= 0")
        if not refs:
            raise ValueError("an observation must carry evidence refs (no fake learning)")
        return Observation(
            id="obsv-" + uuid.uuid4().hex[:12], stance=stance, weight=float(weight),
            observed_at=observed_at or now_iso(), refs=dict(refs), note=note)


@dataclass
class Hypothesis:
    id: str
    bot: str
    persona: str
    segment: dict
    statement: str
    supporting: list = field(default_factory=list)     # Observation dicts
    contradicting: list = field(default_factory=list)  # Observation dicts
    created_at: str = field(default_factory=now_iso)
    last_updated: str = field(default_factory=now_iso)
    forked_from: str | None = None
    origin_contradiction_refs: list = field(default_factory=list)

    @property
    def scope(self) -> dict:
        return {"bot": self.bot, "persona": self.persona}

    def as_dict(self) -> dict:
        return asdict(self)


def new_hypothesis(bot: str, persona: str, segment: dict,
                   statement: str) -> Hypothesis:
    if not bot or not persona:
        raise PersonaScopeError("a hypothesis requires a bot and a persona scope")
    validate_segment(segment)
    return Hypothesis(id="hyp-" + uuid.uuid4().hex[:12], bot=bot, persona=persona,
                      segment=segment, statement=statement)


def add_observation(hyp: Hypothesis, obs: Observation) -> Hypothesis:
    """Record a raw observation (a fact), not an inferred confidence."""
    bucket = hyp.supporting if obs.stance == SUPPORTS else hyp.contradicting
    bucket.append(asdict(obs))
    hyp.last_updated = now_iso()
    return hyp


def _parse(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def _decayed(obs_list: list[dict], now: datetime, half_life_days: float) -> float:
    total = 0.0
    for o in obs_list:
        age_days = (now - _parse(o["observed_at"])).total_seconds() / 86400.0
        if age_days < 0:
            age_days = 0.0
        total += o.get("weight", 1.0) * math.pow(0.5, age_days / half_life_days)
    return total


def confidence(hyp: Hypothesis, *, now: datetime | None = None,
               half_life_days: float = _DEFAULT_HALF_LIFE_DAYS) -> dict:
    """Derive confidence from decayed evidence. No evidence => unlearned/None."""
    now = now or datetime.now(timezone.utc)
    s = _decayed(hyp.supporting, now, half_life_days)
    c = _decayed(hyp.contradicting, now, half_life_days)
    total = s + c

    all_obs = hyp.supporting + hyp.contradicting
    freshness_days = None
    if all_obs:
        newest = max(_parse(o["observed_at"]) for o in all_obs)
        freshness_days = (now - newest).total_seconds() / 86400.0

    # Every confidence result identifies the persona/workspace scope and the
    # evidence refs it was derived from (acceptance requirement).
    evidence_refs = [{"id": o.get("id"), "stance": o.get("stance"),
                      "refs": o.get("refs", {})} for o in all_obs]
    scope = hyp.scope

    if total < _EPSILON:
        return {"status": "unlearned", "confidence": None,
                "scope": scope, "hypothesis_id": hyp.id,
                "effective_support": round(s, 6), "effective_contradiction": round(c, 6),
                "freshness_days": freshness_days, "evidence_refs": evidence_refs,
                "note": "no (non-decayed) evidence; confidence is not invented"}

    raw = (_PRIOR * _PRIOR_STRENGTH + s) / (_PRIOR_STRENGTH + s + c)
    conf = max(_CONF_MIN, min(_CONF_MAX, raw))
    return {"status": "learned", "confidence": round(conf, 6),
            "scope": scope, "hypothesis_id": hyp.id,
            "effective_support": round(s, 6), "effective_contradiction": round(c, 6),
            "freshness_days": freshness_days, "evidence_refs": evidence_refs,
            "half_life_days": half_life_days}


def should_fork(hyp: Hypothesis, *, now: datetime | None = None,
                half_life_days: float = _DEFAULT_HALF_LIFE_DAYS) -> bool:
    """Contradicting evidence materially outweighs support => fork a rival."""
    now = now or datetime.now(timezone.utc)
    s = _decayed(hyp.supporting, now, half_life_days)
    c = _decayed(hyp.contradicting, now, half_life_days)
    return c >= _EPSILON and c > s * _FORK_RATIO


def fork_hypothesis(hyp: Hypothesis, new_statement: str, *,
                    segment: dict | None = None) -> Hypothesis:
    """Create a competing hypothesis for a DIFFERENT statement, IN THE SAME
    persona/workspace as the parent.

    Contradiction of the parent A is evidence that A is wrong; it is NOT positive
    evidence for the fork's arbitrary alternative B. So the fork starts with NO
    supporting evidence (``unlearned`` until real support for B arrives). The
    triggering contradiction is recorded only as provenance
    (``origin_contradiction_refs``), never as support.

    A private fork ALWAYS stays in the source persona/workspace — there is no
    re-scope parameter, because carrying A's provenance/contradiction into a
    different persona would be an implicit cross-persona private-memory transfer.
    Any cross-workspace import must go through a separate explicit contract.
    """
    seg = validate_segment(segment) if segment is not None else dict(hyp.segment)
    fork = Hypothesis(
        id="hyp-" + uuid.uuid4().hex[:12],
        bot=hyp.bot,
        persona=hyp.persona,          # never cross-persona
        segment=seg,
        statement=new_statement,
        forked_from=hyp.id,
        origin_contradiction_refs=[
            {"observation_id": o.get("id"), "refs": o.get("refs", {})}
            for o in hyp.contradicting
        ],
    )
    fork.last_updated = now_iso()
    return fork


# --------------------------------------------------------------------------- #
# Persistence — persona/workspace scoped. One JSON file per hypothesis under
# memory/<bot>/audience/<persona>/. Ops reject/exclude other personas.
# --------------------------------------------------------------------------- #
def _dir(bot: str, persona: str):
    if not bot or not persona:
        raise PersonaScopeError("audience memory ops require bot and persona")
    d = paths.memory_dir(bot) / "audience" / persona
    d.mkdir(parents=True, exist_ok=True)
    return d


def save(bot: str, persona: str, hyp: Hypothesis) -> None:
    """Persist a hypothesis under its persona scope.

    Refuses to write a hypothesis whose own bot/persona scope does not match the
    requested scope — a persona cannot write into another's private memory.
    """
    if hyp.bot != bot or hyp.persona != persona:
        raise PersonaScopeError(
            f"hypothesis scope {hyp.scope} does not match save scope "
            f"{{'bot': {bot!r}, 'persona': {persona!r}}}")
    write_json(_dir(bot, persona) / f"{hyp.id}.json", hyp.as_dict())


def load(bot: str, persona: str, hyp_id: str) -> Hypothesis | None:
    """Load a hypothesis from a persona scope, or None if it is not that
    persona's. Cross-persona reads never return another persona's hypothesis."""
    data = read_json(_dir(bot, persona) / f"{hyp_id}.json")
    if not data:
        return None
    hyp = Hypothesis(**data)
    if hyp.bot != bot or hyp.persona != persona:
        # Defensive: stored scope must match the requested scope.
        return None
    return hyp


def list_hypotheses(bot: str, persona: str) -> list[Hypothesis]:
    """List only the given persona's hypotheses on the given bot runtime."""
    d = _dir(bot, persona)
    out = []
    for path in sorted(d.glob("hyp-*.json")):
        data = read_json(path)
        if not data:
            continue
        hyp = Hypothesis(**data)
        if hyp.bot == bot and hyp.persona == persona:
            out.append(hyp)
    return out
