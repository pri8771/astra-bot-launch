#!/usr/bin/env python3
"""Generate SB-V05-001 evidence from FIXTURE captures only.

This is engineering evidence produced with explicit test fixtures. It is NOT
operational live capture: every receipt here reports capture_mode="fixture" and
is_operational_live_evidence()==False by construction.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Isolate all writes to a throwaway home; only the SUMMARY below is committed.
os.environ["SBOTS_HOME"] = tempfile.mkdtemp(prefix="sbv05-")

from runtime import collector  # noqa: E402

OUT = ROOT / "receipts" / "evidence" / "SB-V05-001-collector"
OUT.mkdir(parents=True, exist_ok=True)

URL = "https://example.org/fixture-article"


def brief(r):
    return {
        "receipt_id": r.receipt_id,
        "source_url": r.source_url,
        "canonical_id": r.canonical_id,
        "status": r.status,
        "capture_mode": r.capture_mode,
        "transport_trusted": r.transport_trusted,
        "provenance": r.provenance,
        "content_hash": r.content_hash,
        "extraction_status": r.extraction_status,
        "is_verified_capture": r.is_verified_capture(),
        "is_operational_live_evidence": r.is_operational_live_evidence(),
        "has_usable_extraction": r.has_usable_extraction(),
    }


checks = {}

# 1) same source captured twice unchanged -> separate receipts, stable hash.
c = collector.Collector(collector.FixtureFetcher({URL: b"stable body v1"}))
r1, r2 = c.capture(URL), c.capture(URL)
checks["same_source_twice"] = {
    "receipt_1": brief(r1),
    "receipt_2": brief(r2),
    "separate_receipts": r1.receipt_id != r2.receipt_id,
    "stable_hash": r1.content_hash == r2.content_hash,
    "pass": r1.receipt_id != r2.receipt_id and r1.content_hash == r2.content_hash,
}

# 2) changed content -> changed hash.
c2 = collector.Collector(collector.FixtureFetcher({URL: b"stable body v2"}))
r3 = c2.capture(URL)
checks["changed_content"] = {
    "old_hash": r1.content_hash,
    "new_hash": r3.content_hash,
    "changed": r1.content_hash != r3.content_hash,
    "pass": r1.content_hash != r3.content_hash,
}

# 3) failed retrieval -> cannot be verified current evidence.
cf = collector.Collector(collector.FixtureFetcher({}))
rf = cf.capture(URL)
checks["failed_retrieval_not_verified"] = {
    "receipt": brief(rf),
    "pass": (not rf.is_verified_capture()) and (not rf.is_operational_live_evidence()),
}

# 4) fixture never masquerades as operational live evidence.
checks["fixture_not_operational"] = {
    "capture_mode": r1.capture_mode,
    "is_operational_live_evidence": r1.is_operational_live_evidence(),
    "pass": r1.capture_mode == "fixture" and not r1.is_operational_live_evidence(),
}

# 5) an arbitrary caller object declaring mode="live" is NOT operational-live
#    evidence — provenance is downgraded to unverified-untrusted-transport.
class _UntrustedLive:
    mode = collector.MODE_LIVE
    name = "untrusted-live"

    def fetch(self, url):
        return collector.FetchResult(ok=True, content=b"claimed-live",
                                     final_url=url, http_status=200)


ru = collector.Collector(_UntrustedLive()).capture(URL)
checks["untrusted_live_not_operational"] = {
    "receipt": brief(ru),
    "pass": (ru.capture_mode == "live"
             and not ru.transport_trusted
             and ru.provenance == "unverified-untrusted-transport"
             and not ru.is_operational_live_evidence()),
}

# 6) live retrieval is restricted to validated public HTTP(S): unsafe
#    destinations (loopback / private / link-local / disallowed scheme) are
#    refused before any network contact.
unsafe = {
    "loopback": "http://127.0.0.1/x",
    "cloud_metadata_link_local": "http://169.254.169.254/latest/meta-data/",
    "private": "http://10.0.0.1/x",
    "disallowed_scheme": "file:///etc/passwd",
}
unsafe_results = {}
for label, u in unsafe.items():
    try:
        collector.validate_public_url(u)
        unsafe_results[label] = {"rejected": False}
    except collector.UnsafeDestinationError as exc:
        unsafe_results[label] = {"rejected": True, "reason": str(exc)}
checks["unsafe_destinations_rejected"] = {
    "results": unsafe_results,
    "pass": all(v["rejected"] for v in unsafe_results.values()),
}

# 7) destination pinning + fail-closed redirects (LEAD-018 hardening).
pinned = collector.resolve_and_validate("https://93.184.216.34/x")
try:
    collector.resolve_and_validate("http://127.0.0.1/secret")
    private_rejected = False
except collector.UnsafeDestinationError:
    private_rejected = True
checks["destination_pinning_and_fail_closed"] = {
    "pinned_ip": pinned.ip,
    "private_rejected": private_rejected,
    "no_public_registration_api": not hasattr(collector, "register_trusted_transport"),
    "pass": (pinned.ip == "93.184.216.34" and private_rejected
             and not hasattr(collector, "register_trusted_transport")),
}

# 7b) operational bridge rejects fixture/untrusted; general bridge labels honestly.
fx = collector.Collector(collector.FixtureFetcher({URL: b"fx"})).capture(URL)
op_rejected_fixture = False
try:
    collector.to_operational_signal(fx, title="T", summary="S")
except ValueError:
    op_rejected_fixture = True
checks["operational_bridge_rejects_fixture"] = {
    "evidence_class": collector.evidence_class(fx),
    "op_rejected_fixture": op_rejected_fixture,
    "pass": (collector.evidence_class(fx) == collector.EVIDENCE_FIXTURE
             and op_rejected_fixture),
}

# 8) extraction failure is never usable factual support and is never smuggled
#    into the extracted evidence dict.
def _boom(content, res):
    raise RuntimeError("parse-failure")


re_fail = collector.Collector(
    collector.FixtureFetcher({URL: b"body"})).capture(URL, extractor=_boom)
checks["extraction_failure_not_usable"] = {
    "extraction_status": re_fail.extraction_status,
    "extracted": re_fail.extracted,
    "extraction_error": re_fail.extraction_error,
    "pass": (re_fail.extraction_status == collector.EXTRACTION_FAILED
             and re_fail.extracted == {}
             and not re_fail.has_usable_extraction()),
}

summary = {
    "artifact": "SB-V05-001",
    "kind": "fixture-evidence",
    "warning": "FIXTURE evidence only; not operational live capture.",
    "collector_name": collector.COLLECTOR_NAME,
    "collector_version": collector.COLLECTOR_VERSION,
    "checks": checks,
    "all_pass": all(v.get("pass") for v in checks.values()),
}

(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({"all_pass": summary["all_pass"], "out": str(OUT)}, indent=2))
if not summary["all_pass"]:
    sys.exit(1)
