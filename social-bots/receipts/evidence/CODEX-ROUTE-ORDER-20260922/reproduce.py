import json, os, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path.cwd() / "social-bots"
sys.path.insert(0, str(SOURCE))
from runtime import account_routes

NOW = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)
BASE = {
    "platform": "x", "bot": "social-a", "persona": "social-a",
    "route_type": "API", "capabilities": {"draft": True, "publish": False},
    "publish_authorized": False,
}
bad = {**BASE, "route_id": "revoked-first", "health_status": "revoked",
       "last_verified_at": "2026-09-22T11:00:00+00:00"}
good = {**BASE, "route_id": "fresh-second", "health_status": "verified",
        "last_verified_at": "2026-09-22T11:00:00+00:00"}

with tempfile.TemporaryDirectory(prefix="bots-route-order-") as home:
    path = Path(home) / "accounts" / "registry.json"
    path.parent.mkdir(parents=True)
    results = {}
    for label, routes in (("bad_then_good", [bad, good]), ("good_then_bad", [good, bad])):
        path.write_text(json.dumps({"schema_version": 1, "routes": routes}))
        results[label] = account_routes.availability_for(
            "social-a", "social-a", ["x"], home=home, now=NOW
        )["availability"]["x"]
    print(json.dumps(results, indent=2, sort_keys=True))
    assert results["bad_then_good"]["account_available"] is False
    assert results["good_then_bad"]["account_available"] is True
    assert results["bad_then_good"]["route_id"] == "revoked-first"
    assert results["good_then_bad"]["route_id"] == "fresh-second"
