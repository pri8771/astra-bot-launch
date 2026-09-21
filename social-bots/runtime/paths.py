"""Namespace path helpers enforcing per-bot / per-persona isolation.

Every runtime writes only under its own namespace. Cross-bot facts must go
through the explicit ``shared`` namespace, never into another bot's private tree.
This mirrors the ``pri8771/bots`` memory convention (per-agent dirs; never write
into another agent's directory) — see social-bots/SOURCE_REUSE_MAP.md.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

# Repo-relative root: .../social-bots
ROOT = Path(__file__).resolve().parent.parent

BOTS = ("social-a", "social-b", "social-c")
SHARED = "shared"

_SAFE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")


def _check(ns: str) -> str:
    if ns != SHARED and not _SAFE.match(ns):
        raise ValueError(f"unsafe namespace: {ns!r}")
    return ns


def base() -> Path:
    """Runtime data root. Overridable via SBOTS_HOME for tests / alt hosts."""
    return Path(os.environ.get("SBOTS_HOME", str(ROOT)))


def _kind_dir(kind: str, ns: str) -> Path:
    p = base() / kind / _check(ns)
    p.mkdir(parents=True, exist_ok=True)
    return p


def state_dir(ns: str) -> Path:
    return _kind_dir("state", ns)


def memory_dir(ns: str) -> Path:
    return _kind_dir("memory", ns)


def experiments_dir(ns: str) -> Path:
    return _kind_dir("experiments", ns)


def receipts_dir(ns: str) -> Path:
    return _kind_dir("receipts", ns)


def analytics_dir(ns: str) -> Path:
    return _kind_dir("analytics", ns)


def leases_dir() -> Path:
    p = base() / "leases"
    p.mkdir(parents=True, exist_ok=True)
    return p


def content_dir(ns: str) -> Path:
    return _kind_dir("content", ns)
