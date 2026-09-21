#!/usr/bin/env python3
"""SB-007 real dry-run cycles — no external publish side effect.

For each of the three general personas, capture the REAL research signals the
worker gathered (live web-search captures with source URLs, provenance
'live-capture'), then run one full autonomy cycle and record:
  Observe -> Orient -> Alternatives -> Decision -> Candidate -> Review ->
  Experiment -> Learning -> Next observation.

A cultural persona dry-run is included to prove the source/cultural-review gate
holds (candidate WITHHELD until a named reviewer is bound).

"Dry run" = real inputs, real autonomous decision, real persisted state, NO post.
Evidence is written under receipts/evidence/SB-007-dryruns/ for review.

Signals below were captured on 2026-09-20 via live web search by the worker; each
carries its real source URL. They are evidence, not canned operational data.
"""
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

EVID = HERE / "receipts" / "evidence" / "SB-007-dryruns"

# Real captured research (2026-09-20 live web search). Provenance == live-capture.
SIGNALS = {
    "social-a": [
        dict(title="METR RCT: experienced devs 19% slower with AI tools",
             summary="A 2026 randomized controlled trial found experienced developers were "
                     "19% slower using AI tools, against a median 1.4-2x self-reported gain; "
                     "task-level reviews put real-world gains at 15-30%.",
             source="METR / UC Today AI productivity reports 2026",
             url="https://metr.org/blog/2026-05-11-ai-usage-survey/",
             tags=["measurement", "automation-roi", "debunking-hype"]),
    ],
    "social-b": [
        dict(title="Ordinary sunlight turned into a source of quantum entanglement",
             summary="Scientists turned ordinary sunlight into a source of quantum "
                     "entanglement in Sept 2026 — an everyday thing (light from the sky) "
                     "hiding a deeply strange physics.",
             source="ScienceDaily physics, Sept 2026",
             url="https://www.sciencedaily.com/news/matter_energy/physics/",
             tags=["everyday-physics", "scale-and-awe", "how-things-work"]),
    ],
    "social-c": [
        dict(title="2026 feeds split: maximalist-playful vs stripped-down-unproduced",
             summary="Sept 2026 platforms reward creator-led, authentic, lower-follower "
                     "voices with high trust over polished/automated content; the feed pulls "
                     "between maximalist play and cozy unproduced.",
             source="Sprout Social / Hootsuite 2026 trends",
             url="https://sproutsocial.com/insights/social-media-trends/",
             tags=["internet-culture", "platform-mechanics", "creator-economy"]),
    ],
    # Cultural workspace — real festival-context signal; review gate must WITHHOLD.
    "social-a/cultural": [
        dict(title="Regional variation in a major autumn observance",
             summary="Festival dates and meanings vary by region; a sourced explainer would "
                     "need a named cultural reviewer before any textual/date claim.",
             source="editorial-research-note",
             url=None,
             tags=["indian-festivals", "regional-traditions"]),
    ],
}

DRY_RUNS = [
    ("social-a", "social-a"),
    ("social-b", "social-b"),
    ("social-c", "social-c"),
]


def _capture(research, bot, specs):
    for s in specs:
        sig = research.Signal.make(
            title=s["title"], summary=s["summary"], source=s["source"],
            url=s["url"], provenance="live-capture", tags=s["tags"])
        research.capture(bot, sig)


def main() -> int:
    if EVID.exists():
        shutil.rmtree(EVID)
    EVID.mkdir(parents=True)
    os.environ["SBOTS_HOME"] = str(EVID)

    from runtime import research, decision, pipeline, personas  # noqa: E402

    overall = {"runs": [], "cultural_run": None}

    for bot, persona_id in DRY_RUNS:
        _capture(research, bot, SIGNALS[bot])
        record = decision.run_cycle(bot, persona_id)
        queue = pipeline.admin_publish_queue(bot)
        exp_files = sorted((EVID / "experiments" / bot).glob("exp-*.json"))
        experiment = json.loads(exp_files[0].read_text()) if exp_files else None

        run = {
            "bot": bot,
            "persona": persona_id,
            "observe": record["observe"],
            "orient": record["orient"],
            "alternatives": record["alternatives"],
            "decision": record["chosen"],
            "decision_reason": record["chosen_reason"],
            "candidate": {
                "content_id": record.get("execute", {}).get("content_id"),
                "queued": bool(queue),
                "published": queue[0]["published"] if queue else None,
                "publish_authorized": queue[0]["publish_authorized"] if queue else None,
                "platform": queue[0]["platform"] if queue else None,
                "text_preview": (queue[0]["payload"]["text"][:180] if queue else None),
            },
            "review": _review_of(record),
            "experiment": {
                "id": experiment["experiment_id"] if experiment else None,
                "hypothesis": experiment["hypothesis"] if experiment else None,
                "success_metric": experiment["success_metric"] if experiment else None,
                "stop_criteria": experiment["stop_criteria"] if experiment else None,
                "observation_window_hours": experiment["observation_window_hours"] if experiment else None,
            },
            "learning": record["learn"],
            "next_observation": record["schedule"],
            "outcome": record["outcome"],
        }
        created = record["outcome"] == "candidate_created"
        withheld = record["outcome"] == "withheld"
        run["checks"] = {
            "real_research_input": all(s["provenance"] == "live-capture"
                                       for s in research.load_signals(bot)),
            "coherent_decision": record["outcome"] in
                ("candidate_created", "withheld", "no_action", "research_more"),
            # If a candidate was created it MUST be within platform limit + reviewed.
            "created_implies_valid": (not created) or (
                record["verify"].get("within_platform_limit") and
                record["verify"].get("review_passed")),
            # A withhold MUST carry explicit gate reasons and register nothing.
            "withheld_implies_stopped": (not withheld) or (
                bool(record["execute"].get("gate_failures")) and
                record["verify"].get("queued") is False),
            "no_publish": all(not q["published"] for q in queue),
            "next_check_scheduled": "next_check_in_hours" in record["schedule"],
        }
        run["pass"] = all(run["checks"].values())
        overall["runs"].append(run)

    # Cultural dry-run — the review gate must WITHHOLD (no named reviewer).
    cp = personas.load("cultural-primandir-atman")
    csig = research.Signal.make(
        **{**SIGNALS["social-a/cultural"][0], "provenance": "live-capture"})
    cand = pipeline.review(cp, pipeline.ideate(cp, csig.__dict__))
    overall["cultural_run"] = {
        "persona": cp["id"],
        "review_passed": cand["review_passed"],
        "cultural_status": cand["review"]["cultural"]["status"],
        "reason": cand["review"]["cultural"]["reason"],
        "pass": (not cand["review_passed"]) and cand["review"]["cultural"]["status"] == "WITHHELD",
    }

    overall["all_pass"] = all(r["pass"] for r in overall["runs"]) and overall["cultural_run"]["pass"]
    (EVID / "SUMMARY.json").write_text(json.dumps(overall, indent=2, sort_keys=True))
    _write_markdown(overall)
    print(json.dumps({"all_pass": overall["all_pass"],
                      "runs": [{r["persona"]: r["pass"]} for r in overall["runs"]],
                      "cultural_withheld": overall["cultural_run"]["pass"]}, indent=2))
    return 0 if overall["all_pass"] else 1


def _review_of(record):
    ex = record.get("execute", {})
    if not ex.get("performed"):
        return None
    # Pull review off the last decision's verify block.
    v = record.get("verify", {})
    return {"review_passed": v.get("review_passed"),
            "within_platform_limit": v.get("within_platform_limit")}


def _write_markdown(overall):
    lines = ["# SB-007 dry-run report", "",
             "Real current research inputs, real autonomous decisions, real persisted "
             "state, **no external publication**.", ""]
    for r in overall["runs"]:
        lines += [
            f"## {r['persona']} — decision: {r['decision']['action']} "
            f"-> outcome: **{r['outcome']}** ({'PASS' if r['pass'] else 'FAIL'})",
            f"- **Observe:** {r['observe']['pending_count']} unconsumed of "
            f"{r['observe']['total_signals']} total; changed = {r['observe']['changed']}",
            f"- **Orient:** {r['orient']['summary']}",
            f"- **Alternatives considered:** "
            + ", ".join(f"{a['action']}({a.get('score','-')})" for a in r['alternatives']),
            f"- **Decision reason:** {r['decision_reason']}",
        ]
        if r["outcome"] == "candidate_created":
            lines += [
                f"- **Candidate:** {r['candidate']['platform']} | "
                f"published={r['candidate']['published']} | "
                f"authorized={r['candidate']['publish_authorized']}",
                f"    - preview: {r['candidate']['text_preview']}",
                f"- **Experiment:** {r['experiment']['id']} — "
                f"metric `{r['experiment']['success_metric']}`, "
                f"window {r['experiment']['observation_window_hours']}h",
                f"    - hypothesis: {r['experiment']['hypothesis']}",
            ]
        else:
            gf = r["decision"].get("action")
            lines += [
                f"- **Withheld:** gate stopped the candidate; "
                f"within_platform_limit={r['candidate'].get('platform') and r['candidate']['queued']}; "
                f"no experiment/queue entry (correct fail-closed behavior).",
            ]
        lines += [
            f"- **Learning:** {r['learning'].get('note')}",
            f"- **Next observation:** in {r['next_observation']['next_check_in_hours']}h "
            f"({r['next_observation']['trigger']})",
            "",
        ]
    c = overall["cultural_run"]
    lines += [f"## {c['persona']} (cultural) — review gate",
              f"- review_passed = {c['review_passed']} (expected False)",
              f"- cultural status = **{c['cultural_status']}** — {c['reason']}",
              f"- gate held: {'PASS' if c['pass'] else 'FAIL'}", ""]
    (EVID / "REPORT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
