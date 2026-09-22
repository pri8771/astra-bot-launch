# V1.7 gate dossier — one record per owner gate (LEAD-048/050, C09)

Machine-readable twin: `V17_PREFLIGHT.json`. Raw capture: `receipts/evidence/SB-V17-PREFLIGHT/run-20260922T013826Z/` (read-only commands only; no login, post, spend or mutation; `claude auth status` is a local credential check, not a model call).

## Where things actually run (verified, not assumed)

| Fact | Observed |
|---|---|
| Execution host | ephemeral Claude Code Remote Linux VM `vm`, kernel 6.18.44-fc-v37, root, Python 3.11.15, PID 1 `process_api`, uptime minutes, session-scoped disk. **Not a Mac, not persistent.** |
| Native scheduler | none: no cron daemon, no systemd init, no launchd, no `at` |
| Tools | `claude` 2.1.278 on PATH; `git`; `gh` absent (GitHub via MCP); docker binary present (daemon unverified) |
| Provider | `claude` CLI logged in via subscription OAuth (firstParty) on this VM; API-key route absent and refused by posture; **0 model calls made** |
| Authorization | `social-bots/authorizations/` exists on **no** branch (HEAD `b5fd038`, canonical `550f2b1`) → every LIVE_MODEL route fails closed |
| Network | outbound only through the agent proxy; CONNECT to x.com, api.x.com, reddit.com, oauth.reddit.com, instagram.com, graph.facebook.com, tiktok.com, youtube.com → **403**; api.github.com → 200 |
| Accounts | 0 AccountRoute registry entries in Git (schema only); `ACCOUNT_BROWSER_MAP.md` records every route as not verified; no platform reachable from here to verify one |
| Cultural review | both cultural personas require a named reviewer; none is configured |

Consequence by evidence class: OFFLINE_FIXTURE and REAL_PROCESS can be produced here; NATIVE_SCHEDULER, LIVE_SOURCE, LIVE_MODEL, LIVE_ACCOUNT, LIVE_PUBLIC_EFFECT and LIVE_ANALYTICS cannot.

## Gate records

Each block is the OWNER_GATES.md request template filled with what is known. None of these is an approval; until the owner explicitly approves and the lead manifest exists, the worker prepares only.

### G-HOST — BLOCKED_HOST
- Requested: owner designates the persistent host by alias and confirms native scheduler (launchd/cron/systemd timer), install permission, sleep/reboot behaviour, secret-safe git access and the runtime home path.
- Artifacts: SB-V07-001, SB-V07-recurring, C08, C09, C26. Calls 0 · effects 0 · zero spend · no expiry.
- Next action on that host: `python3 bin/prove_cross_process_lock.py`; a `worker_once` dry run with `--skip-fetch --allow-deterministic --home <home>`; install the scheduler entry; capture job history.

### G-LEAD-LOOP — observed, not worker-blocking
- Lead direction arrives as canonical commits (LEAD-050, 2026-09-22T00:51Z) and is consumed via git; Issue #3 used for visibility. Nothing requested from the worker.

### G-MODEL-V04 — BLOCKED_AUTHORIZATION
- Request text: *approve run `v04-divergence-<date>` on verified host `<alias>`, using provider `claude-cli` (subscription OAuth, no API key) for artifacts SB-V04-002, SB-V04-004, frozen inputs `<sha256 of PREPARED_MATRIX.json>`, maximum 5 calls and 0 effects, no automatic retry, zero new spend, expiry `<timestamp>`.*
- Lead manifest: `social-bots/authorizations/<id>.json` (schema v1; artifact_scope [SB-V04-002, SB-V04-004]; run_scope `v04-divergence-<date>`; lane; provider_mode `claude-cli`; max_calls 5; expires_at; all five safety flags false).
- Observed capability: CLI authenticated here (but this is not the persistent host); gate + durable budget enforced (`12c807e`).
- Next action: prepare-only status (`runtime.divergence_prepare.prepare_only_status`); `execute_batch` only after both references exist.

### G-MODEL-RUNS — BLOCKED_AUTHORIZATION
- Requested: owner states the model-call budget for scheduled worker runs (per invocation and per day) with expiry; lead issues manifests for run_scope `worker-once:<lane>` (artifact SB-V07-001) and `run-worker:<bot>`; no PAYG fallback.
- Observed: entrypoints hold every provider to one dispatch scope; a run without a manifest fails closed and leaves evidence pending.

### G-ACCOUNTS — BLOCKED_ACCOUNT
- Requested: owner lists existing accounts to reuse per platform (X, Reddit → social-a; Instagram, TikTok → social-b; TikTok, X → social-c; Instagram → cultural workspaces) as credential-free AccountRoute records (account_alias, route_type, credential_reference_alias in an external keychain, analytics_route); confirms the verified Google Cloud alias mechanism only where a new address is strictly necessary; MFA/consent stay owner actions; no accounts created merely to show activity.
- Next action: worker writes `social-bots/accounts/registry.json` (no secrets) on the persistent host and runs read-only route verification.

### G-PUBLISH — BLOCKED_AUTHORIZATION
- Requested: per-persona/account/content-hash/effect-count grant for canaries. Proposed: exactly 1 post per general bot on its primary platform, content identified by `final_text_sha256` from the bound review (C05/C06), deletion/correction scoped separately, UNCERTAIN never retried. Effects `<owner-set, proposed 3>` · zero spend · expiry `<owner-set>`.
- Observed: the queue never authorizes (`publish_authorized` False); no publisher exists on the V1.7 path.

### G-MEASURE — BLOCKED_ACCOUNT
- Requested: analytics route per account (API tier / native insights) and acceptance of the predeclared 48h windows. Raw observations only; missing data stays missing; experiments remain PROSPECTIVE (C07) until a real window closes.

### G-CULTURAL — BLOCKED_DATA
- Requested: owner names the cultural reviewer identity and version (`source_requirements.named_reviewer`) for `cultural-primandir-atman` and `cultural-primandir-utsava` and the review event method. The runtime now requires the binding to name the exact final text (`content_sha256`); automated review never claims human endorsement. Cultural candidates stay WITHHELD until then.

### G-SPEND — zero spend held
- Nothing requested. Note: X API write access is paid-tier, so X publishing would be manual-assisted unless the owner separately decides otherwise.

## What proceeds without any gate

Offline V1.7 work on this VM: §A repairs (A1–A6 delivered), D consolidation and loop wiring with fixtures, E community path offline with negative controls, and the final packet. Everything above stays prepared-only until its gate is explicitly opened.
