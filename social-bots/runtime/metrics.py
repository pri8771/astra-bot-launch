"""Normalized analytics brain (SB-V13-001).

A truthful cross-platform metric model. Two rules dominate the design:

1. **MISSING != ZERO.** A metric a platform did not report is *missing*, not
   zero. A metric a platform has no equivalent for is *not supported*. Neither
   is ever silently turned into ``0``.
2. **No false equivalence.** Platform-native metrics are mapped into shared
   semantic categories only through an explicit, versioned per-platform table.
   A category with no mapping for a platform stays MISSING/NOT_SUPPORTED rather
   than borrowing an unrelated metric.

Every normalized observation retains the full raw metric payload, its
platform/account/persona/content/experiment identifiers, the observation window,
the collection timestamp, the normalization version, and a staleness flag.
Derived metrics record their formula and formula version, and are MISSING when
any input is missing.

This module is additive; ``analytics.py`` (the accepted append-only event log) is
left unchanged.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from . import paths
from .jsonstore import append_jsonl, read_jsonl, now_iso

NORMALIZATION_VERSION = "1.0.0"

# ------------------------------------------------------------------------- #
# Semantic categories and availability states.
# ------------------------------------------------------------------------- #
REACH = "reach"
VIEW = "view"
COMPLETION = "completion"
SAVE = "save"
SHARE = "share"
REPLY = "reply"
CLICK = "click"
FOLLOW = "follow"
CONVERSION = "conversion"

SEMANTICS = (REACH, VIEW, COMPLETION, SAVE, SHARE, REPLY, CLICK, FOLLOW, CONVERSION)

# Availability is a first-class distinction, NOT a numeric sentinel.
PRESENT = "present"              # observed (value may legitimately be 0)
MISSING = "missing"             # platform supports it but it was not reported
NOT_SUPPORTED = "not_supported"  # platform has no equivalent metric

# ------------------------------------------------------------------------- #
# Per-platform normalization tables. Only these explicit mappings cross the
# platform boundary; anything unmapped stays MISSING/NOT_SUPPORTED.
#
# ``supports`` is the set of semantics the platform *could* report — used to
# tell MISSING (supported, absent) apart from NOT_SUPPORTED (no equivalent).
# ``raw_to_semantic`` maps a platform-native raw metric name to a semantic.
# ------------------------------------------------------------------------- #
PLATFORM_MAP: dict[str, dict] = {
    "x": {
        "supports": {REACH, VIEW, REPLY, SHARE, CLICK, FOLLOW},
        "raw_to_semantic": {
            "impressions": REACH,
            "video_views": VIEW,
            "replies": REPLY,
            "retweets": SHARE,
            "url_link_clicks": CLICK,
            "follows": FOLLOW,
        },
    },
    "instagram": {
        "supports": {REACH, VIEW, COMPLETION, SAVE, SHARE, REPLY, FOLLOW},
        "raw_to_semantic": {
            "reach": REACH,
            "plays": VIEW,
            "video_completions": COMPLETION,
            "saved": SAVE,
            "shares": SHARE,
            "comments": REPLY,
            "follows": FOLLOW,
        },
    },
    "tiktok": {
        "supports": {VIEW, COMPLETION, SAVE, SHARE, REPLY, FOLLOW},
        "raw_to_semantic": {
            "video_views": VIEW,
            "completion_views": COMPLETION,
            "favourites": SAVE,
            "shares": SHARE,
            "comments": REPLY,
            "new_followers": FOLLOW,
        },
    },
    "reddit": {
        # Reddit has no native reach/view/completion equivalent -> NOT_SUPPORTED.
        "supports": {SHARE, REPLY, CLICK, SAVE},
        "raw_to_semantic": {
            "crossposts": SHARE,
            "num_comments": REPLY,
            "outbound_clicks": CLICK,
            "saves": SAVE,
        },
    },
}


@dataclass(frozen=True)
class MetricValue:
    """A single semantic metric with an explicit availability state."""
    semantic: str
    availability: str
    value: float | None
    raw_name: str | None
    raw_value: float | None

    def is_missing(self) -> bool:
        return self.availability != PRESENT


@dataclass(frozen=True)
class NormalizedObservation:
    observation_id: str
    platform: str
    source: str                 # collection provenance (e.g. collector/receipt id)
    account_alias: str | None
    persona: str | None
    content_id: str | None
    experiment_id: str | None
    window_start: str | None
    window_end: str | None
    collected_at: str
    normalization_version: str
    raw_metrics: dict            # FULL raw retention, verbatim
    normalized: dict             # semantic -> MetricValue-as-dict
    unmapped_raw: list           # raw names with no semantic mapping (kept, not blended)

    def metric(self, semantic: str) -> MetricValue:
        d = self.normalized[semantic]
        return MetricValue(**d)

    def as_dict(self) -> dict:
        return asdict(self)


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def normalize(*, platform: str, raw_metrics: dict, source: str,
              account_alias: str | None = None, persona: str | None = None,
              content_id: str | None = None, experiment_id: str | None = None,
              window_start: str | None = None, window_end: str | None = None,
              collected_at: str | None = None) -> NormalizedObservation:
    """Normalize a platform's raw metric payload into semantic categories.

    Retains the full raw payload. A raw metric present with any numeric value
    (including 0) is PRESENT. A supported semantic with no raw metric is MISSING.
    A semantic the platform has no equivalent for is NOT_SUPPORTED. Nothing is
    coerced to 0.
    """
    pmap = PLATFORM_MAP.get(platform)
    if pmap is None:
        # Unknown platform: everything is MISSING (we cannot assert support).
        supports: set = set()
        raw_to_sem: dict = {}
    else:
        supports = pmap["supports"]
        raw_to_sem = pmap["raw_to_semantic"]

    # Invert mapping: semantic -> (raw_name, raw_value) if the platform reported it.
    sem_to_raw: dict[str, tuple[str, object]] = {}
    unmapped: list[str] = []
    for raw_name, raw_value in raw_metrics.items():
        sem = raw_to_sem.get(raw_name)
        if sem is None:
            unmapped.append(raw_name)
            continue
        sem_to_raw[sem] = (raw_name, raw_value)

    normalized: dict[str, dict] = {}
    for sem in SEMANTICS:
        if sem in sem_to_raw:
            raw_name, raw_value = sem_to_raw[sem]
            if isinstance(raw_value, (int, float)):
                mv = MetricValue(sem, PRESENT, float(raw_value), raw_name, float(raw_value))
            else:
                # Present key but non-numeric / null -> collected-but-unavailable.
                mv = MetricValue(sem, MISSING, None, raw_name, None)
        elif sem in supports:
            mv = MetricValue(sem, MISSING, None, None, None)
        else:
            mv = MetricValue(sem, NOT_SUPPORTED, None, None, None)
        normalized[sem] = asdict(mv)

    return NormalizedObservation(
        observation_id="obs-" + uuid.uuid4().hex[:16],
        platform=platform,
        source=source,
        account_alias=account_alias,
        persona=persona,
        content_id=content_id,
        experiment_id=experiment_id,
        window_start=window_start,
        window_end=window_end,
        collected_at=collected_at or now_iso(),
        normalization_version=NORMALIZATION_VERSION,
        raw_metrics=dict(raw_metrics),
        normalized=normalized,
        unmapped_raw=sorted(unmapped),
    )


# ------------------------------------------------------------------------- #
# Derived metrics — always record formula + version; MISSING if any input is.
# ------------------------------------------------------------------------- #
DERIVED_FORMULA_VERSION = "1.0.0"


@dataclass(frozen=True)
class DerivedMetric:
    name: str
    availability: str
    value: float | None
    formula: str
    formula_version: str
    inputs: dict

    def as_dict(self) -> dict:
        return asdict(self)


def _ratio(obs: NormalizedObservation, name: str, num_sem: str, den_sem: str,
           formula: str) -> DerivedMetric:
    num = obs.metric(num_sem)
    den = obs.metric(den_sem)
    inputs = {num_sem: num.value, den_sem: den.value}
    if num.is_missing() or den.is_missing() or den.value in (None, 0):
        avail = MISSING
        value = None
    else:
        avail = PRESENT
        value = num.value / den.value
    return DerivedMetric(name, avail, value, formula, DERIVED_FORMULA_VERSION, inputs)


def completion_rate(obs: NormalizedObservation) -> DerivedMetric:
    return _ratio(obs, "completion_rate", COMPLETION, VIEW, "completion / view")


def save_rate(obs: NormalizedObservation) -> DerivedMetric:
    return _ratio(obs, "save_rate", SAVE, REACH, "save / reach")


def click_through_rate(obs: NormalizedObservation) -> DerivedMetric:
    return _ratio(obs, "click_through_rate", CLICK, REACH, "click / reach")


DERIVED = {
    "completion_rate": completion_rate,
    "save_rate": save_rate,
    "click_through_rate": click_through_rate,
}


def derive_all(obs: NormalizedObservation) -> dict[str, dict]:
    return {name: fn(obs).as_dict() for name, fn in DERIVED.items()}


# ------------------------------------------------------------------------- #
# Staleness — an observation window is stale when its end is older than horizon.
# ------------------------------------------------------------------------- #
def observation_age_seconds(obs: NormalizedObservation,
                            now: datetime | None = None) -> float | None:
    end = _parse_iso(obs.window_end) or _parse_iso(obs.collected_at)
    if end is None:
        return None
    now = now or datetime.now(timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return (now - end).total_seconds()


def is_stale(obs: NormalizedObservation, *, max_age_hours: float,
             now: datetime | None = None) -> bool:
    age = observation_age_seconds(obs, now)
    if age is None:
        return True  # cannot establish freshness -> treat as stale, never fresh
    return age > max_age_hours * 3600.0


# ------------------------------------------------------------------------- #
# Persistence + trace + honest aggregation.
# ------------------------------------------------------------------------- #
def _store(bot: str) -> Path:
    return paths.analytics_dir(bot) / "normalized_metrics.jsonl"


def record(bot: str, obs: NormalizedObservation) -> None:
    append_jsonl(_store(bot), obs.as_dict())


def observations_for(bot: str) -> list[dict]:
    return read_jsonl(_store(bot))


def trace_content(bot: str, content_id: str) -> dict:
    """Trace one content item from raw metrics up to persona/experiment."""
    obs = [o for o in observations_for(bot) if o.get("content_id") == content_id]
    personas = sorted({o.get("persona") for o in obs if o.get("persona")})
    experiments = sorted({o.get("experiment_id") for o in obs if o.get("experiment_id")})
    return {
        "bot": bot,
        "content_id": content_id,
        "personas": personas,
        "experiments": experiments,
        "observation_count": len(obs),
        "observations": obs,
    }


def aggregate_semantic(bot: str, semantic: str) -> dict:
    """Sum a semantic metric, grouped BY platform — never blended across them.

    Missing/not-supported values are excluded from the sum (not counted as 0)
    and reported separately so the caller can see coverage honestly.
    """
    by_platform: dict[str, dict] = {}
    for o in observations_for(bot):
        plat = o.get("platform")
        mv = o.get("normalized", {}).get(semantic)
        if mv is None:
            continue
        bucket = by_platform.setdefault(
            plat, {"sum": 0.0, "present": 0, "missing": 0, "not_supported": 0})
        avail = mv.get("availability")
        if avail == PRESENT and isinstance(mv.get("value"), (int, float)):
            bucket["sum"] += mv["value"]
            bucket["present"] += 1
        elif avail == NOT_SUPPORTED:
            bucket["not_supported"] += 1
        else:
            bucket["missing"] += 1
    return {
        "bot": bot,
        "semantic": semantic,
        "by_platform": by_platform,
        "note": "grouped per platform; missing excluded from sum (not treated as 0)",
    }
