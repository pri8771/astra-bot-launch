"""SB-R07-072 — persistent-host preflight for V0.7 recurring liveness.

Records observable facts about the machine this process is running on and
decides whether it is an **owner-controlled persistent host** suitable for
V0.7 OS-scheduled worker invocations.

Honesty rules
-------------
* No guessing. Missing facts are recorded as missing, not inferred as OK.
* A Cursor Cloud / CCR / overlay / ephemeral agent environment is **not** a
  persistent host. The verdict must say so explicitly.
* This module never installs a scheduler and never claims LIVE V0.7 acceptance.
* Secrets are recorded as presence booleans only.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

PREFLIGHT_ID = "SB-R07-072"
SCHEMA_VERSION = 1

VERDICT_SUITABLE = "SUITABLE_PERSISTENT_HOST_CANDIDATE"
VERDICT_UNSUITABLE = "UNSUITABLE_NOT_PERSISTENT_OWNER_HOST"
VERDICT_INCONCLUSIVE = "INCONCLUSIVE_NEED_OWNER_CONFIRMATION"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _cmd(args: list[str], timeout: float = 10) -> dict:
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        return {"argv": args, "returncode": proc.returncode, "output": out[:400]}
    except FileNotFoundError:
        return {"argv": args, "returncode": None, "output": "executable not found"}
    except Exception as exc:  # noqa: BLE001
        return {"argv": args, "returncode": None, "output": f"{type(exc).__name__}: {exc}"}


def _flock_available() -> bool:
    try:
        import fcntl  # noqa: F401
        return True
    except ImportError:
        return False


def _fs_type(path: str) -> str | None:
    row = _cmd(["findmnt", "-no", "FSTYPE", path])
    if row["returncode"] == 0 and row["output"]:
        return row["output"].splitlines()[0].strip() or None
    return None


@dataclass
class HostPreflight:
    """Structured preflight receipt. ``suitable`` is never True on ephemeral hosts."""

    preflight_id: str = PREFLIGHT_ID
    schema_version: int = SCHEMA_VERSION
    recorded_at: str = field(default_factory=_now_iso)
    host: dict = field(default_factory=dict)
    python: dict = field(default_factory=dict)
    repo: dict = field(default_factory=dict)
    locking: dict = field(default_factory=dict)
    scheduling: dict = field(default_factory=dict)
    permissions: dict = field(default_factory=dict)
    zero_spend: dict = field(default_factory=dict)
    persistence_signals: dict = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    verdict: str = VERDICT_INCONCLUSIVE
    suitable_for_v07_live_scheduler: bool = False
    live_claim: bool = False
    evidence_class: str = "ENGINEERING"
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def collect(*, repo_root: str | Path | None = None,
            owner_attested_persistent: bool = False) -> HostPreflight:
    """Observe the current host and return an honest suitability receipt.

    ``owner_attested_persistent`` is an explicit owner/lead assertion that this
    machine is the durable V0.7 host. It cannot override ephemeral markers.
    """
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parent.parent
    hostname = socket.gethostname()[:64]
    system = platform.system()
    root_fs = _fs_type("/")
    workspace_fs = _fs_type(str(root)) or _fs_type("/workspace")

    systemctl = shutil.which("systemctl")
    crontab = shutil.which("crontab")
    launchctl = shutil.which("launchctl")
    schtasks = shutil.which("schtasks")

    systemd_user = _cmd(["systemctl", "--user", "is-system-running"]) if systemctl else {
        "argv": ["systemctl", "--user", "is-system-running"],
        "returncode": None, "output": "systemctl not on PATH",
    }

    ephemeral_markers: list[str] = []
    host_l = hostname.lower()
    if host_l in {"cursor", "codespaces", "sandbox"} or host_l.startswith("cursor-"):
        ephemeral_markers.append(f"hostname={hostname!r} indicates a cloud/agent host")
    if root_fs in {"overlay", "tmpfs", "ramfs"}:
        ephemeral_markers.append(f"root filesystem type {root_fs!r} is ephemeral/overlay")
    if workspace_fs in {"overlay", "tmpfs", "ramfs"}:
        ephemeral_markers.append(f"workspace filesystem type {workspace_fs!r} is ephemeral/overlay")
    if os.environ.get("CURSOR_AGENT") or os.environ.get("CURSOR"):
        ephemeral_markers.append("CURSOR/CURSOR_AGENT environment markers present")
    if str(root).startswith("/workspace") and host_l == "cursor":
        ephemeral_markers.append("repo under /workspace on hostname cursor (Cloud Agent pattern)")

    blockers: list[str] = []
    if ephemeral_markers:
        blockers.append(
            "host appears ephemeral / non-persistent (Cloud Agent, overlay, or "
            "temporary environment); V0.7 LIVE recurring liveness requires an "
            "owner-controlled persistent machine")
        blockers.extend(ephemeral_markers)
    if not _flock_available():
        blockers.append("fcntl.flock unavailable; POSIX strong locking path not present")
    if system == "Linux":
        if not systemctl and not crontab:
            blockers.append("neither systemctl nor crontab available for OS scheduling")
        elif systemctl and systemd_user.get("output", "").strip().lower() in {
            "offline", "inactive", "unknown",
        }:
            blockers.append(
                f"systemd user instance is {systemd_user.get('output')!r}; "
                f"user timers are not ready on this host")
        if crontab is None and systemctl and "offline" in (systemd_user.get("output") or ""):
            blockers.append("no usable user-level scheduler (systemd user offline; no crontab)")
    elif system == "Darwin" and not launchctl:
        blockers.append("launchctl unavailable on Darwin")
    elif system == "Windows" and not schtasks:
        blockers.append("schtasks unavailable on Windows")

    # Spend posture: never print secret values.
    api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    oauth = bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"))
    if api_key:
        blockers.append(
            "ANTHROPIC_API_KEY is present; subscription-only / zero-new-spend "
            "posture is violated for live adaptive work on this host")

    suitable = False
    if ephemeral_markers:
        verdict = VERDICT_UNSUITABLE
    elif blockers:
        verdict = VERDICT_UNSUITABLE
    elif owner_attested_persistent:
        verdict = VERDICT_SUITABLE
        suitable = True
    else:
        verdict = VERDICT_INCONCLUSIVE
        blockers.append(
            "observable tooling looks present, but owner has not attested this "
            "machine as the persistent V0.7 host; do not install LIVE schedulers "
            "or claim V0.7 acceptance without that attestation")

    git_present = (root / ".git").exists()
    if not git_present:
        # social-bots/ often lives inside the repo root one level up.
        git_present = (root.parent / ".git").exists()

    return HostPreflight(
        host={
            "hostname": hostname,
            "platform": system,
            "platform_release": platform.release()[:64],
            "machine": platform.machine(),
            "root_fs": root_fs,
            "workspace_fs": workspace_fs,
        },
        python={
            "version": platform.python_version(),
            "executable": sys_executable(),
        },
        repo={
            "path": str(root.resolve()),
            "git_dir_present": git_present,
        },
        locking={
            "fcntl_flock_available": _flock_available(),
            "strong_path": "posix-flock" if _flock_available() else "unavailable",
        },
        scheduling={
            "systemctl": systemctl,
            "crontab": crontab,
            "launchctl": launchctl,
            "schtasks": schtasks,
            "systemd_user": systemd_user,
        },
        permissions={
            "uid": getattr(os, "getuid", lambda: None)(),
            "euid": getattr(os, "geteuid", lambda: None)(),
            "writable_repo": os.access(root, os.W_OK),
        },
        zero_spend={
            "ANTHROPIC_API_KEY_present": api_key,
            "CLAUDE_CODE_OAUTH_TOKEN_present": oauth,
            "policy": "no PAYG / no new spend; subscription route only when authorized",
        },
        persistence_signals={
            "ephemeral_markers": ephemeral_markers,
            "cursor_env": bool(os.environ.get("CURSOR") or os.environ.get("CURSOR_AGENT")),
        },
        blockers=blockers,
        verdict=verdict,
        suitable_for_v07_live_scheduler=suitable,
        live_claim=False,
        evidence_class="ENGINEERING",
        notes=(
            "SB-R07-072 preflight only. Never claim V0.7 LIVE acceptance from "
            "this receipt. Ephemeral Cloud Agent / CCR / overlay hosts must be "
            "UNSUITABLE; continue dependency-safe non-LIVE artifacts."
        ),
    )


def sys_executable() -> str:
    import sys
    return sys.executable


def write_receipt(preflight: HostPreflight, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(preflight.to_dict(), indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path
