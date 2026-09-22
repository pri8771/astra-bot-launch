import json
import os
import tempfile
from datetime import datetime, timezone
from runtime import metrics

NOW = "2026-09-22T12:00:00+00:00"
invalid_sources = ["", "   ", 17, None]
with tempfile.TemporaryDirectory(prefix="bots-v13-source-") as home:
    os.environ["SBOTS_HOME"] = home
    made = []
    for index, source in enumerate(invalid_sources):
        obs = metrics.normalize(
            platform="x", source=source,
            account_alias="acct-a", persona="persona-a",
            content_id=f"content-{index}", experiment_id="experiment-a",
            window_start="2026-09-22T11:00:00+00:00", window_end=NOW,
            collected_at=NOW, raw_metrics={"impressions": index + 1},
        )
        metrics.record("bot-a", obs)
        made.append({"source_input": source, "normalized_source": obs.source,
                     "trace": metrics.trace_content("bot-a", obs.content_id)})
    persisted = metrics.observations_for("bot-a")
    aggregate = metrics.aggregate_semantic("bot-a", metrics.REACH)
print(json.dumps({
    "source_sha": "3f10d0f6eb031c00fff679aae18aa8045d8bd025",
    "cases": made,
    "persisted_sources": [row["source"] for row in persisted],
    "aggregate": aggregate,
}, indent=2, sort_keys=True))
