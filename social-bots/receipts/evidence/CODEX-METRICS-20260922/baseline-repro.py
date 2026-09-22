#!/usr/bin/env python3
"""Synthetic V1.3 reproduction. No network, provider, scheduler, or public action."""
import math
import os
import sys
import tempfile
from pathlib import Path

SOURCE = Path("/Users/pchordia/Downloads/swarm_codex/review/bots-integrity-source/social-bots")
sys.path.insert(0, str(SOURCE))
from runtime import metrics  # noqa: E402

with tempfile.TemporaryDirectory(prefix="bots-v13-invalid-") as home:
    os.environ["SBOTS_HOME"] = home
    print("source_head=9d497b4567e022a8e7f93a3ee890af206272b5be")
    for index, value in enumerate((True, float("nan"), float("inf"), float("-inf")), 1):
        obs = metrics.normalize(
            platform="x", source="fixture:invalid-metric-repro",
            account_alias="acct-fixture", persona="social-a",
            content_id=f"content-{index}",
            window_end=f"2026-09-22T0{index}:00:00+00:00",
            raw_metrics={"impressions": value},
        )
        mv = obs.metric(metrics.REACH)
        print(
            f"normalize input={value!r} type={type(value).__name__} "
            f"availability={mv.availability} value={mv.value!r} "
            f"finite={math.isfinite(mv.value) if isinstance(mv.value, float) else None}"
        )
        metrics.record("social-a", obs)

    persisted = metrics.observations_for("social-a")
    print(f"persisted_count={len(persisted)}")
    print("persisted_values=" + repr([
        row["normalized"][metrics.REACH]["value"] for row in persisted
    ]))
    aggregate = metrics.aggregate_semantic("social-a", metrics.REACH)
    result = aggregate["by_platform"]["x"]
    print("aggregate=" + repr(result))

