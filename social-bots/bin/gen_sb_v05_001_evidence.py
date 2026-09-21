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
        "provenance": r.provenance,
        "content_hash": r.content_hash,
        "is_verified_capture": r.is_verified_capture(),
        "is_operational_live_evidence": r.is_operational_live_evidence(),
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
