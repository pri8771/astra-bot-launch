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

Persona-scoped persistence (SB-V15-001 boundary repair)
-------------------------------------------------------
Persistence and reads are authoritatively **bot + persona** scoped. Each
persona's experiments live in a physically separate directory
(``engine/personas/<persona>/``), so a persona-facing ``save_experiment`` /
``load_experiment`` / ``list_experiments`` / ``register_experiment`` can only
ever touch that persona's own partition — a normal persona cannot enumerate or
read another persona's experiments. Cross-persona / whole-runtime access is
available ONLY through the explicitly named ``admin_*`` readers, which are for
operator/admin auditing and must not be exposed to a persona flow.

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


def find_overlaps_for_persona(bot: str, persona: str,
                              exp: Experiment) -> list[dict]:
    """Persona-scoped overlap detection: only THIS persona's experiments are
    considered, so a persona's overlap check never reads another persona's data.
    """
    _require_owner(bot, persona, exp)
    return [o for o in list_experiments(bot, persona) if overlaps(exp, o)]


def find_overlaps(bot: str, exp: Experiment) -> list[dict]:
    """Backwards-compatible overlap check, scoped to the experiment's own
    persona (derived from ``exp.persona``)."""
    return find_overlaps_for_persona(bot, exp.persona, exp)


# --------------------------------------------------------------------------- #
# Persistence — AUTHORITATIVELY bot + persona scoped (SB-V15-001).
#
# Every persona's experiments live in a physically separate directory
# (``engine/personas/<persona>/``). A persona-facing save/load/list/read requires
# BOTH ``bot`` and ``persona`` and can only ever touch that persona's directory,
# so a normal persona cannot enumerate or read another persona's experiments —
# the isolation is structural (separate path), not merely a filter. Persona
# identifiers are validated (``paths._check``) so a crafted persona string cannot
# traverse out of its partition. Cross-persona / whole-runtime reads are provided
# ONLY through the explicitly named ``admin_*`` readers below.
# --------------------------------------------------------------------------- #
def _engine_dir(bot: str):
    d = paths.experiments_dir(bot) / "engine"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_persona(persona: str) -> str:
    """Validate a persona identifier for use as a path component."""
    if not isinstance(persona, str):
        raise ValueError(f"persona must be a string, got {type(persona).__name__}")
    try:
        return paths._check(persona)
    except ValueError as exc:
        raise ValueError(f"unsafe persona identifier: {persona!r}") from exc


def _persona_dir(bot: str, persona: str):
    d = _engine_dir(bot) / "personas" / _safe_persona(persona)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _require_owner(bot: str, persona: str, exp: Experiment) -> None:
    """Refuse to save/register an experiment under a (bot, persona) it does not
    belong to — a persona cannot write into another persona's partition."""
    _safe_persona(persona)
    if exp.bot != bot or exp.persona != persona:
        raise PermissionError(
            f"experiment {exp.id} belongs to (bot={exp.bot!r}, "
            f"persona={exp.persona!r}), not (bot={bot!r}, persona={persona!r})")


# ----- persona-facing production APIs (require bot + persona) --------------- #
def save_experiment(bot: str, persona: str, exp: Experiment) -> None:
    """Persona-scoped write. Requires bot+persona and that the experiment
    actually belongs to them."""
    _require_owner(bot, persona, exp)
    write_json(_persona_dir(bot, persona) / f"{exp.id}.json", exp.as_dict())


def register_experiment(bot: str, persona: str, exp: Experiment, *,
                        reject_overlap: bool = True) -> Experiment:
    """Persona-scoped register: overlap detection and persistence stay inside
    this persona's partition."""
    _require_owner(bot, persona, exp)
    dups = find_overlaps_for_persona(bot, persona, exp)
    if dups and reject_overlap:
        raise ValueError(
            f"overlapping active experiment(s) detected: {[d['id'] for d in dups]}")
    save_experiment(bot, persona, exp)
    append_jsonl(_persona_dir(bot, persona) / "index.jsonl", {
        "id": exp.id, "persona": exp.persona, "primary_metric": exp.primary_metric,
        "intervention": exp.intervention, "status": exp.status,
        "registered_at": now_iso()})
    return exp


def load_experiment(bot: str, persona: str, exp_id: str) -> Experiment | None:
    """Persona-scoped read: returns the experiment ONLY if it belongs to this
    persona. Another persona's experiment id is not visible here (returns None) —
    the record lives in a different directory and is never reached."""
    data = read_json(_persona_dir(bot, persona) / f"{exp_id}.json")
    if not data:
        return None
    exp = Experiment(**data)
    # Defense in depth: never hand back a record whose stored owner differs.
    if exp.bot != bot or exp.persona != persona:
        return None
    return exp


def list_experiments(bot: str, persona: str) -> list[dict]:
    """Persona-scoped enumeration: ONLY this persona's experiments."""
    d = _persona_dir(bot, persona)
    out = []
    for p in sorted(d.glob("exp-*.json")):
        data = read_json(p)
        if data and data.get("bot") == bot and data.get("persona") == persona:
            out.append(data)
    return out


# ----- ADMIN / INTERNAL whole-runtime readers (NOT persona-facing) --------- #
def admin_load_all_experiments(bot: str) -> list[dict]:
    """ADMIN/INTERNAL whole-runtime reader: every persona's experiments for the
    bot, across all persona partitions (plus any legacy flat records).

    This deliberately crosses persona boundaries and MUST NOT be exposed to a
    normal persona flow — it exists for operator/admin auditing only. Persona
    code paths use :func:`list_experiments` / :func:`load_experiment` instead.
    """
    out: list[dict] = []
    personas_root = _engine_dir(bot) / "personas"
    if personas_root.exists():
        for pd in sorted(personas_root.iterdir()):
            if pd.is_dir():
                for p in sorted(pd.glob("exp-*.json")):
                    data = read_json(p)
                    if data:
                        out.append(data)
    # Legacy flat records written before persona partitioning (defensive).
    for p in sorted(_engine_dir(bot).glob("exp-*.json")):
        data = read_json(p)
        if data:
            out.append(data)
    return out


def admin_load_experiment(bot: str, exp_id: str) -> Experiment | None:
    """ADMIN/INTERNAL cross-persona lookup by id. NOT persona-facing."""
    for data in admin_load_all_experiments(bot):
        if data.get("id") == exp_id:
            return Experiment(**data)
    return None


# ----- backwards-compatible aliases (route to persona-scoped storage) ------ #
def save(bot: str, exp: Experiment) -> None:
    """Compat: persist using the experiment's own persona partition."""
    save_experiment(bot, exp.persona, exp)


def register(bot: str, exp: Experiment, *, reject_overlap: bool = True) -> Experiment:
    """Compat: register into the experiment's own persona partition."""
    return register_experiment(bot, exp.persona, exp, reject_overlap=reject_overlap)


def load(bot: str, exp_id: str) -> Experiment | None:
    """ADMIN/INTERNAL compat lookup by id across personas.

    Retained for existing callers/tests; it is a whole-runtime (cross-persona)
    read and is therefore NOT persona-facing. Persona code must use
    :func:`load_experiment` with an explicit persona.
    """
    return admin_load_experiment(bot, exp_id)


def load_all(bot: str) -> list[dict]:
    """ADMIN/INTERNAL alias for :func:`admin_load_all_experiments` (not
    persona-facing)."""
    return admin_load_all_experiments(bot)
