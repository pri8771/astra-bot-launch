"""Sanitized start / finish / failure / review receipts + an append-only index.

Every bounded work unit writes a start receipt, then exactly one terminal
receipt (finish or failure). Receipts are the audit trail ChatGPT reviews;
they never contain secrets. Review receipts are content-review anchors, not
worker lifecycle completion events.
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path

from . import paths
from .jsonstore import write_json, append_jsonl, now_iso

# Defensive redaction: never let a token-shaped string reach a committed receipt.
_SECRET_HINT = re.compile(
    r"(password|passwd|secret|token|apikey|api_key|bearer|cookie|totp|"
    r"authorization|recovery.?code|private.?key)", re.I)


def _sanitize(obj):
    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            if _SECRET_HINT.search(str(k)):
                clean[k] = "[REDACTED-REF]"
            else:
                clean[k] = _sanitize(v)
        return clean
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, str) and _SECRET_HINT.search(obj) and len(obj) > 40:
        return "[REDACTED]"
    return obj


def write_receipt(namespace: str, kind: str, task_id: str, worker_id: str,
                  lease_id: str | None, detail: dict) -> Path:
    """kind in {'start','finish','failure','review'}. Returns the receipt path."""
    assert kind in {"start", "finish", "failure", "review"}
    rid = f"{now_iso().replace(':', '').replace('-', '')}-{kind}-{uuid.uuid4().hex[:8]}"
    receipt = {
        "receipt_id": rid,
        "kind": kind,
        "namespace": namespace,
        "task_id": task_id,
        "worker_id": worker_id,
        "lease_id": lease_id,
        "recorded_at": now_iso(),
        "detail": _sanitize(detail),
    }
    path = paths.receipts_dir(namespace) / f"{rid}.json"
    write_json(path, receipt)
    # Index for quick review.
    append_jsonl(paths.receipts_dir(namespace) / "index.jsonl", {
        "receipt_id": rid, "kind": kind, "task_id": task_id,
        "worker_id": worker_id, "recorded_at": receipt["recorded_at"],
    })
    return path


def count_invocations(namespace: str = "shared") -> int:
    idx = paths.receipts_dir(namespace) / "index.jsonl"
    if not idx.exists():
        return 0
    from .jsonstore import read_jsonl
    return sum(1 for r in read_jsonl(idx) if r.get("kind") == "start")
