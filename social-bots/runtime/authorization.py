"""SB-V04-002/004 — fail-closed live-execution authorization gate and call budget.

Canonical rule (V04_DIVERGENCE_ACCEPTANCE_PLAN.md, LEAD-037, LEAD-038):

    No live divergence execution may occur merely because code supports it.

A live adaptive batch requires BOTH

1. a fresh explicit owner authorization, and
2. a corresponding **lead-created canonical authorization manifest** naming the
   artifact/run scope and the exact maximum call count,

and until that manifest exists, live execution must **fail closed before spawning
Claude**. This module is that gate. Nothing here can create an authorization: it
only finds, validates and consumes one. There is no bypass flag, no "force" and
no environment override, deliberately.

Three cooperating pieces
------------------------
``load_manifest`` / ``validate_manifest``
    Strict schema + posture validation of a manifest file under
    ``social-bots/authorizations/``. Every safety field must be explicitly
    present and false/absent-permissive values are rejected rather than defaulted.

``CallBudget``
    Exact call-budget enforcement with **atomic pre-spawn accounting**. A slot is
    reserved with ``O_CREAT | O_EXCL`` *before* a provider is constructed or a
    subprocess is spawned, so a crash between reservation and invocation can only
    ever over-count (safe), never under-count (unsafe). Slots are never reused —
    that is what makes the **no-retry** rule structural rather than advisory: a
    malformed, unavailable or non-divergent outcome consumes its slot and is
    recorded truthfully instead of being rerun until it passes.

``authorize``
    The single entry point a live executor must call. It returns an
    ``ExecutionGrant`` or raises ``AuthorizationDenied``. It also re-checks the
    process posture (no ``ANTHROPIC_API_KEY``, no injected runner) because a
    manifest authorizes a *subscription* batch, never a paid-API one.

Honesty boundary on authorship
------------------------------
This code cannot cryptographically prove that a manifest was authored by the
ChatGPT lead rather than by a worker. Authorship is a *repository provenance*
fact: which commit introduced the file, on which branch, by which author. The
gate therefore records the manifest's file digest and its declared
``created_by`` / ``owner_authorization_ref`` truthfully into every receipt and
ledger entry, so an independent audit can verify provenance against git history.
It never asserts lead authorship on its own. A worker that writes its own
manifest produces evidence that visibly says so.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Canonical location a lead-created manifest must live in. A manifest found
# anywhere else is not canonical and is not honoured by ``authorize``.
MANIFEST_DIR = ROOT / "authorizations"

MANIFEST_SCHEMA_VERSION = "v1"

# Absolute ceiling on a single authorized batch, independent of what a manifest
# claims. The conservative V0.4 acceptance matrix is exactly five calls; a
# manifest asking for more is rejected as out of policy rather than trusted.
HARD_MAX_CALLS = 5

# Every one of these must be present AND exactly ``False``. They are listed
# explicitly (rather than defaulted) so a manifest that simply omits a safety
# posture is invalid instead of silently permissive.
_REQUIRED_FALSE_FIELDS = (
    "retry_allowed",
    "public_effect_allowed",
    "spend_authorized",
    "api_key_allowed",
    "injected_runner_allowed",
)

_REQUIRED_FIELDS = (
    "schema_version", "manifest_id", "created_by", "created_at",
    "owner_authorization_ref", "artifact_scope", "run_scope", "lane",
    "provider_mode", "max_calls", "expires_at",
) + _REQUIRED_FALSE_FIELDS

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,95}$")


class AuthorizationDenied(Exception):
    """Raised whenever live execution is NOT authorized. Always fail closed."""


class CallBudgetExhausted(AuthorizationDenied):
    """Raised when the exact authorized call count has already been reserved."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_json(obj) -> str:
    """Stable digest of a JSON-serializable object (key order independent)."""
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


# --------------------------------------------------------------------------- #
# Manifest validation
# --------------------------------------------------------------------------- #
def validate_manifest(manifest, *, now: datetime | None = None) -> list[str]:
    """Return a list of violations ([] means the manifest is structurally valid).

    Structural validity is necessary but NOT sufficient: ``authorize`` additionally
    checks that the manifest actually covers the requested artifact/lane/run scope
    and that the process posture matches.
    """
    if not isinstance(manifest, dict):
        return [f"manifest is not an object: {type(manifest).__name__}"]
    errs: list[str] = []
    for fld in _REQUIRED_FIELDS:
        if fld not in manifest:
            errs.append(f"missing required field {fld!r}")
    if errs:
        return errs  # deeper checks on a structurally incomplete manifest are unsafe

    if manifest["schema_version"] != MANIFEST_SCHEMA_VERSION:
        errs.append(f"schema_version {manifest['schema_version']!r} != {MANIFEST_SCHEMA_VERSION!r}")

    for fld in ("manifest_id", "run_scope", "lane"):
        if not isinstance(manifest[fld], str) or not _ID_RE.match(manifest[fld]):
            errs.append(f"{fld} {manifest[fld]!r} is not a safe identifier")

    for fld in ("created_by", "owner_authorization_ref"):
        if not isinstance(manifest[fld], str) or not manifest[fld].strip():
            errs.append(f"{fld} must be a non-empty string")

    scope = manifest["artifact_scope"]
    if not isinstance(scope, list) or not scope or not all(
            isinstance(a, str) and a.strip() for a in scope):
        errs.append("artifact_scope must be a non-empty list of artifact ids")

    # Subscription-authenticated Claude Code provider only.
    if manifest["provider_mode"] != "claude-cli":
        errs.append(f"provider_mode {manifest['provider_mode']!r} is not the authorized "
                    f"subscription route 'claude-cli'")

    max_calls = manifest["max_calls"]
    if isinstance(max_calls, bool) or not isinstance(max_calls, int) or max_calls < 1:
        errs.append(f"max_calls {max_calls!r} must be a positive integer")
    elif max_calls > HARD_MAX_CALLS:
        errs.append(f"max_calls {max_calls} exceeds the hard ceiling {HARD_MAX_CALLS}")

    for fld in _REQUIRED_FALSE_FIELDS:
        if manifest[fld] is not False:
            errs.append(f"{fld} must be exactly False (got {manifest[fld]!r}); this gate "
                        f"never authorizes retries, spend, public effect, API-key auth "
                        f"or an injected runner")

    now = now or _now()
    created = _parse_iso(manifest["created_at"])
    expires = _parse_iso(manifest["expires_at"])
    if created is None:
        errs.append(f"created_at {manifest['created_at']!r} is not an ISO-8601 timestamp")
    if expires is None:
        errs.append(f"expires_at {manifest['expires_at']!r} is not an ISO-8601 timestamp")
    elif expires <= now:
        errs.append(f"manifest expired at {manifest['expires_at']} (now {now.isoformat()})")
    if created is not None and expires is not None and expires <= created:
        errs.append("expires_at must be after created_at")
    return errs


def load_manifest(path: str | Path) -> tuple[dict, str]:
    """Load a manifest file and return ``(manifest, file_digest)``.

    The digest is over the exact file BYTES, so the receipt records what was on
    disk rather than a re-serialization of it.
    """
    path = Path(path)
    raw = path.read_bytes()
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorizationDenied(f"manifest {path} is not valid JSON: {exc}") from exc
    return manifest, sha256_bytes(raw)


def find_manifests(directory: str | Path | None = None) -> list[Path]:
    """Canonical manifest files present on disk. Empty is the expected V0.4 state."""
    directory = Path(directory) if directory is not None else MANIFEST_DIR
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.json") if p.is_file())


# --------------------------------------------------------------------------- #
# Exact call budget with atomic pre-spawn accounting and no-retry semantics.
# --------------------------------------------------------------------------- #
@dataclass
class CallSlot:
    """One irrevocably consumed call slot."""
    slot: int
    run_scope: str
    manifest_id: str
    manifest_digest: str
    reserved_at: str
    lane: str
    artifact: str
    context_digest: str | None = None
    outcome: str | None = None
    outcome_recorded_at: str | None = None
    detail: dict = field(default_factory=dict)


class CallBudget:
    """Exact, crash-safe, non-reusable accounting of authorized live calls.

    Each slot is a file created with ``O_CREAT | O_EXCL`` under
    ``<home>/call-budget/<run_scope>/``. Exclusive creation is the atomic
    primitive: two concurrent workers cannot both take slot N, and a worker that
    dies after reserving leaves the slot consumed.

    That last property is intentional. Over-counting a crashed call is safe (we
    lose a slot); under-counting is not (we could exceed the owner's exact
    authorization). A "wasted" slot is recorded truthfully as
    ``reserved_not_recorded`` by ``audit()`` rather than being reclaimed.
    """

    SLOT_GLOB = "slot-*.json"

    def __init__(self, run_scope: str, max_calls: int, *,
                 home: str | Path | None = None):
        if not _ID_RE.match(run_scope):
            raise AuthorizationDenied(f"unsafe run_scope {run_scope!r}")
        if isinstance(max_calls, bool) or not isinstance(max_calls, int) or max_calls < 1:
            raise AuthorizationDenied(f"max_calls {max_calls!r} must be a positive integer")
        self.run_scope = run_scope
        self.max_calls = min(max_calls, HARD_MAX_CALLS)
        base = Path(home) if home is not None else Path(
            os.environ.get("SBOTS_HOME", str(ROOT)))
        self.dir = base / "call-budget" / run_scope
        self.dir.mkdir(parents=True, exist_ok=True)

    # -- state -------------------------------------------------------------- #
    def _slot_path(self, n: int) -> Path:
        return self.dir / f"slot-{n:04d}.json"

    def remaining(self) -> int:
        return max(0, self.max_calls - self.consumed())

    def slots(self) -> list[dict]:
        out = []
        for p in sorted(self.dir.glob(self.SLOT_GLOB)):
            try:
                out.append(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                try:
                    number = int(p.stem.split("-")[-1])
                except ValueError:                    # pragma: no cover - defensive
                    number = None
                out.append({"slot": number, "slot_file": p.name,
                            "unreadable": True, "outcome": None})
        return out

    # -- reservation -------------------------------------------------------- #
    def _high_water(self) -> int:
        """Highest slot number ever taken, from the slot filenames themselves.

        Reservation starts above this rather than at the first *gap*, so deleting
        a slot file cannot buy another call. Removing evidence must never widen
        an authorization.
        """
        highest = 0
        for p in self.dir.glob(self.SLOT_GLOB):
            try:
                highest = max(highest, int(p.stem.split("-")[-1]))
            except ValueError:                        # pragma: no cover - defensive
                continue
        return highest

    def consumed(self) -> int:
        """Slots irrevocably taken, whether or not the call succeeded.

        The high-water mark, not a file count, so deleting a slot file does not
        appear to free budget.
        """
        return self._high_water()

    def reserve(self, *, manifest_id: str, manifest_digest: str, lane: str,
                artifact: str, context_digest: str | None = None) -> CallSlot:
        """Atomically consume the next slot. MUST be called BEFORE spawning.

        Raises ``CallBudgetExhausted`` when the exact authorized count is spent.
        """
        for n in range(self._high_water() + 1, self.max_calls + 1):
            path = self._slot_path(n)
            slot = CallSlot(
                slot=n, run_scope=self.run_scope, manifest_id=manifest_id,
                manifest_digest=manifest_digest,
                reserved_at=_now().replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                lane=lane, artifact=artifact, context_digest=context_digest)
            payload = json.dumps(asdict(slot), indent=2, sort_keys=True).encode("utf-8")
            try:
                fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                continue  # someone else already took slot n; try the next one
            try:
                with os.fdopen(fd, "wb") as fh:
                    fh.write(payload)
                    fh.flush()
                    os.fsync(fh.fileno())
            except BaseException:
                # The slot stays consumed on purpose: we cannot know whether a
                # spawn followed, and over-counting is the safe direction.
                raise
            return slot
        raise CallBudgetExhausted(
            f"call budget exhausted for run_scope {self.run_scope!r}: "
            f"{self.consumed()}/{self.max_calls} slots consumed. No retry is "
            f"authorized — a new owner authorization and lead manifest are required.")

    def record_outcome(self, slot: CallSlot | int, outcome: str,
                       detail: dict | None = None) -> dict:
        """Record the TRUTHFUL outcome of a consumed slot. Never frees the slot.

        ``outcome`` is recorded verbatim, including failures
        (``provider_unavailable``, ``invalid_envelope``, ``no_material_divergence``).
        Recording a failure does not permit a retry: the slot stays consumed.
        """
        n = slot.slot if isinstance(slot, CallSlot) else int(slot)
        path = self._slot_path(n)
        if not path.exists():
            raise AuthorizationDenied(
                f"cannot record an outcome for unreserved slot {n} in {self.run_scope!r}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            # A slot torn by an earlier crash must not abort the rest of the
            # batch. The slot stays consumed; we rebuild a minimal record that
            # says so rather than pretending it is free.
            data = {"slot": n, "run_scope": self.run_scope,
                    "unreadable_prior_content": f"{type(exc).__name__}",
                    "outcome": None}
        if data.get("outcome") is not None:
            raise AuthorizationDenied(
                f"slot {n} already recorded outcome {data['outcome']!r}; a slot's "
                f"outcome is write-once (no-retry semantics)")
        data["outcome"] = str(outcome)
        data["outcome_recorded_at"] = _now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
        data["detail"] = detail or {}
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        return data

    def audit(self) -> dict:
        """Truthful budget state, including slots reserved but never recorded."""
        slots = self.slots()
        unrecorded = [s.get("slot") for s in slots if s.get("outcome") is None]
        return {
            "run_scope": self.run_scope,
            "max_calls": self.max_calls,
            "consumed": self.consumed(),
            "remaining": self.remaining(),
            "reserved_not_recorded": unrecorded,
            "outcomes": [{"slot": s.get("slot"), "outcome": s.get("outcome")} for s in slots],
            "retry_permitted": False,
        }


# --------------------------------------------------------------------------- #
# The gate
# --------------------------------------------------------------------------- #
@dataclass
class ExecutionGrant:
    """Proof, for receipts, that a specific live batch was properly authorized."""
    manifest_id: str
    manifest_path: str
    manifest_digest: str
    created_by: str
    owner_authorization_ref: str
    artifact: str
    lane: str
    run_scope: str
    provider_mode: str
    max_calls: int
    expires_at: str
    granted_at: str
    authorship_attested_by_code: bool = False   # see the module docstring
    retry_allowed: bool = False


def posture_violations(*, injected_runner: bool) -> list[str]:
    """Process-level posture checks that no manifest can waive."""
    errs: list[str] = []
    if os.environ.get("ANTHROPIC_API_KEY"):
        errs.append("ANTHROPIC_API_KEY is present; only the existing subscription "
                    "route is authorized (no PAYG/API-key billing)")
    if injected_runner:
        errs.append("an injected runner was supplied; a live authorized batch must "
                    "use the real provider, never a test seam")
    return errs


def authorize(*, artifact: str, lane: str, run_scope: str,
              manifest_dir: str | Path | None = None,
              injected_runner: bool = False) -> ExecutionGrant:
    """Authorize ONE live adaptive batch, or raise ``AuthorizationDenied``.

    Call this **before** constructing a provider or spawning anything. There is no
    override: with no canonical manifest on disk this raises, which is the correct
    and expected V0.4 state.

    Expiry is judged against the real clock, deliberately. ``validate_manifest``
    accepts an injected ``now`` so unit tests can exercise its other rules
    deterministically, but the gate itself never takes one — a caller-supplied
    clock would be exactly the kind of override this module promises not to have.
    """
    now = _now()
    candidates = find_manifests(manifest_dir)
    if not candidates:
        directory = Path(manifest_dir) if manifest_dir is not None else MANIFEST_DIR
        raise AuthorizationDenied(
            f"no canonical authorization manifest in {directory}. A live adaptive "
            f"batch requires BOTH a fresh explicit owner authorization AND a "
            f"lead-created canonical manifest naming the artifact/run scope and "
            f"exact maximum call count. Failing closed before spawning.")

    reasons: list[str] = []
    for path in candidates:
        try:
            manifest, digest = load_manifest(path)
        except AuthorizationDenied as exc:
            reasons.append(f"{path.name}: {exc}")
            continue
        errs = validate_manifest(manifest, now=now)
        if errs:
            reasons.append(f"{path.name}: " + "; ".join(errs))
            continue
        if artifact not in manifest["artifact_scope"]:
            reasons.append(f"{path.name}: does not cover artifact {artifact!r} "
                           f"(scope {manifest['artifact_scope']})")
            continue
        if manifest["lane"] != lane:
            reasons.append(f"{path.name}: authorizes lane {manifest['lane']!r}, not {lane!r}")
            continue
        if manifest["run_scope"] != run_scope:
            reasons.append(f"{path.name}: authorizes run_scope {manifest['run_scope']!r}, "
                           f"not {run_scope!r}")
            continue
        posture = posture_violations(injected_runner=injected_runner)
        if posture:
            # A manifest cannot waive process posture; this is a hard stop, not a
            # reason to try the next candidate manifest.
            raise AuthorizationDenied("; ".join(posture))
        return ExecutionGrant(
            manifest_id=manifest["manifest_id"],
            manifest_path=str(path),
            manifest_digest=digest,
            created_by=manifest["created_by"],
            owner_authorization_ref=manifest["owner_authorization_ref"],
            artifact=artifact, lane=lane, run_scope=run_scope,
            provider_mode=manifest["provider_mode"],
            max_calls=min(int(manifest["max_calls"]), HARD_MAX_CALLS),
            expires_at=manifest["expires_at"],
            granted_at=now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )

    raise AuthorizationDenied(
        f"no canonical manifest authorizes artifact={artifact!r} lane={lane!r} "
        f"run_scope={run_scope!r}. Rejected candidates: " + " | ".join(reasons))


def gate_status(*, artifact: str, lane: str, run_scope: str,
                manifest_dir: str | Path | None = None,
                injected_runner: bool = False) -> dict:
    """Non-raising view of the gate, for reports and the prepare-only CLI."""
    try:
        grant = authorize(artifact=artifact, lane=lane, run_scope=run_scope,
                          manifest_dir=manifest_dir, injected_runner=injected_runner)
    except AuthorizationDenied as exc:
        directory = Path(manifest_dir) if manifest_dir is not None else MANIFEST_DIR
        return {
            "authorized": False,
            "reason": str(exc),
            "manifest_dir": str(directory),
            "manifests_present": [p.name for p in find_manifests(manifest_dir)],
            "live_execution_permitted": False,
        }
    return {"authorized": True, "grant": asdict(grant), "live_execution_permitted": True}
