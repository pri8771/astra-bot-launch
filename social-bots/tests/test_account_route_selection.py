"""LEAD-057 deterministic account-route selection regressions."""
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

from runtime import account_routes, community, community_loop


NOW = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)
BOT = PERSONA = "social-a"


def route(route_id, *, platform="x", bot=BOT, persona=PERSONA, alias=None,
          health="verified", verified="2026-09-22T11:00:00+00:00",
          draft=True, publish=False, publish_authorized=False,
          reply=True, reply_authorized=True, analytics="analytics-default"):
    return {
        "route_id": route_id, "platform": platform, "bot": bot, "persona": persona,
        "route_type": "API", "account_alias": alias or f"alias-{route_id}",
        "capabilities": {"draft": draft, "publish": publish, "reply": reply},
        "publish_authorized": publish_authorized, "reply_authorized": reply_authorized,
        "analytics_route": analytics, "health_status": health,
        "last_verified_at": verified,
    }


class AccountRouteSelectionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bots-route-selection-")
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

    def availability(self, routes):
        self.write(routes)
        return account_routes.availability_for(BOT, PERSONA, ["x"], now=NOW)["availability"]["x"]

    def test_unique_eligible_is_order_invariant_among_revoked_and_stale(self):
        fresh = route("fresh")
        revoked = route("revoked", health="revoked")
        stale = route("stale", verified="2026-09-21T11:59:59+00:00")
        results = [self.availability(rows) for rows in
                   ([revoked, fresh, stale], [stale, fresh, revoked])]
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0]["route_id"], "fresh")
        self.assertTrue(results[0]["account_available"])

    def test_zero_eligible_has_same_factual_diagnostic_across_orders(self):
        revoked = route("revoked", health="revoked")
        stale = route("stale", verified="2026-09-21T11:59:59+00:00")
        results = [self.availability(rows) for rows in ([revoked, stale], [stale, revoked])]
        self.assertEqual(results[0], results[1])
        self.assertIsNone(results[0]["route_id"])
        self.assertFalse(results[0]["account_available"])
        self.assertFalse(results[0]["authorized"])
        self.assertFalse(results[0]["publishable"])
        self.assertIn("no eligible route", results[0]["reason"].lower())
        self.assertIn("revoked", results[0]["reason"])
        self.assertIn("stale", results[0]["reason"])

    def test_multiple_eligible_is_explicit_ambiguity_and_order_invariant(self):
        first, second = route("eligible-a"), route("eligible-b")
        results = [self.availability(rows) for rows in ([first, second], [second, first])]
        self.assertEqual(results[0], results[1])
        self.assertIsNone(results[0]["route_id"])
        self.assertFalse(results[0]["account_available"])
        self.assertFalse(results[0]["authorized"])
        self.assertFalse(results[0]["publishable"])
        self.assertIn("ambiguous", results[0]["reason"].lower())
        self.assertIn("multiple eligible", results[0]["reason"].lower())

    def test_only_exact_scope_matches_participate(self):
        result = self.availability([
            route("wrong-bot", bot="other"), route("wrong-persona", persona="other"),
            route("wrong-platform", platform="other"), route("exact"),
        ])
        self.assertEqual(result["route_id"], "exact")
        self.assertTrue(result["account_available"])

    def test_downstream_flags_come_only_from_unique_selected_route(self):
        selected = route("selected", draft=False, publish=True, publish_authorized=True,
                         analytics="selected-analytics")
        revoked = route("revoked", health="revoked", draft=True, analytics="wrong")
        results = [self.availability(rows) for rows in ([revoked, selected], [selected, revoked])]
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0]["route_id"], "selected")
        self.assertTrue(results[0]["account_available"])
        self.assertFalse(results[0]["authorized"])
        self.assertTrue(results[0]["publishable"])
        self.assertEqual(results[0]["analytics_route"], "selected-analytics")

    def _reply_clearance(self, routes, *, alias, platform="x"):
        self.write(routes)
        signal = community.CommunitySignal.ingest(
            thread_id=f"thread-{alias}-{platform}",
            text="How does surface tension actually keep the leaf up? Is it the same for oil?",
            source="fixture", persona=PERSONA, account_alias=alias, observed_at=NOW.isoformat())
        with mock.patch.object(community_loop, "_thread_platform", return_value=platform):
            community_loop.run_community_cycle(BOT, PERSONA, signals=[signal], now=NOW)
        return community_loop.reply_candidates(BOT, PERSONA)[-1]

    def test_community_blocks_alias_when_two_routes_are_eligible_for_platform(self):
        routes = [route("one", alias="shared"), route("two", alias="shared")]
        reply = self._reply_clearance(routes, alias="shared")
        self.assertFalse(reply["cleared_for_effect"])
        self.assertEqual(reply["effect_status"], "BLOCKED_NO_AUTHORITY")

    def test_community_does_not_use_eligible_alias_from_different_platform(self):
        routes = [route("other-platform", platform="linkedin", alias="shared")]
        reply = self._reply_clearance(routes, alias="shared", platform="x")
        self.assertFalse(reply["cleared_for_effect"])
        self.assertEqual(reply["effect_status"], "BLOCKED_NO_AUTHORITY")


if __name__ == "__main__":
    unittest.main()
