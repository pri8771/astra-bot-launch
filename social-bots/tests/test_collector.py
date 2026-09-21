"""SB-V05-001 — machine-captured source collector acceptance tests.

All tests use explicit FIXTURE fetchers. Fixtures are marked as fixtures by the
collector and never masquerade as operational live capture.
"""
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import collector, research  # noqa: E402


URL = "https://example.org/article"


def _extract_len(content, res):
    return {"byte_len": len(content or b""), "http_status": res.http_status}


# --------------------------------------------------------------------------- #
# Production-path fakes for SB-V05-001 / LEAD-020 regression.
#
# These fake ONLY the socket and TLS I/O so that the REAL
# ``http.client.HTTPSConnection`` / ``HTTPConnection`` constructor and request
# machinery are exercised. That is what makes the regression able to catch an
# invalid stdlib constructor signature (e.g. the previous
# ``HTTPSConnection(..., server_hostname=...)`` defect, which raises TypeError):
# nothing here swallows constructor kwargs the way a fully mocked connection
# would.
# --------------------------------------------------------------------------- #
class _FakeSocket:
    """A minimal socket that replays a canned raw HTTP response.

    Implements just enough of the socket API for ``http.client`` to send a
    request and parse a response: ``sendall`` (records outbound bytes),
    ``makefile`` (serves the response bytes) and ``close``.
    """

    def __init__(self, response_bytes: bytes):
        self._response = response_bytes
        self.sent = bytearray()
        self.closed = False

    def sendall(self, data):
        self.sent += data

    # http.client also uses send() in some paths.
    def send(self, data):
        self.sent += data
        return len(data)

    def makefile(self, mode="rb", *a, **k):
        return io.BytesIO(self._response)

    def settimeout(self, _t):
        pass

    def close(self):
        self.closed = True


import ssl as _ssl  # noqa: E402  (for the SSLContext subclass below)


class _RecordingTLSContext(_ssl.SSLContext):
    """A REAL ``ssl.SSLContext`` subclass whose ``wrap_socket`` is stubbed.

    Subclassing the real context means the stdlib ``HTTPSConnection``
    constructor (which reads ``verify_mode`` / ``check_hostname``) still works
    unchanged, while ``wrap_socket`` skips real TLS: it records the SNI
    ``server_hostname`` (so a test can assert SNI/cert verification binds to the
    ORIGINAL validated hostname, never the pinned IP) and returns the underlying
    fake socket as-is.
    """

    def __new__(cls):
        # SSLContext configures itself in __new__ (protocol, default verify
        # mode / check_hostname). __init__ is object.__init__ and takes no args.
        return super().__new__(cls, _ssl.PROTOCOL_TLS_CLIENT)

    def __init__(self):
        self.recorded_sni = None
        self.wrapped = False

    def wrap_socket(self, sock, server_hostname=None, **_k):
        self.recorded_sni = server_hostname
        self.wrapped = True
        return sock


class _Dialer:
    """Records ``socket.create_connection`` calls and returns a fake socket."""

    def __init__(self, sock):
        self._sock = sock
        self.addresses = []
        self.timeouts = []

    def __call__(self, address, timeout=None, *a, **k):
        self.addresses.append(address)
        self.timeouts.append(timeout)
        return self._sock


class CollectorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    # --- anti-forgery: provenance is derived, not caller-declared ---------- #
    def test_caller_cannot_declare_live_capture_on_a_fixture(self):
        c = collector.Collector(collector.FixtureFetcher({URL: b"hello world"}))
        r = c.capture(URL)
        # A fixture is honestly a fixture; there is NO api to set live mode.
        self.assertEqual(r.capture_mode, collector.MODE_FIXTURE)
        self.assertEqual(r.provenance, "fixture")
        self.assertFalse(r.is_operational_live_evidence())
        # There is no way to pass capture_mode / provenance into capture().
        with self.assertRaises(TypeError):
            c.capture(URL, capture_mode="live")  # type: ignore[call-arg]

    def test_trusted_operational_evidence_predicate(self):
        # Trusted-operational evidence is built via the collector only through a
        # policy-owned transport. We unit-test the receipt predicate/contract by
        # constructing a receipt with the collector-derived trust flag set.
        r = collector.CaptureReceipt(
            receipt_id="cap-x", source_url=URL, canonical_id="src-x",
            retrieved_at="2026-01-01T00:00:00+00:00", status=collector.STATUS_OK,
            capture_mode=collector.MODE_LIVE, transport_trusted=True,
            collector_name="c", collector_version="1", fetcher_name="urllib",
            content_hash="abc", content_bytes=3, http_status=200, final_url=URL,
            provenance="live-capture", error=None, partial=False)
        self.assertTrue(r.is_operational_live_evidence())
        self.assertEqual(collector.evidence_class(r),
                         collector.EVIDENCE_TRUSTED_OPERATIONAL)

    def test_no_public_registration_api(self):
        # LEAD-018: ordinary callers must NOT be able to grant operational trust.
        self.assertFalse(hasattr(collector, "register_trusted_transport"))

    def test_arbitrary_live_fetcher_is_not_operational_live_evidence(self):
        """An ad-hoc object declaring mode='live' must NOT be trusted merely
        because it says so — the core SB-V05-001 repair contract."""
        class UntrustedLiveStub:
            mode = collector.MODE_LIVE
            name = "untrusted-live-stub"

            def fetch(self, url):
                return collector.FetchResult(ok=True, content=b"payload",
                                             final_url=url, http_status=200)

        c = collector.Collector(UntrustedLiveStub())
        r = c.capture(URL)
        self.assertEqual(r.capture_mode, collector.MODE_LIVE)
        self.assertFalse(r.transport_trusted)
        self.assertEqual(r.provenance, "unverified-untrusted-transport")
        self.assertFalse(r.is_operational_live_evidence())
        # It is still a content-verified retrieval, just not operational-live.
        self.assertTrue(r.is_verified_capture())

    def test_builtin_urllib_fetcher_is_trusted(self):
        self.assertTrue(collector.is_trusted_transport(collector.UrllibFetcher()))
        self.assertFalse(collector.is_trusted_transport(
            collector.FixtureFetcher({})))

    def test_invalid_fetcher_mode_rejected(self):
        class BadFetcher:
            mode = "totally-real"
            name = "bad"

            def fetch(self, url):
                return collector.FetchResult(ok=True, content=b"x")

        with self.assertRaises(ValueError):
            collector.Collector(BadFetcher())

    # --- same source twice: separate receipts, stable hash ---------------- #
    def test_same_source_twice_separate_receipts_stable_hash(self):
        c = collector.Collector(collector.FixtureFetcher({URL: b"unchanged bytes"}))
        r1 = c.capture(URL)
        r2 = c.capture(URL)
        self.assertNotEqual(r1.receipt_id, r2.receipt_id)          # separate receipts
        self.assertEqual(r1.canonical_id, r2.canonical_id)         # same source id
        self.assertEqual(r1.content_hash, r2.content_hash)         # stable content hash
        self.assertTrue(r1.is_verified_capture())
        self.assertTrue(r2.is_verified_capture())

    # --- changed content: changed hash ------------------------------------ #
    def test_changed_content_changes_hash(self):
        first = collector.Collector(collector.FixtureFetcher({URL: b"version one"}))
        second = collector.Collector(collector.FixtureFetcher({URL: b"version two"}))
        r1 = first.capture(URL)
        r2 = second.capture(URL)
        self.assertEqual(r1.canonical_id, r2.canonical_id)
        self.assertNotEqual(r1.content_hash, r2.content_hash)

    # --- failed retrieval cannot be verified current evidence ------------- #
    def test_failed_retrieval_not_verified(self):
        c = collector.Collector(collector.FixtureFetcher({}))  # URL not present
        r = c.capture(URL)
        self.assertEqual(r.status, collector.STATUS_FAILED)
        self.assertIsNone(r.content_hash)
        self.assertFalse(r.is_verified_capture())
        self.assertFalse(r.is_operational_live_evidence())
        self.assertTrue(r.provenance.startswith("unverified"))

    def test_empty_and_partial_states(self):
        empty = collector.Collector(
            collector.FixtureFetcher({URL: collector.FetchResult(ok=True, content=b"")}))
        r_empty = empty.capture(URL)
        self.assertEqual(r_empty.status, collector.STATUS_EMPTY)
        self.assertFalse(r_empty.is_verified_capture())

        partial = collector.Collector(
            collector.FixtureFetcher(
                {URL: collector.FetchResult(ok=True, content=b"half", partial=True)}))
        r_partial = partial.capture(URL)
        self.assertEqual(r_partial.status, collector.STATUS_PARTIAL)
        self.assertFalse(r_partial.is_verified_capture())

    # --- receipt retains the required minimum fields ---------------------- #
    def test_receipt_minimum_fields(self):
        c = collector.Collector(collector.FixtureFetcher({URL: b"content"}))
        r = c.capture(URL, extractor=_extract_len)
        d = r.as_dict()
        for key in ("source_url", "canonical_id", "retrieved_at", "status",
                    "collector_name", "collector_version", "content_hash",
                    "provenance", "error", "extracted"):
            self.assertIn(key, d)
        self.assertEqual(r.collector_version, collector.COLLECTOR_VERSION)
        self.assertEqual(r.extracted["byte_len"], len(b"content"))

    def test_no_secrets_in_receipt(self):
        c = collector.Collector(collector.FixtureFetcher({URL: b"data"}))
        r = c.capture(URL)
        blob = str(r.as_dict()).lower()
        for forbidden in ("cookie", "password", "authorization", "token", "secret"):
            self.assertNotIn(forbidden, blob)

    # --- persistence: each capture is a distinct durable receipt ---------- #
    def test_persist_writes_separate_receipts(self):
        c = collector.Collector(collector.FixtureFetcher({URL: b"same"}))
        collector.persist("social-a", c.capture(URL))
        collector.persist("social-a", c.capture(URL))
        idx = collector.load_captures("social-a")
        self.assertEqual(len(idx), 2)
        self.assertEqual(idx[0]["content_hash"], idx[1]["content_hash"])
        self.assertNotEqual(idx[0]["receipt_id"], idx[1]["receipt_id"])

    # --- safe public-destination validation (SSRF defence) ---------------- #
    def test_validate_public_url_rejects_unsafe_destinations(self):
        unsafe = [
            "http://127.0.0.1/x",          # loopback
            "http://localhost/x",          # loopback by name
            "http://10.0.0.1/x",           # private
            "http://192.168.1.10/x",       # private
            "http://172.16.5.4/x",         # private
            "http://169.254.169.254/",     # link-local (cloud metadata)
            "http://[::1]/x",              # IPv6 loopback
            "http://224.0.0.1/x",          # multicast
            "http://0.0.0.0/x",            # unspecified
            "ftp://example.org/x",         # disallowed scheme
            "file:///etc/passwd",          # disallowed scheme
            "http:///nohost",              # missing host
        ]
        for url in unsafe:
            with self.assertRaises(collector.UnsafeDestinationError, msg=url):
                collector.validate_public_url(url)

    def test_validate_public_url_accepts_public_literal_ip(self):
        # A literal public IP needs no DNS; classification is offline-safe.
        parsed = collector.validate_public_url("https://93.184.216.34/x")
        self.assertEqual(parsed.scheme, "https")

    def test_urllib_fetcher_refuses_unsafe_initial_destination(self):
        f = collector.UrllibFetcher()
        res = f.fetch("http://169.254.169.254/latest/meta-data/")
        self.assertFalse(res.ok)
        self.assertTrue(res.error.startswith("unsafe-destination"))

    def test_resolve_and_validate_pins_public_ip(self):
        # A literal public IP resolves offline and is pinned for connection.
        pinned = collector.resolve_and_validate("https://93.184.216.34/x")
        self.assertEqual(pinned.ip, "93.184.216.34")
        self.assertEqual(pinned.scheme, "https")
        self.assertEqual(pinned.port, 443)

    def test_resolve_and_validate_rejects_private(self):
        with self.assertRaises(collector.UnsafeDestinationError):
            collector.resolve_and_validate("http://10.0.0.1/x")

    # --- SB-V05-001 / LEAD-020: the REAL production HTTPS connection path ---- #
    def test_production_https_path_pins_ip_and_uses_original_host(self):
        """Exercise the real ``_perform`` HTTPS construction end-to-end with only
        the socket/TLS I/O faked.

        This is the regression that would have caught the LEAD-020 defect: the
        real ``http.client.HTTPSConnection`` constructor runs here, so an
        unsupported keyword (the old ``server_hostname=`` argument) would raise
        ``TypeError`` and fail this test. It also proves the safety semantics:
        the socket connects to the PINNED validated IP, while TLS SNI and the
        HTTP Host header use the ORIGINAL hostname (not the IP).
        """
        response = (b"HTTP/1.1 200 OK\r\n"
                    b"Content-Length: 5\r\n"
                    b"Content-Type: text/plain\r\n\r\nhello")
        sock = _FakeSocket(response)
        dialer = _Dialer(sock)
        ctx = _RecordingTLSContext()
        pinned = collector.PinnedDestination(
            scheme="https", host="example.com", ip="93.184.216.34", port=443)

        with mock.patch.object(collector.socket, "create_connection", dialer), \
             mock.patch.object(collector.ssl, "create_default_context",
                               return_value=ctx):
            res = collector.UrllibFetcher()._perform(
                "https://example.com/path?q=1", pinned)

        # A real, successful retrieval — not a swallowed constructor error.
        self.assertTrue(res.ok, msg=f"error={res.error}")
        self.assertEqual(res.content, b"hello")
        self.assertEqual(res.http_status, 200)
        # Socket connected to the PINNED validated public IP (no re-resolution).
        self.assertEqual(dialer.addresses, [("93.184.216.34", 443)])
        # TLS SNI / cert verification bound to the ORIGINAL hostname.
        self.assertTrue(ctx.wrapped)
        self.assertEqual(ctx.recorded_sni, "example.com")
        # Host header carries the original hostname; the pinned IP is not leaked
        # into the request line/headers.
        sent = bytes(sock.sent)
        self.assertIn(b"Host: example.com", sent)
        self.assertIn(b"GET /path?q=1", sent)
        self.assertNotIn(b"93.184.216.34", sent)
        self.assertTrue(sock.closed)

    def test_production_http_path_pins_ip_no_tls(self):
        """The plain-HTTP production path also connects to the pinned IP and
        never invokes TLS wrapping."""
        response = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nhi"
        sock = _FakeSocket(response)
        dialer = _Dialer(sock)
        ctx = _RecordingTLSContext()
        pinned = collector.PinnedDestination(
            scheme="http", host="example.com", ip="93.184.216.34", port=80)

        with mock.patch.object(collector.socket, "create_connection", dialer), \
             mock.patch.object(collector.ssl, "create_default_context",
                               return_value=ctx):
            res = collector.UrllibFetcher()._perform(
                "http://example.com/x", pinned)

        self.assertTrue(res.ok, msg=f"error={res.error}")
        self.assertEqual(res.content, b"hi")
        self.assertEqual(dialer.addresses, [("93.184.216.34", 80)])
        self.assertFalse(ctx.wrapped)  # no TLS on plain HTTP
        self.assertIn(b"Host: example.com", bytes(sock.sent))

    def test_production_https_path_fails_closed_on_redirect(self):
        """A 3xx over the real construction path is a failed retrieval, never
        followed."""
        response = (b"HTTP/1.1 302 Found\r\n"
                    b"Location: https://elsewhere.example/\r\n"
                    b"Content-Length: 0\r\n\r\n")
        sock = _FakeSocket(response)
        dialer = _Dialer(sock)
        ctx = _RecordingTLSContext()
        pinned = collector.PinnedDestination(
            scheme="https", host="ex.org", ip="93.184.216.34", port=443)

        with mock.patch.object(collector.socket, "create_connection", dialer), \
             mock.patch.object(collector.ssl, "create_default_context",
                               return_value=ctx):
            res = collector.UrllibFetcher()._perform("https://ex.org/a", pinned)

        self.assertFalse(res.ok)
        self.assertTrue(res.error.startswith("redirect-not-followed"))
        self.assertEqual(res.http_status, 302)
        # Even on a redirect, SNI was bound to the original host, not the IP.
        self.assertEqual(ctx.recorded_sni, "ex.org")

    # --- downstream bridges distinguish evidence classes ------------------ #
    def test_operational_bridge_rejects_fixture_and_untrusted(self):
        # fixture receipt -> operational bridge rejects.
        fx = collector.Collector(collector.FixtureFetcher({URL: b"x"})).capture(URL)
        self.assertEqual(collector.evidence_class(fx), collector.EVIDENCE_FIXTURE)
        with self.assertRaises(ValueError):
            collector.to_operational_signal(fx, title="T", summary="S")

        # verified-untrusted live receipt -> operational bridge rejects.
        class UntrustedLive:
            mode = collector.MODE_LIVE
            name = "untrusted"

            def fetch(self, url):
                return collector.FetchResult(ok=True, content=b"y", final_url=url,
                                             http_status=200)

        un = collector.Collector(UntrustedLive()).capture(URL)
        self.assertEqual(collector.evidence_class(un),
                         collector.EVIDENCE_VERIFIED_UNTRUSTED)
        with self.assertRaises(ValueError):
            collector.to_operational_signal(un, title="T", summary="S")

        # general bridge still accepts a verified fixture (honestly labelled).
        sig = collector.to_signal(fx, title="T", summary="S")
        self.assertEqual(sig.provenance, "fixture")

    # --- extraction status: failure is never usable factual support ------- #
    def test_extraction_failure_is_not_usable_support(self):
        def boom(content, res):
            raise RuntimeError("bad parse")

        c = collector.Collector(collector.FixtureFetcher({URL: b"content"}))
        r = c.capture(URL, extractor=boom)
        self.assertEqual(r.extraction_status, collector.EXTRACTION_FAILED)
        self.assertEqual(r.extracted, {})
        self.assertEqual(r.extraction_error, "RuntimeError")
        self.assertFalse(r.has_usable_extraction())
        # The error text is never smuggled into extracted factual support.
        self.assertNotIn("extraction_error", r.extracted)

    def test_extraction_success_is_usable(self):
        c = collector.Collector(collector.FixtureFetcher({URL: b"content"}))
        r = c.capture(URL, extractor=_extract_len)
        self.assertEqual(r.extraction_status, collector.EXTRACTION_OK)
        self.assertTrue(r.has_usable_extraction())

    def test_extraction_not_attempted_without_extractor(self):
        c = collector.Collector(collector.FixtureFetcher({URL: b"content"}))
        r = c.capture(URL)
        self.assertEqual(r.extraction_status, collector.EXTRACTION_NOT_ATTEMPTED)
        self.assertFalse(r.has_usable_extraction())

    # --- bridge to signal API: unverified cannot become a signal ---------- #
    def test_to_signal_requires_verified_capture(self):
        good = collector.Collector(collector.FixtureFetcher({URL: b"ok"}))
        sig = collector.to_signal(good.capture(URL), title="T", summary="S",
                                  tags=["x"])
        self.assertIsInstance(sig, research.Signal)
        self.assertEqual(sig.provenance, "fixture")
        self.assertEqual(sig.url, URL)

        bad = collector.Collector(collector.FixtureFetcher({}))
        with self.assertRaises(ValueError):
            collector.to_signal(bad.capture(URL), title="T", summary="S")


if __name__ == "__main__":
    unittest.main()
