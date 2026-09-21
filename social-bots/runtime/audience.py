"""Audience memory (SB-V14-001).

Evidence-backed audience *hypotheses* that evolve only with measured results.

Key rules
---------
- **Observation vs inference are separate.** Observations are stored raw facts
  (with refs to the content/experiment/metric that produced them). Confidence is
  an inference *derived* from those observations on read — never a stored,
  hand-edited number.
- **No metrics => no fake learning.** A hypothesis with no (non-decayed)
  evidence is ``unlearned`` with confidence ``None``. Confidence cannot move
  without real observations.
- **Repeated support raises confidence within bounds; contrary evidence lowers
  it.** Confidence is a bounded evidence ratio with a neutral prior.
- **Old evidence decays** (exponential half-life), so stale support fades.
- **Contradictions reduce confidence or fork** a competing hypothesis.
- **No sensitive-person profiling.** Segment descriptors naming sensitive
  attributes are rejected.
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

# Sensitive-person attribute categories that must never drive targeting.
SENSITIVE_ATTRS = {
    "race", "ethnicity", "religion", "religious", "health", "medical",
    "diagnosis", "disability", "sexual_orientation", "sexuality", "gender_identity",
    "political", "political_affiliation", "immigration", "citizenship", "genetic",
    "biometric", "precise_location", "home_address", "minor", "minors", "children",
    "criminal_record", "financial_account", "union_membership",
}


class SensitiveSegmentError(ValueError):
    """Raised when a segment descriptor names a sensitive-person attribute."""


def validate_segment(segment: dict) -> dict:
    """Reject segments that target sensitive-person attributes.

    Segments describe *content/context* affinities (topic, format, timezone
    band, platform), never protected personal attributes.
    """
    if not isinstance(segment, dict):
        raise SensitiveSegmentError("segment must be a mapping of context keys")
    for key, val in segment.items():
        k = str(key).strip().lower()
        if k in SENSITIVE_ATTRS:
            raise SensitiveSegmentError(f"sensitive segment attribute not allowed: {key!r}")
        v = str(val).strip().lower()
        if v in SENSITIVE_ATTRS:
            raise SensitiveSegmentError(f"sensitive segment value not allowed: {val!r}")
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
    segment: dict
    statement: str
    supporting: list = field(default_factory=list)     # Observation dicts
    contradicting: list = field(default_factory=list)  # Observation dicts
    created_at: str = field(default_factory=now_iso)
    last_updated: str = field(default_factory=now_iso)
    forked_from: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def new_hypothesis(segment: dict, statement: str) -> Hypothesis:
    validate_segment(segment)
    return Hypothesis(id="hyp-" + uuid.uuid4().hex[:12], segment=segment,
                      statement=statement)


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

    if total < _EPSILON:
        return {"status": "unlearned", "confidence": None,
                "effective_support": round(s, 6), "effective_contradiction": round(c, 6),
                "freshness_days": freshness_days,
                "note": "no (non-decayed) evidence; confidence is not invented"}

    raw = (_PRIOR * _PRIOR_STRENGTH + s) / (_PRIOR_STRENGTH + s + c)
    conf = max(_CONF_MIN, min(_CONF_MAX, raw))
    return {"status": "learned", "confidence": round(conf, 6),
            "effective_support": round(s, 6), "effective_contradiction": round(c, 6),
            "freshness_days": freshness_days,
            "half_life_days": half_life_days}


def should_fork(hyp: Hypothesis, *, now: datetime | None = None,
                half_life_days: float = _DEFAULT_HALF_LIFE_DAYS) -> bool:
    """Contradicting evidence materially outweighs support => fork a rival."""
    now = now or datetime.now(timezone.utc)
    s = _decayed(hyp.supporting, now, half_life_days)
    c = _decayed(hyp.contradicting, now, half_life_days)
    return c >= _EPSILON and c > s * _FORK_RATIO


def fork_hypothesis(hyp: Hypothesis, new_statement: str,
                    segment: dict | None = None) -> Hypothesis:
    """Create a competing hypothesis carrying the contradicting evidence as its
    supporting evidence. The original is left intact."""
    seg = validate_segment(segment) if segment is not None else dict(hyp.segment)
    fork = Hypothesis(id="hyp-" + uuid.uuid4().hex[:12], segment=seg,
                      statement=new_statement, forked_from=hyp.id)
    # The evidence that contradicted the parent supports the alternative.
    for o in hyp.contradicting:
        supp = dict(o)
        supp["stance"] = SUPPORTS
        fork.supporting.append(supp)
    fork.last_updated = now_iso()
    return fork


# --------------------------------------------------------------------------- #
# Persistence — one JSON file per hypothesis under the bot's memory namespace.
# --------------------------------------------------------------------------- #
def _dir(bot: str):
    d = paths.memory_dir(bot) / "audience"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save(bot: str, hyp: Hypothesis) -> None:
    write_json(_dir(bot) / f"{hyp.id}.json", hyp.as_dict())


def load(bot: str, hyp_id: str) -> Hypothesis | None:
    data = read_json(_dir(bot) / f"{hyp_id}.json")
    return Hypothesis(**data) if data else None
