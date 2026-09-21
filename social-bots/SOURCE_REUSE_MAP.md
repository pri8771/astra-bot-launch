# Source reuse map (SB-001)

**Refreshed:** 2026-09-20T20:26Z by Claude Code (implementation worker).
**Method:** direct inspection of current refs, not September status text. Historical
claims are labeled as such and are **not** treated as current runtime/account state.

## Evidence refs pinned at reconciliation time

| Repo / path | Ref inspected | Access from this session |
|---|---|---|
| `pri8771/astra-bot-launch` (coordination + `reference/`) | commit `9f2f4d2` (branch `chatgpt/social-bots-plan-20260920`, == origin/main + `social-bots/`) | Direct (working tree) |
| `pri8771/bots` (shared conventions / memory) | commit `7f2ec1a` (shallow clone) | Attached via `add_repo`, cloned to `/home/user/bots` |
| `pri8771/one-person-ops` | not inspected | **Blocked** — not attached to this session (see blockers) |
| `pri8771/autonomous_apps` | not inspected | **Blocked** — not attached to this session |
| `pri8771/orchestrator/wait-how-big-social/` | not inspected | **Blocked** — not attached to this session |
| `pri8771/priyanshchordia.com/ventures/bidetfit/` | not inspected | **Blocked** — not attached to this session |

> Note: `pri8771/bots` **contains** subtrees named `onepersonops/`, `waithowbig/`,
> and `commercelint/`. These are *coordination/evidence mirrors inside the bots repo*,
> not the standalone product repos of the same names. They were inspected at `7f2ec1a`
> and are recorded below; the standalone product repos remain un-inspected (blocked).

## Classification key

- **REUSE-CONVENTION** — reuse the pattern/rule/format, not code.
- **REUSE-CONTENT** — concrete content/reference assets usable as research seeds.
- **REUSE-PATTERN** — an implementation shape worth mirroring (receipts, acceptance tests).
- **HISTORICAL** — dated planning/state; evidence only, never current truth.
- **NONE-RUNTIME** — no importable autonomous-bot runtime code found here.
- **BLOCKED** — could not be verified from this session.

## Inventory

### `pri8771/bots` @ `7f2ec1a`

| Asset | Path | Class | Notes |
|---|---|---|---|
| Portable memory format | `memory/MEMORY_SPEC.md` | REUSE-CONVENTION | Plain-Markdown, append-only, dated notes, **never store secrets** (private ≠ security). Adopted for `state/` + `memory/` layout below. |
| "Current state, no history" file | `memory/shared/STATE.md` | REUSE-CONVENTION + HISTORICAL | Pattern adopted. Content dated **2026-09-01** → historical: says Shopify write path absent, `memory_search` index empty, Gemini/LM Studio lanes down, Ollama `dolphin3` only. Not current evidence. |
| Lease/heartbeat/failover lessons | `reference/ACCOUNTS_CHANNELS_AND_HOSTS.md` (mirror) & STATE | REUSE-CONVENTION | "One active operator per mission owns external writes; host leases/heartbeats + action IDs + destination readback prevent duplicate publication; a timed-out heartbeat alone does not prove the primary stopped; reconcile uncertain actions before failover." Directly drives our lease + reconciliation design. |
| OPO Contract Check | `onepersonops/contract-check/` (Node ESM) | REUSE-PATTERN | Bounded validator with **evidence receipts**, `hash-artifacts`, `browser-smoke`, and a `node --test` acceptance suite. We mirror the *evidence-receipt + acceptance-test* shape (not the code; it validates JSON contracts, unrelated to autonomy). |
| waithowbig / commercelint subtrees | `waithowbig/README.md`, `commercelint/` | HISTORICAL | README-only stubs at this ref; no publishing/research code present to import. |
| Runtime code for autonomous bots | — | NONE-RUNTIME | **No Python/JS autonomous-bot runtime exists in this repo** (`find *.py` → 0; only OPO Node validator). Runtime is therefore built fresh under `social-bots/runtime/`. |

### `pri8771/astra-bot-launch` `reference/` @ `9f2f4d2`

| Asset | Path | Class | Notes |
|---|---|---|---|
| Corrected mission register | `reference/MISSION_GOALS.md` | HISTORICAL (owner intent, 12 Sep) | Confirms old ventures are **missions/experiments, not persona identities**. Explicitly warns against conflating mission ↔ product ↔ first experiment. Backs the rule: OPO/WHB/CommerceLint/BidetFit/Guru ≠ the five new personas. |
| Accounts/channels/hosts policy | `reference/ACCOUNTS_CHANNELS_AND_HOSTS.md` | REUSE-CONVENTION (12 Sep, plan not evidence) | Account registry fields (resource ID, purpose, capabilities, **credential reference not value**, verified-access date, lifecycle). LinkedIn prohibits site automation; GitHub disallows machine-user registration; Substack multi-publication allowed. Hosts: R730 central hub, Windows fallback, i9 Mac staging. Adopted for SB-005. |
| Audience experiment scorecard | same file | REUSE-CONVENTION | Freeze window/baseline/collection route/metric defs before a test; don't blend followers/impressions/subs. Adopted into analytics + experiment schema. |
| Autonomous experiment loop | `reference/AUTONOMOUS_EXPERIMENTS.md` | REUSE-CONVENTION | Dedup contract + experiment discipline (referenced by accounts doc). Feeds SB-006 dedup + experiment registry. |
| Guru "Sadhana Notes" candidate | `reference/guru-sadhana-candidate/` | REUSE-CONTENT | Frozen persona contract, moderation runbook, 3 four-slide carousels (`content/*.md`), alt-text, `source-ledger.json` (**empty entries, cultural review WITHHELD, no handle, publication blocked BOTS-130/132**). Strong **seed** for a cultural persona; identity must stay "independent editorial project, never a real guru / fictitious human". Paraphrase-by-default, bind public-domain source + named reviewer before any textual claim. |

## Mapping decisions (evidence-based, per owner rule "do not force OPO=A…")

- The **five old ventures are reuse pools, not the five personas.** `MISSION_GOALS.md`
  itself makes this correction, so no forced 1:1 mapping is applied.
- **Guru → cultural persona seed only.** The guru candidate seeds cultural persona
  research/voice/moderation posture; it does **not** dictate a runtime identity, and its
  publication remains blocked (no handle, no cultural reviewer, no grant).
- **WHB / OPO / CommerceLint / BidetFit → convention & pattern pools** (metric
  discipline, account-registry fields, evidence-receipt shape). No runtime code to lift.
- **`pri8771/bots` → conventions + lessons**, not a code dependency. Runtime built fresh.

## Blockers (exact)

1. **Reuse-pool repos not attached.** `one-person-ops`, `autonomous_apps`,
   `orchestrator` (wait-how-big-social), `priyanshchordia.com` are not in this session's
   GitHub scope and were not attached. Exact next step: attach each via `add_repo`
   (or owner confirms they are the intended standalone homes) before their emails/
   accounts/analytics/publishing adapters can be verified for reuse. Until then they are
   **BLOCKED**, not "no reuse".
2. **No account/credential evidence** exists in any inspected repo (correctly — secrets
   are never committed). Account reuse is deferred to SB-005 and stays at the
   "reference-only" level with exact human steps.

## What was NOT reused and why

- No September STATE/plan text is treated as current runtime or account state.
- No autonomous-bot runtime code was copied (none exists); building fresh avoids a
  phantom dependency and keeps Social Bots independent of SwarmAI and of `bots`.
- No secrets, handles, or private identity mappings were copied.


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
