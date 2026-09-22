# Compact Codex session record

Use this format when Codex actually starts coordinating. This file is a specification, not a fabricated active session/heartbeat. Persist one small checkpoint on the appropriate coordination branch at material handoffs, not every thought or timer tick. Keep private local paths/host details out of shared logs where unnecessary.

## Session header

Actual session ID; coordinator role; start/update time with timezone; approved scope; current project; last safely completed action; next permitted action. Current default target for each project is live V1.7 and stop, subject to refreshed native control. Record any newer explicit owner scope change rather than editing historical intent.

## One row per project

Project ID; repository; canonical ref and observed SHA; actual source branch and SHA; assigned worker/session/epoch; observed process or UNKNOWN; artifact; status classification; actual test/evidence refs; latest heartbeat ref and meaningful activity time; exact missing live predicate; blocker; next small task; claimed files; reviewer requirement.

Use UNAVAILABLE/UNVERIFIED when access or evidence is absent. Do not fill blanks with plausible guesses. An old code test remains attached to its original candidate. One cross-project table does not create a common implementation branch, acceptance gate or percentage complete.

## Gate index

For each unresolved gate: project, artifact, action, account/provider/host alias, input hashes, attempt/call limit, spend limit, expiration, actual owner-approval reference, lead-manifest reference and next exact step. No secrets or raw private evidence. Deduplicate repeated requests while keeping project authority separate.

## Handoff example structure (field names, not an execution record)

session_id / role / target_scope / updated_at
projects[]: project_id / coordination_ref / coordination_sha / source_ref / source_sha / owner / heartbeat_ref / activity_observation / current_artifact / evidence_refs / blocker / next_action
changes[]: repository / source_commit / evidence_commit / commands / discovered / passed / failed / errors / skipped / limitations
owner_actions[]: project_id / gate_id / missing_action / existing_authority_ref / requested_scope
next_resume: project_id / artifact_id / required_reads / exact_next_command_or_action

Never record ACCEPTED or COMPLETE without the actual applicable lead decision. Codex's review recommendation uses READY_FOR_LEAD_REVIEW / RECOMMEND_ACCEPT / REWORK_SUGGESTED or the native worker equivalents. Before ending, mark ended implementation sessions truthfully and avoid implying a stopped model continues in the background.

## 2026-09-22 current public capture checkpoint

`session_id`: `codex-current-capture-prep-20260922`
`role`: coordinator / released capture-preparation executor
`target_scope`: LEAD-065 only; exactly two public current-source captures; no model/provider, matrix activation, account, posting, spend, host, or scheduler action.
`updated_at`: `2026-09-22T11:28:42+00:00`
`project`: Social Bots
`coordination_ref`: `chatgpt/social-bots-plan-20260920@7451465a74bd06a2676efd7a04cd0f60a86463c5`
`source_ref`: `codex/bots-execution-binding-20260922@fec97738ec0e9407415f60228f7c3938613396c3` (tree `43e80b92d8ae559db55a41ed33329695e6fd03fc`)
`artifact`: LEAD-065 current-public capture preparation
`activity`: exactly two accepted-collector captures frozen: E1 Meta Reels India (`cap-7920a4414afe4fe4`) and E2 TikTok creator-led series (`cap-9701ad2cb45c4b19`), each `ok` / trusted `live-capture` / HTTP 200; raw hashes and receipt-file hashes are in `social-bots/receipts/evidence/CODEX_CURRENT_CAPTURE_20260922/CAPTURE_INDEX.json`.
`review_state`: READY_FOR_LEAD_SUITABILITY_REVIEW; no self-acceptance.
`blocker`: final-divergence-input suitability and any subsequent matrix/owner model-call gate remain lead-controlled.
`next_action`: lead review of the frozen bytes, receipts, signals and relevance notes in `social-bots/lead-reviews/CODEX_CURRENT_CAPTURE_PREP_20260922.md`; no capture retry or model action before disposition.

## 2026-09-22 portfolio implementation checkpoint

`session_id`: `codex-v17-v07-implementation-20260922`

`role`: coordinator and bounded repair executor; ChatGPT remains formal
acceptance authority.

`updated_at`: `2026-09-22T13:03:59Z`

`target_scope`: Jobs V1.7, Social Bots V0.7 owner ceiling, and SwarmAI V1.7.
The native Bots state remains V0.4.x; this record does not replace its native
scope or release a later milestone.

| Project | Current source/evidence | Classification | Next permitted action |
|---|---|---|---|
| Jobs | `origin/main@1a4efbb`; owner-input request `codex/portfolio-rollup-20260922@350b11f` | **REVIEW_BLOCKED** — G14–G17 have no genuine product-path proof; worker activity is UNKNOWN after its stale five-minute report | Obtain explicit bounded live-frontier inputs, then independently review the unaccepted `dd2e0de` batch before any assignment |
| Social Bots | canonical `chatgpt/social-bots-plan-20260920@7451465`; capture source `033b973`; integrity review `7119645` | **RECOMMEND_ACCEPT** for E1/E2 byte/receipt integrity only; **REVIEW_BLOCKED** for suitability, model activation, and V0.7 progression | Formal lead disposition of E1/E2; no matrix, provider call, host, scheduler, or new SESSION_ONCE before it |
| SwarmAI | failed evidence `codex/swarm-r28d3-evidence-20260922@e917825`; repair `codex/swarm-r28d3-async-gateway-20260922@e87c523` | **REWORK_FOUND** for the one released live-local mission; repair **READY_FOR_LEAD_REVIEW** | Independent exact-SHA lead review and a successor one-run release before any second live invocation |

No project was merged, deployed, dispatched to Fable, or coupled to another
project runtime. Existing native heartbeat rules remain unchanged.
