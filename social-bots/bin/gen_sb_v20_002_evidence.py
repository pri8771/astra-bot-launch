#!/usr/bin/env python3
"""Generate SB-V20-002 evidence from FIXTURE evidence bundles only.

Engineering fixtures; NOT real analytics/audience/experiment data.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from runtime import growth_evaluator as ge, metrics  # noqa: E402

OUT = ROOT / "receipts" / "evidence" / "SB-V20-002-growth"
OUT.mkdir(parents=True, exist_ok=True)

BOT, P1, P2 = "social-a", "general-1", "cultural-1"


def avail(*p):
    return {x: {"available": True} for x in p}


def opp(id, platform, persona=P1, **kw):
    return ge.OpportunityInput(id=id, bot=BOT, persona=persona, platform=platform,
                               format="text", **kw)


checks = {}

# 1) different evidence => different allocation.
a1 = [opp("a", "x", performance={"value": 0.8, "samples": 20},
          audience_support={"confidence": 0.8}),
      opp("b", "reddit", performance={"value": 0.2, "samples": 20},
          audience_support={"confidence": 0.5})]
a2 = [opp("a", "x", performance={"value": 0.2, "samples": 20},
          audience_support={"confidence": 0.5}),
      opp("b", "reddit", performance={"value": 0.8, "samples": 20},
          audience_support={"confidence": 0.8})]
o1 = ge.evaluate(a1, availability=avail("x", "reddit"), learning_weight=0.1)
o2 = ge.evaluate(a2, availability=avail("x", "reddit"), learning_weight=0.1)
checks["different_evidence_different_allocation"] = {
    "run1_top": o1["allocation"][0]["opportunity_id"],
    "run2_top": o2["allocation"][0]["opportunity_id"],
    "pass": o1["allocation"][0]["opportunity_id"] == "a"
            and o2["allocation"][0]["opportunity_id"] == "b",
}

# 2) learning beats reach when justified.
known = opp("known", "x", performance={"value": 0.6, "samples": 30},
            audience_support={"confidence": 0.7})
explore = opp("explore", "reddit", performance=None, learning_question=True)
low = ge.evaluate([known, explore], availability=avail("x", "reddit"), learning_weight=0.2)
high = ge.evaluate([known, explore], availability=avail("x", "reddit"), learning_weight=5.0)
checks["learning_can_beat_reach"] = {
    "low_lw_top": low["allocation"][0]["opportunity_id"],
    "high_lw_top": high["allocation"][0]["opportunity_id"],
    "pass": low["allocation"][0]["opportunity_id"] == "known"
            and high["allocation"][0]["opportunity_id"] == "explore",
}

# 3) missing data not zero; insufficient => no recommendation.
miss = ge.evaluate([opp("m", "x", performance=None, learning_question=True)],
                   availability=avail("x"))
insuf = ge.evaluate([opp("i", "x", performance=None, learning_question=False)],
                    availability=avail("x"))
checks["missing_and_insufficient"] = {
    "missing_is_learning_not_growth": (miss["growth_opportunities"] == []
                                       and len(miss["learning_opportunities"]) == 1),
    "missing_performance_is_none": miss["learning_opportunities"][0]["performance"] is None,
    "insufficient_no_allocation": insuf["allocation"] == []
                                  and len(insuf["insufficient_evidence"]) == 1,
    "pass": (miss["growth_opportunities"] == []
             and miss["learning_opportunities"][0]["performance"] is None
             and insuf["allocation"] == []),
}

# 4) no monetary spend authorized.
checks["no_spend"] = {"spend_authorized": o1["spend_authorized"],
                      "pass": o1["spend_authorized"] is False}

# 5) two personas on one runtime stay distinguishable in every record.
two = ge.evaluate([opp("a", "x", persona=P1,
                       performance={"value": 0.6, "samples": 10},
                       audience_support={"confidence": 0.6}),
                   opp("b", "x", persona=P2,
                       performance={"value": 0.6, "samples": 10},
                       audience_support={"confidence": 0.6})],
                  availability=avail("x"))
personas = sorted({a["persona"] for a in two["allocation"]})
checks["persona_distinguishable"] = {
    "allocation_personas": personas,
    "pass": personas == sorted([P1, P2]),
}

# 6) arbitrary numeric input is test-only; evidence-backed is growth-eligible.
test_only = opp("t", "x", performance={"value": 0.9, "samples": 10},
                audience_support={"confidence": 0.9})
to_out = ge.evaluate([test_only], availability=avail("x"), require_evidence=True)
obs = metrics.normalize(platform="x", source="fixture", persona=P1, content_id="c1",
                        window_start="2026-09-20T00:00:00+00:00",
                        window_end="2026-09-21T00:00:00+00:00",
                        raw_metrics={"impressions": 1000})
ev_opp = ge.opportunity_from_evidence(
    id="e", bot=BOT, persona=P1, platform="x", format="text",
    performance_value=0.7, samples=10, metric_observation=obs,
    audience_confidence={"confidence": 0.8, "hypothesis_id": "hyp-1",
                         "scope": {"bot": BOT, "persona": P1}},
    now=datetime(2026, 9, 21, 1, tzinfo=timezone.utc))
ev_out = ge.evaluate([ev_opp], availability=avail("x"), require_evidence=True)
checks["typed_evidence_vs_test_only"] = {
    "test_only_growth": to_out["growth_opportunities"],
    "evidence_growth_count": len(ev_out["growth_opportunities"]),
    "pass": (to_out["growth_opportunities"] == []
             and len(ev_out["growth_opportunities"]) == 1
             and ev_opp.provenance == ge.PROV_EVIDENCE),
}

# 7) stale evidence demoted to learning, never growth.
old_end = (datetime.now(timezone.utc) - timedelta(hours=100)).isoformat()
stale_obs = metrics.normalize(platform="x", source="fixture", persona=P1,
                              content_id="c1", window_end=old_end,
                              raw_metrics={"impressions": 1000})
stale_opp = ge.opportunity_from_evidence(
    id="s", bot=BOT, persona=P1, platform="x", format="text",
    performance_value=0.9, metric_observation=stale_obs, max_age_hours=48.0)
stale_out = ge.evaluate([stale_opp], availability=avail("x"), require_evidence=True)
checks["stale_evidence_not_growth"] = {
    "growth": stale_out["growth_opportunities"],
    "learning_count": len(stale_out["learning_opportunities"]),
    "pass": (stale_out["growth_opportunities"] == []
             and len(stale_out["learning_opportunities"]) == 1),
}

summary = {
    "artifact": "SB-V20-002",
    "kind": "fixture-evidence",
    "warning": "FIXTURE evidence bundles only; not real analytics/audience data.",
    "checks": checks,
    "all_pass": all(v["pass"] for v in checks.values()),
}
(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({"all_pass": summary["all_pass"], "out": str(OUT)}, indent=2))
if not summary["all_pass"]:
    sys.exit(1)
