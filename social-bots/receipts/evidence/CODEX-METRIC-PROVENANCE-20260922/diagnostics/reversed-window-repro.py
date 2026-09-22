import json
import os
import tempfile

from runtime import metrics

tmp = tempfile.mkdtemp(prefix="bots-metrics-window-")
os.environ["SBOTS_HOME"] = tmp

obs = metrics.normalize(
    platform="tiktok",
    source="fixture:window-repro",
    account_alias="acct",
    persona="social-a",
    content_id="content-1",
    window_start="2026-09-22T02:00:00+00:00",
    window_end="2026-09-22T01:00:00+00:00",
    raw_metrics={"new_followers": 7},
)
metrics.record("social-a", obs)
stored = metrics.observations_for("social-a")
aggregate = metrics.aggregate_semantic("social-a", metrics.FOLLOW)

print(json.dumps({
    "temp_home": tmp,
    "normalized_window": [obs.window_start, obs.window_end],
    "stored_count": len(stored),
    "stored_window": [stored[0]["window_start"], stored[0]["window_end"]],
    "aggregate": aggregate,
}, indent=2, sort_keys=True))
