"""Durable round-robin cursor for scheduled due-work selection (V1.7 §A).

``bin/worker_once.py`` runs at most ONE bounded unit per scheduled invocation and
used to try its candidate runtimes in a fixed order. When the first runtime
always has claimable work, the others never run: first-bot starvation. The
cursor here is a small JSON file shared by every scheduler process on the host
(next to the leases, under the runtime root): after a claim of bot X the next
invocation starts with the bot AFTER X, so claimable bots are served in turn
whichever process wakes up.

Properties
----------
- Durable and cross-process: written atomically (``jsonstore.write_json``) and
  re-read by every invocation; a restart continues the rotation.
- Fail-safe: a missing, corrupt or foreign cursor degrades to the caller's
  order — selection is never blocked by the cursor itself.
- Only a real claim advances the cursor. Skipped (lease-held) candidates do not,
  so a bot skipped this time is first in line the next time round.
- Deterministic: pure function of (candidates, cursor) — no clock involved.
"""
from __future__ import annotations

from pathlib import Path

from . import paths
from .jsonstore import now_iso, read_json, write_json

SCHEMA_VERSION = 1
CURSOR_FILE = "claim_rotation.json"


def cursor_path(home: str | Path | None = None) -> Path:
    base = Path(home) if home is not None else paths.base()
    return base / "scheduler" / CURSOR_FILE


def read_cursor(home: str | Path | None = None) -> dict | None:
    try:
        data = read_json(cursor_path(home), default=None)
    except (OSError, ValueError):                     # unreadable/corrupt: no cursor
        return None
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION \
            or not isinstance(data.get("last_claimed"), str):
        return None
    return data


def ordered(bots: list[str], home: str | Path | None = None) -> list[str]:
    """The candidate order for this invocation: rotated past the last claimed bot.

    A last-claimed bot that is no longer a candidate (config changed) leaves the
    caller's order untouched.
    """
    bots = list(bots)
    cursor = read_cursor(home)
    if cursor is None or cursor["last_claimed"] not in bots:
        return bots
    i = bots.index(cursor["last_claimed"])
    return bots[i + 1:] + bots[:i + 1]


def record_claim(bot: str, bots: list[str], home: str | Path | None = None, *,
                 session_id: str | None = None) -> dict:
    """Advance the cursor after a REAL claim (atomic write, never partial)."""
    data = {
        "schema_version": SCHEMA_VERSION,
        "last_claimed": bot,
        "claimed_at": now_iso(),
        "candidates": list(bots),
        "session_id": session_id,
    }
    write_json(cursor_path(home), data)
    return data
