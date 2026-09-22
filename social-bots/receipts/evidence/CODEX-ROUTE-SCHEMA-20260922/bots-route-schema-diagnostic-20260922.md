# Account route schema diagnostic

Source: `3f10d0f6eb031c00fff679aae18aa8045d8bd025`.

Contract: `social-bots/ACCOUNT_REGISTRY_SCHEMA.md:17` restricts `route_type` to `API | browser | Buffer | manual | unsupported`.

Observed: a synthetic credential-free registry route with `route_type: "telepathy"`, otherwise current verified health and a valid boolean draft capability, is accepted by `load_routes`; `_route_ok` rejects only the literal `unsupported`; `availability_for` reports `account_available: true` and `authorized: true`. No external action occurred.

Root cause: `load_routes` validates presence of `route_type` but not membership in the documented enum, while `_route_ok` implements a denylist of one enum member rather than an allowlist of supported route types.

Smallest repair: reject any `route_type` outside the documented enum while loading the registry (poison the malformed registry consistently with other schema errors), and retain `_route_ok`'s `unsupported` ineligibility for a valid-but-deliberately-unavailable route. Add one malformed-enum regression proving all requested platforms fail closed with `registry_error`, plus a valid-enum compatibility case. Boolean capability typing should be handled only if the native contract is made explicit; this reproducer does not depend on that ambiguity.
