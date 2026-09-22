# Route-selection causal note

Accepted parent `ccfbaf7865557ba30d9148bcce6839b71e9159f1` filtered exact bot/persona/platform matches but evaluated only `matches[0]`. Registry order therefore controlled availability: an ineligible first route hid a unique eligible route, two eligible routes silently selected the first, and unavailable diagnostics exposed whichever route happened to be first. Capabilities were read from that same premature choice.

The community consumer independently built reply authority per route and keyed it only by alias. It could clear both an ambiguous same-platform alias and an alias whose eligible route belonged to a different platform.

Candidate `3f10d0f6eb031c00fff679aae18aa8045d8bd025` evaluates all exact-scope matches through the existing route-type, health, and freshness predicate, selects only a unique eligible route, and otherwise fails closed with deterministic factual diagnostics. Capabilities are applied after selection. Community authority is keyed by `(platform, alias)` and derives only from the shared unique selector. Persona aliases remain available for input-scope checks.
