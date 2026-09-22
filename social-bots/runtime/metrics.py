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

import math
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from . import paths
from .jsonstore import append_jsonl, read_jsonl, now_iso

NORMALIZATION_VERSION = "1.1.2"


def _finite_number(value: object) -> float | None:
    """A collected number must be representable, finite, and not a boolean."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        number = float(value)
    except (OverflowError, ValueError):
        return None
    return number if math.isfinite(number) else None

# ------------------------------------------------------------------------- #
# Metric semantic kinds (SB-V13-001 repair). Every normalized/derived metric
# declares exactly one. The kind decides how a metric may be aggregated:
#
# - cumulative_snapshot: a running total-to-date. NEVER naively summed over
#   time; the latest snapshot in a series is authoritative.
# - delta: a change within an observation window. Additive across windows.
# - gauge: a point-in-time level (e.g. follower count). Not summed; averaged.
# - rate: a ratio/derived rate. Not summed; averaged.
# ------------------------------------------------------------------------- #
CUMULATIVE_SNAPSHOT = "cumulative_snapshot"
DELTA = "delta"
GAUGE = "gauge"
RATE = "rate"
METRIC_KINDS = (CUMULATIVE_SNAPSHOT, DELTA, GAUGE, RATE)

# The safe default for a mapped count with no explicit kind: a snapshot is never
# naively summed, so defaulting here fails closed against false aggregation.
DEFAULT_METRIC_KIND = CUMULATIVE_SNAPSHOT

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
        # Lifetime content counts are cumulative-to-date snapshots; "follows"
        # reported for an analytics window is the count of new follows (a delta).
        "kinds": {
            "impressions": CUMULATIVE_SNAPSHOT,
            "video_views": CUMULATIVE_SNAPSHOT,
            "replies": CUMULATIVE_SNAPSHOT,
            "retweets": CUMULATIVE_SNAPSHOT,
            "url_link_clicks": CUMULATIVE_SNAPSHOT,
            "follows": DELTA,
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
        "kinds": {
            "reach": CUMULATIVE_SNAPSHOT,
            "plays": CUMULATIVE_SNAPSHOT,
            "video_completions": CUMULATIVE_SNAPSHOT,
            "saved": CUMULATIVE_SNAPSHOT,
            "shares": CUMULATIVE_SNAPSHOT,
            "comments": CUMULATIVE_SNAPSHOT,
            "follows": DELTA,
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
        "kinds": {
            "video_views": CUMULATIVE_SNAPSHOT,
            "completion_views": CUMULATIVE_SNAPSHOT,
            "favourites": CUMULATIVE_SNAPSHOT,
            "shares": CUMULATIVE_SNAPSHOT,
            "comments": CUMULATIVE_SNAPSHOT,
            "new_followers": DELTA,
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
        "kinds": {
            "crossposts": CUMULATIVE_SNAPSHOT,
            "num_comments": CUMULATIVE_SNAPSHOT,
            "outbound_clicks": CUMULATIVE_SNAPSHOT,
            "saves": CUMULATIVE_SNAPSHOT,
        },
    },
}


@dataclass(frozen=True)
class MetricValue:
    """A single semantic metric with an explicit availability state and an
    explicit semantic kind (cumulative_snapshot / delta / gauge / rate)."""
    semantic: str
    availability: str
    value: float | None
    raw_name: str | None
    raw_value: float | None
    metric_kind: str | None = None

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
        d = dict(self.normalized[semantic])
        d.setdefault("metric_kind", None)
        return MetricValue(**d)

    def as_dict(self) -> dict:
        return asdict(self)


def _parse_iso(ts: object) -> datetime | None:
    if not isinstance(ts, str) or not ts.strip():
        return None
    try:
        parsed = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _metadata_error(o: dict) -> str | None:
    """Validate attributable source and any supplied observation time boundaries."""
    source = o.get("source")
    if not isinstance(source, str) or not source.strip():
        return "invalid_source"
    if _parse_iso(o.get("collected_at")) is None:
        return "invalid_collected_at"
    for field in ("window_start", "window_end"):
        if o.get(field) is not None and _parse_iso(o[field]) is None:
            return f"invalid_{field}"
    start, end = _parse_iso(o.get("window_start")), _parse_iso(o.get("window_end"))
    if start is not None and end is not None and start >= end:
        return "invalid_window_order"
    return None


def _observation_error(o: dict) -> str | None:
    """Recheck persisted normalized claims before treating them as evidence."""
    error = _metadata_error(o)
    if error:
        return error
    normalized = o.get("normalized")
    if not isinstance(normalized, dict):
        return "invalid_normalized_metrics"
    platform = o.get("platform")
    pmap = PLATFORM_MAP.get(platform) if isinstance(platform, str) else None
    mapping = pmap["raw_to_semantic"] if pmap else {}
    for semantic, metric in normalized.items():
        if not isinstance(metric, dict):
            return "invalid_normalized_metrics"
        if metric.get("availability") != PRESENT:
            continue
        if metric.get("metric_kind") not in METRIC_KINDS:
            return "invalid_metric_kind"
        raw_name = metric.get("raw_name")
        if (not isinstance(raw_name, str) or mapping.get(raw_name) != semantic
                or metric.get("semantic") != semantic):
            return "invalid_metric_mapping"
    return None


def _kind_for(pmap: dict | None, raw_name: str,
              raw_kinds: dict | None) -> str:
    """Resolve the semantic kind for a mapped raw metric.

    Priority: explicit per-call override (``raw_kinds``) > platform declaration
    > safe default (cumulative_snapshot). An invalid kind is rejected.
    """
    kind = None
    if raw_kinds and raw_name in raw_kinds:
        kind = raw_kinds[raw_name]
    elif pmap:
        kind = pmap.get("kinds", {}).get(raw_name)
    kind = kind or DEFAULT_METRIC_KIND
    if kind not in METRIC_KINDS:
        raise ValueError(f"invalid metric_kind {kind!r} for raw metric {raw_name!r}")
    return kind


def _expected_semantic_kinds(pmap: dict | None, raw_kinds: dict | None) -> dict:
    """Map each semantic the platform *supports* to its expected metric kind.

    Used so a supported-but-MISSING metric still records the kind the platform
    would report (LEAD-018 Next 3). Semantics with no known raw mapping stay
    absent (their kind is genuinely unknown).
    """
    if not pmap:
        return {}
    out: dict[str, str] = {}
    for raw_name, sem in pmap.get("raw_to_semantic", {}).items():
        out[sem] = _kind_for(pmap, raw_name, raw_kinds)
    return out


def normalize(*, platform: str, raw_metrics: dict, source: str,
              account_alias: str | None = None, persona: str | None = None,
              content_id: str | None = None, experiment_id: str | None = None,
              window_start: str | None = None, window_end: str | None = None,
              collected_at: str | None = None,
              raw_kinds: dict | None = None) -> NormalizedObservation:
    """Normalize a platform's raw metric payload into semantic categories.

    Retains the full raw payload. A raw metric present with any numeric value
    (including 0) is PRESENT. A supported semantic with no raw metric is MISSING.
    A semantic the platform has no equivalent for is NOT_SUPPORTED. Nothing is
    coerced to 0. Every PRESENT metric declares a semantic kind
    (cumulative_snapshot / delta / gauge / rate); ``raw_kinds`` overrides the
    platform's declared kind per raw metric.
    """
    collected_at = now_iso() if collected_at is None else collected_at
    error = _metadata_error({"source": source, "collected_at": collected_at,
                             "window_start": window_start, "window_end": window_end})
    if error:
        raise ValueError(error)
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

    expected_kinds = _expected_semantic_kinds(pmap, raw_kinds)

    normalized: dict[str, dict] = {}
    for sem in SEMANTICS:
        if sem in sem_to_raw:
            raw_name, raw_value = sem_to_raw[sem]
            number = _finite_number(raw_value)
            if number is not None:
                kind = _kind_for(pmap, raw_name, raw_kinds)
                mv = MetricValue(sem, PRESENT, number, raw_name,
                                 number, metric_kind=kind)
            else:
                # Present key but non-numeric / null -> collected-but-unavailable.
                # Keep the expected kind: the platform knows what this metric IS.
                mv = MetricValue(sem, MISSING, None, raw_name, None,
                                 metric_kind=expected_kinds.get(sem))
        elif sem in supports:
            # Supported but not reported: MISSING, but its expected kind is known.
            mv = MetricValue(sem, MISSING, None, None, None,
                             metric_kind=expected_kinds.get(sem))
        else:
            mv = MetricValue(sem, NOT_SUPPORTED, None, None, None, metric_kind=None)
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
        collected_at=collected_at,
        normalization_version=NORMALIZATION_VERSION,
        raw_metrics=dict(raw_metrics),
        normalized=normalized,
        unmapped_raw=sorted(unmapped),
    )


# ------------------------------------------------------------------------- #
# Derived metrics — always record formula + version; MISSING if any input is.
# ------------------------------------------------------------------------- #
DERIVED_FORMULA_VERSION = "1.0.1"


@dataclass(frozen=True)
class DerivedMetric:
    name: str
    availability: str
    value: float | None
    formula: str
    formula_version: str
    inputs: dict
    metric_kind: str = RATE
    derivation: dict | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def _ratio(obs: NormalizedObservation, name: str, num_sem: str, den_sem: str,
           formula: str) -> DerivedMetric:
    num = obs.metric(num_sem)
    den = obs.metric(den_sem)
    inputs = {num_sem: num.value, den_sem: den.value}
    error = _observation_error(obs.as_dict())
    if error:
        return DerivedMetric(name, MISSING, None, formula, DERIVED_FORMULA_VERSION,
                             inputs, metric_kind=RATE,
                             derivation={"ok": False, "reason": error})
    numerator, denominator = _finite_number(num.value), _finite_number(den.value)
    if num.is_missing() or den.is_missing() or numerator is None or denominator in (None, 0):
        avail = MISSING
        value = None
    else:
        value = _finite_number(numerator / denominator)
        avail = PRESENT if value is not None else MISSING
    return DerivedMetric(name, avail, value, formula, DERIVED_FORMULA_VERSION,
                         inputs, metric_kind=RATE)


# ------------------------------------------------------------------------- #
# Snapshot -> delta derivation (SB-V13-001 acceptance).
#
# A cumulative snapshot may be converted to a delta ONLY with a valid earlier
# comparable snapshot, and the derivation is recorded explicitly.
# ------------------------------------------------------------------------- #
def _series_key(obs: NormalizedObservation) -> tuple:
    return (obs.platform, obs.account_alias, obs.persona, obs.content_id)


def derive_delta_from_snapshots(previous: NormalizedObservation,
                                current: NormalizedObservation,
                                semantic: str) -> DerivedMetric:
    """Derive a DELTA for ``semantic`` from two comparable cumulative snapshots.

    Requires: both observations PRESENT and kind ``cumulative_snapshot`` for the
    semantic, the SAME series (platform/account/persona/content), and the current
    window ending at or after the previous window. Otherwise returns a MISSING
    derived metric explaining why — never a fabricated delta.
    """
    prev = previous.metric(semantic)
    curr = current.metric(semantic)
    name = f"{semantic}_delta"
    inputs = {"previous": prev.value, "current": curr.value}

    def _missing(reason: str) -> DerivedMetric:
        return DerivedMetric(name, MISSING, None,
                             formula="current_snapshot - previous_snapshot",
                             formula_version=DERIVED_FORMULA_VERSION,
                             inputs=inputs, metric_kind=DELTA,
                             derivation={"ok": False, "reason": reason})

    error = _observation_error(previous.as_dict()) or _observation_error(current.as_dict())
    if error:
        return _missing(error)
    if prev.is_missing() or curr.is_missing():
        return _missing("a snapshot input is missing")
    previous_value, current_value = _finite_number(prev.value), _finite_number(curr.value)
    if previous_value is None or current_value is None:
        return _missing("a snapshot input is not a finite number")
    if prev.metric_kind != CUMULATIVE_SNAPSHOT or curr.metric_kind != CUMULATIVE_SNAPSHOT:
        return _missing("both inputs must be cumulative_snapshot")
    if _series_key(previous) != _series_key(current):
        return _missing("snapshots are not from the same comparable series")

    prev_end = _parse_iso(previous.window_end) or _parse_iso(previous.collected_at)
    curr_end = _parse_iso(current.window_end) or _parse_iso(current.collected_at)
    if prev_end is None or curr_end is None:
        return _missing("cannot establish snapshot ordering without windows")
    if curr_end < prev_end:
        return _missing("current snapshot precedes previous snapshot")
    if current_value < previous_value:
        # A cumulative counter that decreased indicates a reset/deletion; a naive
        # difference would be a misleading negative delta.
        return _missing("cumulative snapshot decreased; not a valid delta")

    delta = _finite_number(current_value - previous_value)
    if delta is None:
        return _missing("snapshot difference is not a finite number")

    derivation = {
        "ok": True,
        "previous_observation_id": previous.observation_id,
        "current_observation_id": current.observation_id,
        "series_key": list(_series_key(current)),
        "previous_window_end": previous.window_end,
        "current_window_end": current.window_end,
    }
    return DerivedMetric(name, PRESENT, delta,
                         formula="current_snapshot - previous_snapshot",
                         formula_version=DERIVED_FORMULA_VERSION,
                         inputs=inputs, metric_kind=DELTA, derivation=derivation)


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
    if _observation_error(obs.as_dict()):
        return None
    end = _parse_iso(obs.window_end) or _parse_iso(obs.collected_at)
    if end is None:
        return None
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        return None
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
    error = _observation_error(obs.as_dict())
    if error:
        raise ValueError(error)
    append_jsonl(_store(bot), obs.as_dict())


def observations_for(bot: str) -> list[dict]:
    return read_jsonl(_store(bot))


def trace_content(bot: str, content_id: str) -> dict:
    """Trace one content item from raw metrics up to persona/experiment."""
    rows = [o for o in observations_for(bot) if o.get("content_id") == content_id]
    excluded = [{"reason": error, "observation": o} for o in rows
                if (error := _observation_error(o))]
    obs = [o for o in rows if _observation_error(o) is None]
    personas = sorted({o.get("persona") for o in obs if o.get("persona")})
    experiments = sorted({o.get("experiment_id") for o in obs if o.get("experiment_id")})
    return {
        "bot": bot,
        "content_id": content_id,
        "personas": personas,
        "experiments": experiments,
        "observation_count": len(obs),
        "observations": obs,
        "excluded_observation_count": len(excluded),
        "excluded_observations": excluded,
    }


def _obs_time(o: dict) -> datetime:
    """Order validated observations by actual instants, not ISO text/UTC offset."""
    value = _parse_iso(o.get("window_end")) or _parse_iso(o.get("collected_at"))
    assert value is not None  # metadata was checked before entering aggregation
    return value


def _series_key_dict(o: dict) -> tuple:
    return (o.get("platform"), o.get("account_alias"), o.get("persona"),
            o.get("content_id"))


def _win(o: dict) -> tuple | None:
    """Parsed (start, end) window for an observation, or None if incomplete."""
    s, e = o.get("window_start"), o.get("window_end")
    if not s or not e:
        return None
    a, b = _parse_iso(s), _parse_iso(e)
    if a is None or b is None or a >= b:
        return None
    return (a, b)


def _window_overlaps_any(win: tuple, accepted: list[tuple]) -> bool:
    """True if ``win`` overlaps or duplicates any window already accepted."""
    s, e = win
    for (a, b) in accepted:
        # Half-open overlap; equal windows (duplicates) overlap too.
        if s < b and a < e:
            return True
        if s == a and e == b:
            return True
    return False


def aggregate_semantic(bot: str, semantic: str) -> dict:
    """Aggregate a semantic metric SEMANTIC-KIND-AWARE, grouped by platform.

    Aggregation depends on each metric's declared kind — the SB-V13-001 core
    fix so cumulative snapshots are never naively summed:

    - ``delta``:  additive across windows -> summed.
    - ``cumulative_snapshot``: NOT summed over time. Within a series
      (platform/account/persona/content) the latest snapshot is authoritative;
      the platform total is the sum of the latest-per-series snapshots.
    - ``gauge`` / ``rate``: not summed -> mean of the latest-per-series values.

    Missing / not-supported values are excluded (never counted as 0) and reported
    separately so coverage is visible.
    """
    # Collect PRESENT observations by platform then by kind.
    by_platform: dict[str, dict] = {}
    for o in observations_for(bot):
        plat = o.get("platform")
        bucket = by_platform.setdefault(plat, {
            "kinds": {}, "present": 0, "missing": 0, "not_supported": 0, "invalid": 0})
        if _observation_error(o):
            bucket["invalid"] += 1
            continue
        mv = o["normalized"].get(semantic)
        if mv is None:
            continue
        avail = mv.get("availability")
        number = _finite_number(mv.get("value"))
        if avail == PRESENT and number is not None:
            bucket["present"] += 1
            kind = mv.get("metric_kind") or DEFAULT_METRIC_KIND
            bucket["kinds"].setdefault(kind, []).append(
                {"value": number, "obs": o})
        elif avail == NOT_SUPPORTED:
            bucket["not_supported"] += 1
        else:
            bucket["missing"] += 1

    # Reduce each (platform, kind) group by its kind-appropriate rule.
    for plat, bucket in by_platform.items():
        reduced: dict[str, dict] = {}
        for kind, entries in bucket["kinds"].items():
            if kind == DELTA:
                # Deltas are additive ONLY across non-overlapping, non-duplicate
                # windows within a series. Overlapping/duplicate windows would
                # double-count, so they are excluded from the sum.
                per_series: dict[tuple, list] = {}
                for e in entries:
                    per_series.setdefault(_series_key_dict(e["obs"]), []).append(e)
                total = 0.0
                counted = 0
                excluded = 0
                for sk, es in per_series.items():
                    es_sorted = sorted(es, key=lambda e: _obs_time(e["obs"]))
                    accepted: list[tuple] = []
                    for e in es_sorted:
                        win = _win(e["obs"])
                        if win is None or _window_overlaps_any(win, accepted):
                            # No verifiable window, or overlaps/duplicates an
                            # already-counted window -> do not double-count.
                            excluded += 1
                            continue
                        accepted.append(win)
                        total += e["value"]
                        counted += 1
                reduced[kind] = {
                    "kind": kind, "aggregation": "sum_non_overlapping_deltas",
                    "value": total, "count": counted,
                    "excluded_overlapping": excluded,
                }
            else:
                # Snapshot / gauge / rate: reduce each series to its latest value.
                series: dict[tuple, dict] = {}
                for e in entries:
                    sk = _series_key_dict(e["obs"])
                    t = _obs_time(e["obs"])
                    if sk not in series or t >= series[sk]["t"]:
                        series[sk] = {"t": t, "value": e["value"]}
                latest_vals = [s["value"] for s in series.values()]
                if kind == CUMULATIVE_SNAPSHOT:
                    reduced[kind] = {
                        "kind": kind,
                        "aggregation": "latest_per_series_then_sum",
                        "value": sum(latest_vals),
                        "series_count": len(series),
                        "count": len(entries),
                        "note": "snapshots never summed over time; latest per series",
                    }
                else:  # GAUGE or RATE
                    mean = sum(latest_vals) / len(latest_vals) if latest_vals else None
                    reduced[kind] = {
                        "kind": kind, "aggregation": "mean_of_series_latest",
                        "value": mean, "series_count": len(series),
                        "count": len(entries),
                    }
        for result in reduced.values():
            if result["value"] is not None and _finite_number(result["value"]) is None:
                result["value"] = None
                result["unavailable_reason"] = "non_finite_result"
        bucket["kinds"] = reduced

    return {
        "bot": bot,
        "semantic": semantic,
        "by_platform": by_platform,
        "note": ("kind-aware: deltas summed; cumulative snapshots reduced to "
                 "latest-per-series then summed (never summed over time); "
                 "gauges/rates averaged; missing excluded (not treated as 0)"),
    }
