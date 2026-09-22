import json, os, tempfile
from runtime import metrics
from runtime.jsonstore import append_jsonl

CASES = []
def promote(obs, *, raw_name, raw_value):
    row = obs.as_dict()
    row["normalized"][metrics.REACH] = {
        "semantic": metrics.REACH, "availability": metrics.PRESENT,
        "value": float(raw_value), "raw_name": raw_name,
        "raw_value": float(raw_value), "metric_kind": metrics.CUMULATIVE_SNAPSHOT,
    }
    row["raw_metrics"] = {raw_name: raw_value}
    return row

with tempfile.TemporaryDirectory(prefix="bots-v13-map-") as home:
    os.environ["SBOTS_HOME"] = home
    tiktok = metrics.normalize(platform="tiktok", source="capture:tiktok", persona="p",
        content_id="tt", collected_at="2026-09-22T12:00:00+00:00",
        raw_metrics={"video_views": 1})
    x = metrics.normalize(platform="x", source="capture:x", persona="p",
        content_id="x", collected_at="2026-09-22T12:00:00+00:00",
        raw_metrics={"likes": 1})
    append_jsonl(metrics._store("bot-a"), promote(tiktok, raw_name="impressions", raw_value=11))
    append_jsonl(metrics._store("bot-a"), promote(x, raw_name="likes", raw_value=13))
    print(json.dumps({"stored": metrics.observations_for("bot-a"),
                      "aggregate": metrics.aggregate_semantic("bot-a", metrics.REACH)},
                     indent=2, sort_keys=True))
