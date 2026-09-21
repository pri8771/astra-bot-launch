"""Machine-captured current-source receipt collector (SB-V05-001).

Purpose
-------
Eliminate the defect where a caller can hand-write a Python dict and *label* it
"live-capture". Provenance is no longer something a caller asserts; it is
something the collector **derives from an actual retrieval it performed through a
trusted, collector-owned transport**.

Model
-----
A ``Fetcher`` performs a real retrieval and returns only the raw transport
outcome (bytes, transport status, final URL, error). The ``Collector`` — not the
caller and not the fetcher — owns everything that makes evidence trustworthy:

- the retrieval timestamp;
- the content hash (sha256 of the exact bytes retrieved);
- the collector identity/version;
- the derived retrieval status;
- the derived provenance classification;
- whether the transport was a *trusted, collector-owned* transport.

Anti-forgery invariants (SB-V05-001 repair contract)
---------------------------------------------------
1. **Operational-live provenance requires a trusted transport, not just a
   ``mode="live"`` claim.** A receipt can only carry ``provenance ==
   "live-capture"`` (and report ``is_operational_live_evidence() is True``) when
   the retrieval ran through a transport that is *registered as trusted* AND the
   transport declares itself live AND the retrieval completed. An arbitrary
   custom ``Fetcher`` that merely sets ``mode = "live"`` is downgraded to
   ``provenance == "unverified-untrusted-transport"`` and can never be
   operational live evidence.
2. **Live retrieval is restricted to validated public HTTP(S).** The trusted
   live transport (:class:`UrllibFetcher`) rejects non-HTTP(S) schemes and any
   destination that resolves to a loopback / private / link-local / multicast /
   reserved / unspecified address, and re-validates every redirect hop and the
   final destination. Unsafe destinations yield a failed retrieval, never
   evidence.
3. **Extraction failure cannot be presented as extracted factual support.** Each
   receipt records an ``extraction_status`` (``not_attempted`` / ``ok`` /
   ``failed`` / ``empty``). Extraction errors are recorded out-of-band in
   ``extraction_error`` and are never placed inside ``extracted``; downstream
   consumers must gate on :meth:`CaptureReceipt.has_usable_extraction`.

A fixture fetcher always yields ``capture_mode == "fixture"`` receipts, which
report ``is_operational_live_evidence() is False`` — so a fixture can never
masquerade as operational capture. A failed retrieval yields a receipt that
reports ``is_verified_capture() is False`` — so it can never be presented as
verified current evidence.

No secrets or private browser state are ever placed in a receipt; only the
public source URL, transport metadata, a content hash, and collector-extracted
evidence are retained.
"""
from __future__ import annotations

import hashlib
import ipaddress
import socket
import urllib.parse
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Callable, Protocol, runtime_checkable

from . import paths
from .jsonstore import write_json, append_jsonl, now_iso

# Collector identity/version is baked into every receipt so evidence is
# attributable to the exact collector that produced it.
COLLECTOR_NAME = "sbots.source-collector"
COLLECTOR_VERSION = "1.1.0"

# Retrieval status vocabulary (collector-derived, never caller-supplied).
STATUS_OK = "ok"            # a complete retrieval with content
STATUS_EMPTY = "empty"      # transport succeeded but returned no content
STATUS_PARTIAL = "partial"  # transport reported an incomplete body
STATUS_FAILED = "failed"    # transport failed / errored / unsafe destination

# Capture modes. "live" is only ever assigned from a fetcher that declares
# itself live; "fixture" is for deterministic tests and offline development.
MODE_LIVE = "live"
MODE_FIXTURE = "fixture"
_VALID_MODES = {MODE_LIVE, MODE_FIXTURE}

# Extraction status vocabulary. Extraction failure is never usable factual
# support (SB-V05-001 repair: "extraction failure cannot be used as extracted
# factual support").
EXTRACTION_NOT_ATTEMPTED = "not_attempted"
EXTRACTION_OK = "ok"
EXTRACTION_FAILED = "failed"
EXTRACTION_EMPTY = "empty"

# Only HTTP(S) is a permitted live retrieval scheme.
ALLOWED_SCHEMES = ("http", "https")


# --------------------------------------------------------------------------- #
# Safe public-destination validation (SSRF defence for live retrieval).
# --------------------------------------------------------------------------- #
class UnsafeDestinationError(ValueError):
    """Raised when a URL is not a validated public HTTP(S) destination."""


def _ip_is_public(ip_str: str) -> bool:
    """True only for a genuinely public, routable unicast address.

    Rejects loopback, private, link-local, multicast, reserved and unspecified
    ranges — including IPv4-mapped IPv6 forms, which are unwrapped first.
    """
    ip = ipaddress.ip_address(ip_str)
    if getattr(ip, "ipv4_mapped", None) is not None:
        ip = ip.ipv4_mapped
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve_addresses(host: str) -> set[str]:
    """Resolve ``host`` to the set of IP strings it maps to.

    A literal IP resolves to itself without any DNS lookup, so destination
    classification for literal addresses needs no network access.
    """
    infos = socket.getaddrinfo(host, None)
    return {info[4][0] for info in infos}


def validate_public_url(url: str) -> urllib.parse.ParseResult:
    """Validate that ``url`` is a public HTTP(S) destination.

    Raises :class:`UnsafeDestinationError` for a non-HTTP(S) scheme, a missing
    host, an unresolvable host, or any resolved address that is not public.
    Returns the parsed URL on success.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise UnsafeDestinationError(
            f"scheme {parsed.scheme!r} is not an allowed public scheme "
            f"{ALLOWED_SCHEMES}")
    host = parsed.hostname
    if not host:
        raise UnsafeDestinationError("URL has no host")
    try:
        addresses = _resolve_addresses(host)
    except OSError as exc:
        raise UnsafeDestinationError(f"host {host!r} did not resolve: {exc}")
    if not addresses:
        raise UnsafeDestinationError(f"host {host!r} resolved to no addresses")
    for addr in addresses:
        try:
            public = _ip_is_public(addr)
        except ValueError as exc:
            raise UnsafeDestinationError(f"unparseable address {addr!r}: {exc}")
        if not public:
            raise UnsafeDestinationError(
                f"host {host!r} resolves to non-public address {addr!r}")
    return parsed


# --------------------------------------------------------------------------- #
# Trusted-transport registry.
#
# Operational-live provenance may only be produced by collector-owned trusted
# transports. Trust is granted by an explicit, auditable registration — never by
# a caller merely declaring ``mode = "live"`` on an ad-hoc object.
# --------------------------------------------------------------------------- #
_TRUSTED_TRANSPORT_CLASSES: set[type] = set()


def register_trusted_transport(cls: type) -> type:
    """Register (and return) a transport class as a trusted, collector-owned
    transport. Usable as a decorator."""
    _TRUSTED_TRANSPORT_CLASSES.add(cls)
    return cls


def is_trusted_transport(fetcher: object) -> bool:
    """True only when ``fetcher``'s exact class is a registered trusted
    transport. Subclasses are NOT trusted implicitly — each must be registered,
    so a subclass cannot silently inherit trust while overriding retrieval."""
    return type(fetcher) in _TRUSTED_TRANSPORT_CLASSES


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

    ``mode`` MUST be one of ``{"live", "fixture"}``. ``mode`` alone is NOT
    sufficient for operational-live provenance — the transport must also be a
    registered trusted transport.
    """
    mode: str
    name: str

    def fetch(self, url: str) -> FetchResult: ...


@dataclass(frozen=True)
class CaptureReceipt:
    """Collector-generated evidence receipt. Construct ONLY via ``Collector``.

    Every field a downstream consumer would trust (timestamp, hash, status,
    provenance, transport trust, collector identity) is assigned by the collector
    from an actual retrieval, not accepted from the caller.
    """
    receipt_id: str
    source_url: str
    canonical_id: str
    retrieved_at: str
    status: str
    capture_mode: str           # live | fixture (mirrors the fetcher's mode)
    transport_trusted: bool     # collector-derived from the trusted registry
    collector_name: str
    collector_version: str
    fetcher_name: str
    content_hash: str | None    # sha256 of exact bytes, None when no content
    content_bytes: int | None
    http_status: int | None
    final_url: str | None
    provenance: str             # collector-derived; not caller-supplied
    error: str | None
    partial: bool
    extraction_status: str = EXTRACTION_NOT_ATTEMPTED
    extraction_error: str | None = None
    extracted: dict = field(default_factory=dict)

    # ----- honesty predicates (the anti-forgery contract) ----------------- #
    def is_verified_capture(self) -> bool:
        """True only when the retrieval completed with a stable content hash.

        A failed / empty / partial retrieval is NOT verified current evidence.
        """
        return self.status == STATUS_OK and self.content_hash is not None

    def is_operational_live_evidence(self) -> bool:
        """True only for a *trusted, live* transport that actually retrieved
        content.

        A fixture receipt, or a live-but-untrusted transport, returns False here
        by construction — so neither a test fixture nor an ad-hoc caller object
        declaring ``mode="live"`` can be presented as operational live capture.
        """
        return (self.capture_mode == MODE_LIVE
                and self.transport_trusted
                and self.is_verified_capture())

    def has_usable_extraction(self) -> bool:
        """True only when extraction actually succeeded with content.

        Extraction that was not attempted, failed, or produced nothing is never
        usable factual support.
        """
        return self.extraction_status == EXTRACTION_OK and bool(self.extracted)

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


def _derive_provenance(mode: str, status: str, trusted: bool) -> str:
    """Provenance is a function of (fetcher mode, retrieval status, trust) only.

    There is deliberately no path to "live-capture" without a *trusted* live
    transport that completed a retrieval — this is the core fix for SB-V05-001:
    a caller declaring ``mode="live"`` on an untrusted transport is classified
    ``unverified-untrusted-transport``, not live capture.
    """
    if status != STATUS_OK:
        # A failed/partial/empty retrieval is never verified current evidence,
        # regardless of mode or trust.
        return f"unverified-{status}"
    if mode == MODE_LIVE:
        if trusted:
            return "live-capture"
        return "unverified-untrusted-transport"
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
        # Trust is derived from the registry, never from the fetcher's own claim.
        self.transport_trusted = is_trusted_transport(fetcher)

    @property
    def mode(self) -> str:
        return self.fetcher.mode

    def capture(self, url: str, *, extractor: Extractor | None = None) -> CaptureReceipt:
        """Retrieve ``url`` and return a collector-generated receipt.

        The receipt's timestamp, hash, status, provenance and transport-trust are
        derived here from the actual retrieval — the caller cannot supply or
        override them.
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
        provenance = _derive_provenance(self.mode, status, self.transport_trusted)

        extraction_status = EXTRACTION_NOT_ATTEMPTED
        extraction_error: str | None = None
        extracted: dict = {}
        if extractor is not None:
            if content is None:
                extraction_status = EXTRACTION_EMPTY
            else:
                try:
                    extracted = dict(extractor(content, res))
                    extraction_status = EXTRACTION_OK if extracted else EXTRACTION_EMPTY
                except Exception as exc:  # failure must not forge factual support
                    # The error is recorded out-of-band; it is NEVER placed in
                    # `extracted`, so a failed extraction cannot be mistaken for
                    # extracted factual support.
                    extracted = {}
                    extraction_status = EXTRACTION_FAILED
                    extraction_error = type(exc).__name__

        return CaptureReceipt(
            receipt_id=f"cap-{uuid.uuid4().hex[:16]}",
            source_url=url,
            canonical_id=canonical_source_id(res.final_url or url),
            retrieved_at=now_iso(),
            status=status,
            capture_mode=self.mode,
            transport_trusted=self.transport_trusted,
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
            extraction_status=extraction_status,
            extraction_error=extraction_error,
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
        "transport_trusted": receipt.transport_trusted,
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
    signal's provenance mirrors the receipt's collector-derived provenance — a
    fixture stays a fixture, a trusted live capture stays a live capture, and an
    untrusted live transport stays honestly ``unverified-untrusted-transport``.
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
        provenance=receipt.provenance,
        tags=tags or [],
    )


# --------------------------------------------------------------------------- #
# Built-in fetchers.
# --------------------------------------------------------------------------- #
class FixtureFetcher:
    """A deterministic fetcher for tests / offline development.

    It serves caller-provided bytes but is HONEST about it: ``mode`` is always
    ``"fixture"`` and it is NOT a trusted transport, so receipts it produces can
    never claim operational live evidence. Changing the fixture bytes changes the
    content hash.
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


# Sentinel for the redirect loop: a validated redirect target to follow next.
@dataclass(frozen=True)
class _Redirect:
    url: str


@register_trusted_transport
class UrllibFetcher:
    """A trusted live fetcher over validated public HTTP(S).

    This is the *only* built-in transport that can produce operational-live
    evidence, because it is registered as a trusted transport AND it enforces the
    safety contract:

    - only ``http`` / ``https`` schemes are permitted;
    - the initial destination and every redirect hop must resolve to a public
      address (loopback/private/link-local/multicast/reserved/unspecified are
      rejected);
    - redirects are followed manually and re-validated, up to ``max_redirects``.

    Network access is environment-gated; unit tests exercise the validation and
    redirect logic without live network by overriding ``_perform``. No cookies,
    auth headers or private browser state are sent or stored.
    """
    mode = MODE_LIVE

    def __init__(self, *, name: str = "urllib", timeout: float = 15.0,
                 max_bytes: int = 5_000_000, max_redirects: int = 5,
                 user_agent: str | None = None):
        self.name = name
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects
        self.user_agent = user_agent or f"{COLLECTOR_NAME}/{COLLECTOR_VERSION}"

    def fetch(self, url: str) -> FetchResult:
        # Validate the caller-supplied destination before any network contact.
        try:
            validate_public_url(url)
        except UnsafeDestinationError as exc:
            return FetchResult(ok=False, error=f"unsafe-destination:{exc}",
                               final_url=url)

        current = url
        for _ in range(self.max_redirects + 1):
            try:
                outcome = self._perform(current)
            except Exception as exc:  # network/DNS/timeout — a failed retrieval
                return FetchResult(ok=False, error=type(exc).__name__,
                                   final_url=current)
            if isinstance(outcome, _Redirect):
                # Re-validate the redirect target BEFORE following it, so a
                # public URL cannot bounce us to a private/loopback destination.
                try:
                    validate_public_url(outcome.url)
                except UnsafeDestinationError as exc:
                    return FetchResult(ok=False, error=f"unsafe-redirect:{exc}",
                                       final_url=outcome.url)
                current = outcome.url
                continue
            return outcome
        return FetchResult(ok=False, error="too-many-redirects", final_url=current)

    def _perform(self, url: str) -> FetchResult | _Redirect:
        """Perform one HTTP(S) exchange WITHOUT auto-following redirects.

        Returns a :class:`_Redirect` when the server responded with a redirect,
        or a :class:`FetchResult` for a terminal response. Overridable in tests
        to exercise the redirect/validation loop without network access.
        """
        import urllib.request

        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None  # never auto-follow; the fetch loop validates hops

        opener = urllib.request.build_opener(_NoRedirect)
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with opener.open(req, timeout=self.timeout) as resp:
            status = getattr(resp, "status", None) or resp.getcode()
            location = resp.headers.get("Location")
            if status and 300 <= int(status) < 400 and location:
                target = urllib.parse.urljoin(url, location)
                return _Redirect(target)
            raw = resp.read(self.max_bytes + 1)
            partial = len(raw) > self.max_bytes
            content = raw[: self.max_bytes]
            final_url = resp.geturl()
            return FetchResult(ok=True, content=content, final_url=final_url,
                               http_status=int(status) if status else None,
                               partial=partial)
