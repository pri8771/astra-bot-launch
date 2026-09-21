"""SB-V07-001 — consuming ChatGPT lead direction from GitHub, without a human relay.

V0.7 requires that a scheduled worker session picks up new lead direction from
GitHub *without the owner copying and pasting it*. This module is that path.

How it works
------------
Plain ``git`` against the canonical coordination branch. A fetch followed by
``git show <ref>:<path>`` reads lead direction straight out of the repository:

* no ``gh`` CLI, no GitHub API token and no MCP transport is required — the
  clone's existing remote credentials are the only thing needed;
* nothing is written to the remote, so consuming direction can never mutate
  canonical state;
* the exact commit SHA the direction was read from is recorded, so an audit can
  say precisely which coordination state a given invocation acted on.

Direction sources, in precedence order
--------------------------------------
1. ``social-bots/directions/<lane>.json`` — the machine-readable contract. The
   lead writes it; a worker only reads it.
2. ``social-bots/STATE.json`` ``worker_lanes.<lane>`` — the fallback, so this
   works against canonical state exactly as it exists today, with no migration
   required before the first scheduled run.

Offline behaviour is degraded, never dishonest: if the fetch fails, the last
locally known ref is used and ``fetch_ok: false`` is recorded with the error, so
a reader can tell a fresh read from a stale one.

Halting
-------
A direction may tell a lane to stand down (``halt``). The fallback infers it from
a lane ``activity`` that reads frozen/halted/stopped/paused. A halted lane claims
no task; it still emits its heartbeat and its invocation receipt, because "the
session ran and was correctly told to do nothing" is itself the evidence.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

CANONICAL_BRANCH = "chatgpt/social-bots-plan-20260920"
DEFAULT_REMOTE = "origin"

STATE_PATH = "social-bots/STATE.json"
DIRECTIONS_PATH_TEMPLATE = "social-bots/directions/{lane}.json"

SOURCE_DIRECTIONS_FILE = "directions-file"
SOURCE_STATE_FALLBACK = "state-json-fallback"
SOURCE_UNAVAILABLE = "unavailable"

# Lane activity words that mean "do not claim work".
_HALT_WORDS = re.compile(r"frozen|halt|stopped|stand[_\- ]?down|paused|suspended", re.I)

_GIT_TIMEOUT_S = 120


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


class DirectionError(Exception):
    """Raised when direction cannot be read at all (not merely stale)."""


def _git(args: list[str], repo_root: Path, *, check: bool = True
         ) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True,
                          text=True, timeout=_GIT_TIMEOUT_S, check=check)


@dataclass
class Direction:
    """What the lead currently tells this lane to do."""

    lane: str
    source: str
    direction_id: str | None
    halt: bool
    assignment: str | None
    artifacts: list = field(default_factory=list)
    bots: list = field(default_factory=list)
    live_model_calls_authorized: bool = False
    notes: str | None = None
    canonical_ref: str | None = None
    canonical_sha: str | None = None
    fetch_ok: bool = False
    fetch_error: str | None = None
    raw_digest: str | None = None
    consumed_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


def fetch_canonical(repo_root: str | Path, *, remote: str = DEFAULT_REMOTE,
                    branch: str = CANONICAL_BRANCH) -> tuple[bool, str | None]:
    """Fetch the canonical coordination branch. Returns ``(ok, error)``.

    Read-only against the remote: a fetch never pushes and never rewrites local
    branches, so consuming direction cannot disturb another lane's work.
    """
    repo_root = Path(repo_root)
    try:
        proc = _git(["fetch", remote, branch], repo_root, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()
        return False, tail[-1][:200] if tail else f"git fetch exit {proc.returncode}"
    return True, None


def resolve_ref(repo_root: str | Path, *, remote: str = DEFAULT_REMOTE,
                branch: str = CANONICAL_BRANCH) -> tuple[str, str]:
    """Return ``(ref, sha)`` for the canonical branch as this clone currently sees it."""
    repo_root = Path(repo_root)
    for ref in (f"{remote}/{branch}", branch):
        proc = _git(["rev-parse", "--verify", "--quiet", ref], repo_root, check=False)
        sha = (proc.stdout or "").strip()
        if proc.returncode == 0 and sha:
            return ref, sha
    raise DirectionError(
        f"canonical branch {branch!r} is not present in this clone (tried "
        f"{remote}/{branch} and {branch}); a scheduled worker cannot read direction")


def read_file_at(repo_root: str | Path, ref: str, path: str) -> str | None:
    """``git show <ref>:<path>``; None when the path does not exist at that ref."""
    proc = _git(["show", f"{ref}:{path}"], Path(repo_root), check=False)
    if proc.returncode != 0:
        return None
    return proc.stdout


def _from_directions_file(lane: str, text: str) -> dict:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DirectionError(f"directions file for lane {lane!r} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise DirectionError(f"directions file for lane {lane!r} is not a JSON object")
    if data.get("lane") not in (None, lane):
        raise DirectionError(
            f"directions file declares lane {data.get('lane')!r}, not {lane!r}")
    return {
        "direction_id": data.get("direction_id"),
        "halt": bool(data.get("halt", False)),
        "assignment": data.get("assignment"),
        "artifacts": list(data.get("artifacts") or []),
        "bots": list(data.get("bots") or []),
        "live_model_calls_authorized": bool(data.get("live_model_calls_authorized", False)),
        "notes": data.get("notes"),
    }


def _from_state(lane: str, text: str) -> dict:
    try:
        state = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DirectionError(f"STATE.json is not valid JSON: {exc}") from exc
    if not isinstance(state, dict):
        raise DirectionError("STATE.json is not a JSON object")
    lanes = state.get("worker_lanes") or {}
    entry = lanes.get(lane)
    if not isinstance(entry, dict):
        # Lane keys in STATE.json are logical ("core"), while report directories
        # are host-flavoured ("windows-core"); fall back to matching on the branch
        # name instead of forcing the two naming schemes to agree.
        #
        # The match must be UNIQUE. Taking the first of several candidates would
        # silently bind a session to the wrong lane — and if the lane the lead
        # actually froze is the one not picked, the halt is missed and the worker
        # claims work it was told to stand down from. Ambiguity fails closed.
        matches = [(key, value) for key, value in lanes.items()
                   if isinstance(value, dict) and lane in str(value.get("branch", ""))]
        if len(matches) > 1:
            raise DirectionError(
                f"lane {lane!r} matches {len(matches)} STATE.json worker_lanes "
                f"entries by branch ({sorted(k for k, _ in matches)}); refusing to "
                f"guess which direction applies")
        if matches:
            entry = matches[0][1]
    if not isinstance(entry, dict):
        raise DirectionError(f"STATE.json has no worker_lanes entry matching lane {lane!r}")
    activity = str(entry.get("activity") or "")
    review = (state.get("lead_review") or {}).get("review_id")
    public = state.get("public_actions") or {}
    return {
        "direction_id": review,
        "halt": bool(_HALT_WORDS.search(activity)),
        "assignment": entry.get("assignment"),
        "artifacts": [],
        "bots": list((state.get("runtime_scope") or {}).get("autonomous_bots") or []),
        # Absent an explicit grant, live model calls are NOT authorized. The
        # canonical flag is a hard negative today; treat a missing flag the same.
        "live_model_calls_authorized": not bool(public.get("no_further_live_model_calls", True)),
        "notes": entry.get("activity"),
    }


def consume(lane: str, repo_root: str | Path, *, remote: str = DEFAULT_REMOTE,
            branch: str = CANONICAL_BRANCH, fetch: bool = True) -> Direction:
    """Fetch and read the current lead direction for ``lane``.

    Never raises for a failed fetch (that is recorded and the last known ref is
    used). Raises ``DirectionError`` only when no canonical ref or no direction
    source can be read at all.
    """
    repo_root = Path(repo_root)
    fetch_ok, fetch_error = (False, "fetch skipped by caller")
    if fetch:
        fetch_ok, fetch_error = fetch_canonical(repo_root, remote=remote, branch=branch)

    ref, sha = resolve_ref(repo_root, remote=remote, branch=branch)

    directions_text = read_file_at(repo_root, ref, DIRECTIONS_PATH_TEMPLATE.format(lane=lane))
    if directions_text:
        fields = _from_directions_file(lane, directions_text)
        source, raw = SOURCE_DIRECTIONS_FILE, directions_text
    else:
        state_text = read_file_at(repo_root, ref, STATE_PATH)
        if not state_text:
            raise DirectionError(
                f"neither {DIRECTIONS_PATH_TEMPLATE.format(lane=lane)} nor {STATE_PATH} "
                f"exists at {ref}")
        fields = _from_state(lane, state_text)
        source, raw = SOURCE_STATE_FALLBACK, state_text

    return Direction(lane=lane, source=source, canonical_ref=ref, canonical_sha=sha,
                     fetch_ok=fetch_ok, fetch_error=fetch_error,
                     raw_digest=_sha256_text(raw), **fields)


def acknowledge(direction: Direction, *, session_id: str, invocation_id: str | None,
                root: str | Path | None = None) -> Path:
    """Record that this session consumed this exact direction.

    Written to ``worker-reports/<lane>/DIRECTION_ACK.json``. The acknowledgement
    is the worker's half of the loop: the lead can see, from the repository
    alone, which canonical SHA a scheduled session actually acted on. It records
    consumption only — never agreement, and never acceptance.
    """
    base = Path(root) if root is not None else Path(__file__).resolve().parent.parent
    path = base / "worker-reports" / direction.lane / "DIRECTION_ACK.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "acknowledged_at": _now_iso(),
        "session_id": session_id,
        "invocation_id": invocation_id,
        "direction": direction.to_dict(),
        "acknowledgement_means": "consumed and acted on; not agreement or acceptance",
    }
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path
