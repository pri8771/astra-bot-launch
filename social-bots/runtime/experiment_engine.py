"""Autonomous experiment lifecycle engine (SB-V15-001).

Design -> register -> run/observe -> close/learn, for bounded experiments.

Honesty rules
-------------
- An experiment cannot close before its required observation window elapses,
  unless a stop/safety criterion fires.
- **Baseline and treatment bind to normalized metric OBSERVATIONS** (SB-V13-001
  `NormalizedObservation` ids), not to loose numbers. The engine reads the value
  from the observation; a caller cannot hand it an unattributed figure.
- **Semantic + kind + window compatibility is validated** before an effect is
  computed. Comparing a snapshot to a delta, two different semantics, or two
  incomparable windows yields INCONCLUSIVE, never a fabricated effect.
- **Missing primary-metric data => INCONCLUSIVE, never SUCCESS.** A missing
  metric is not treated as zero effect.
- Duplicate / overlapping experiments (same target + intervention + primary
  metric, overlapping time) are detected.
- A closed experiment feeds audience/strategy only through explicit evidence
  refs that trace to the baseline/treatment measurement observation ids, and
  only when it produced a real (non-inconclusive) effect.

This module is additive; the accepted `pipeline.Experiment` registry is left
unchanged. Experiments here persist under an `engine/` subnamespace.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone

from . import paths
from .jsonstore import write_json, read_json, append_jsonl, read_jsonl, now_iso

# Status = where the experiment is in its lifecycle.
DRAFT = "draft"
RUNNING = "running"
CLOSED = "closed"

# Outcome = what the closed experiment concluded (distinct from status).
SUCCESS = "SUCCESS"
FAILURE = "FAILURE"
INCONCLUSIVE = "INCONCLUSIVE"
STOPPED_SAFETY = "STOPPED_SAFETY"


def _parse(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


# Window durations are comparable when their ratio stays within this tolerance.
_WINDOW_RATIO_TOLERANCE = 2.0


@dataclass(frozen=True)
class MeasurementRef:
    """A binding to one normalized metric observation (SB-V13-001).

    The value is read FROM the observation; ``observation_id`` is what makes the
    measurement attributable and traceable back to captured metrics.
    """
    observation_id: str
    semantic: str
    metric_kind: str | None
    value: float | None
    present: bool
    window_start: str | None
    window_end: str | None
    source: str | None

    def as_dict(self) -> dict:
        return asdict(self)


def measurement_from_observation(obs, semantic: str) -> MeasurementRef:
    """Build a MeasurementRef for ``semantic`` from a NormalizedObservation.

    Reads availability/value/kind/window from the observation itself — the
    caller cannot inject an unattributed number.
    """
    mv = obs.metric(semantic)
    return MeasurementRef(
        observation_id=obs.observation_id,
        semantic=semantic,
        metric_kind=mv.metric_kind,
        value=mv.value if not mv.is_missing() else None,
        present=not mv.is_missing(),
        window_start=obs.window_start,
        window_end=obs.window_end,
        source=obs.source,
    )


def _window_seconds(ref: MeasurementRef) -> float | None:
    if not ref.window_start or not ref.window_end:
        return None
    try:
        return (_parse(ref.window_end) - _parse(ref.window_start)).total_seconds()
    except ValueError:
        return None


def compatibility(baseline: MeasurementRef,
                  treatment: MeasurementRef) -> tuple[bool, str]:
    """Validate semantic + kind + window compatibility of two measurements."""
    if not baseline.present or not treatment.present:
        return False, "primary metric missing in baseline and/or treatment"
    if baseline.semantic != treatment.semantic:
        return False, (f"semantic mismatch: baseline={baseline.semantic} "
                       f"treatment={treatment.semantic}")
    if baseline.metric_kind != treatment.metric_kind:
        return False, (f"metric kind mismatch: baseline={baseline.metric_kind} "
                       f"treatment={treatment.metric_kind}")
    b_win, t_win = _window_seconds(baseline), _window_seconds(treatment)
    if b_win is None or t_win is None:
        return False, "baseline/treatment observation windows are not comparable"
    if b_win <= 0 or t_win <= 0:
        return False, "non-positive observation window"
    ratio = max(b_win, t_win) / min(b_win, t_win)
    if ratio > _WINDOW_RATIO_TOLERANCE:
        return False, (f"observation windows differ too much (ratio {ratio:.2f} "
                       f"> {_WINDOW_RATIO_TOLERANCE})")
    return True, "compatible"


@dataclass
class Experiment:
    id: str
    bot: str
    persona: str
    hypothesis: str
    baseline: dict                 # MeasurementRef dict bound to an observation
    intervention: str
    primary_metric: str            # semantic metric name (SB-V13-001)
    min_observation_hours: float
    stop_criteria: dict            # {min_effect, direction, safety, ...}
    status: str = DRAFT
    started_at: str | None = None
    closed_at: str | None = None
    outcome: str | None = None
    result: dict | None = None
    learning_refs: list = field(default_factory=list)
    created_at: str = field(default_factory=now_iso)

    def baseline_ref(self) -> MeasurementRef:
        return MeasurementRef(**self.baseline)

    def as_dict(self) -> dict:
        return asdict(self)


def design(bot: str, persona: str, *, hypothesis: str, baseline_observation,
           intervention: str, primary_metric: str, min_observation_hours: float,
           stop_criteria: dict | None = None) -> Experiment:
    """Design an experiment whose baseline binds to a normalized observation.

    ``baseline_observation`` is a SB-V13-001 ``NormalizedObservation``; the
    baseline for ``primary_metric`` must be PRESENT in it (a real measurement),
    otherwise the experiment cannot have a meaningful baseline.
    """
    base_ref = measurement_from_observation(baseline_observation, primary_metric)
    if not base_ref.present:
        raise ValueError(
            f"baseline observation has no PRESENT '{primary_metric}' measurement")
    return Experiment(
        id="exp-" + uuid.uuid4().hex[:12], bot=bot, persona=persona,
        hypothesis=hypothesis, baseline=base_ref.as_dict(), intervention=intervention,
        primary_metric=primary_metric, min_observation_hours=float(min_observation_hours),
        stop_criteria=dict(stop_criteria or {}))


def start(exp: Experiment, *, now: datetime | None = None) -> Experiment:
    if exp.status != DRAFT:
        raise ValueError(f"cannot start experiment in status {exp.status}")
    exp.status = RUNNING
    exp.started_at = (now or datetime.now(timezone.utc)).isoformat()
    return exp


def window_elapsed(exp: Experiment, *, now: datetime | None = None) -> bool:
    if not exp.started_at:
        return False
    now = now or datetime.now(timezone.utc)
    end = _parse(exp.started_at) + timedelta(hours=exp.min_observation_hours)
    return now >= end


def can_close(exp: Experiment, *, now: datetime | None = None,
              safety_triggered: bool = False) -> bool:
    """Closeable only after the observation window, unless a stop criterion fires."""
    if exp.status != RUNNING:
        return False
    return safety_triggered or window_elapsed(exp, now=now)


def _evaluate(exp: Experiment, treatment: MeasurementRef) -> tuple[str, dict]:
    metric = exp.primary_metric
    base_ref = exp.baseline_ref()
    ok, reason = compatibility(base_ref, treatment)
    if not ok:
        return INCONCLUSIVE, {
            "reason": reason,
            "primary_metric": metric,
            "baseline_observation_id": base_ref.observation_id,
            "treatment_observation_id": treatment.observation_id,
            "baseline": base_ref.value,
            "treatment": treatment.value,
        }
    base = float(base_ref.value)
    treat = float(treatment.value)
    effect = treat - base
    rel = (effect / base) if base != 0 else None
    direction = exp.stop_criteria.get("direction", "increase")
    min_effect = float(exp.stop_criteria.get("min_effect", 0.0))
    improved = effect >= min_effect if direction == "increase" else -effect >= min_effect
    outcome = SUCCESS if improved else FAILURE
    return outcome, {
        "primary_metric": metric, "baseline": base, "treatment": treat,
        "effect_size": effect, "relative_effect": rel,
        "direction": direction, "min_effect": min_effect,
        "metric_kind": base_ref.metric_kind,
        "baseline_observation_id": base_ref.observation_id,
        "treatment_observation_id": treatment.observation_id,
    }


def close(exp: Experiment, treatment_observation, *, now: datetime | None = None,
          safety_triggered: bool = False, safety_reason: str = "") -> Experiment:
    """Close the experiment, computing an honest outcome.

    ``treatment_observation`` is a SB-V13-001 ``NormalizedObservation``; the
    treatment value is read from it and bound by observation id. Refuses to close
    before the observation window unless a safety stop fired.
    """
    if not can_close(exp, now=now, safety_triggered=safety_triggered):
        raise ValueError("cannot close before required observation window "
                         "(no stop criterion triggered)")
    now = now or datetime.now(timezone.utc)
    treat_ref = measurement_from_observation(treatment_observation, exp.primary_metric)
    exp.status = CLOSED
    exp.closed_at = now.isoformat()

    if safety_triggered:
        exp.outcome = STOPPED_SAFETY
        exp.result = {"reason": safety_reason or "safety/stop criterion triggered",
                      "treatment_observation_id": treat_ref.observation_id,
                      "treatment_seen": treat_ref.value}
    else:
        exp.outcome, exp.result = _evaluate(exp, treat_ref)
    return exp


def to_learning_ref(exp: Experiment) -> dict | None:
    """Evidence ref for feeding audience/strategy — only for a real effect.

    INCONCLUSIVE / STOPPED_SAFETY produce NO learning ref (no fake learning).
    The ref points back to this experiment's id and result, never a raw number
    lifted out of context.
    """
    if exp.status != CLOSED or exp.outcome not in (SUCCESS, FAILURE):
        return None
    result = exp.result or {}
    ref = {
        "experiment_id": exp.id, "bot": exp.bot, "persona": exp.persona,
        "primary_metric": exp.primary_metric, "outcome": exp.outcome,
        "effect_size": result.get("effect_size"),
        # Trace the learning back to the exact measurement observations.
        "baseline_observation_id": result.get("baseline_observation_id"),
        "treatment_observation_id": result.get("treatment_observation_id"),
        "closed_at": exp.closed_at,
    }
    exp.learning_refs.append(ref)
    return ref


# --------------------------------------------------------------------------- #
# Duplicate / overlap detection.
# --------------------------------------------------------------------------- #
def overlaps(exp: Experiment, other: dict) -> bool:
    """Same target + intervention + primary metric while the other is active."""
    return (
        other.get("bot") == exp.bot
        and other.get("persona") == exp.persona
        and other.get("primary_metric") == exp.primary_metric
        and other.get("intervention") == exp.intervention
        and other.get("status") in (DRAFT, RUNNING)
        and other.get("id") != exp.id
    )


def find_overlaps(bot: str, exp: Experiment) -> list[dict]:
    return [o for o in load_all(bot) if overlaps(exp, o)]


# --------------------------------------------------------------------------- #
# Persistence (engine subnamespace; does not touch pipeline's registry).
# --------------------------------------------------------------------------- #
def _dir(bot: str):
    d = paths.experiments_dir(bot) / "engine"
    d.mkdir(parents=True, exist_ok=True)
    return d


def register(bot: str, exp: Experiment, *, reject_overlap: bool = True) -> Experiment:
    """Persist an experiment; refuse a duplicate overlapping one by default."""
    dups = find_overlaps(bot, exp)
    if dups and reject_overlap:
        raise ValueError(
            f"overlapping active experiment(s) detected: {[d['id'] for d in dups]}")
    save(bot, exp)
    append_jsonl(_dir(bot) / "index.jsonl", {
        "id": exp.id, "persona": exp.persona, "primary_metric": exp.primary_metric,
        "intervention": exp.intervention, "status": exp.status,
        "registered_at": now_iso()})
    return exp


def save(bot: str, exp: Experiment) -> None:
    write_json(_dir(bot) / f"{exp.id}.json", exp.as_dict())


def load(bot: str, exp_id: str) -> Experiment | None:
    data = read_json(_dir(bot) / f"{exp_id}.json")
    return Experiment(**data) if data else None


def load_all(bot: str) -> list[dict]:
    d = _dir(bot)
    return [read_json(p) for p in sorted(d.glob("exp-*.json")) if read_json(p)]
