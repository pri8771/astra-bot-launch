#!/usr/bin/env python3
"""Generate SB-V05-002 evidence (LEAD-018 hardened, fail-closed).

Fixture captures + a DIAGNOSTIC assessor. No operational semantic assessor is
bundled, so operational support fails closed. Operational gating logic is
demonstrated with constructed operational assessments over trusted-operational
refs (representing what the Core adaptive provider will supply). NOT operational
content review.
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

diag = fc.KeywordSupportAssessor()


def _fx_ref(content, url):
    r = collector.Collector(collector.FixtureFetcher({url: content})).capture(url)
    return r, fc.evidence_ref_from_receipt(r)


def _trusted_ref(rid, h):
    return fc.EvidenceRef(receipt_id=rid, source_url="https://ex.org/x",
                          content_hash=h, retrieved_at="2026-01-01T00:00:00+00:00",
                          evidence_class=fc.EVIDENCE_TRUSTED_OPERATIONAL)


def _op(cid, stance, ref):
    return fc.SupportAssessment(claim_id=cid, stance=stance, evidence=ref,
                               excerpt="e", span=None,
                               assessor_name="core-semantic-assessor",
                               assessor_version="x", operational=True, rationale="core")


checks = {}

# 1) built-in assessor is diagnostic, not operational; no public registration API.
checks["diagnostic_not_operational"] = {
    "assessor_operational": diag.operational,
    "is_operational": fc.is_operational_assessor(diag),
    "no_registration_api": not hasattr(fc, "register_operational_assessor"),
    "pass": (not diag.operational and not fc.is_operational_assessor(diag)
             and not hasattr(fc, "register_operational_assessor")),
}

# 2) fail closed: diagnostic SUPPORTS does not pass a required factual claim.
r, ref = _fx_ref(b"body", "https://ex.org/a")
claim = fc.Claim("c1", "Water expands when it freezes.")
b = fc.assess_bindings(claim, [fc.EvidenceItem(ref, "water expands when it freezes")], diag)
rev = fc.review_claims([claim], b, {r.receipt_id: r.content_hash})
checks["diagnostic_fails_closed"] = {
    "diag_stance": b[0].stance,
    "binding_operational": b[0].operational,
    "status": rev.claim_results[0]["status"],
    "pass": (b[0].stance == fc.SUPPORTS and not b[0].operational
             and not rev.passed and rev.claim_results[0]["status"] == fc.UNKNOWN),
}

# 3) fixtures are test-only: operational stance requires trusted-operational evidence.
checks["fixture_evidence_class"] = {
    "evidence_class": ref.evidence_class,
    "pass": ref.evidence_class == fc.EVIDENCE_FIXTURE,
}

# 4) operational SUPPORTED passes with exact evidence ref.
tref = _trusted_ref("cap-op", "h-op")
cl = fc.Claim("c4", "Water expands when it freezes.")
rev4 = fc.review_claims([cl], [_op(cl.id, fc.SUPPORTS, tref)], {tref.receipt_id: tref.content_hash})
checks["operational_supported_passes"] = {
    "status": rev4.claim_results[0]["status"],
    "pass": rev4.passed and rev4.claim_results[0]["status"] == fc.SUPPORTED,
}

# 5) conflicting operational sources -> CONFLICTED/withheld.
ra, rb = _trusted_ref("cap-a", "ha"), _trusted_ref("cap-b", "hb")
cl5 = fc.Claim("c5", "Vaccines reduce transmission.")
rev5 = fc.review_claims([cl5], [_op(cl5.id, fc.SUPPORTS, ra), _op(cl5.id, fc.REFUTES, rb)],
                        {ra.receipt_id: ra.content_hash, rb.receipt_id: rb.content_hash})
checks["conflicting_conflicted"] = {
    "status": rev5.claim_results[0]["status"],
    "pass": (not rev5.passed) and rev5.claim_results[0]["status"] == fc.CONFLICTED,
}

# 6) changed source hash invalidates stale operational support.
rc = _trusted_ref("cap-c", "orig")
cl6 = fc.Claim("c6", "The bridge spans 500 meters.")
rev6 = fc.review_claims([cl6], [_op(cl6.id, fc.SUPPORTS, rc)], {rc.receipt_id: "changed"})
checks["changed_hash_invalidates"] = {
    "status": rev6.claim_results[0]["status"],
    "stale_reason": rev6.claim_results[0]["stale_evidence"][0]["reason"],
    "pass": (not rev6.passed) and rev6.claim_results[0]["status"] == fc.UNSUPPORTED,
}

# 7) omitted material factual claim cannot bypass review.
text = "Trust us, it's great. Sales grew 300 percent in 2023."
rev7 = fc.review_candidate(text, caller_claims=[], bindings=[], current_hashes={})
checks["omitted_claim_cannot_bypass"] = {
    "identified_claims": rev7.identified_claims,
    "pass": (not rev7.passed) and bool(rev7.identified_claims),
}

summary = {
    "artifact": "SB-V05-002",
    "kind": "fixture-evidence",
    "warning": ("FIXTURE captures + DIAGNOSTIC assessor; operational support is "
                "fail-closed. Operational gating shown with constructed operational "
                "assessments (Core provider stand-in). NOT operational content review."),
    "diagnostic_assessor": diag.name,
    "operational_semantic_provider": "NOT BUNDLED — Core adaptive provider dependency",
    "extractor": fc.HeuristicClaimExtractor().name,
    "checks": checks,
    "all_pass": all(v.get("pass") for v in checks.values()),
}

(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({"all_pass": summary["all_pass"], "out": str(OUT)}, indent=2))
if not summary["all_pass"]:
    sys.exit(1)
