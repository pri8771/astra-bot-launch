"""LEAD-056 freshness boundaries and community route clearance."""
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from runtime import account_routes, community, community_loop

NOW = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
BOT = PERSONA = "social-a"


def route(route_id, *, verified="2026-09-22T11:00:00+00:00", health="verified",
          draft=True, publish=True, publish_authorized=True,
          reply=True, reply_authorized=True, alias=None):
    r = {
        "route_id": route_id, "platform": "x", "bot": BOT, "persona": PERSONA,
        "route_type": "API", "account_alias": alias or f"alias-{route_id}",
        "capabilities": {"read": True, "draft": draft, "publish": publish,
                         "reply": reply, "analytics": True},
        "publish_authorized": publish_authorized,
        "reply_authorized": reply_authorized,
        "health_status": health,
    }
    if verified is not None:
        r["last_verified_at"] = verified
    return r


class RouteFreshnessTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bots-route-freshness-")
        self.old_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp.name

    def tearDown(self):
        if self.old_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.old_home
        self.tmp.cleanup()

    def write(self, routes):
        path = account_routes.registry_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"schema_version": 1, "routes": routes}), encoding="utf-8")

    def test_helper_boundaries_and_aware_offset(self):
        failures = {
            "missing": None,
            "malformed": "not-a-time",
            "naive": "2026-09-22T11:00:00",
            "over_24h": (NOW - timedelta(hours=24, microseconds=1)).isoformat(),
            "over_future_5m": (NOW + timedelta(minutes=5, microseconds=1)).isoformat(),
        }
        for label, value in failures.items():
            with self.subTest(label=label):
                self.assertFalse(account_routes.verification_freshness(value, now=NOW)[0])

        successes = {
            "exact_24h": (NOW - timedelta(hours=24)).isoformat(),
            "exact_future_5m": (NOW + timedelta(minutes=5)).isoformat(),
            "aware_offset_same_instant": "2026-09-22T08:00:00-04:00",
        }
        for label, value in successes.items():
            with self.subTest(label=label):
                self.assertTrue(account_routes.verification_freshness(value, now=NOW)[0])

    def test_every_freshness_failure_blocks_all_availability_flags(self):
        failures = (None, "not-a-time", "2026-09-22T11:00:00",
                    (NOW - timedelta(days=100)).isoformat(),
                    (NOW - timedelta(hours=24, microseconds=1)).isoformat(),
                    (NOW + timedelta(minutes=5, microseconds=1)).isoformat())
        for index, verified in enumerate(failures):
            with self.subTest(verified=verified):
                self.write([route(f"bad-{index}", verified=verified)])
                item = account_routes.availability_for(
                    BOT, PERSONA, ["x"], now=NOW)["availability"]["x"]
                self.assertFalse(item["account_available"])
                self.assertFalse(item["authorized"])
                self.assertFalse(item["publishable"])

    def test_fresh_route_remains_conditional_on_health_and_capabilities(self):
        self.write([route("no-draft", draft=False)])
        item = account_routes.availability_for(BOT, PERSONA, ["x"], now=NOW)["availability"]["x"]
        self.assertTrue(item["account_available"])
        self.assertFalse(item["authorized"])
        self.assertTrue(item["publishable"])

        self.write([route("no-publish-cap", publish=False)])
        item = account_routes.availability_for(BOT, PERSONA, ["x"], now=NOW)["availability"]["x"]
        self.assertTrue(item["account_available"])
        self.assertTrue(item["authorized"])
        self.assertFalse(item["publishable"])

        self.write([route("revoked", health="revoked")])
        item = account_routes.availability_for(BOT, PERSONA, ["x"], now=NOW)["availability"]["x"]
        self.assertFalse(item["account_available"])
        self.assertFalse(item["authorized"])
        self.assertFalse(item["publishable"])

    def test_community_reply_routes_reject_bad_and_admit_fresh_without_effect(self):
        routes = [
            route("revoked", health="revoked", alias="alias-revoked"),
            route("stale", verified=(NOW - timedelta(hours=24, microseconds=1)).isoformat(),
                  alias="alias-stale"),
            route("missing", verified=None, alias="alias-missing"),
            route("fresh", verified=(NOW - timedelta(hours=1)).isoformat(), alias="alias-fresh"),
        ]
        self.write(routes)
        present, aliases, reply_ok = community_loop._route_aliases(BOT, PERSONA, now=NOW)
        self.assertTrue(present)
        self.assertEqual(aliases, {"alias-revoked", "alias-stale", "alias-missing", "alias-fresh"})
        self.assertEqual(set(reply_ok), {"alias-fresh"})

        signals = [community.CommunitySignal.ingest(
            thread_id=f"thread-{alias}",
            text="How does surface tension actually keep the leaf up? Is it the same for oil?",
            source="fixture", persona=PERSONA, account_alias=alias,
            observed_at=NOW.isoformat()) for alias in sorted(aliases)]
        result = community_loop.run_community_cycle(BOT, PERSONA, signals=signals, now=NOW)
        self.assertEqual(result["effects_performed"], 0)
        replies = {item["thread_id"]: item for item in community_loop.reply_candidates(BOT, PERSONA)}
        self.assertEqual(len(replies), 4)
        for alias in aliases:
            reply = replies[f"thread-{alias}"]
            self.assertEqual(reply["cleared_for_effect"], alias == "alias-fresh")
            self.assertEqual(reply["effect_status"], "CLEARED_NO_EFFECT_PERFORMED"
                             if alias == "alias-fresh" else "BLOCKED_NO_AUTHORITY")
            self.assertFalse(reply["published"])



if __name__ == "__main__":
    unittest.main()
