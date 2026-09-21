"""Autonomous experiment lifecycle engine (SB-V15-001).

Design -> register -> run/observe -> close/learn, for bounded experiments.

Honesty rules
-------------
- An experiment cannot close before its required observation window elapses,
  unless a stop/safety criterion fires.
- **Missing primary-metric data => INCONCLUSIVE, never SUCCESS.** A missing
  metric is not treated as zero effect.
- Duplicate / overlapping experiments (same target + intervention + primary
  metric, overlapping time) are detected.
- A closed experiment feeds audience/strategy only through explicit evidence
  refs, and only when it produced a real (non-inconclusive) effect.

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


@dataclass
class Experiment:
    id: str
    bot: str
    persona: str
    hypothesis: str
    baseline: dict                 # {metric: number|None} measured baseline
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

    def as_dict(self) -> dict:
        return asdict(self)


def design(bot: str, persona: str, *, hypothesis: str, baseline: dict,
           intervention: str, primary_metric: str, min_observation_hours: float,
           stop_criteria: dict | None = None) -> Experiment:
    return Experiment(
        id="exp-" + uuid.uuid4().hex[:12], bot=bot, persona=persona,
        hypothesis=hypothesis, baseline=dict(baseline), intervention=intervention,
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


def _metric_present(measurement: dict, metric: str) -> bool:
    """Present iff the key exists with a numeric value. Missing != zero."""
    return isinstance(measurement.get(metric), (int, float))


def _evaluate(exp: Experiment, treatment: dict) -> tuple[str, dict]:
    metric = exp.primary_metric
    if not _metric_present(exp.baseline, metric) or not _metric_present(treatment, metric):
        return INCONCLUSIVE, {
            "reason": "primary metric missing in baseline and/or treatment",
            "baseline": exp.baseline.get(metric),
            "treatment": treatment.get(metric),
            "primary_metric": metric,
        }
    base = float(exp.baseline[metric])
    treat = float(treatment[metric])
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
    }


def close(exp: Experiment, treatment: dict, *, now: datetime | None = None,
          safety_triggered: bool = False, safety_reason: str = "") -> Experiment:
    """Close the experiment, computing an honest outcome.

    Refuses to close before the observation window unless a safety stop fired.
    """
    if not can_close(exp, now=now, safety_triggered=safety_triggered):
        raise ValueError("cannot close before required observation window "
                         "(no stop criterion triggered)")
    now = now or datetime.now(timezone.utc)
    exp.status = CLOSED
    exp.closed_at = now.isoformat()

    if safety_triggered:
        exp.outcome = STOPPED_SAFETY
        exp.result = {"reason": safety_reason or "safety/stop criterion triggered",
                      "treatment_seen": treatment}
    else:
        exp.outcome, exp.result = _evaluate(exp, treatment)
    return exp


def to_learning_ref(exp: Experiment) -> dict | None:
    """Evidence ref for feeding audience/strategy — only for a real effect.

    INCONCLUSIVE / STOPPED_SAFETY produce NO learning ref (no fake learning).
    The ref points back to this experiment's id and result, never a raw number
    lifted out of context.
    """
    if exp.status != CLOSED or exp.outcome not in (SUCCESS, FAILURE):
        return None
    ref = {
        "experiment_id": exp.id, "bot": exp.bot, "persona": exp.persona,
        "primary_metric": exp.primary_metric, "outcome": exp.outcome,
        "effect_size": (exp.result or {}).get("effect_size"),
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
