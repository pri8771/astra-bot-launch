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
