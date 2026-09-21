"""SB-S23-002 — specialist scratch-state sandbox.

Isolates a temporary specialist's scratch state, inputs, outputs and cleanup
from the persistent persona/brand stores (``V20_TO_V23_IMPLEMENTATION_SPEC.md``
§5, SB-S23-002 row).

Layout (derived here; ``runtime/paths.py`` is not modified)::

    <SBOTS_HOME>/scratch/<bot>/<worker_id>/          mode 0o700, one per worker
        context/    read-only snapshots the parent materialized for the worker
        inputs/     earlier artifacts the parent handed in
        outputs/    what the worker produced
    <SBOTS_HOME>/receipts/<bot>/specialists/<worker_id>/   kept, attributable evidence

Guarantees
----------
* A specialist can only read what was materialized into its scratch directory
  and can only write inside it. Every path is validated *before* any
  filesystem call: absolute paths, ``..`` / ``.`` components, backslashes,
  NULs, symlinked components and anything that resolves outside the scratch
  root raise ``SandboxEscape`` and create nothing.
* ``materialize_context`` hands the worker *files* (JSON snapshots with a
  sha256), never live objects: a ``PersonaState`` / ``RuntimeState`` instance,
  a store path, or an ``admin_*`` reader is never exposed. The
  ``PersonaSnapshotResolver`` reads through ``runtime.isolation`` persona-scoped
  readers for the contract's own persona only and raises ``ScopeError`` for any
  other persona or bot.
* A resolver failure leaves ``context/FAILED.json`` and raises
  ``ContextError``; the lifecycle (SB-S23-008) must not run the adapter.
* ``retire`` moves only the explicitly kept, containment-validated outputs to
  the receipts tree (with a sha256 ``INDEX.json``) and deletes everything else.
  A ``keep`` entry that fails containment yields ``FAILED`` with nothing copied
  and the scratch left in place for audit. Retiring twice is a no-op.
* The sandbox never touches ``state/``, ``content/``, ``experiments/``,
  ``memory/`` or ``analytics/``. Adoption into persona stores is SB-S23-006.

Everything here is deterministic; no provider, no model call, no network.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Any, Protocol

from . import isolation, paths
from .jsonstore import now_iso
from .specialist_contract import WorkerContract, validate_contract

SCRATCH_ROOT_NAME = "scratch"
KEPT_ROOT_NAME = "specialists"
CONTEXT_DIR, INPUTS_DIR, OUTPUTS_DIR = "context", "inputs", "outputs"
FAILED_NOTE = f"{CONTEXT_DIR}/FAILED.json"
INDEX_FILE = "INDEX.json"

STATUS_PENDING, STATUS_RETIRED, STATUS_FAILED = "PENDING", "RETIRED", "FAILED"

# Stores a specialist may receive read-only snapshots of (the persona-scoped
# readers in ``runtime.isolation``). Nothing private-to-runtime is listed.
SNAPSHOT_KINDS: tuple[str, ...] = tuple(isolation.PERSONA_SCOPED_READERS)

_WIN_DRIVE = re.compile(r"^[A-Za-z]:")


class SandboxError(Exception):
    """Sandbox misuse (invalid contract, reuse, wrong state)."""


class SandboxEscape(SandboxError):
    """A path would leave the scratch directory. Nothing was created."""


class ScopeError(SandboxError):
    """A context ref points at another persona/bot."""


class ContextError(SandboxError):
    """A bounded context ref could not be materialized; the worker must not run."""


# --------------------------------------------------------------------------- #
# roots
# --------------------------------------------------------------------------- #
def scratch_root() -> Path:
    """``<SBOTS_HOME>/scratch`` (not created here)."""
    return paths.base() / SCRATCH_ROOT_NAME


def scratch_dir(contract: WorkerContract) -> Path:
    return scratch_root() / contract.bot / contract.worker_id


def kept_dir(contract: WorkerContract) -> Path:
    """Where retired-but-kept outputs land (created only at retire time)."""
    return paths.receipts_dir(contract.bot) / KEPT_ROOT_NAME / contract.worker_id


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _to_bytes(data: bytes | dict | list) -> bytes:
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    if isinstance(data, (dict, list)):
        return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    raise SandboxError(f"unsupported data type {type(data).__name__}; use bytes or dict/list")


# --------------------------------------------------------------------------- #
# resolvers — how the parent hands read-only snapshots to a worker
# --------------------------------------------------------------------------- #
class ContextResolver(Protocol):
    def read(self, ref: dict) -> bytes | dict: ...


class DictContextResolver:
    """Fixture resolver: ``ref['id']`` (or ``ref['evidence_id']``) -> data.

    Returns a deep copy so the worker can never reach the fixture's objects.
    """

    def __init__(self, data: dict[str, Any]):
        self._data = dict(data)

    def read(self, ref: dict) -> bytes | dict:
        key = ref.get("id") or ref.get("evidence_id")
        if key not in self._data:
            raise KeyError(f"unknown context ref {key!r}")
        return copy.deepcopy(self._data[key])


class PersonaSnapshotResolver:
    """Read-only snapshots of the contract's OWN persona through the sanctioned
    ``runtime.isolation`` persona-scoped readers.

    ``ref`` must be ``{"kind": <SNAPSHOT_KINDS>, "bot": <bot>, "persona": <persona>}``
    (optionally ``"limit": n``). Any other persona or bot raises ``ScopeError``.
    The result is a plain dict of plain records — never a state object, a path
    or an admin reader.
    """

    def __init__(self, bot: str, persona: str):
        self.bot, self.persona = bot, persona

    def read(self, ref: dict) -> dict:
        if not isinstance(ref, dict):
            raise ScopeError("context ref must be a dict")
        if ref.get("bot") != self.bot or ref.get("persona") != self.persona:
            raise ScopeError(
                f"ref scope {ref.get('bot')!r}/{ref.get('persona')!r} is not this "
                f"resolver's {self.bot!r}/{self.persona!r}")
        kind = ref.get("kind")
        if kind not in SNAPSHOT_KINDS:
            raise ScopeError(f"unknown or non-snapshot kind {kind!r}; allowed {SNAPSHOT_KINDS}")
        records = isolation.persona_records(self.bot, self.persona, kind)
        limit = ref.get("limit")
        if isinstance(limit, int) and not isinstance(limit, bool) and limit >= 0:
            records = records[-limit:] if limit else []
        return {"kind": kind, "bot": self.bot, "persona": self.persona,
                "snapshot_at": now_iso(), "records": copy.deepcopy(records)}


# --------------------------------------------------------------------------- #
# Sandbox
# --------------------------------------------------------------------------- #
class Sandbox:
    def __init__(self, contract: WorkerContract):
        errs = validate_contract(contract)
        if errs:
            raise SandboxError("invalid contract: " + "; ".join(errs))
        self.contract = contract
        self.root = scratch_dir(contract)
        self.status = STATUS_PENDING
        self._created = False
        self._materialized = False
        self._retired_at: str | None = None

    # -- lifecycle ---------------------------------------------------------
    def create(self) -> Path:
        """Create the private scratch tree (0o700). Refuses an existing dir:
        a worker id is never reused."""
        if self._created or self.root.exists() or self.root.is_symlink():
            raise SandboxError(f"scratch for {self.contract.worker_id} already exists; "
                               f"a worker id is never reused")
        self.root.parent.mkdir(parents=True, exist_ok=True)
        self.root.mkdir(mode=0o700)
        os.chmod(self.root, 0o700)            # umask-independent
        if self.root.is_symlink():            # defensive: never operate through a link
            raise SandboxEscape("scratch root is a symlink")
        for sub in (CONTEXT_DIR, INPUTS_DIR, OUTPUTS_DIR):
            (self.root / sub).mkdir(mode=0o700)
        self._created = True
        return self.root

    def _require_live(self) -> None:
        if not self._created:
            raise SandboxError("sandbox not created")
        if self.status != STATUS_PENDING:
            raise SandboxError(f"sandbox is {self.status}; no further access")

    # -- containment -------------------------------------------------------
    def _resolve(self, relpath: Any) -> Path:
        """Map a worker-relative path to a contained absolute path, or raise
        ``SandboxEscape`` BEFORE any filesystem write."""
        if not isinstance(relpath, str) or not relpath or relpath != relpath.strip():
            raise SandboxEscape(f"invalid relative path {relpath!r}")
        if relpath.startswith("/") or "\\" in relpath or "\x00" in relpath or _WIN_DRIVE.match(relpath):
            raise SandboxEscape(f"absolute or non-portable path {relpath!r}")
        parts = relpath.split("/")
        if any(part in ("", ".", "..") for part in parts):
            raise SandboxEscape(f"path {relpath!r} contains an empty, '.' or '..' component")
        root_real = self.root.resolve()
        # Walk existing prefixes: a symlinked component anywhere is an escape.
        cur = self.root
        for part in parts:
            cur = cur / part
            if cur.is_symlink():
                raise SandboxEscape(f"path {relpath!r} traverses a symlink at {part!r}")
            if not cur.exists():
                break
        candidate = self.root / relpath
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError) as exc:
            raise SandboxEscape(f"path {relpath!r} cannot be resolved: {exc}") from exc
        if resolved != root_real and root_real not in resolved.parents:
            raise SandboxEscape(f"path {relpath!r} resolves outside the scratch root")
        return candidate

    # -- I/O ---------------------------------------------------------------
    def write(self, relpath: str, data: bytes | dict | list) -> Path:
        self._require_live()
        p = self._resolve(relpath)
        payload = _to_bytes(data)
        if p.exists() and (p.is_symlink() or not p.is_file()):
            raise SandboxEscape(f"{relpath!r} exists and is not a regular file")
        _atomic_write_bytes(p, payload)
        return p

    def read(self, relpath: str) -> bytes:
        self._require_live()
        p = self._resolve(relpath)
        if p.is_symlink() or not p.is_file():
            raise SandboxEscape(f"{relpath!r} is not a regular file inside the sandbox")
        return p.read_bytes()

    def list(self) -> list[str]:
        self._require_live()
        out: list[str] = []
        for p in self.root.rglob("*"):
            if p.is_symlink() or not p.is_file():
                continue
            out.append(p.relative_to(self.root).as_posix())
        return sorted(out)

    def sha256(self, relpath: str) -> str:
        return _sha256(self.read(relpath))

    # -- context -----------------------------------------------------------
    def materialize_context(self, resolver: ContextResolver) -> list[dict]:
        """Snapshot every ``bounded_context_ref`` into ``context/`` as files.

        Returns ``[{"index", "ref", "path", "sha256", "bytes"}]`` — copies of the
        refs plus file metadata, never the resolver's live objects. On any
        resolver failure, writes ``context/FAILED.json`` and raises
        ``ContextError``; the worker must not be run.
        """
        self._require_live()
        if self._materialized:
            raise SandboxError("context already materialized")
        out: list[dict] = []
        for n, ref in enumerate(self.contract.bounded_context_refs):
            try:
                data = resolver.read(ref)
                payload = _to_bytes(data)
            except Exception as exc:                        # noqa: BLE001 - recorded, not hidden
                note = {"index": n, "ref": copy.deepcopy(ref), "error": f"{type(exc).__name__}: {exc}",
                        "at": now_iso(), "materialized_before_failure": [o["path"] for o in out]}
                _atomic_write_bytes(self.root / FAILED_NOTE, _to_bytes(note))
                raise ContextError(
                    f"context ref {n} could not be materialized ({type(exc).__name__}); "
                    f"see {FAILED_NOTE}") from exc
            digest = _sha256(payload)
            ext = "json" if isinstance(data, (dict, list)) else "bin"
            rel = f"{CONTEXT_DIR}/{n:03d}-{digest[:8]}.{ext}"
            _atomic_write_bytes(self._resolve(rel), payload)
            out.append({"index": n, "ref": copy.deepcopy(ref), "path": rel,
                        "sha256": digest, "bytes": len(payload)})
        self._materialized = True
        return out

    def context_failed(self) -> bool:
        return (self.root / FAILED_NOTE).is_file()

    # -- retire ------------------------------------------------------------
    def retire(self, *, keep: list[str] | None = None) -> str:
        """Keep attributable outputs under the receipts tree, delete the rest.

        Returns ``RETIRED`` or ``FAILED``. A second call returns the recorded
        status without error. A ``keep`` entry failing containment => ``FAILED``,
        nothing copied, scratch left in place for audit.
        """
        if self.status != STATUS_PENDING:
            return self.status
        if not self._created:
            raise SandboxError("sandbox not created")
        keep = list(keep or [])
        payloads: list[tuple[str, bytes]] = []
        try:
            for rel in keep:
                payloads.append((rel, self.read(rel)))     # containment + regular-file checks
        except SandboxError:
            self.status = STATUS_FAILED
            self._retired_at = now_iso()
            return self.status
        try:
            if payloads:
                dest_root = kept_dir(self.contract)
                index = []
                for rel, data in payloads:
                    dest = dest_root / rel
                    if dest_root.resolve() not in dest.resolve().parents:
                        raise SandboxEscape(f"kept path {rel!r} escapes the receipts dir")
                    _atomic_write_bytes(dest, data)
                    index.append({"path": rel, "sha256": _sha256(data), "bytes": len(data)})
                _atomic_write_bytes(dest_root / INDEX_FILE, _to_bytes({
                    "worker_id": self.contract.worker_id,
                    "parent_run_id": self.contract.parent_run_id,
                    "bot": self.contract.bot, "persona": self.contract.persona,
                    "role": self.contract.role, "retired_at": now_iso(),
                    "kept": index, "provenance": self.contract.provenance,
                }))
            shutil.rmtree(self.root)
            self.status = STATUS_RETIRED
        except Exception:                                   # noqa: BLE001 - status is the signal
            self.status = STATUS_FAILED
        self._retired_at = now_iso()
        return self.status

    @property
    def retired_at(self) -> str | None:
        return self._retired_at

    def mode(self) -> int:
        return stat.S_IMODE(os.lstat(self.root).st_mode)
