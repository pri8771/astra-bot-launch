# Source reuse map

Initial lead map. Claude must refresh with current refs and actual account evidence in SB-001.

| Source | Intended reuse | Current lead classification |
|---|---|---|
| pri8771/bots | agent utilities, memory conventions, scheduling/lease lessons | Reuse candidate; current state file is dated |
| pri8771/astra-bot-launch | coordination, historical launch receipts, Guru references | Canonical coordination; historical launch claims need refresh |
| pri8771/orchestrator/wait-how-big-social/ | social research/editorial/publishing patterns | Strong reuse candidate |
| reference/guru-sadhana-candidate/ | cultural/religious research and editorial references | Reference reuse candidate; not a runtime |
| pri8771/one-person-ops | account/email/analytics/automation assets where relevant | Reuse pool, not a social-bot identity |
| pri8771/autonomous_apps | account/email/analytics/automation assets where relevant | Reuse pool, not a social-bot identity |
| pri8771/priyanshchordia.com/ventures/bidetfit/ | account/email/analytics/publishing assets where relevant | Reuse pool, not a social-bot identity |

Claude must add exact refs/paths, last verification, limits and account aliases without secrets.


## Lead-side current evidence supplied to Claude — 2026-09-20

This section is lead research supplied to unblock SB-001. Claude should consume it rather than repeat the same discovery, and should still inspect exact source paths when implementation reuse is proposed.

| Source | Current ref/evidence | Lead finding | Reuse guidance |
|---|---|---|---|
| `pri8771/one-person-ops` | latest main commit observed `ea532b3037c08cbeca83c562592a106b4fce7a8c`; current README fetched | Repository has newer agent-exchange commits, while the README still describes the storefront as private/no analytics. | Inspect the exchange implementation/provenance before borrowing anything. Do not assume the README alone describes all current source. Reuse patterns/components only if they fit Social Bots; OPO is not a persona identity. |
| `pri8771/autonomous_apps` / CommerceLint | latest observed main `3611767f662c781ea2946c98a9cead17827f6f31`; watchdog commit at 2026-09-20T21:48:58Z; README current | This is a genuinely active zero-budget autonomous operator with hourly operator, independent watchdog, six-hour growth planner, durable state/audit diary, fail-closed spend behavior and verified deployment receipts. | Strong reuse-pattern source for wake/load/observe/rank/act/verify/record/sleep, watchdog separation, evidence receipts, state/audit contracts and fail-closed spending. Do not couple Social Bots runtime to CommerceLint. |
| `pri8771/orchestrator/wait-how-big-social/` | latest repo main observed `bffc2030059d56dab7c26f31089017decb2f8b24`; WHB README last updated 2026-08-31 | Historical handoff records a free Buffer workspace and public X/Instagram/TikTok brand profiles, plus an email alias and a prepared publishing operator. The handoff explicitly says these facts need fresh live verification before current claims; the operator had a known module-name failure and no verified post receipts at that time. | Strong account/profile/media/publishing reuse candidate. Reverify current account connections and operator state before using them. Do not copy private login mappings or credential details into Social Bots Git. |
| `pri8771/priyanshchordia.com/ventures/bidetfit/` | BidetFit autonomous run commit `f3554580081d3461c177f353223ea9f794f64ad5` at 2026-09-20T20:47:34Z | The historical `ventures/bidetfit/README.md` path is absent, but the venture itself is active: `ventures/bidetfit/STATE.json`, `RUNS.csv`, logs and workflow evidence show a successful six-hour operator health run and live GitHub Pages status. Metrics remain explicitly unmeasured. | Reuse health/run-receipt/operator-governance patterns. Do not infer business performance from health. BidetFit is not a social persona identity. |

### Lead boundary

The lead may provide:
- verified repository/source facts;
- acceptance criteria;
- product/version contracts;
- account-safe metadata already evidenced in source;
- PR review and failure analysis.

Claude remains responsible for implementation, tests, host-side execution and attributable worker receipts.
