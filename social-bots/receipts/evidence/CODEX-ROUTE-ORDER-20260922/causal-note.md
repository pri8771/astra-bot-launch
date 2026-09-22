# Bots next diagnostic — route registry order dependence

Source: `ccfbaf7865557ba30d9148bcce6839b71e9159f1`
Canonical: `647c41ada56ec1addc7fa71482ed4f184bf809e7`

Command (cwd `/Users/pchordia/Downloads/swarm_codex/review/bots-routes-source`):

    python3 /tmp/bots-next-diagnostic-route-order-20260922.py

Result: exit 0. With two matching bot/persona/platform routes, availability is blocked when a revoked route precedes a fresh verified route, but allowed when the same records are reversed. `availability_for` filters all matches then unconditionally evaluates `matches[0]` (`social-bots/runtime/account_routes.py:153-162`). The registry schema does not require uniqueness for bot/persona/platform and only says persona/destination mismatch is a hard stop and stale verification cannot be presented as current connectivity (`social-bots/ACCOUNT_REGISTRY_SCHEMA.md`).

Runtime consequence: `decision.select_delivery` consumes this availability at `social-bots/runtime/decision.py:370`; a healthy configured route can therefore be hidden solely by JSON ordering. No external effect was attempted.

Smallest compatibility direction (not implemented): evaluate matching routes deterministically, prefer an eligible healthy/fresh route, and fail closed on ambiguity only if native policy requires unique routing. Add an order-reversal regression. Lead/native policy should decide tie-breaking when multiple eligible routes exist.
