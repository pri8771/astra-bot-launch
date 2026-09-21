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
1. **Operational-live provenance requires a policy-owned trusted transport, not
   just a ``mode="live"`` claim.** A receipt can only carry ``provenance ==
   "live-capture"`` (and report ``is_operational_live_evidence() is True``) when
   the retrieval ran through a transport in the *static, internal trust policy*
   (:data:`_TRUSTED_OPERATIONAL_TRANSPORTS`) AND the transport declares itself
   live AND the retrieval completed. There is no public API to grant trust, so an
   ordinary runtime caller cannot make an arbitrary transport operational. An
   untrusted ``mode="live"`` fetcher is downgraded to
   ``provenance == "unverified-untrusted-transport"``.
2. **Live retrieval is restricted to validated public HTTP(S), pinned to the
   validated IP.** The trusted transport (:class:`UrllibFetcher`) rejects
   non-HTTP(S) schemes and any destination that resolves to a loopback /
   private / link-local / multicast / reserved / unspecified address, then
   connects to the pinned validated IP (closing the validate-to-connect TOCTOU /
   DNS-rebinding window). Redirects are refused (fail-closed): a 3xx is a failed
   retrieval, never followed.
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
import http.client
import ipaddress
import socket
import ssl
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
COLLECTOR_VERSION = "1.3.0"

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
# Trusted-transport POLICY (LEAD-018 hardening).
#
# Operational-live provenance may only be produced by a *policy-owned, static,
# internal* transport. There is deliberately NO public registration API: an
# ordinary runtime caller cannot make an arbitrary transport operational-trusted.
# The trusted set is fixed at import time to this module's own built-in
# transports (populated at the bottom of the file, after the class is defined).
# --------------------------------------------------------------------------- #
_TRUSTED_OPERATIONAL_TRANSPORTS: frozenset[type] = frozenset()


def is_trusted_transport(fetcher: object) -> bool:
    """True only when ``fetcher``'s exact class is in the static trust policy.

    Subclasses are NOT trusted implicitly — a subclass that overrides retrieval
    is a different class and is therefore untrusted, which prevents inheriting
    trust while changing behaviour.
    """
    return type(fetcher) in _TRUSTED_OPERATIONAL_TRANSPORTS


# Evidence classes for downstream bridges (fixture vs verified-untrusted vs
# trusted-operational vs unverified).
EVIDENCE_TRUSTED_OPERATIONAL = "trusted_operational"
EVIDENCE_VERIFIED_UNTRUSTED = "verified_untrusted"
EVIDENCE_FIXTURE = "fixture"
EVIDENCE_UNVERIFIED = "unverified"


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
def evidence_class(receipt: CaptureReceipt) -> str:
    """Classify a receipt for downstream bridges.

    Distinguishes fixture, verified-untrusted, trusted-operational and
    unverified evidence so a bridge can enforce its own trust requirement.
    """
    if not receipt.is_verified_capture():
        return EVIDENCE_UNVERIFIED
    if receipt.capture_mode == MODE_FIXTURE:
        return EVIDENCE_FIXTURE
    if receipt.is_operational_live_evidence():
        return EVIDENCE_TRUSTED_OPERATIONAL
    return EVIDENCE_VERIFIED_UNTRUSTED


def to_signal(receipt: CaptureReceipt, *, title: str, summary: str,
              tags: list[str] | None = None):
    """Build a ``research.Signal`` from a *verified* capture receipt.

    This is the GENERAL (non-operational) bridge: it accepts any verified
    capture (including fixtures) and mirrors the receipt's collector-derived
    provenance so the signal stays honestly labelled. It refuses unverified
    (failed/partial/empty) retrievals. For operational use, prefer
    :func:`to_operational_signal`, which additionally rejects fixture and
    verified-untrusted evidence.
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


def to_operational_signal(receipt: CaptureReceipt, *, title: str, summary: str,
                          tags: list[str] | None = None):
    """Operational bridge: build a signal ONLY from trusted-operational evidence.

    Rejects fixture and verified-untrusted receipts, so an operational consumer
    can never be fed a fixture or an unvalidated-transport capture.
    """
    cls = evidence_class(receipt)
    if cls != EVIDENCE_TRUSTED_OPERATIONAL:
        raise ValueError(
            f"operational bridge requires trusted-operational evidence, got {cls!r}")
    return to_signal(receipt, title=title, summary=summary, tags=tags)


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


@dataclass(frozen=True)
class PinnedDestination:
    """A validated destination pinned to a specific public IP.

    Pinning the exact validated address for the actual connection closes the
    validate-then-connect TOCTOU / DNS-rebinding window: the socket connects to
    ``ip`` (proven public), while TLS SNI / cert verification and the HTTP Host
    header still use ``host``.
    """
    scheme: str
    host: str
    ip: str
    port: int


def resolve_and_validate(url: str) -> PinnedDestination:
    """Validate ``url`` and pin it to one validated public IP for connection.

    Raises :class:`UnsafeDestinationError` for a bad scheme/host or any resolved
    address that is not public. The returned IP is the one the caller MUST
    connect to (do not re-resolve), so the connection cannot be rebound to a
    private address after validation.
    """
    parsed = validate_public_url(url)  # scheme + all resolved addrs are public
    host = parsed.hostname
    scheme = parsed.scheme.lower()
    port = parsed.port or (443 if scheme == "https" else 80)
    # validate_public_url already proved EVERY resolved address is public; pick
    # the first and pin it for the actual connection.
    addresses = sorted(_resolve_addresses(host))
    for addr in addresses:
        if _ip_is_public(addr):
            return PinnedDestination(scheme=scheme, host=host, ip=addr, port=port)
    raise UnsafeDestinationError(f"host {host!r} has no public address to pin")


class UrllibFetcher:
    """The built-in trusted live fetcher over validated public HTTP(S).

    Trust is conferred by the static module policy (see
    ``_TRUSTED_OPERATIONAL_TRANSPORTS`` at the bottom of this file), NOT by any
    caller-invokable registration. It enforces the safety contract:

    - only ``http`` / ``https`` schemes are permitted;
    - the destination is resolved, every resolved address must be public, and
      the connection is PINNED to a validated public IP (closing the
      validate-to-connect TOCTOU / DNS-rebinding window);
    - **redirects are refused (fail-closed).** A 3xx response is not followed;
      it returns a failed retrieval. Following redirects safely would require
      re-validating and re-pinning each hop; rather than claim that capability
      without an end-to-end tested implementation, this transport deliberately
      fails closed on redirects.

    Network access is environment-gated. No cookies, auth headers or private
    browser state are sent or stored.
    """
    mode = MODE_LIVE

    def __init__(self, *, name: str = "urllib", timeout: float = 15.0,
                 max_bytes: int = 5_000_000, user_agent: str | None = None):
        self.name = name
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.user_agent = user_agent or f"{COLLECTOR_NAME}/{COLLECTOR_VERSION}"

    def fetch(self, url: str) -> FetchResult:
        # Validate + pin the destination before any network contact.
        try:
            pinned = resolve_and_validate(url)
        except UnsafeDestinationError as exc:
            return FetchResult(ok=False, error=f"unsafe-destination:{exc}",
                               final_url=url)
        try:
            return self._perform(url, pinned)
        except Exception as exc:  # network/DNS/timeout/TLS — a failed retrieval
            return FetchResult(ok=False, error=type(exc).__name__, final_url=url)

    def _perform(self, url: str, pinned: PinnedDestination) -> FetchResult:
        """Perform one HTTP(S) exchange against the PINNED IP, failing closed on
        redirects.

        Correct pinned-IP HTTPS (the SB-V05-001 / LEAD-020 repair)
        ----------------------------------------------------------
        The stdlib ``http.client.HTTPSConnection`` constructor does **not**
        accept a ``server_hostname`` keyword, and connecting it to the pinned IP
        as its ``host`` would make TLS verify the certificate against the IP and
        emit an IP ``Host`` header. Both are wrong. Instead we:

        1. open exactly one TCP socket to the already-validated **pinned public
           IP** (``socket.create_connection``) — the hostname is never
           re-resolved here, so the validate-to-connect TOCTOU / DNS-rebinding
           window stays closed;
        2. for HTTPS, complete the TLS handshake over that pinned socket with
           ``SSLContext.wrap_socket(..., server_hostname=<original host>)`` so
           **SNI and certificate hostname verification use the original validated
           hostname**, not the IP (a hostname-mismatched cert still fails);
        3. build the connection object with the **original hostname** (so the
           ``Host`` header carries correct host semantics) and hand it the
           already-connected pinned socket via ``conn.sock`` — this suppresses
           any internal ``connect()`` (and therefore any re-resolution), so the
           bytes travel over the socket we pinned in step 1.

        This exercises real, supported stdlib API only; a production HTTPS
        retrieval actually succeeds instead of dying on an unsupported
        constructor argument.
        """
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        # (1) One connect(), to the validated pinned public IP. No re-resolution.
        sock = socket.create_connection((pinned.ip, pinned.port),
                                        timeout=self.timeout)
        conn = None
        try:
            if pinned.scheme == "https":
                # (2) TLS over the pinned socket; SNI + cert verification bind to
                # the ORIGINAL validated hostname, never the pinned IP.
                ctx = ssl.create_default_context()
                sock = ctx.wrap_socket(sock, server_hostname=pinned.host)
                conn = http.client.HTTPSConnection(
                    pinned.host, pinned.port, timeout=self.timeout, context=ctx)
            else:
                conn = http.client.HTTPConnection(
                    pinned.host, pinned.port, timeout=self.timeout)
            # (3) Reuse the pinned (TLS-wrapped) socket; http.client will not dial
            # out again, so the hostname is not re-resolved for the transfer.
            conn.sock = sock
            # Explicit Host header preserves the original hostname semantics and
            # (being present) suppresses http.client's own IP-derived Host header.
            conn.request("GET", path, headers={
                "Host": pinned.host, "User-Agent": self.user_agent})
            resp = conn.getresponse()
            status = int(resp.status)
            if 300 <= status < 400:
                # Fail closed: do not follow redirects.
                return FetchResult(ok=False,
                                   error=f"redirect-not-followed:{status}",
                                   http_status=status, final_url=url)
            raw = resp.read(self.max_bytes + 1)
            partial = len(raw) > self.max_bytes
            content = raw[: self.max_bytes]
            return FetchResult(ok=True, content=content, final_url=url,
                               http_status=status, partial=partial)
        finally:
            if conn is not None:
                conn.close()   # closes the pinned socket it now owns
            else:
                sock.close()   # never handed to a connection; close it ourselves


# --------------------------------------------------------------------------- #
# Static trust policy (LEAD-018): the ONLY operational-trusted transports.
# Assigned once here, after the class is defined; there is no public API to add
# to this set, so an ordinary runtime caller cannot grant operational trust.
# --------------------------------------------------------------------------- #
_TRUSTED_OPERATIONAL_TRANSPORTS = frozenset({UrllibFetcher})
