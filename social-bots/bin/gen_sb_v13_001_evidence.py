#!/usr/bin/env python3
"""Generate SB-V13-001 evidence from FIXTURE metric payloads only.

These are engineering fixtures, NOT real social metrics.
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["SBOTS_HOME"] = tempfile.mkdtemp(prefix="sbv13-")

from runtime import metrics  # noqa: E402

OUT = ROOT / "receipts" / "evidence" / "SB-V13-001-metrics"
OUT.mkdir(parents=True, exist_ok=True)

checks = {}

# 1) MISSING != ZERO and NOT_SUPPORTED distinct.
ig = metrics.normalize(platform="instagram", source="fixture",
                       raw_metrics={"reach": 0, "plays": 50})
rd = metrics.normalize(platform="reddit", source="fixture",
                       raw_metrics={"num_comments": 3})
checks["missing_zero_notsupported"] = {
    "reach_zero_is_present": ig.metric(metrics.REACH).availability == metrics.PRESENT,
    "save_absent_is_missing": ig.metric(metrics.SAVE).availability == metrics.MISSING,
    "reddit_reach_not_supported": rd.metric(metrics.REACH).availability == metrics.NOT_SUPPORTED,
    "pass": (ig.metric(metrics.REACH).availability == metrics.PRESENT
             and ig.metric(metrics.SAVE).availability == metrics.MISSING
             and rd.metric(metrics.REACH).availability == metrics.NOT_SUPPORTED),
}

# 2) no false equivalence: X reach present, tiktok reach not supported.
x = metrics.normalize(platform="x", source="fixture", raw_metrics={"impressions": 1000})
tt = metrics.normalize(platform="tiktok", source="fixture", raw_metrics={"video_views": 1000})
checks["no_false_equivalence"] = {
    "x_reach": x.metric(metrics.REACH).availability,
    "tiktok_reach": tt.metric(metrics.REACH).availability,
    "pass": (x.metric(metrics.REACH).availability == metrics.PRESENT
             and tt.metric(metrics.REACH).availability == metrics.NOT_SUPPORTED),
}

# 3) traceability raw -> persona/experiment.
obs = metrics.normalize(platform="x", source="capture:cap-xyz", persona="social-a",
                        content_id="c-100", experiment_id="e-7",
                        raw_metrics={"impressions": 42, "replies": 5})
metrics.record("social-a", obs)
trace = metrics.trace_content("social-a", "c-100")
checks["traceability"] = {
    "personas": trace["personas"],
    "experiments": trace["experiments"],
    "raw_impressions": trace["observations"][0]["raw_metrics"]["impressions"],
    "pass": trace["personas"] == ["social-a"] and trace["experiments"] == ["e-7"],
}

# 4) stale window marked; derived records formula/version and MISSING propagation.
old_end = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
stale_obs = metrics.normalize(platform="x", source="fixture", window_end=old_end,
                              raw_metrics={"impressions": 1})
der_ok = metrics.completion_rate(metrics.normalize(
    platform="tiktok", source="fixture",
    raw_metrics={"video_views": 200, "completion_views": 50}))
der_missing = metrics.completion_rate(metrics.normalize(
    platform="tiktok", source="fixture", raw_metrics={"video_views": 200}))
checks["stale_and_derived"] = {
    "stale_marked": metrics.is_stale(stale_obs, max_age_hours=24),
    "derived_value": der_ok.value,
    "derived_formula": der_ok.formula,
    "derived_formula_version": der_ok.formula_version,
    "derived_missing_when_input_missing": der_missing.availability == metrics.MISSING,
    "pass": (metrics.is_stale(stale_obs, max_age_hours=24)
             and abs(der_ok.value - 0.25) < 1e-9
             and der_ok.formula_version == metrics.DERIVED_FORMULA_VERSION
             and der_missing.availability == metrics.MISSING),
}

summary = {
    "artifact": "SB-V13-001",
    "kind": "fixture-evidence",
    "warning": "FIXTURE metric payloads only; NOT real social metrics.",
    "normalization_version": metrics.NORMALIZATION_VERSION,
    "derived_formula_version": metrics.DERIVED_FORMULA_VERSION,
    "checks": checks,
    "all_pass": all(v.get("pass") for v in checks.values()),
}
(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({"all_pass": summary["all_pass"], "out": str(OUT)}, indent=2))
if not summary["all_pass"]:
    sys.exit(1)
