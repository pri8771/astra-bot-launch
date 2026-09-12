# Cursor Windows — CommerceLint release lane

## Objective

Make the shortest evidence-backed path to a CommerceLint release from the Windows primary machine. Keep the work on CommerceLint; do not expand into OPO, WHB content, general fleet migration, or unattended operation. Root will provide the exact `autonomous_apps` repository identity/remote. Do not guess or clone a similarly named repository.

## Starting facts

- The current BOTS checkout is `D:/Astra/repos/bots`, clean `main` at `d5b3b7f399b8d3e3ba4b926d0d89f30aacac6e11` when checked. It is not evidence that CommerceLint lives there.
- Windows reports Python 3.11.9, Node 24.19.0, Ollama 0.33.2; Claude auth was valid at the last check, but no Claude inference is evidenced. Git read/clone worked; `gh` was unauthenticated, so push/PR access is unknown.
- A bounded local Ollama smoke already passed two synthetic URL cases at 2026-09-12 18:16:40/41 UTC (122 input and 22 output tokens total); `ollama ps` showed 100% GPU, 2048 context, 3.1 GB. Source: `D:/Astra/control/windows_smoke.ps1`; receipts: `D:/Astra/pilots/local-smoke-20260912-1812`. This is a two-case local smoke only, not CommerceLint QA or unattended qualification. Do not rerun without a specific gap.
- The operating notes make Windows the requested primary but say existing BOTS dispatch uses POSIX locks/process groups. Do not claim the Mac dispatcher is Windows-compatible or recovered.

## Bounded work

1. Root verified the CommerceLint source remote as `https://github.com/pri8771/autonomous_apps.git` from the existing Mac checkout. Use a new Windows-local clone at `D:/Astra/repos/autonomous_apps` if absent, then an isolated task worktree. If present, inspect and preserve it. Verify remote, current revision and clean/dirty state before acting; do not substitute the BOTS charter repository for the product source. Git read/clone can work even while gh is unsigned-in; verify actual access, never assume push/PR permission.
2. Inspect CommerceLint's current source, release instructions, tests, build and deployment bindings. Map the smallest path from the admitted business goal to a releasable artifact. Record actual public URL/host, deployment owner, credentials availability (status only), and unresolved dependencies as verified or unknown; do not infer them from old notes.
3. Run only bounded local deterministic checks needed for that path. Keep full commands, exit status, timestamps, checkout revision and concise output in the private outbox. Do not expose credentials, install broad tooling, modify shared source, or invoke models just to fill time.
4. Before any product-code change, confirm the designated sole Jira writer has established exact current task admission and readback. Historical Jira keys and planning docs are pointers, not admission. If absent, finish the source-first release-readiness packet and stop before editing product code.
5. If admitted, work only in the isolated task worktree, run specified checks and return a candidate diff/release receipt. The owner's explicit goal is to get CommerceLint operating, not merely produce more plans. Carry the candidate through attributable review and the existing qualified release route where current task/account authority permits; read back the actual destination and retain rollback evidence. Do not guess destinations, fabricate payment readiness, override platform requirements or turn an unavailable input into approval. Ask only for the exact missing prerequisite, with the release otherwise ready.

## Return and stop rules

Write only to a new private local outbox such as `D:/Astra/outbox/windows-primary-wave-2026-09-12/cursor-cl/` (choose a unique sibling if it exists). Return `SESSION_RETURN.md` plus a compact evidence index with repository URL/identity, base and final SHAs, clean/dirty state, Windows tool versions, commands/results, exact task admission/readback, release destination evidence, and remaining blockers. Distinguish performed work from a proposed next step. Stop on repository ambiguity, unadmitted scope, unexpected dirty files, missing/uncertain release access, failed safety check, or any action outside the admitted task; preserve all evidence and report the blocker. Do not activate inherited cron or claim unattended recovery.
