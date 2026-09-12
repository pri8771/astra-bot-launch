# Antigravity Windows — independent readiness and QA

## Objective

Provide a small, independent, read-only readiness assessment across CommerceLint, OPO, and Windows execution prerequisites. Cursor Windows owns CommerceLint release work; Mac Cursor owns OPO; Mac Antigravity owns WHB content. Do not duplicate their edits or content work. This packet creates no Jira admission and authorizes no product changes or external writes.

## Starting facts

- Windows BOTS checkout: `D:/Astra/repos/bots`, reported clean `main` at `d5b3b7f399b8d3e3ba4b926d0d89f30aacac6e11`.
- Reported Windows versions: Python 3.11.9, Node 24.19.0, Ollama 0.33.2. Claude auth was valid on the last check, not proof of inference. Git read/clone succeeded; `gh` was unauthenticated.
- The two synthetic local Ollama URL cases already passed at 18:16:40/41 UTC with 122 input/22 output tokens total; receipt location is `D:/Astra/pilots/local-smoke-20260912-1812`. Treat this only as a bounded smoke result, not product QA, launch readiness, or unattended recovery.
- Current planning says OPO's full domain is pending and public hosting/message storage are unverified. Do not fill these gaps by guessing. SMB mapping was requested for Windows but is deferred behind this first product wave; record it as queued, do not investigate or mount shares now.

## Bounded checks

1. CommerceLint source is `https://github.com/pri8771/autonomous_apps.git`; Cursor Windows owns its clone/worktree at `D:/Astra/repos/autonomous_apps`. Read only a recorded stable revision or its immutable return; do not change that checkout. OPO's product source remains on Mac, while `D:/Astra/repos/bots/onepersonops` is charter/history. Record the missing Windows product copy rather than auditing the wrong folder. Check only directly relevant build/test commands, actual bindings, Windows prerequisites and gaps. Treat missing task admission as a hard stop for code changes.
2. Check Windows-local readiness that affects these lanes: installed tools/versions, repository cleanliness/identity, configured app presence, and auth/connectivity state only where the target is explicit in current source/config. Record status and source of observation without opening or copying secrets. Do not access an unverified account/project by inference from the `unsubscribe.me` Chrome profile; verify its identity before any relevant use.
3. Keep this assessment to the local Windows prerequisites relevant to the CommerceLint/OPO source workflows; do not overlap the separate Mac WHB content/readiness lane. Use existing evidence for hardware/model facts; do not repeat scans or pulls. Do not run a model, install software, edit repo/config files, alter credentials, start a service, or change system settings.

## Return and stop rules

Write a concise `READINESS.md` and evidence index only under a new private, task-specific local outbox such as `D:/Astra/outbox/windows-primary-wave-2026-09-12/antigravity-windows-qa/`; choose a unique sibling if it exists. No shared-file writes, Jira, Git commits, pushes, deployment, publication, SMB mount, Plex change, or credentials in the report. For each finding give its source path/URL, observed revision/time, evidence status (`verified`, `reported`, or `unknown`) and the exact next prerequisite. Stop if repository identity, account/project identity, task admission, or destination is ambiguous; preserve prior user files and report the blocker. Do not activate any inherited cron or imply unattended recovery.
