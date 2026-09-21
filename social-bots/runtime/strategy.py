"""SB-S20-001 — versioned strategy-state store.

Implements ``STRATEGY_SCHEMA.md`` / ``V20_TO_V23_IMPLEMENTATION_SPEC.md`` §2.1:
immutable ``StrategyState`` versions per (bot, persona), an active-version
pointer, and an append-only history with content hashes.

Layout (persona-private, derived here — ``runtime/paths.py`` is not modified)::

    state/<bot>/strategy/<persona>/v0001.json     immutable version file
    state/<bot>/strategy/<persona>/HEAD.json      {"active_version": int|None, ...}
    state/<bot>/strategy/<persona>/HISTORY.jsonl  append-only events with sha256

Guarantees
----------
* A version file is never overwritten (``StrategyVersionExists``) and versions
  are contiguous (``StrategyVersionGap``): ``save_version`` only accepts
  ``latest_version + 1`` and a ``supersedes`` that already exists.
* Every save records the file's sha256 in HISTORY; ``history()`` re-hashes the
  files and flags ``tampered: True`` (or ``missing: True``) instead of silently
  repairing anything.
* Durable writes go through ``leasing.Fence.fenced_commit`` when a ``fence`` is
  supplied, so an obsolete owner writes nothing (``FenceLost``); with
  ``fence=None`` (unit tests, dry runs) the same writes run unguarded, exactly
  like ``decision._commit``.
* Weight maps are relative priorities (non-negative, finite, summing to 1.0 or
  empty), never spending authority. Evidence refs are dicts (``EvidenceRef`` or
  ``{"kind","id"}``), never bare numbers.
* Persona scope is structural: one persona's directory is never read for another;
  ``admin_all_strategies`` is the only cross-persona reader.

This slice stores and reads. It contains no proposal, policy, lifecycle or
rollback logic (SB-S20-003/004, SB-S21-*, SB-S20-006) and no runtime hook.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field, fields, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import paths
from .jsonstore import write_json, read_json, append_jsonl, read_jsonl, now_iso

SCHEMA_VERSION = 1

# Full lifecycle enum (SB-S21-001 owns the transitions). This slice itself only
# ever produces ACTIVE / SUPERSEDED / ROLLED_BACK but must store every status.
STATUSES = ("PROPOSED", "ACTIVE", "COOLING", "SUPERSEDED", "ROLLED_BACK", "EXPIRED")
PROVENANCES = ("fixture", "evidence")

HEAD_FILE = "HEAD.json"
HISTORY_FILE = "HISTORY.jsonl"
_WEIGHT_TOL = 1e-6

# Same shape as ``paths._SAFE`` (copied; the private name is not imported).
_SAFE_NS = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
_VERSION_FILE_RE = re.compile(r"^v(\d{4,})\.json$")

# Fields a derived version may change. Anything else is refused: no arbitrary
# dictionary merge into strategy state (STRATEGY_SCHEMA.md "Change operations").
MUTABLE_FIELDS = frozenset({
    "objective", "priority_audiences", "priority_topics", "platform_weights",
    "format_weights", "experiment_priorities", "active_hypotheses", "constraints",
    "evidence_refs", "confidence", "review_by", "expires_at",
})


class StrategyError(ValueError):
    """Invalid strategy state or refused store operation."""


class StrategyVersionExists(StrategyError):
    """A version file with this number already exists; versions are immutable."""


class StrategyVersionGap(StrategyError):
    """The version is not latest+1 or supersedes a version that does not exist."""


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_scope(bot: str, persona: str) -> None:
    """Refuse unsafe ids BEFORE any filesystem access (no stray mkdir)."""
    if not isinstance(bot, str) or bot not in paths.BOTS:
        raise StrategyError(f"bot must be one of {paths.BOTS}, got {bot!r}")
    if not isinstance(persona, str) or not _SAFE_NS.match(persona):
        raise StrategyError(f"unsafe persona id {persona!r}")


def strategy_id_for(bot: str, persona: str) -> str:
    return f"strat-{bot}-{persona}"


def strategy_dir(bot: str, persona: str, *, create: bool = False) -> Path:
    """Persona-private strategy directory (validates scope first).

    Reads never create it: a read for a persona that has no strategy must leave
    no trace, otherwise ``admin_all_strategies`` would list phantom personas.
    Only the write paths (``save_version``, ``set_active``) pass ``create=True``.
    """
    check_scope(bot, persona)
    d = paths.state_dir(bot) / "strategy" / persona
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


def version_path(bot: str, persona: str, version: int) -> Path:
    return strategy_dir(bot, persona) / f"v{int(version):04d}.json"


def _validate_weights(name: str, w: Any, errs: list[str]) -> None:
    if not isinstance(w, dict):
        errs.append(f"{name} must be a dict")
        return
    total = 0.0
    for k, v in w.items():
        if not isinstance(k, str) or not k:
            errs.append(f"{name} has a non-string/empty key")
            continue
        if not _is_number(v):
            errs.append(f"{name}[{k!r}] must be a finite number")
            continue
        if v < 0:
            errs.append(f"{name}[{k!r}] must not be negative")
        total += float(v)
    if w and abs(total - 1.0) > _WEIGHT_TOL:
        errs.append(f"{name} must sum to 1.0 (got {total:.6f})")


def _validate_refs(refs: Any, errs: list[str]) -> None:
    if not isinstance(refs, list):
        errs.append("evidence_refs must be a list")
        return
    for i, r in enumerate(refs):
        if not isinstance(r, dict):
            errs.append(f"evidence_refs[{i}] must be a dict (EvidenceRef or {{kind,id}}), "
                        f"not {type(r).__name__}")
            continue
        has_evidence_id = isinstance(r.get("evidence_id"), str) and r["evidence_id"]
        has_kind_id = (isinstance(r.get("kind"), str) and r["kind"]
                       and isinstance(r.get("id"), str) and r["id"])
        if not (has_evidence_id or has_kind_id):
            errs.append(f"evidence_refs[{i}] needs 'evidence_id' or 'kind'+'id'")


def _str_list(name: str, v: Any, errs: list[str]) -> None:
    if not isinstance(v, list) or not all(isinstance(x, str) and x for x in v):
        errs.append(f"{name} must be a list of non-empty str")


# --------------------------------------------------------------------------- #
# StrategyState
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class StrategyState:
    strategy_id: str
    version: int
    bot: str
    persona: str
    objective: str
    created_at: str
    priority_audiences: list = field(default_factory=list)
    priority_topics: list = field(default_factory=list)
    platform_weights: dict = field(default_factory=dict)
    format_weights: dict = field(default_factory=dict)
    experiment_priorities: list = field(default_factory=list)
    active_hypotheses: list = field(default_factory=list)
    constraints: list = field(default_factory=list)
    evidence_refs: list = field(default_factory=list)
    supersedes: int | None = None
    status: str = "ACTIVE"
    confidence: float | None = None
    review_by: str | None = None
    expires_at: str | None = None
    revision: dict | None = None
    provenance: str = "fixture"
    schema_version: int = SCHEMA_VERSION

    def as_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "StrategyState":
        """Strict reload: unknown/missing keys or invalid content are errors."""
        if not isinstance(data, dict):
            raise StrategyError("strategy data must be a dict")
        expected = {f.name for f in fields(cls)}
        unknown = sorted(set(data) - expected)
        missing = sorted(expected - set(data))
        if unknown:
            raise StrategyError(f"unknown strategy keys: {unknown}")
        if missing:
            raise StrategyError(f"missing strategy keys: {missing}")
        s = cls(**data)
        errs = validate_state(s)
        if errs:
            raise StrategyError("; ".join(errs))
        return s


def validate_state(s: Any) -> list[str]:
    if not isinstance(s, StrategyState):
        return [f"not a StrategyState: {type(s).__name__}"]
    errs: list[str] = []
    if s.schema_version != SCHEMA_VERSION:
        errs.append(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(s.bot, str) or s.bot not in paths.BOTS:
        errs.append(f"bot must be one of {paths.BOTS}")
    if not isinstance(s.persona, str) or not _SAFE_NS.match(s.persona):
        errs.append("persona is not a safe namespace id")
    if not errs and s.strategy_id != strategy_id_for(s.bot, s.persona):
        errs.append("strategy_id must equal strategy_id_for(bot, persona)")
    if not isinstance(s.version, int) or isinstance(s.version, bool) or s.version < 1:
        errs.append("version must be an int >= 1")
    if not isinstance(s.objective, str) or not s.objective.strip():
        errs.append("objective is required")
    if _parse_iso(s.created_at) is None:
        errs.append("created_at is not an ISO-8601 timestamp")
    _str_list("priority_audiences", s.priority_audiences, errs)
    _str_list("priority_topics", s.priority_topics, errs)
    _str_list("experiment_priorities", s.experiment_priorities, errs)
    _str_list("active_hypotheses", s.active_hypotheses, errs)
    _str_list("constraints", s.constraints, errs)
    _validate_weights("platform_weights", s.platform_weights, errs)
    _validate_weights("format_weights", s.format_weights, errs)
    _validate_refs(s.evidence_refs, errs)
    if s.supersedes is not None:
        if (not isinstance(s.supersedes, int) or isinstance(s.supersedes, bool)
                or s.supersedes < 1 or (isinstance(s.version, int) and s.supersedes >= s.version)):
            errs.append("supersedes must be an existing lower version number or None")
    elif isinstance(s.version, int) and s.version > 1:
        errs.append("a version above 1 must name the version it supersedes")
    if s.status not in STATUSES:
        errs.append(f"status must be one of {STATUSES}")
    if s.confidence is not None and not (_is_number(s.confidence) and 0.0 <= s.confidence <= 1.0):
        errs.append("confidence must be None or a number in [0, 1]")
    for name in ("review_by", "expires_at"):
        v = getattr(s, name)
        if v is not None and _parse_iso(v) is None:
            errs.append(f"{name} must be None or an ISO-8601 timestamp")
    if s.revision is not None and not isinstance(s.revision, dict):
        errs.append("revision must be None or a dict")
    if s.provenance not in PROVENANCES:
        errs.append(f"provenance must be one of {PROVENANCES}")
    return errs


def new_initial(bot: str, persona: str, objective: str, *, platform_weights=None,
                format_weights=None, priority_audiences=(), priority_topics=(),
                experiment_priorities=(), active_hypotheses=(), constraints=(),
                evidence_refs=(), status: str = "ACTIVE", confidence=None,
                review_by=None, expires_at=None, provenance: str = "fixture") -> StrategyState:
    """Build (not persist) version 1 for a persona. Raises on invalid input."""
    check_scope(bot, persona)
    s = StrategyState(
        strategy_id=strategy_id_for(bot, persona), version=1, bot=bot, persona=persona,
        objective=objective, created_at=now_iso(),
        priority_audiences=list(priority_audiences), priority_topics=list(priority_topics),
        platform_weights=dict(platform_weights or {}), format_weights=dict(format_weights or {}),
        experiment_priorities=list(experiment_priorities),
        active_hypotheses=list(active_hypotheses), constraints=list(constraints),
        evidence_refs=[dict(r) if isinstance(r, dict) else r for r in evidence_refs],
        supersedes=None, status=status, confidence=confidence, review_by=review_by,
        expires_at=expires_at, revision=None, provenance=provenance)
    errs = validate_state(s)
    if errs:
        raise StrategyError("; ".join(errs))
    return s


def next_version(current: StrategyState, *, status: str = "ACTIVE", revision: dict | None = None,
                 provenance: str | None = None, **changes) -> StrategyState:
    """Build (not persist) ``current.version + 1`` superseding ``current``.

    Only ``MUTABLE_FIELDS`` may change; any other key is refused so callers
    cannot dict-merge arbitrary state. Typed change *operations* live in
    SB-S20-003/004; this is the store-level constructor they build on.
    """
    errs = validate_state(current)
    if errs:
        raise StrategyError("current is invalid: " + "; ".join(errs))
    unknown = sorted(set(changes) - MUTABLE_FIELDS)
    if unknown:
        raise StrategyError(f"fields {unknown} cannot be changed on a strategy version")
    data = current.as_dict()
    data.update(changes)
    data.update({
        "version": current.version + 1, "supersedes": current.version,
        "status": status, "revision": revision, "created_at": now_iso(),
        "provenance": provenance or current.provenance,
    })
    s = StrategyState(**data)
    errs = validate_state(s)
    if errs:
        raise StrategyError("; ".join(errs))
    return s


# --------------------------------------------------------------------------- #
# store
# --------------------------------------------------------------------------- #
def _version_files(d: Path) -> dict[int, Path]:
    out: dict[int, Path] = {}
    if not d.is_dir():
        return out
    for p in d.iterdir():
        m = _VERSION_FILE_RE.match(p.name)
        if m and p.is_file():
            out[int(m.group(1))] = p
    return out


def latest_version(bot: str, persona: str) -> int:
    """Highest stored version number, or 0 when none exists."""
    files = _version_files(strategy_dir(bot, persona))
    return max(files) if files else 0


def _run(fence, commit):
    """Run ``commit`` inside the ownership fence when one is supplied."""
    if fence is None:
        return commit()
    return fence.fenced_commit(commit)


def save_version(state: StrategyState, *, activate: bool = False, event: str = "SAVED",
                 proposal_id: str | None = None, verdict_id: str | None = None,
                 fence=None) -> Path:
    """Persist one immutable version (+ HISTORY row, + HEAD when ``activate``).

    Refuses: invalid state; an existing version file (immutable); a version other
    than ``latest + 1``; a ``supersedes`` that is not stored. All writes happen
    inside one fenced commit when ``fence`` is given (version file first, then
    HISTORY, then HEAD), so a lost fence writes nothing.
    """
    errs = validate_state(state)
    if errs:
        raise StrategyError("; ".join(errs))
    d = strategy_dir(state.bot, state.persona, create=True)
    path = d / f"v{state.version:04d}.json"

    def commit():
        files = _version_files(d)
        if path.exists() or state.version in files:
            raise StrategyVersionExists(f"{path.name} already exists; versions are immutable")
        latest = max(files) if files else 0
        if state.version != latest + 1:
            raise StrategyVersionGap(
                f"version {state.version} is not latest+1 (latest stored is {latest})")
        if state.supersedes is not None and state.supersedes not in files:
            raise StrategyVersionGap(
                f"supersedes={state.supersedes} is not a stored version")
        write_json(path, state.as_dict())
        digest = _sha256_file(path)
        append_jsonl(d / HISTORY_FILE, {
            "version": state.version, "event": event, "status": state.status,
            "supersedes": state.supersedes, "proposal_id": proposal_id,
            "verdict_id": verdict_id, "sha256": digest, "at": now_iso(),
        })
        if activate:
            _write_head(d, state.strategy_id, state.version)
            append_jsonl(d / HISTORY_FILE, {
                "version": state.version, "event": "ACTIVATED", "status": state.status,
                "supersedes": state.supersedes, "proposal_id": proposal_id,
                "verdict_id": verdict_id, "sha256": digest, "at": now_iso(),
            })
        return path

    return _run(fence, commit)


def _write_head(d: Path, strategy_id: str, version: int | None) -> None:
    write_json(d / HEAD_FILE, {
        "schema_version": SCHEMA_VERSION, "strategy_id": strategy_id,
        "active_version": version, "updated_at": now_iso(),
    })


def set_active(bot: str, persona: str, version: int, *, event: str = "ACTIVATED",
               fence=None) -> None:
    """Point HEAD at a stored version (HISTORY row + HEAD, one fenced commit)."""
    d = strategy_dir(bot, persona, create=True)

    def commit():
        files = _version_files(d)
        if version not in files:
            raise StrategyVersionGap(f"version {version} is not stored for {persona}")
        digest = _sha256_file(files[version])
        append_jsonl(d / HISTORY_FILE, {
            "version": version, "event": event, "sha256": digest, "at": now_iso(),
        })
        _write_head(d, strategy_id_for(bot, persona), version)

    _run(fence, commit)


def load_version(bot: str, persona: str, version: int) -> StrategyState | None:
    """Strictly reload one stored version (None if absent)."""
    p = version_path(bot, persona, version)
    data = read_json(p, default=None)
    if data is None:
        return None
    s = StrategyState.from_dict(data)
    if s.bot != bot or s.persona != persona or s.version != int(version):
        raise StrategyError(f"{p.name} does not belong to {bot}/{persona} v{version}")
    return s


def head(bot: str, persona: str) -> dict:
    return read_json(strategy_dir(bot, persona) / HEAD_FILE, default=None) or {
        "schema_version": SCHEMA_VERSION, "strategy_id": strategy_id_for(bot, persona),
        "active_version": None, "updated_at": None}


def active(bot: str, persona: str) -> StrategyState | None:
    """The persona's active strategy version, or None (never another persona's)."""
    v = head(bot, persona).get("active_version")
    if v is None:
        return None
    return load_version(bot, persona, int(v))


def history(bot: str, persona: str) -> list[dict]:
    """HISTORY rows with integrity annotations.

    Each row that carries a ``sha256`` is re-checked against the version file on
    disk: ``tampered: True`` when the bytes changed, ``missing: True`` when the
    file is gone. Nothing is repaired or hidden.
    """
    d = strategy_dir(bot, persona)
    rows = read_jsonl(d / HISTORY_FILE)
    files = _version_files(d)
    out: list[dict] = []
    for row in rows:
        row = dict(row)
        v, digest = row.get("version"), row.get("sha256")
        if isinstance(v, int) and isinstance(digest, str):
            if v not in files:
                row["missing"] = True
            else:
                row["tampered"] = _sha256_file(files[v]) != digest
        out.append(row)
    return out


def versions(bot: str, persona: str) -> list[int]:
    return sorted(_version_files(strategy_dir(bot, persona)))


def admin_all_strategies(bot: str) -> dict[str, dict]:
    """EXPLICIT cross-persona admin reader (mirrors ``isolation.admin_all_records``).

    The only path that enumerates more than one persona's strategy state.
    """
    if bot not in paths.BOTS:
        raise StrategyError(f"bot must be one of {paths.BOTS}")
    root = paths.state_dir(bot) / "strategy"
    out: dict[str, dict] = {}
    if not root.is_dir():
        return out
    for pd in sorted(p for p in root.iterdir() if p.is_dir() and _SAFE_NS.match(p.name)):
        persona = pd.name
        out[persona] = {
            "active_version": head(bot, persona).get("active_version"),
            "versions": versions(bot, persona),
        }
    return out
