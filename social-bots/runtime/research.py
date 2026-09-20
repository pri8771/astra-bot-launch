"""Research inputs = captured evidence with provenance, never canned lists.

A *signal* is a real observation captured from the outside world with a source,
a URL (or explicit provenance), and a capture timestamp. The pipeline consumes
signals; it never invents them. Live capture (e.g. from a web search the worker
actually ran) is written into a signals inbox as evidence; deterministic tests
read fixture signals that are clearly marked as fixtures.

This module deliberately does NOT fabricate trend data. If no real signal exists,
the correct behaviour is "no new evidence" — which the decision loop turns into a
legitimate NO_ACTION, not a fabricated topic.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path

from . import paths
from .jsonstore import read_jsonl, append_jsonl, now_iso


@dataclass
class Signal:
    id: str
    title: str
    summary: str
    source: str
    url: str | None
    captured_at: str
    provenance: str            # 'live-capture' | 'fixture' | 'operator-supplied'
    tags: list[str]

    @staticmethod
    def make(title: str, summary: str, source: str, url: str | None,
             provenance: str, tags: list[str]) -> "Signal":
        basis = f"{title}|{url or source}".encode()
        return Signal(
            id="sig-" + hashlib.sha256(basis).hexdigest()[:12],
            title=title, summary=summary, source=source, url=url,
            captured_at=now_iso(), provenance=provenance, tags=tags,
        )


def _inbox(bot: str) -> Path:
    return paths.memory_dir(bot) / "signals_inbox.jsonl"


def capture(bot: str, signal: Signal) -> None:
    """Persist a captured signal as durable evidence."""
    if signal.provenance not in {"live-capture", "fixture", "operator-supplied"}:
        raise ValueError(f"bad provenance {signal.provenance!r}")
    append_jsonl(_inbox(bot), asdict(signal))


def load_signals(bot: str) -> list[dict]:
    return read_jsonl(_inbox(bot))


def evidence_fingerprint(signals: list[dict]) -> str | None:
    """Stable hash of the *set* of signal ids. None if empty. (Diagnostic only.)"""
    if not signals:
        return None
    ids = sorted(s["id"] for s in signals)
    return hashlib.sha256("|".join(ids).encode()).hexdigest()[:16]


def unconsumed_signals(bot: str, consumed_ids) -> list[dict]:
    """Signals in inbox arrival order whose id is NOT in ``consumed_ids``.

    This is the correct evidence-consumption primitive: it tracks *which specific
    signals* have been decided upon, not a whole-inbox fingerprint. A later signal
    arriving after earlier ones were consumed is returned here; a batch of new
    signals is returned in full so none can be silently skipped when the caller
    consumes one per cycle. De-duplicates by id (first occurrence wins) so a
    signal captured twice is a single unit of evidence.
    """
    consumed = set(consumed_ids or ())
    out, seen = [], set()
    for s in load_signals(bot):
        sid = s["id"]
        if sid in consumed or sid in seen:
            continue
        seen.add(sid)
        out.append(s)
    return out
