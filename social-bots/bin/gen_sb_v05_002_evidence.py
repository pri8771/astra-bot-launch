#!/usr/bin/env python3
"""Generate SB-V05-002 evidence from FIXTURE captures + a deterministic assessor.

This is engineering evidence produced with explicit test fixtures and the
inspectable KeywordSupportAssessor. It is NOT operational content review: no
live model or external service is involved, and every capture is a fixture.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["SBOTS_HOME"] = tempfile.mkdtemp(prefix="sbv05002-")

from runtime import factcheck as fc, collector  # noqa: E402

OUT = ROOT / "receipts" / "evidence" / "SB-V05-002-factcheck"
OUT.mkdir(parents=True, exist_ok=True)

assessor = fc.KeywordSupportAssessor()


def _ref(content, url):
    r = collector.Collector(collector.FixtureFetcher({url: content})).capture(url)
    return r, fc.evidence_ref_from_receipt(r)


def _item(ref, excerpt):
    return fc.EvidenceItem(ref=ref, excerpt=excerpt)


checks = {}

# 1) supported claim passes via operational assessor with exact evidence ref.
r, ref = _ref(b"body", "https://ex.org/a")
claim = fc.Claim("c1", "Water expands when it freezes.")
b = fc.assess_bindings(claim, [_item(ref, "Tests show water expands when it freezes.")], assessor)
rev = fc.review_claims([claim], b, {r.receipt_id: r.content_hash})
checks["supported_passes"] = {
    "status": rev.claim_results[0]["status"],
    "assessors": rev.claim_results[0]["assessors"],
    "pass": rev.passed and rev.claim_results[0]["status"] == fc.SUPPORTED,
}

# 2) caller-declared (manual) stance is non-operational -> withheld.
r2, ref2 = _ref(b"body", "https://ex.org/b")
claim2 = fc.Claim("c2", "Sales tripled last quarter.")
manual = fc.ManualAssessor({claim2.id: fc.SUPPORTS})
bm = fc.assess_bindings(claim2, [_item(ref2, "unrelated")], manual)
rev2 = fc.review_claims([claim2], bm, {r2.receipt_id: r2.content_hash})
checks["caller_stance_not_operational"] = {
    "binding_operational": bm[0].operational,
    "status": rev2.claim_results[0]["status"],
    "pass": (not bm[0].operational) and (not rev2.passed)
    and rev2.claim_results[0]["status"] == fc.UNKNOWN,
}

# 3) URL present but unsupported fails.
r3, ref3 = _ref(b"body", "https://ex.org/c")
claim3 = fc.Claim("c3", "The lake froze in July.")
b3 = fc.assess_bindings(claim3, [_item(ref3, "This is about quarterly revenue.")], assessor)
rev3 = fc.review_claims([claim3], b3, {r3.receipt_id: r3.content_hash})
checks["url_present_unsupported_fails"] = {
    "status": rev3.claim_results[0]["status"],
    "pass": (not rev3.passed) and rev3.claim_results[0]["status"] == fc.UNSUPPORTED,
}

# 4) conflicting sources -> CONFLICTED/withheld.
ra, refa = _ref(b"s", "https://ex.org/pos")
rb, refb = _ref(b"r", "https://ex.org/neg")
claim4 = fc.Claim("c4", "Vaccines reduce transmission.")
b4 = fc.assess_bindings(claim4, [
    _item(refa, "Vaccines reduce transmission across the cohort."),
    _item(refb, "There is no evidence vaccines reduce transmission."),
], assessor)
rev4 = fc.review_claims([claim4], b4,
                        {ra.receipt_id: ra.content_hash, rb.receipt_id: rb.content_hash})
checks["conflicting_sources_conflicted"] = {
    "status": rev4.claim_results[0]["status"],
    "pass": (not rev4.passed) and rev4.claim_results[0]["status"] == fc.CONFLICTED,
}

# 5) changed source hash invalidates stale support.
r5, ref5 = _ref(b"original", "https://ex.org/d")
claim5 = fc.Claim("c5", "The bridge spans 500 meters.")
b5 = fc.assess_bindings(claim5, [_item(ref5, "The bridge spans 500 meters over the river.")], assessor)
changed = collector.Collector(collector.FixtureFetcher({"https://ex.org/d": b"rewritten"})).capture("https://ex.org/d")
rev5 = fc.review_claims([claim5], b5, {r5.receipt_id: changed.content_hash})
checks["changed_hash_invalidates"] = {
    "status": rev5.claim_results[0]["status"],
    "stale_reason": rev5.claim_results[0]["stale_evidence"][0]["reason"],
    "pass": (not rev5.passed) and rev5.claim_results[0]["status"] == fc.UNSUPPORTED,
}

# 6) omitted material factual claim cannot bypass review.
text = "Trust us, it's great. Sales grew 300 percent in 2023."
rev6 = fc.review_candidate(text, caller_claims=[], bindings=[], current_hashes={})
checks["omitted_claim_cannot_bypass"] = {
    "identified_claims": rev6.identified_claims,
    "pass": (not rev6.passed) and bool(rev6.identified_claims),
}

summary = {
    "artifact": "SB-V05-002",
    "kind": "fixture-evidence",
    "warning": "FIXTURE evidence + deterministic assessor; not operational content review.",
    "assessor_name": assessor.name,
    "assessor_version": assessor.version,
    "extractor": fc.HeuristicClaimExtractor().name,
    "checks": checks,
    "all_pass": all(v.get("pass") for v in checks.values()),
}

(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({"all_pass": summary["all_pass"], "out": str(OUT)}, indent=2))
if not summary["all_pass"]:
    sys.exit(1)
