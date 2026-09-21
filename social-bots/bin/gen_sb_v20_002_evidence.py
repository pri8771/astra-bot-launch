#!/usr/bin/env python3
"""Generate SB-V20-002 evidence from FIXTURE evidence bundles only.

Engineering fixtures; NOT real analytics/audience/experiment data.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from runtime import growth_evaluator as ge  # noqa: E402

OUT = ROOT / "receipts" / "evidence" / "SB-V20-002-growth"
OUT.mkdir(parents=True, exist_ok=True)


def avail(*p):
    return {x: {"available": True} for x in p}


checks = {}

# 1) different evidence => different allocation.
a1 = [ge.OpportunityInput("a", "x", "text", performance={"value": 0.8, "samples": 20},
                          audience_support={"confidence": 0.8}),
      ge.OpportunityInput("b", "reddit", "text", performance={"value": 0.2, "samples": 20},
                          audience_support={"confidence": 0.5})]
a2 = [ge.OpportunityInput("a", "x", "text", performance={"value": 0.2, "samples": 20},
                          audience_support={"confidence": 0.5}),
      ge.OpportunityInput("b", "reddit", "text", performance={"value": 0.8, "samples": 20},
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
known = ge.OpportunityInput("known", "x", "text",
                            performance={"value": 0.6, "samples": 30},
                            audience_support={"confidence": 0.7})
explore = ge.OpportunityInput("explore", "reddit", "text", performance=None,
                              learning_question=True)
low = ge.evaluate([known, explore], availability=avail("x", "reddit"), learning_weight=0.2)
high = ge.evaluate([known, explore], availability=avail("x", "reddit"), learning_weight=5.0)
checks["learning_can_beat_reach"] = {
    "low_lw_top": low["allocation"][0]["opportunity_id"],
    "high_lw_top": high["allocation"][0]["opportunity_id"],
    "pass": low["allocation"][0]["opportunity_id"] == "known"
            and high["allocation"][0]["opportunity_id"] == "explore",
}

# 3) missing data not zero; insufficient => no recommendation.
miss = ge.evaluate([ge.OpportunityInput("m", "x", "text", performance=None,
                                        learning_question=True)],
                   availability=avail("x"))
insuf = ge.evaluate([ge.OpportunityInput("i", "x", "text", performance=None,
                                         learning_question=False)],
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
checks["no_spend"] = {
    "spend_authorized": o1["spend_authorized"],
    "pass": o1["spend_authorized"] is False,
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
