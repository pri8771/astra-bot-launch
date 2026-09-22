import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from runtime.account_routes import availability_for

NOW = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)
route = {
    "route_id": "malformed-route-type",
    "platform": "x",
    "bot": "social-a",
    "persona": "social-a",
    "route_type": "telepathy",
    "capabilities": {"draft": True, "publish": False},
    "publish_authorized": False,
    "health_status": "verified",
    "last_verified_at": "2026-09-22T11:00:00+00:00",
}
with tempfile.TemporaryDirectory(prefix="bots-route-schema-") as home:
    registry = Path(home) / "accounts" / "registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(json.dumps({"schema_version": 1, "routes": [route]}), encoding="utf-8")
    result = availability_for("social-a", "social-a", ["x"], home=home, now=NOW)
print(json.dumps({"source_sha": "3f10d0f6eb031c00fff679aae18aa8045d8bd025", "safe_input": route, "result": result}, indent=2, sort_keys=True))
