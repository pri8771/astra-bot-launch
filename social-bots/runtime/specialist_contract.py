"""SB-S23-001 — temporary specialist worker contract runtime (schema v2).

Implements ``SPECIALIST_WORKER_CONTRACT_SCHEMA.md`` (canonical schema version 2)
and the least-authority construction rules in
``V20_TO_V23_IMPLEMENTATION_SPEC.md`` §2.6 / §5.1 / §5.2.

What this module is
-------------------
The *typed* boundary between a persistent Social Bot (the parent) and a bounded,
short-lived specialist (researcher / analyst / writer / reviewer / media / qa).
It defines:

* ``SpecialistAuthority`` — a frozen dataclass with exactly three least-authority
  booleans (``read_context_refs``, ``write_scratch``, ``emit_result``). It has NO
  public-post, spend, message, credential, destructive-action, state-mutation or
  child-spawn field. ``runtime.decision.Authority`` is deliberately NOT reused:
  a type that *has* ``can_public_post`` can be mis-set; a type that has no such
  field cannot. "A specialist cannot exceed granted effect authority" is
  therefore a property of the type, not of caller discipline.
* ``WorkerContract`` / ``WorkerResult`` — frozen records carrying the schema v2
  fields. ``external_effect_budget`` is an ``init=False`` field fixed at ``0``:
  the constructor cannot set it, ``frozen=True`` means it cannot be reassigned,
  and ``validate_contract`` / ``from_dict`` reject any non-zero value on reload.
* ``ROLE_TOOLS`` — per-role tool allowlists. Nothing in any allowlist can
  publish, enqueue, spend, message, mutate persona/runtime state, register an
  experiment, or spawn a child worker.
* ``new_contract`` — the least-authority constructor. It only ever returns a
  contract that passes ``validate_contract``; otherwise it raises
  ``ContractError``. Unknown keyword arguments (including ``can_public_post`` or
  any other ``decision.Authority`` field) are refused before construction, and
  credential-shaped keys anywhere in the bounded context are refused too:
  specialists never receive credentials, not even by reference.
* ``validate_contract`` / ``validate_result`` — return ``list[str]`` of errors
  (empty means valid), in the style of ``reasoning.validate_candidate``. The
  integrator (SB-S23-006) treats ANY error as REJECT.

What this module is not
-----------------------
No execution, no sandbox (SB-S23-002), no adapters (SB-S23-003..005), no lease,
no provider, no model call, no integration with ``decision.py``. Nothing here
performs an effect, so ``effect_attempts`` on a result produced by code in this
module is always 0 by construction.

Provenance: contracts and results built by tests carry ``provenance="fixture"``.
That label is engineering evidence only and never promotes an operational gate.
"""
from __future__ import annotations

import math
import re
import uuid
from dataclasses import dataclass, field, fields, asdict
from datetime import datetime, timedelta, timezone
from typing import Any

from . import paths
from .jsonstore import now_iso

SCHEMA_VERSION = 2

ROLES = ("researcher", "analyst", "writer", "reviewer", "media", "qa")

# Per-role tool allowlists (spec §5.2). Deliberately narrow: read what the parent
# materialized, read earlier scratch inputs, write inside the sandbox. The
# researcher may also run a capture through an injected Collector (a fixture in
# every engineering slice). No entry can publish/enqueue/spend/message/mutate
# state/register experiments/spawn.
ROLE_TOOLS: dict[str, frozenset[str]] = {
    "researcher": frozenset({"read_context", "capture_source", "write_scratch"}),
    "analyst":    frozenset({"read_context", "read_scratch_inputs", "write_scratch"}),
    "reviewer":   frozenset({"read_context", "read_scratch_inputs", "write_scratch"}),
    "writer":     frozenset({"read_context", "read_scratch_inputs", "write_scratch"}),
    "media":      frozenset({"read_context", "read_scratch_inputs", "write_scratch"}),
    "qa":         frozenset({"read_context", "read_scratch_inputs", "write_scratch"}),
}

# Every tool any role may hold. Anything else (publish, enqueue, spend,
# message_users, update_state, register_experiment, spawn_specialist, ...) is
# not a specialist tool and is rejected at construction and at validation.
ALL_SPECIALIST_TOOLS: frozenset[str] = frozenset().union(*ROLE_TOOLS.values())

RESULT_STATES = ("COMPLETED", "FAILED", "TIMED_OUT", "BUDGET_EXHAUSTED", "STOPPED")
CLEANUP_STATES = ("PENDING", "RETIRED", "FAILED")
PROVENANCES = ("fixture", "evidence")

# Keys that would widen authority if they appeared anywhere on/inside a contract.
# ``decision.Authority``'s fields are listed explicitly so passing that object's
# dict form (or any of its fields) is refused, as is the superseded free-form
# ``authority_scope`` (schema v1) and the fixed effect budget.
FORBIDDEN_AUTHORITY_KEYS: frozenset[str] = frozenset({
    "can_public_post", "can_spend", "can_message_users", "can_create_candidate",
    "can_register_experiment", "can_update_state", "authority_scope",
    "external_effect_budget", "spawn_specialist", "public_authority",
})

# Credential-shaped keys are refused anywhere in bounded context / inputs.
# (Mirrors the redaction hint in ``runtime.receipts`` but as a hard refusal:
# a specialist must not receive a credential even by reference.)
_SECRET_KEY_RE = re.compile(
    r"(credential|token|password|passwd|cookie|secret|session|apikey|api_key|"
    r"bearer|totp|private.?key|recovery.?code)", re.I)

# Same shape as ``paths._SAFE`` (copied; the private name is not imported).
_SAFE_NS = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
# A worker id names a scratch directory component (SB-S23-002), so it must be a
# safe single path component — same discipline as session_heartbeat lanes.
_SAFE_WORKER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SCHEMA_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*/[0-9]+$")   # e.g. ResearchResult/1


class ContractError(ValueError):
    """Raised by the constructors when a contract/result cannot be built validly."""


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def _is_finite_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _walk_keys(obj: Any):
    """Yield every dict key found anywhere inside a nested structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _walk_keys(v)


def forbidden_keys_in(obj: Any) -> list[str]:
    """Authority-widening or credential-shaped keys found anywhere in ``obj``."""
    bad: list[str] = []
    for k in _walk_keys(obj):
        ks = str(k)
        if ks in FORBIDDEN_AUTHORITY_KEYS or _SECRET_KEY_RE.search(ks):
            if ks not in bad:
                bad.append(ks)
    return bad


def _list_of_dicts(name: str, value: Any, errs: list[str]) -> None:
    if not isinstance(value, list):
        errs.append(f"{name} must be a list")
        return
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            errs.append(f"{name}[{i}] must be a dict")


def _rel_path_ok(p: Any) -> bool:
    """A result output path must be relative, contained, and portable."""
    if not isinstance(p, str) or not p or p != p.strip():
        return False
    if p.startswith("/") or "\\" in p or "\x00" in p:
        return False
    if re.match(r"^[A-Za-z]:", p):          # Windows drive prefix
        return False
    parts = p.split("/")
    return all(part not in ("", ".", "..") for part in parts)


# --------------------------------------------------------------------------- #
# SpecialistAuthority — least authority, by type
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SpecialistAuthority:
    """Exactly three least-authority booleans. Nothing else exists to escalate."""

    read_context_refs: bool = True
    write_scratch: bool = True
    emit_result: bool = True

    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            if not isinstance(v, bool):
                raise ContractError(f"SpecialistAuthority.{f.name} must be a bool")

    def as_dict(self) -> dict:
        return asdict(self)


_AUTHORITY_FIELDS = tuple(f.name for f in fields(SpecialistAuthority))


def validate_authority(a: Any) -> list[str]:
    """Reject anything that is not exactly a ``SpecialistAuthority`` (no subclass
    may add fields; ``decision.Authority`` is a different type entirely)."""
    if type(a) is not SpecialistAuthority:
        return [f"authority must be a SpecialistAuthority, got {type(a).__name__}"]
    names = tuple(f.name for f in fields(a))
    if names != _AUTHORITY_FIELDS:
        return [f"authority fields must be exactly {_AUTHORITY_FIELDS}"]
    return [f"authority.{n} must be a bool" for n in names
            if not isinstance(getattr(a, n), bool)]


# --------------------------------------------------------------------------- #
# WorkerContract
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class WorkerContract:
    worker_id: str
    parent_run_id: str
    bot: str
    persona: str
    role: str
    objective: str
    expected_output_schema: str
    time_budget_s: float
    scratch_scope: str
    created_at: str
    expires_at: str
    bounded_context_refs: list = field(default_factory=list)
    allowed_tools: list = field(default_factory=list)
    denied_tools: list = field(default_factory=list)
    authority: SpecialistAuthority = field(default_factory=SpecialistAuthority)
    input_artifacts: list = field(default_factory=list)
    model_call_budget: int = 0
    stop_conditions: list = field(default_factory=list)
    provenance: str = "fixture"
    schema_version: int = SCHEMA_VERSION
    # Fixed at zero and NOT a constructor parameter: a caller cannot widen it,
    # and ``frozen=True`` means it cannot be reassigned after construction.
    external_effect_budget: int = field(default=0, init=False)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["authority"] = self.authority.as_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "WorkerContract":
        """Strict reload: unknown or missing keys, a non-zero effect budget or a
        malformed authority are errors — never silently widened or defaulted."""
        if not isinstance(data, dict):
            raise ContractError("contract data must be a dict")
        expected = {f.name for f in fields(cls)}
        unknown = sorted(set(data) - expected)
        missing = sorted(expected - set(data))
        if unknown:
            raise ContractError(f"unknown contract keys: {unknown}")
        if missing:
            raise ContractError(f"missing contract keys: {missing}")
        if data.get("external_effect_budget") != 0:
            raise ContractError("external_effect_budget must be 0")
        auth = data["authority"]
        if isinstance(auth, dict):
            if set(auth) != set(_AUTHORITY_FIELDS):
                raise ContractError(
                    f"authority keys must be exactly {sorted(_AUTHORITY_FIELDS)}")
            auth = SpecialistAuthority(**auth)
        elif type(auth) is not SpecialistAuthority:
            raise ContractError("authority must be a SpecialistAuthority")
        kwargs = {k: v for k, v in data.items()
                  if k not in ("authority", "external_effect_budget")}
        c = cls(authority=auth, **kwargs)
        errs = validate_contract(c)
        if errs:
            raise ContractError("; ".join(errs))
        return c


def new_worker_id() -> str:
    return f"w-{uuid.uuid4().hex[:12]}"


def new_contract(*, bot: str, persona: str, parent_run_id: str, role: str,
                 objective: str, expected_output_schema: str, time_budget_s: float,
                 bounded_context_refs=(), model_call_budget: int = 0,
                 allowed_tools=None, denied_tools=(), input_artifacts=(),
                 stop_conditions=(), ttl_s: float | None = None,
                 provenance: str = "fixture", worker_id: str | None = None,
                 authority: SpecialistAuthority | None = None,
                 **unexpected) -> WorkerContract:
    """Least-authority constructor.

    * Refuses unknown keyword arguments before anything is built — including
      ``can_public_post``/``can_spend``/... (``decision.Authority`` fields),
      ``authority_scope`` (schema v1) and ``external_effect_budget``.
    * ``authority`` may only narrow: it must be a ``SpecialistAuthority``
      (``decision.Authority`` or a dict is refused).
    * ``allowed_tools`` defaults to the role's allowlist; a requested tool outside
      it is refused (``publish``, ``spawn_specialist``, ... can never be granted).
    * Credential-shaped or authority-widening keys anywhere inside
      ``bounded_context_refs`` / ``input_artifacts`` / ``stop_conditions`` are
      refused.
    * ``expires_at = created_at + (ttl_s or 2 * time_budget_s)``.

    Returns a contract for which ``validate_contract`` is empty, or raises
    ``ContractError``.
    """
    if unexpected:
        raise ContractError(
            f"unsupported contract parameters (authority cannot be widened): "
            f"{sorted(unexpected)}")
    if authority is None:
        authority = SpecialistAuthority()
    auth_errs = validate_authority(authority)
    if auth_errs:
        raise ContractError("; ".join(auth_errs))
    if role not in ROLES:
        raise ContractError(f"unknown role {role!r}; expected one of {ROLES}")

    bad = forbidden_keys_in([list(bounded_context_refs), list(input_artifacts),
                             list(stop_conditions)])
    if bad:
        raise ContractError(
            f"authority-widening or credential-shaped keys are not allowed in a "
            f"specialist contract: {bad}")

    role_tools = ROLE_TOOLS[role]
    if allowed_tools is None:
        tools = sorted(role_tools)
    else:
        tools = sorted(set(allowed_tools))
        outside = sorted(set(tools) - role_tools)
        if outside:
            raise ContractError(
                f"tools {outside} are outside the {role!r} allowlist {sorted(role_tools)}")

    if not _is_finite_number(time_budget_s) or time_budget_s <= 0:
        raise ContractError("time_budget_s must be a finite number > 0")
    created = datetime.now(timezone.utc)
    ttl = ttl_s if ttl_s is not None else 2.0 * float(time_budget_s)
    if not _is_finite_number(ttl):
        raise ContractError("ttl_s must be a finite number")
    wid = worker_id or new_worker_id()

    contract = WorkerContract(
        worker_id=wid,
        parent_run_id=parent_run_id,
        bot=bot,
        persona=persona,
        role=role,
        objective=objective,
        expected_output_schema=expected_output_schema,
        time_budget_s=float(time_budget_s),
        scratch_scope=wid,
        created_at=_iso(created),
        expires_at=_iso(created + timedelta(seconds=ttl)),
        bounded_context_refs=[dict(r) for r in bounded_context_refs],
        allowed_tools=tools,
        denied_tools=sorted(set(denied_tools)),
        authority=authority,
        input_artifacts=[dict(a) for a in input_artifacts],
        model_call_budget=model_call_budget,
        stop_conditions=[dict(s) for s in stop_conditions],
        provenance=provenance,
    )
    errs = validate_contract(contract)
    if errs:
        raise ContractError("; ".join(errs))
    return contract


def validate_contract(c: Any) -> list[str]:
    """All the reasons ``c`` is not a valid schema-v2 least-authority contract."""
    if not isinstance(c, WorkerContract):
        return [f"not a WorkerContract: {type(c).__name__}"]
    errs: list[str] = []

    if c.schema_version != SCHEMA_VERSION:
        errs.append(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(c.worker_id, str) or not _SAFE_WORKER_ID.match(c.worker_id):
        errs.append("worker_id is not a safe single path component")
    if not isinstance(c.parent_run_id, str) or not c.parent_run_id.strip():
        errs.append("parent_run_id is required")
    if not isinstance(c.bot, str) or c.bot not in paths.BOTS:
        errs.append(f"bot must be one of {paths.BOTS}")
    if not isinstance(c.persona, str) or not _SAFE_NS.match(c.persona):
        errs.append("persona is not a safe namespace id")
    if c.role not in ROLES:
        errs.append(f"role must be one of {ROLES}")
    if not isinstance(c.objective, str) or not c.objective.strip():
        errs.append("objective is required")
    if (not isinstance(c.expected_output_schema, str)
            or not _SCHEMA_NAME_RE.match(c.expected_output_schema)):
        errs.append("expected_output_schema must look like 'Name/<n>'")

    _list_of_dicts("bounded_context_refs", c.bounded_context_refs, errs)
    _list_of_dicts("input_artifacts", c.input_artifacts, errs)
    _list_of_dicts("stop_conditions", c.stop_conditions, errs)
    if isinstance(c.stop_conditions, list):
        for i, s in enumerate(c.stop_conditions):
            if isinstance(s, dict) and not isinstance(s.get("kind"), str):
                errs.append(f"stop_conditions[{i}].kind is required")
    bad = forbidden_keys_in([c.bounded_context_refs, c.input_artifacts, c.stop_conditions])
    if bad:
        errs.append(f"forbidden keys present: {bad}")

    if not isinstance(c.allowed_tools, list) or not all(isinstance(t, str) for t in c.allowed_tools):
        errs.append("allowed_tools must be a list of str")
    elif c.role in ROLE_TOOLS:
        if len(set(c.allowed_tools)) != len(c.allowed_tools):
            errs.append("allowed_tools contains duplicates")
        outside = sorted(set(c.allowed_tools) - ROLE_TOOLS[c.role])
        if outside:
            errs.append(f"allowed_tools {outside} are outside the {c.role!r} allowlist")
    if not isinstance(c.denied_tools, list) or not all(isinstance(t, str) for t in c.denied_tools):
        errs.append("denied_tools must be a list of str")
    elif isinstance(c.allowed_tools, list):
        overlap = sorted(set(c.allowed_tools) & set(c.denied_tools))
        if overlap:
            errs.append(f"allowed_tools and denied_tools overlap: {overlap}")

    errs.extend(validate_authority(c.authority))

    if not _is_finite_number(c.time_budget_s) or c.time_budget_s <= 0:
        errs.append("time_budget_s must be a finite number > 0")
    if not isinstance(c.model_call_budget, int) or isinstance(c.model_call_budget, bool) \
            or c.model_call_budget < 0:
        errs.append("model_call_budget must be an int >= 0")
    if c.external_effect_budget != 0:
        errs.append("external_effect_budget must be 0")
    if c.scratch_scope != c.worker_id:
        errs.append("scratch_scope must equal worker_id")

    created = _parse_iso(c.created_at)
    expires = _parse_iso(c.expires_at)
    if created is None:
        errs.append("created_at is not an ISO-8601 timestamp")
    if expires is None:
        errs.append("expires_at is not an ISO-8601 timestamp")
    if created is not None and expires is not None and expires <= created:
        errs.append("expires_at must be after created_at")
    if c.provenance not in PROVENANCES:
        errs.append(f"provenance must be one of {PROVENANCES}")
    return errs


# --------------------------------------------------------------------------- #
# WorkerResult
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class WorkerResult:
    worker_id: str
    parent_run_id: str
    bot: str
    persona: str
    role: str
    started_at: str
    finished_at: str
    source_ref: str
    result: str
    outputs: list = field(default_factory=list)          # [{"schema","path","sha256"}]
    evidence_refs: list = field(default_factory=list)
    calls_used: int = 0
    effect_attempts: int = 0
    limitations: list = field(default_factory=list)
    cleanup_status: str = "PENDING"
    provenance: str = "fixture"
    error: str | None = None
    schema_version: int = SCHEMA_VERSION

    def as_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WorkerResult":
        if not isinstance(data, dict):
            raise ContractError("result data must be a dict")
        expected = {f.name for f in fields(cls)}
        unknown = sorted(set(data) - expected)
        if unknown:
            raise ContractError(f"unknown result keys: {unknown}")
        required = expected - {"error", "schema_version", "outputs", "evidence_refs",
                               "calls_used", "effect_attempts", "limitations",
                               "cleanup_status", "provenance"}
        missing = sorted(required - set(data))
        if missing:
            raise ContractError(f"missing result keys: {missing}")
        return cls(**data)


def validate_result(r: Any, c: Any) -> list[str]:
    """All the reasons ``r`` is not an acceptable result for contract ``c``.

    The integrator must treat any error as REJECT. Checks identity match,
    zero effect attempts, call budget, enumerations, timestamps, contained
    relative output paths with sha256, and provenance.
    """
    if not isinstance(r, WorkerResult):
        return [f"not a WorkerResult: {type(r).__name__}"]
    if not isinstance(c, WorkerContract):
        return [f"not a WorkerContract: {type(c).__name__}"]
    errs: list[str] = []

    if r.schema_version != SCHEMA_VERSION:
        errs.append(f"schema_version must be {SCHEMA_VERSION}")
    for name in ("worker_id", "parent_run_id", "bot", "persona", "role"):
        if getattr(r, name) != getattr(c, name):
            errs.append(f"{name} mismatch: result {getattr(r, name)!r} vs contract "
                        f"{getattr(c, name)!r}")

    if not isinstance(r.effect_attempts, int) or isinstance(r.effect_attempts, bool) \
            or r.effect_attempts < 0:
        errs.append("effect_attempts must be an int >= 0")
    elif r.effect_attempts > 0:
        errs.append(f"effect_attempts={r.effect_attempts}: a specialist attempted an "
                    f"external effect (budget is 0)")

    if not isinstance(r.calls_used, int) or isinstance(r.calls_used, bool) or r.calls_used < 0:
        errs.append("calls_used must be an int >= 0")
    elif isinstance(c.model_call_budget, int) and r.calls_used > c.model_call_budget:
        errs.append(f"calls_used={r.calls_used} exceeds model_call_budget="
                    f"{c.model_call_budget}")

    if r.result not in RESULT_STATES:
        errs.append(f"result must be one of {RESULT_STATES}")
    if r.cleanup_status not in CLEANUP_STATES:
        errs.append(f"cleanup_status must be one of {CLEANUP_STATES}")
    if not isinstance(r.source_ref, str) or not r.source_ref.strip():
        errs.append("source_ref is required")
    if r.provenance not in PROVENANCES:
        errs.append(f"provenance must be one of {PROVENANCES}")
    if r.error is not None and not isinstance(r.error, str):
        errs.append("error must be a str or None")

    started = _parse_iso(r.started_at)
    finished = _parse_iso(r.finished_at)
    if started is None:
        errs.append("started_at is not an ISO-8601 timestamp")
    if finished is None:
        errs.append("finished_at is not an ISO-8601 timestamp")
    if started is not None and finished is not None and finished < started:
        errs.append("finished_at must not precede started_at")

    if not isinstance(r.outputs, list):
        errs.append("outputs must be a list")
    else:
        seen: set[str] = set()
        for i, out in enumerate(r.outputs):
            if not isinstance(out, dict):
                errs.append(f"outputs[{i}] must be a dict")
                continue
            extra = sorted(set(out) - {"schema", "path", "sha256"})
            if extra:
                errs.append(f"outputs[{i}] has unknown keys {extra}")
            if not isinstance(out.get("schema"), str) or not _SCHEMA_NAME_RE.match(out.get("schema") or ""):
                errs.append(f"outputs[{i}].schema must look like 'Name/<n>'")
            p = out.get("path")
            if not _rel_path_ok(p):
                errs.append(f"outputs[{i}].path must be a contained relative path")
            elif p in seen:
                errs.append(f"outputs[{i}].path duplicates an earlier output")
            else:
                seen.add(p)
            if not isinstance(out.get("sha256"), str) or not _SHA256_RE.match(out.get("sha256") or ""):
                errs.append(f"outputs[{i}].sha256 must be 64 lowercase hex chars")
    _list_of_dicts("evidence_refs", r.evidence_refs, errs)
    if not isinstance(r.limitations, list) or not all(isinstance(x, str) for x in r.limitations):
        errs.append("limitations must be a list of str")
    return errs
