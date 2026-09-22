#!/usr/bin/env python3
import os
import sys
import tempfile
from pathlib import Path

# Intentionally imports the checked-out source from the invocation cwd.
sys.path.insert(0, str(Path.cwd()))
from runtime import metrics  # noqa: E402

print(f"metrics_module={Path(metrics.__file__).resolve()}")
print("source_head=9d497b4567e022a8e7f93a3ee890af206272b5be")

huge = 10 ** 10000
try:
    metrics.normalize(platform="x", source="fixture:overflow",
                      raw_metrics={"impressions": huge})
except Exception as exc:
    print(f"normalize_huge_int={type(exc).__name__}: {exc}")

with tempfile.TemporaryDirectory(prefix="bots-metrics-overflow-") as home:
    os.environ["SBOTS_HOME"] = home
    for cid in ("a", "b"):
        metrics.record("social-a", metrics.normalize(
            platform="x", source="fixture:overflow", content_id=cid,
            window_end="2026-09-22T00:00:00+00:00",
            raw_metrics={"impressions": 1e308},
        ))
    snap = metrics.aggregate_semantic("social-a", metrics.REACH)["by_platform"]["x"]["kinds"][metrics.CUMULATIVE_SNAPSHOT]
    print(f"finite_snapshot_inputs={[1e308, 1e308]!r}")
    print(f"snapshot_aggregate={snap['value']!r}")

with tempfile.TemporaryDirectory(prefix="bots-metrics-overflow-delta-") as home:
    os.environ["SBOTS_HOME"] = home
    for cid, start, end in (
        ("a", "2026-09-20T00:00:00+00:00", "2026-09-21T00:00:00+00:00"),
        ("b", "2026-09-21T00:00:00+00:00", "2026-09-22T00:00:00+00:00"),
    ):
        metrics.record("social-a", metrics.normalize(
            platform="x", source="fixture:overflow", content_id=cid,
            window_start=start, window_end=end,
            raw_metrics={"follows": 1e308},
        ))
    delta = metrics.aggregate_semantic("social-a", metrics.FOLLOW)["by_platform"]["x"]["kinds"][metrics.DELTA]
    print(f"delta_aggregate={delta['value']!r}")

