"""SB-V05-001 — machine-captured source collector acceptance tests.

All tests use explicit FIXTURE fetchers. Fixtures are marked as fixtures by the
collector and never masquerade as operational live capture.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import collector, research  # noqa: E402


URL = "https://example.org/article"


def _extract_len(content, res):
    return {"byte_len": len(content or b""), "http_status": res.http_status}


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

    def test_trusted_live_transport_yields_operational_live_evidence(self):
        @collector.register_trusted_transport
        class TrustedLiveStub:
            mode = collector.MODE_LIVE
            name = "trusted-live-stub"

            def fetch(self, url):
                return collector.FetchResult(ok=True, content=b"payload",
                                             final_url=url, http_status=200)

        try:
            c = collector.Collector(TrustedLiveStub())
            r = c.capture(URL)
            self.assertEqual(r.capture_mode, collector.MODE_LIVE)
            self.assertTrue(r.transport_trusted)
            self.assertEqual(r.provenance, "live-capture")
            self.assertTrue(r.is_operational_live_evidence())
        finally:
            collector._TRUSTED_TRANSPORT_CLASSES.discard(TrustedLiveStub)

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

    def test_urllib_fetcher_rejects_redirect_to_private_destination(self):
        """A public URL that redirects to a private/loopback destination is
        rejected at the redirect hop, not followed."""
        class RedirectToPrivate(collector.UrllibFetcher):
            def _perform(self, url):
                return collector._Redirect("http://127.0.0.1/secret")

        c = collector.Collector(RedirectToPrivate())
        # Register the subclass so trust is not the thing under test here.
        collector.register_trusted_transport(RedirectToPrivate)
        try:
            r = c.capture("https://93.184.216.34/start")
            self.assertEqual(r.status, collector.STATUS_FAILED)
            self.assertTrue(r.error.startswith("unsafe-redirect"))
            self.assertFalse(r.is_operational_live_evidence())
        finally:
            collector._TRUSTED_TRANSPORT_CLASSES.discard(RedirectToPrivate)

    def test_urllib_fetcher_follows_validated_public_redirect(self):
        class RedirectThenContent(collector.UrllibFetcher):
            def __init__(self):
                super().__init__()
                self._hops = 0

            def _perform(self, url):
                self._hops += 1
                if self._hops == 1:
                    return collector._Redirect("https://93.184.216.34/final")
                return collector.FetchResult(ok=True, content=b"final-bytes",
                                             final_url=url, http_status=200)

        collector.register_trusted_transport(RedirectThenContent)
        try:
            c = collector.Collector(RedirectThenContent())
            r = c.capture("https://93.184.216.34/start")
            self.assertEqual(r.status, collector.STATUS_OK)
            self.assertTrue(r.is_operational_live_evidence())
        finally:
            collector._TRUSTED_TRANSPORT_CLASSES.discard(RedirectThenContent)

    def test_urllib_fetcher_too_many_redirects(self):
        class AlwaysRedirect(collector.UrllibFetcher):
            def _perform(self, url):
                return collector._Redirect("https://93.184.216.34/next")

        f = AlwaysRedirect()
        res = f.fetch("https://93.184.216.34/start")
        self.assertFalse(res.ok)
        self.assertEqual(res.error, "too-many-redirects")

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
