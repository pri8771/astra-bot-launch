#!/usr/bin/env python3
"""Record REAL facts about the host this worker is running on.

Honest host evidence for the SB-V03-004 supported-locking-path artifact and the
SB-V07-WIN-001 recurring-execution artifact. It records only what it can observe
on THIS machine. Secrets are recorded as booleans only — the value of
``ANTHROPIC_API_KEY`` is never printed, logged or stored.

No network, no external effect, no spend. Prints a JSON document to stdout.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _cmd(args: list[str]) -> str | None:
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=15)
        return (out.stdout or out.stderr).strip() or None
    except Exception:
        return None


def _flock_available() -> bool:
    try:
        import fcntl  # noqa: F401
        return True
    except Exception:
        return False


def _is_wsl() -> bool:
    # WSL exposes "microsoft"/"WSL" in the kernel release/version.
    rel = (platform.release() + " " + platform.version()).lower()
    if "microsoft" in rel or "wsl" in rel:
        return True
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except Exception:
        return False


def collect() -> dict:
    system = platform.system()  # 'Linux' | 'Windows' | 'Darwin'
    is_windows = system == "Windows"
    is_wsl = _is_wsl()

    # Windows Task Scheduler availability (schtasks) — only meaningful on Windows.
    schtasks = shutil.which("schtasks") if is_windows else None
    # POSIX user-level scheduling primitives (cron / systemd --user).
    crontab = shutil.which("crontab")
    systemctl = shutil.which("systemctl")

    return {
        "recorded_by": "social-bots/bin/host_evidence.py",
        "os": {
            "system": system,
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "is_windows": is_windows,
            "is_wsl": is_wsl,
            "platform": sys.platform,
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "tooling": {
            "git_version": _cmd(["git", "--version"]),
            "claude_cli_version": _cmd(["claude", "--version"]),
            "claude_cli_on_path": bool(shutil.which("claude")),
        },
        "locking": {
            "fcntl_flock_available": _flock_available(),
            "strong_path": ("posix-flock" if _flock_available()
                            else "native-windows-required"),
        },
        "scheduling": {
            "windows_task_scheduler_available": bool(schtasks),
            "posix_crontab_available": bool(crontab),
            "systemd_user_available": bool(systemctl),
        },
        "secrets_presence_booleans_only": {
            # NEVER print the value. Boolean presence only, per artifact billing guard.
            "ANTHROPIC_API_KEY_present": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "CLAUDE_CODE_OAUTH_TOKEN_present": bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")),
        },
        "repo_location": str(Path(__file__).resolve().parent.parent),
    }


def main() -> int:
    print(json.dumps(collect(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
