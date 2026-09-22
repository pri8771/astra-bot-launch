"""Documented route types must be enforced at whole-registry ingest."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from runtime import account_routes


NOW = datetime(2026, 9, 22, 12, tzinfo=timezone.utc)


class RouteSchemaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bots-route-schema-")
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "accounts" / "registry.json"
        self.path.parent.mkdir()

    def route(self, kind="API", route_id="route-a"):
        return {"route_id": route_id, "platform": "x", "bot": "social-a",
                "persona": "social-a", "route_type": kind,
                "capabilities": {"draft": True, "publish": True},
                "publish_authorized": True, "health_status": "verified",
                "last_verified_at": NOW.isoformat()}

    def write(self, routes):
        self.path.write_text(json.dumps({"schema_version": 1, "routes": routes}))

    def availability(self):
        return account_routes.availability_for("social-a", "social-a", ["x"],
                                               home=self.tmp.name, now=NOW)

    def test_unknown_or_malformed_type_rejects_whole_registry(self):
        for kind in ("telepathy", "api", "", None, 7, [], {}):
            with self.subTest(kind=kind):
                self.write([self.route(kind)])
                with self.assertRaises(account_routes.RouteRegistryError):
                    account_routes.load_routes(self.tmp.name)
                result = self.availability()
                self.assertIsNotNone(result["registry_error"])
                route = result["availability"]["x"]
                self.assertFalse(route["account_available"])
                self.assertFalse(route["authorized"])
                self.assertFalse(route["publishable"])

    def test_mixed_registry_is_rejected_in_both_orders(self):
        good, bad = self.route(), self.route("telepathy", "route-b")
        bad["bot"] = "another-bot"
        for routes in ([good, bad], [bad, good]):
            with self.subTest(routes=routes):
                self.write(routes)
                with self.assertRaises(account_routes.RouteRegistryError):
                    account_routes.load_routes(self.tmp.name)
                result = self.availability()
                self.assertFalse(result["availability"]["x"]["account_available"])

    def test_documented_supported_types_parse_and_remain_eligible(self):
        for kind in ("API", "browser", "Buffer", "manual"):
            with self.subTest(kind=kind):
                route = self.route(kind)
                self.write([route])
                self.assertEqual(account_routes.load_routes(self.tmp.name), [route])
                self.assertTrue(self.availability()["availability"]["x"]["authorized"])

    def test_unsupported_parses_but_never_grants_authority(self):
        route = self.route("unsupported")
        self.write([route])
        self.assertEqual(account_routes.load_routes(self.tmp.name), [route])
        result = self.availability()
        self.assertIsNone(result["registry_error"])
        availability = result["availability"]["x"]
        for field in ("account_available", "authorized", "publishable"):
            self.assertFalse(availability[field])

    def test_valid_type_does_not_bypass_secret_rejection(self):
        route = self.route()
        route["password"] = "synthetic-forbidden-value"
        self.write([route])
        with self.assertRaises(account_routes.RouteRegistryError):
            account_routes.load_routes(self.tmp.name)


if __name__ == "__main__":
    unittest.main()
