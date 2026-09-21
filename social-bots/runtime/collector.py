"""Machine-captured current-source receipt collector (SB-V05-001).

Purpose
-------
Eliminate the defect where a caller can hand-write a Python dict and *label* it
"live-capture". Provenance is no longer something a caller asserts; it is
something the collector **derives from an actual retrieval it performed**.

Model
-----
A ``Fetcher`` performs a real retrieval and returns only the raw transport
outcome (bytes, transport status, final URL, error). The ``Collector`` — not the
caller and not the fetcher — owns everything that makes evidence trustworthy:

- the retrieval timestamp;
- the content hash (sha256 of the exact bytes retrieved);
- the collector identity/version;
- the derived retrieval status;
- the derived provenance classification.

The honesty invariant is: a receipt can only carry ``capture_mode == "live"`` if
a ``Fetcher`` whose ``mode`` is ``"live"`` actually returned content. A fixture
fetcher always yields ``capture_mode == "fixture"`` receipts, which report
``is_operational_live_evidence() is False`` — so a fixture can never masquerade
as operational capture. A failed retrieval yields a receipt that reports
``is_verified_capture() is False`` — so it can never be presented as verified
current evidence.

No secrets or private browser state are ever placed in a receipt; only the
public source URL, transport metadata, a content hash, and collector-extracted
evidence are retained.
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Callable, Protocol, runtime_checkable

from . import paths
from .jsonstore import write_json, append_jsonl, now_iso

# Collector identity/version is baked into every receipt so evidence is
# attributable to the exact collector that produced it.
COLLECTOR_NAME = "sbots.source-collector"
COLLECTOR_VERSION = "1.0.0"

# Retrieval status vocabulary (collector-derived, never caller-supplied).
STATUS_OK = "ok"            # a complete retrieval with content
STATUS_EMPTY = "empty"      # transport succeeded but returned no content
STATUS_PARTIAL = "partial"  # transport reported an incomplete body
STATUS_FAILED = "failed"    # transport failed / errored

# Capture modes. "live" is only ever assigned from a fetcher that declares
# itself live; "fixture" is for deterministic tests and offline development.
MODE_LIVE = "live"
MODE_FIXTURE = "fixture"
_VALID_MODES = {MODE_LIVE, MODE_FIXTURE}


@dataclass(frozen=True)
class FetchResult:
    """Raw transport outcome returned by a ``Fetcher``.

    A fetcher reports *only* what the transport observed. It never sets the
    timestamp, hash, provenance or status — those are the collector's to derive,
    which is what prevents a caller from forging authentic-looking evidence.
    """
    ok: bool
    content: bytes | None = None
    final_url: str | None = None
    http_status: int | None = None
    error: str | None = None
    partial: bool = False


@runtime_checkable
class Fetcher(Protocol):
    """Something that performs a real retrieval of a source URL.

    ``mode`` MUST be one of ``{"live", "fixture"}`` and is the single source of
    truth for whether resulting receipts are operational live evidence.
    """
    mode: str
    name: str

    def fetch(self, url: str) -> FetchResult: ...


@dataclass(frozen=True)
class CaptureReceipt:
    """Collector-generated evidence receipt. Construct ONLY via ``Collector``.

    Every field a downstream consumer would trust (timestamp, hash, status,
    provenance, collector identity) is assigned by the collector from an actual
    retrieval, not accepted from the caller.
    """
    receipt_id: str
    source_url: str
    canonical_id: str
    retrieved_at: str
    status: str
    capture_mode: str          # live | fixture (mirrors the fetcher's mode)
    collector_name: str
    collector_version: str
    fetcher_name: str
    content_hash: str | None   # sha256 of exact bytes, None when no content
    content_bytes: int | None
    http_status: int | None
    final_url: str | None
    provenance: str            # collector-derived; not caller-supplied
    error: str | None
    partial: bool
    extracted: dict = field(default_factory=dict)

    # ----- honesty predicates (the anti-forgery contract) ----------------- #
    def is_verified_capture(self) -> bool:
        """True only when the retrieval completed with a stable content hash.

        A failed / empty / partial retrieval is NOT verified current evidence.
        """
        return self.status == STATUS_OK and self.content_hash is not None

    def is_operational_live_evidence(self) -> bool:
        """True only for a *live* fetcher that actually retrieved content.

        A fixture receipt returns False here by construction, so a test fixture
        can never be presented as operational live capture.
        """
        return self.capture_mode == MODE_LIVE and self.is_verified_capture()

    def as_dict(self) -> dict:
        return asdict(self)


def canonical_source_id(url: str) -> str:
    """Stable identifier for a source URL (diagnostic / grouping key).

    This identifies the *source*, not a particular retrieval — two captures of
    the same unchanged URL share this id but get distinct ``receipt_id``s.
    """
    return "src-" + hashlib.sha256(url.strip().encode()).hexdigest()[:16]


def _derive_status(res: FetchResult) -> str:
    if not res.ok or res.error:
        return STATUS_FAILED
    if res.partial:
        return STATUS_PARTIAL
    if not res.content:
        return STATUS_EMPTY
    return STATUS_OK


def _derive_provenance(mode: str, status: str) -> str:
    """Provenance is a function of (fetcher mode, retrieval status) only.

    There is deliberately no path to "live-capture" without a live fetcher that
    completed a retrieval — this is the core fix for SB-V05-001.
    """
    if status != STATUS_OK:
        # A failed/partial/empty retrieval is never verified current evidence,
        # regardless of mode.
        return f"unverified-{status}"
    if mode == MODE_LIVE:
        return "live-capture"
    return "fixture"


# An extractor turns retrieved bytes into the small evidence dict the bot uses.
# It never receives secrets; it only sees the retrieved content and metadata.
Extractor = Callable[[bytes | None, FetchResult], dict]


class Collector:
    """Performs retrievals through a ``Fetcher`` and emits capture receipts."""

    def __init__(self, fetcher: Fetcher, *,
                 name: str = COLLECTOR_NAME, version: str = COLLECTOR_VERSION):
        mode = getattr(fetcher, "mode", None)
        if mode not in _VALID_MODES:
            raise ValueError(
                f"fetcher.mode must be one of {sorted(_VALID_MODES)}, got {mode!r}")
        if not getattr(fetcher, "name", None):
            raise ValueError("fetcher must declare a non-empty name")
        self.fetcher = fetcher
        self.name = name
        self.version = version

    @property
    def mode(self) -> str:
        return self.fetcher.mode

    def capture(self, url: str, *, extractor: Extractor | None = None) -> CaptureReceipt:
        """Retrieve ``url`` and return a collector-generated receipt.

        The receipt's timestamp, hash, status and provenance are derived here
        from the actual retrieval — the caller cannot supply or override them.
        """
        if not url or not isinstance(url, str):
            raise ValueError("capture requires a non-empty source URL")

        res = self.fetcher.fetch(url)
        if not isinstance(res, FetchResult):
            raise TypeError("fetcher.fetch must return a FetchResult")

        status = _derive_status(res)
        content = res.content if status in (STATUS_OK, STATUS_PARTIAL) else None
        content_hash = (hashlib.sha256(content).hexdigest()
                        if content is not None else None)
        content_bytes = len(content) if content is not None else None
        provenance = _derive_provenance(self.mode, status)

        extracted: dict = {}
        if extractor is not None and content is not None:
            try:
                extracted = dict(extractor(content, res))
            except Exception as exc:  # extraction failure must not forge evidence
                extracted = {"extraction_error": type(exc).__name__}

        return CaptureReceipt(
            receipt_id=f"cap-{uuid.uuid4().hex[:16]}",
            source_url=url,
            canonical_id=canonical_source_id(res.final_url or url),
            retrieved_at=now_iso(),
            status=status,
            capture_mode=self.mode,
            collector_name=self.name,
            collector_version=self.version,
            fetcher_name=self.fetcher.name,
            content_hash=content_hash,
            content_bytes=content_bytes,
            http_status=res.http_status,
            final_url=res.final_url,
            provenance=provenance,
            error=res.error,
            partial=res.partial,
            extracted=extracted,
        )


# --------------------------------------------------------------------------- #
# Durable persistence — one JSON file per receipt + an append-only index.
# Each capture is a *separate* retrieval receipt even for the same source.
# --------------------------------------------------------------------------- #
def _captures_dir(bot: str) -> Path:
    return paths.memory_dir(bot) / "captures"


def persist(bot: str, receipt: CaptureReceipt) -> Path:
    d = _captures_dir(bot)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{receipt.receipt_id}.json"
    write_json(path, receipt.as_dict())
    append_jsonl(d / "index.jsonl", {
        "receipt_id": receipt.receipt_id,
        "canonical_id": receipt.canonical_id,
        "source_url": receipt.source_url,
        "retrieved_at": receipt.retrieved_at,
        "status": receipt.status,
        "capture_mode": receipt.capture_mode,
        "content_hash": receipt.content_hash,
        "verified": receipt.is_verified_capture(),
        "operational_live": receipt.is_operational_live_evidence(),
    })
    return path


def load_captures(bot: str) -> list[dict]:
    from .jsonstore import read_jsonl
    return read_jsonl(_captures_dir(bot) / "index.jsonl")


# --------------------------------------------------------------------------- #
# Bridge to the accepted V0.3 signal API (research.py is left UNCHANGED).
# --------------------------------------------------------------------------- #
def to_signal(receipt: CaptureReceipt, *, title: str, summary: str,
              tags: list[str] | None = None):
    """Build a ``research.Signal`` from a *verified* capture receipt.

    Refuses to create a signal from an unverified (failed/partial/empty)
    retrieval, so unverified evidence can never enter the signal inbox. The
    signal's provenance mirrors the receipt's collector-derived provenance —
    a fixture stays a fixture, a live capture stays a live capture.
    """
    from . import research
    if not receipt.is_verified_capture():
        raise ValueError(
            f"cannot build a signal from unverified capture (status={receipt.status})")
    return research.Signal(
        id="sig-" + (receipt.content_hash or receipt.receipt_id)[:12],
        title=title,
        summary=summary,
        source=receipt.fetcher_name,
        url=receipt.source_url,
        captured_at=receipt.retrieved_at,
        provenance=receipt.provenance,   # 'live-capture' or 'fixture'
        tags=tags or [],
    )


# --------------------------------------------------------------------------- #
# Built-in fetchers.
# --------------------------------------------------------------------------- #
class FixtureFetcher:
    """A deterministic fetcher for tests / offline development.

    It serves caller-provided bytes but is HONEST about it: ``mode`` is always
    ``"fixture"`` so receipts it produces can never claim operational live
    evidence. Changing the fixture bytes changes the content hash.
    """
    mode = MODE_FIXTURE

    def __init__(self, responses: dict[str, bytes | FetchResult], *,
                 name: str = "fixture"):
        self.name = name
        self._responses = responses

    def fetch(self, url: str) -> FetchResult:
        item = self._responses.get(url)
        if item is None:
            return FetchResult(ok=False, error="fixture-not-found", final_url=url)
        if isinstance(item, FetchResult):
            return item
        return FetchResult(ok=True, content=item, final_url=url, http_status=200)


class UrllibFetcher:
    """A real live fetcher over HTTP(S) using the standard library.

    ``mode`` is ``"live"`` so successful retrievals are operational live
    evidence. Network access is environment-gated; tests use ``FixtureFetcher``.
    No cookies, auth headers or private browser state are sent or stored.
    """
    mode = MODE_LIVE

    def __init__(self, *, name: str = "urllib", timeout: float = 15.0,
                 max_bytes: int = 5_000_000, user_agent: str | None = None):
        self.name = name
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.user_agent = user_agent or f"{COLLECTOR_NAME}/{COLLECTOR_VERSION}"

    def fetch(self, url: str) -> FetchResult:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read(self.max_bytes + 1)
                partial = len(raw) > self.max_bytes
                content = raw[: self.max_bytes]
                final_url = resp.geturl()
                http_status = getattr(resp, "status", None) or resp.getcode()
                return FetchResult(ok=True, content=content, final_url=final_url,
                                   http_status=http_status, partial=partial)
        except urllib.error.HTTPError as exc:
            return FetchResult(ok=False, error=f"http-error-{exc.code}",
                               http_status=exc.code, final_url=url)
        except Exception as exc:  # network/DNS/timeout — a failed retrieval
            return FetchResult(ok=False, error=type(exc).__name__, final_url=url)
