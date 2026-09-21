"""SB-R07-042 — freeze controlled V0.4 divergence inputs (no model call).

Captures two real current public sources through the trusted SB-V05-001 collector
transport, builds the five-case prepare-only matrix, and writes an **immutable**
freeze bundle:

* ``E1.raw`` / ``E2.raw`` — exact retrieved bytes
* ``E1.receipt.json`` / ``E2.receipt.json`` — collector-derived capture receipts
* ``EVIDENCE_BUNDLE.json`` — prepare-compatible live-capture bundle
* ``PREPARED_MATRIX.json`` + ``prompts/`` — hashed bounded contexts / prompts
* ``ISOLATION.json`` — single-variable assertions for P0|P1, P0|P2, P0|P3, P0|E0
* ``FREEZE_MANIFEST.json`` — top-level honesty + digests

Never constructs a reasoning provider. Never spends. Never self-accepts.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

from . import collector, divergence_prepare as dp
from .jsonstore import now_iso

FREEZE_ID = "SB-R07-042"
FREEZE_SCHEMA_VERSION = 1

# Default materially different public sources. Override via freeze_inputs(...).
DEFAULT_E1_URL = "https://example.com/"
DEFAULT_E2_URL = "https://www.rfc-editor.org/rfc/rfc8259.txt"

DEFAULT_OBJECTIVE = (
    "grow a durable, factually sound audience without publishing anything "
    "unreviewed"
)

PERSONA_FILES = {
    "baseline": "social-a.json",
    "variant_b": "social-b.json",
    "variant_c": "social-c.json",
    "cultural": "cultural-primandir-atman.json",
}


class FreezeError(Exception):
    """Raised when a freeze cannot be produced honestly."""


@dataclass
class CapturedSource:
    snapshot_id: str
    url: str
    raw: bytes
    receipt: collector.CaptureReceipt
    signal: dict
    title: str
    summary: str
    tags: list[str]


def _load_personas(persona_dir: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for slot, filename in PERSONA_FILES.items():
        path = persona_dir / filename
        if not path.exists():
            raise FreezeError(f"missing persona file {path}")
        out[slot] = json.loads(path.read_text(encoding="utf-8"))
    return out


def _default_annotations(snapshot_id: str, url: str) -> tuple[str, str, list[str]]:
    """Operator-supplied title/summary/tags for the matrix signal envelope.

    Bytes + collector receipt remain the provenance of truth; these fields are
    human-facing annotations required by the signal schema, not a substitute for
    the capture receipt.
    """
    if snapshot_id == "E1":
        return (
            "Example Domain public homepage",
            "Live HTTPS capture of the public example.com homepage used as "
            "controlled evidence snapshot E1 for the V0.4 divergence matrix.",
            ["public-web", "example-domain", "divergence-e1"],
        )
    return (
        "RFC 8259 JavaScript Object Notation (JSON)",
        "Live HTTPS capture of RFC 8259 plain text from rfc-editor.org used as "
        "controlled evidence snapshot E2, materially different from E1.",
        ["standards", "json", "rfc8259", "divergence-e2"],
    )


def capture_source(snapshot_id: str, url: str, *,
                   title: str | None = None, summary: str | None = None,
                   tags: list[str] | None = None) -> CapturedSource:
    """Live-capture one public URL via the trusted collector transport.

    Trust is conferred only on the exact ``UrllibFetcher`` class (wrappers and
    subclasses are untrusted). We bind a recording ``fetch`` on the *instance*
    so class identity is preserved while the freeze retains the exact bytes
    (receipts store hash + length only).
    """
    fetcher = collector.UrllibFetcher()
    retained: dict[str, collector.FetchResult] = {}

    def _recording_fetch(fetch_url: str) -> collector.FetchResult:
        result = collector.UrllibFetcher.fetch(fetcher, fetch_url)
        retained["last"] = result
        return result

    fetcher.fetch = _recording_fetch  # type: ignore[method-assign]
    col = collector.Collector(fetcher=fetcher)
    receipt = col.capture(url)
    if not receipt.is_operational_live_evidence():
        raise FreezeError(
            f"{snapshot_id}: capture of {url!r} is not trusted-operational "
            f"(status={receipt.status}, provenance={receipt.provenance}, "
            f"transport_trusted={receipt.transport_trusted})")
    last = retained.get("last")
    if last is None or not last.ok or not last.content:
        raise FreezeError(f"{snapshot_id}: no raw content retained for {url!r}")
    raw = last.content
    if hashlib.sha256(raw).hexdigest() != receipt.content_hash:
        raise FreezeError(f"{snapshot_id}: retained bytes do not match receipt hash")

    def_title, def_summary, def_tags = _default_annotations(snapshot_id, url)
    title = title or def_title
    summary = summary or def_summary
    tags = list(tags) if tags is not None else list(def_tags)
    signal_obj = collector.to_operational_signal(
        receipt, title=title, summary=summary, tags=tags)
    signal = asdict(signal_obj)
    return CapturedSource(
        snapshot_id=snapshot_id, url=url, raw=raw, receipt=receipt,
        signal=signal, title=title, summary=summary, tags=tags,
    )


def captured_source_from_bytes(
    snapshot_id: str, url: str, raw: bytes, *,
    title: str, summary: str, tags: list[str] | None = None,
) -> CapturedSource:
    """Build a CapturedSource with a collector-shaped live receipt (test seam).

    Production freezes must use ``capture_source`` (real UrllibFetcher). This
    helper exists so unit tests can exercise the immutable freeze writer without
    a network call; any bundle built this way must be labeled ENGINEERING-ONLY.
    """
    content_hash = hashlib.sha256(raw).hexdigest()
    receipt = collector.CaptureReceipt(
        receipt_id=f"cap-test-{snapshot_id.lower()}",
        source_url=url,
        canonical_id=collector.canonical_source_id(url),
        retrieved_at=now_iso(),
        status=collector.STATUS_OK,
        capture_mode=collector.MODE_LIVE,
        transport_trusted=True,
        collector_name=collector.COLLECTOR_NAME,
        collector_version=collector.COLLECTOR_VERSION,
        fetcher_name="urllib",
        content_hash=content_hash,
        content_bytes=len(raw),
        http_status=200,
        final_url=url,
        provenance="live-capture",
        error=None,
        partial=False,
    )
    signal_obj = collector.to_operational_signal(
        receipt, title=title, summary=summary, tags=tags or [])
    return CapturedSource(
        snapshot_id=snapshot_id, url=url, raw=raw, receipt=receipt,
        signal=asdict(signal_obj), title=title, summary=summary,
        tags=list(tags or []),
    )


def _snapshot_from_capture(cap: CapturedSource) -> dp.EvidenceSnapshot:
    receipt_meta = {
        "collector_receipt_id": cap.receipt.receipt_id,
        "collector_name": cap.receipt.collector_name,
        "collector_version": cap.receipt.collector_version,
        "fetcher_name": cap.receipt.fetcher_name,
        "source_url": cap.receipt.source_url,
        "final_url": cap.receipt.final_url,
        "http_status": cap.receipt.http_status,
        "content_hash": cap.receipt.content_hash,
        "content_bytes": cap.receipt.content_bytes,
        "status": cap.receipt.status,
        "capture_mode": cap.receipt.capture_mode,
        "transport_trusted": cap.receipt.transport_trusted,
        "provenance": cap.receipt.provenance,
        "retrieved_at": cap.receipt.retrieved_at,
        "kind": "sbots-collector-v05-live-capture",
    }
    return dp.EvidenceSnapshot.from_bytes(
        cap.snapshot_id, cap.signal, cap.raw, receipt_meta,
        provenance_label=dp.LIVE_CAPTURE,
        captured_at=cap.receipt.retrieved_at,
    )


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _atomic_write_text(path: Path, text: str) -> None:
    _atomic_write_bytes(path, text.encode("utf-8"))


def freeze_inputs(
    out_dir: str | Path,
    *,
    e1_url: str = DEFAULT_E1_URL,
    e2_url: str = DEFAULT_E2_URL,
    persona_dir: str | Path | None = None,
    objective: str = DEFAULT_OBJECTIVE,
    run_scope: str = "v04-divergence-freeze",
    lane: str = "cursor-recovery",
    live_capture: bool = True,
) -> dict:
    """Capture E1/E2 (live) and write the immutable freeze bundle.

    ``live_capture=True`` (default) performs real network retrieval. Tests may
    pass ``live_capture=False`` only with an injected path via
    ``freeze_from_captures``.
    """
    if not live_capture:
        raise FreezeError(
            "freeze_inputs requires live_capture=True; tests should call "
            "freeze_from_captures with FixtureFetcher-built CapturedSource values")
    e1 = capture_source("E1", e1_url)
    e2 = capture_source("E2", e2_url)
    return freeze_from_captures(
        out_dir, e1=e1, e2=e2, persona_dir=persona_dir, objective=objective,
        run_scope=run_scope, lane=lane,
    )


def freeze_from_captures(
    out_dir: str | Path,
    *,
    e1: CapturedSource,
    e2: CapturedSource,
    persona_dir: str | Path | None = None,
    objective: str = DEFAULT_OBJECTIVE,
    run_scope: str = "v04-divergence-freeze",
    lane: str = "cursor-recovery",
) -> dict:
    """Write the immutable freeze bundle from already-captured sources."""
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()):
        raise FreezeError(f"refusing to write into non-empty freeze dir {out}")
    out.mkdir(parents=True, exist_ok=True)

    if e1.raw == e2.raw:
        raise FreezeError("E1 and E2 raw bytes are identical; evidence must differ")
    if e1.receipt.content_hash == e2.receipt.content_hash:
        raise FreezeError("E1 and E2 content hashes are identical")

    for cap in (e1, e2):
        if not cap.receipt.is_operational_live_evidence():
            raise FreezeError(
                f"{cap.snapshot_id}: not trusted-operational live evidence "
                f"(provenance={cap.receipt.provenance})")
        _atomic_write_bytes(out / f"{cap.snapshot_id}.raw", cap.raw)
        _atomic_write_text(
            out / f"{cap.snapshot_id}.receipt.json",
            json.dumps(cap.receipt.as_dict(), indent=2, sort_keys=True) + "\n",
        )

    snapshots = {
        "E1": _snapshot_from_capture(e1),
        "E2": _snapshot_from_capture(e2),
    }

    # Prepare-compatible evidence bundle (raw_b64 + live-capture label).
    bundle = {}
    for sid, snap in snapshots.items():
        cap = e1 if sid == "E1" else e2
        bundle[sid] = {
            "signal": snap.signal,
            "raw_b64": base64.b64encode(cap.raw).decode("ascii"),
            "receipt": snap.receipt,
            "provenance_label": dp.LIVE_CAPTURE,
            "captured_at": snap.captured_at,
        }
    _atomic_write_text(
        out / "EVIDENCE_BUNDLE.json",
        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
    )

    root = Path(__file__).resolve().parent.parent
    personas = _load_personas(Path(persona_dir) if persona_dir else root / "personas")
    try:
        matrix = dp.build_matrix(
            personas=personas, snapshots=snapshots, objective=objective,
            run_scope=run_scope, lane=lane,
        )
        isolation = dp.verify_isolation(matrix)
    except dp.MatrixError as exc:
        raise FreezeError(f"matrix/isolation failed: {exc}") from exc

    if not matrix.acceptance_eligible:
        raise FreezeError(
            "prepared matrix is not acceptance_eligible despite live-capture "
            f"snapshots: {matrix.engineering_only_reasons}")

    matrix_path = out / "PREPARED_MATRIX.json"
    prompts_dir = out / "prompts"
    dp.write_prepared(matrix, matrix_path)
    dp.write_prompts(matrix, prompts_dir)
    _atomic_write_text(
        out / "ISOLATION.json",
        json.dumps(isolation, indent=2, sort_keys=True) + "\n",
    )

    # Re-verify digests from disk so the freeze is independently checkable.
    verified = dp.verify_written(matrix_path, prompts_dir)
    if not verified.get("verified"):
        raise FreezeError(f"written matrix failed re-verification: {verified}")

    manifest = {
        "schema_version": FREEZE_SCHEMA_VERSION,
        "freeze_id": FREEZE_ID,
        "frozen_at": now_iso(),
        "live_model_call_performed": False,
        "live_network_capture_performed": True,
        "evidence_class": "ENGINEERING",
        "acceptance_claim": False,
        "acceptance_authority": "ChatGPT lead — this freeze never self-accepts",
        "note": (
            "Immutable controlled inputs for a future owner-authorized five-call "
            "V0.4 divergence batch. No adaptive/model provider was constructed."
        ),
        "run_scope": run_scope,
        "lane": lane,
        "objective": objective,
        "sources": {
            "E1": {
                "url": e1.url,
                "content_hash": e1.receipt.content_hash,
                "content_bytes": e1.receipt.content_bytes,
                "receipt_id": e1.receipt.receipt_id,
                "retrieved_at": e1.receipt.retrieved_at,
            },
            "E2": {
                "url": e2.url,
                "content_hash": e2.receipt.content_hash,
                "content_bytes": e2.receipt.content_bytes,
                "receipt_id": e2.receipt.receipt_id,
                "retrieved_at": e2.receipt.retrieved_at,
            },
        },
        "matrix_path": str(matrix_path.name),
        "prompts_dir": str(prompts_dir.name),
        "acceptance_eligible": matrix.acceptance_eligible,
        "isolation_all_isolated": isolation["all_isolated"],
        "required_comparisons": [list(c) for c in dp.REQUIRED_COMPARISONS],
        "case_context_sha256": {
            c.case_id: c.context_sha256 for c in matrix.cases
        },
        "case_prompt_sha256": {
            c.case_id: c.prompt_sha256 for c in matrix.cases
        },
        "written_verification": verified,
        "collector": {
            "name": collector.COLLECTOR_NAME,
            "version": collector.COLLECTOR_VERSION,
        },
    }
    _atomic_write_text(
        out / "FREEZE_MANIFEST.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    return manifest
