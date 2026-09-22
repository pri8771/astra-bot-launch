# Community reply-route health reproduction

Exact source HEAD: `30a2ebdfb45110b2bc6fea0f3d50876583487f9c`.

Modules actually imported:

- `/Users/pchordia/Downloads/swarm_codex/review/bots-metrics-source/social-bots/runtime/community_loop.py`
- `/Users/pchordia/Downloads/swarm_codex/review/bots-metrics-source/social-bots/runtime/account_routes.py`

Synthetic input is retained verbatim in `/tmp/bots-community-route-health-repro-20260922.py`: one matching bot/persona X route per case, with `capabilities.reply=true`, `reply_authorized=true`, and health `expired`, `revoked`, or `unverified`.

Result: `_route_aliases` grants all three routes into `reply_ok` under alias `alias-x`. In the same run, `account_routes.availability_for` correctly marks each route unavailable and unauthorized. Output is `/tmp/bots-community-route-health-repro-20260922.out` (exit 0).

Root cause: `community_loop._route_aliases` lines 127-139 calls `load_routes`, filters only matching bot/persona, reply capability, and the reply-authorized flag. It does not apply `_route_ok` or any equivalent health check.

Downstream boundary: at `community_loop.py:271-277`, membership in `reply_routes` creates `community.AuthorizedRoute(... authorized=True ...)` and feeds it to `community.clear_for_effect`. With a passing final review, `community.py:198-216` sets `cleared_for_effect=True` and `effect_status=CLEARED_NO_EFFECT_PERFORMED`. The loop persists a reply candidate with `publish_authorized=False`, `published=False` (`community_loop.py:278-293`) and records `effects_performed=0` (`community_loop.py:296-303`). This is an incorrect local clearance/authority claim; it is not evidence of a public reply or send, and these modules perform no external effect.

No source files, accounts, providers, network routes, models, schedulers, or public destinations were touched.
