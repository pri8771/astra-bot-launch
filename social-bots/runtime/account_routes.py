"""Credential-free account route registry reader (ACCOUNT_REGISTRY_SCHEMA.md; V1.7 D2).

The registry is the ONLY thing that can make a platform "available" to the
decision loop. It lives at ``<runtime home>/accounts/registry.json`` as a list of
AccountRoute records that carry aliases and capability flags — never a password,
token, cookie, TOTP seed, recovery code or session (a record containing such a
key poisons the whole registry: it is rejected, not partially trusted).

Truth table for platform selection (``availability_for``):

- registry file ABSENT  → ``registry_present`` False; every platform is
  ``account_available`` False / ``authorized`` False with reason "unverified".
  The loop may still DRAFT for the persona's primary platform in an explicitly
  exploratory mode, but nothing is publishable.
- registry PRESENT     → a platform is available only through a healthy route
  for exactly this bot+persona+platform; ``authorized`` (for drafting) needs
  the route's ``capabilities.draft``; ``publishable`` needs an explicit
  ``publish_authorized: true`` (an owner grant recorded by the lead).
- registry REJECTED    → treated as present with every platform blocked and the
  rejection reason attached (fail closed, loudly).
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import paths

REGISTRY_FILE = "registry.json"
SCHEMA_VERSION = 1

_REQUIRED = ("route_id", "platform", "bot", "persona", "route_type", "capabilities")
_SECRET_MARKERS = ("password", "passwd", "token", "cookie", "secret", "totp",
                   "recovery", "session", "private_key", "apikey", "api_key")
_UNHEALTHY = {"unhealthy", "revoked", "suspended", "locked", "expired"}
VERIFICATION_MAX_AGE = timedelta(hours=24)
VERIFICATION_FUTURE_ALLOWANCE = timedelta(minutes=5)


class RouteRegistryError(ValueError):
    """The registry is malformed or carries something that must never be in it."""


def registry_path(home: str | Path | None = None) -> Path:
    base = Path(home) if home is not None else paths.base()
    return base / "accounts" / REGISTRY_FILE


def _scan_for_secrets(obj, trail: str = "") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k).lower()
            if any(m in key for m in _SECRET_MARKERS) and key != "credential_reference_alias":
                raise RouteRegistryError(
                    f"registry entry carries a secret-like key {trail + str(k)!r}; the "
                    f"registry is credential-free by contract (use credential_reference_alias)")
            _scan_for_secrets(v, trail + str(k) + ".")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _scan_for_secrets(v, f"{trail}[{i}].")


def load_routes(home: str | Path | None = None) -> list[dict] | None:
    """Return the validated route list, or None when no registry exists."""
    path = registry_path(home)
    if path.is_symlink():
        raise RouteRegistryError("account registry is a symlink; refusing to read through a link")
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RouteRegistryError(f"account registry unreadable: {type(exc).__name__}") from exc
    if isinstance(data, dict):
        if data.get("schema_version") != SCHEMA_VERSION:
            raise RouteRegistryError(f"account registry schema_version "
                                     f"{data.get('schema_version')!r} != {SCHEMA_VERSION}")
        routes = data.get("routes")
    else:
        routes = data
    if not isinstance(routes, list):
        raise RouteRegistryError("account registry must be a list of routes")
    _scan_for_secrets(routes)
    for i, r in enumerate(routes):
        if not isinstance(r, dict):
            raise RouteRegistryError(f"route[{i}] is not an object")
        missing = [k for k in _REQUIRED if k not in r]
        if missing:
            raise RouteRegistryError(f"route[{i}] missing {missing}")
        if not isinstance(r["capabilities"], dict):
            raise RouteRegistryError(f"route[{i}] capabilities must be an object")
    return routes


def verification_freshness(value: object, *, now: datetime | None = None) -> tuple[bool, str]:
    """LEAD-056: require aware verification within 24 hours / +5 minutes."""
    if not isinstance(value, str) or not value.strip():
        return False, "route verification timestamp missing"
    try:
        verified = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False, "route verification timestamp malformed"
    if verified.tzinfo is None or verified.utcoffset() is None:
        return False, "route verification timestamp must be timezone-aware"
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        return False, "route verification evaluation time must be timezone-aware"
    age = now - verified
    if age < -VERIFICATION_FUTURE_ALLOWANCE:
        return False, "route verification timestamp exceeds 5-minute future allowance"
    if age > VERIFICATION_MAX_AGE:
        return False, "route verification stale (older than 24 hours)"
    return True, "route verification current"


def _route_ok(route: dict, *, now: datetime | None = None) -> tuple[bool, str]:
    if route.get("route_type") == "unsupported":
        return False, "route_type unsupported"
    health = str(route.get("health_status") or "unverified").lower()
    if health in _UNHEALTHY:
        return False, f"route health {health}"
    if health in ("unverified", "unknown", ""):
        return False, "route never verified (last_verified_at absent or stale)"
    fresh, why = verification_freshness(route.get("last_verified_at"), now=now)
    if not fresh:
        return False, why
    return True, f"route {route.get('route_id')} {health}"


def availability_for(bot: str, persona: str, platforms, home: str | Path | None = None,
                     *, now: datetime | None = None) -> dict:
    """Per-platform availability for ``select_platforms`` plus the registry state."""
    platforms = list(platforms)
    out = {"registry_present": False, "registry_error": None, "availability": {}}
    try:
        routes = load_routes(home)
    except RouteRegistryError as exc:
        out["registry_present"] = True
        out["registry_error"] = str(exc)
        for p in platforms:
            out["availability"][p] = {"account_available": False, "authorized": False,
                                      "publishable": False, "route_id": None,
                                      "reason": f"registry rejected: {exc}"}
        return out
    if routes is None:
        for p in platforms:
            out["availability"][p] = {"account_available": False, "authorized": False,
                                      "publishable": False, "route_id": None,
                                      "reason": "no account route registry (unverified)"}
        return out
    out["registry_present"] = True
    for p in platforms:
        matches = [r for r in routes if r.get("platform") == p and r.get("bot") == bot
                   and r.get("persona") == persona]
        if not matches:
            out["availability"][p] = {"account_available": False, "authorized": False,
                                      "publishable": False, "route_id": None,
                                      "reason": f"no route for {bot}/{persona} on {p}"}
            continue
        route = matches[0]
        ok, why = _route_ok(route, now=now)
        caps = route.get("capabilities") or {}
        out["availability"][p] = {
            "account_available": ok,
            "authorized": ok and bool(caps.get("draft")),
            "publishable": ok and bool(caps.get("publish")) and route.get("publish_authorized") is True,
            "route_id": route.get("route_id"),
            "route_type": route.get("route_type"),
            "analytics_route": route.get("analytics_route"),
            "reason": why if ok else why,
        }
    return out
