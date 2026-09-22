#!/usr/bin/env python3
"""Synthetic route-health reproduction; no network or public effect."""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from runtime import account_routes, community_loop  # noqa: E402

BOT = "social-a"
PERSONA = "social-a"
ALIAS = "alias-x"


def route(health):
    return {
        "route_id": f"route-{health}",
        "platform": "x",
        "bot": BOT,
        "persona": PERSONA,
        "route_type": "API",
        "account_alias": ALIAS,
        "capabilities": {"read": True, "draft": True, "reply": True},
        "publish_authorized": False,
        "reply_authorized": True,
        "health_status": health,
        "last_verified_at": "2020-01-01T00:00:00+00:00",
    }


print(f"community_loop_module={Path(community_loop.__file__).resolve()}")
print(f"account_routes_module={Path(account_routes.__file__).resolve()}")
print("source_head=30a2ebdfb45110b2bc6fea0f3d50876583487f9c")
for health in ("expired", "revoked", "unverified"):
    with tempfile.TemporaryDirectory(prefix="bots-community-route-") as home:
        old = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = home
        try:
            path = account_routes.registry_path()
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"schema_version": 1, "routes": [route(health)]}),
                            encoding="utf-8")
            registry_present, aliases, reply_ok = community_loop._route_aliases(BOT, PERSONA)
            decision_availability = account_routes.availability_for(BOT, PERSONA, ["x"])
            print(json.dumps({
                "health": health,
                "registry_present": registry_present,
                "aliases": sorted(aliases),
                "reply_ok_aliases": sorted(reply_ok),
                "reply_route_id": reply_ok.get(ALIAS, {}).get("route_id"),
                "decision_availability": decision_availability["availability"]["x"],
            }, sort_keys=True))
        finally:
            if old is None:
                os.environ.pop("SBOTS_HOME", None)
            else:
                os.environ["SBOTS_HOME"] = old
