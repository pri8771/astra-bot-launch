# Account route type validation diagnostic

**REWORK_FOUND**, diagnostic only at accepted source **3f10d0f6eb031c00fff679aae18aa8045d8bd025**, tree **9efb375fe672df97526b6edf86d629c421d8a5b3**. Root independently repeated the bounded agent reproduction. No source change or external effect.

ACCOUNT_REGISTRY_SCHEMA.md:17 restricts route_type to API, browser, Buffer, manual or unsupported. load_routes validates presence but not membership; _route_ok rejects only literal unsupported. A synthetic exact-scope route with route_type=telepathy, current verification, healthy status and draft=true returns registry_error=null, account_available=true and authorized=true. This is a documented schema boundary failure, not a new route-priority policy. [Reproducer](../receipts/evidence/CODEX-ROUTE-SCHEMA-20260922/bots-route-schema-repro-20260922.py), [raw result](../receipts/evidence/CODEX-ROUTE-SCHEMA-20260922/bots-route-schema-repro-20260922.txt), [causal note](../receipts/evidence/CODEX-ROUTE-SCHEMA-20260922/bots-route-schema-diagnostic-20260922.md).

Smallest proposed repair: reject the whole malformed registry when route_type is outside the documented enum; valid unsupported remains parsed but unavailable. Preserve other accepted selection/freshness/capability gates. Request the bounded lead disposition/release. No boolean-schema requirement is invented where the document does not state one.

LEAD058 at f822070 separately accepts PR11 and releases the SB-V13-002 offline metrics audit, which proceeds independently. All live/account/provider/model/public/scheduler gates remain unchanged; no Fable dispatch or new SESSION_ONCE.
