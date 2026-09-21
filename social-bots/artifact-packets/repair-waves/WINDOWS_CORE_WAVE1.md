# Repair wave — Windows Core / Host

Worker instance: Windows Claude
Suggested branch: `claude/social-bots-windows-core-host`

## Clean-machine bootstrap

Assume this Windows instance starts with **no repository clone, no project folders, and no local Social Bots state**.

Before implementation:

1. Choose a normal local working directory you can write to. Do not assume any pre-existing project path.
2. Verify Git is available. If Git is missing, stop at that exact environment blocker rather than inventing a workaround.
3. Use the machine's existing Git/GitHub authentication if already configured. Never request, print, paste into logs, or commit credentials/tokens.
4. Clone the repository:
   - repository: `https://github.com/pri8771/astra-bot-launch.git`
5. Enter the new `astra-bot-launch` working tree.
6. Run `git fetch --all --prune`.
7. Verify these remote branches exist:
   - `origin/claude/social-bots-core-to-v2`
   - `origin/chatgpt/social-bots-plan-20260920`
8. Create the new Windows branch **from the previous completed Core implementation**, not from main:
   - `git switch -c claude/social-bots-windows-core-host origin/claude/social-bots-core-to-v2`
   - or the equivalent checkout command if the installed Git is older.
9. Merge the latest canonical coordination branch into the new branch:
   - `git merge origin/chatgpt/social-bots-plan-20260920`
10. Resolve conflicts carefully:
   - preserve the previous Core implementation;
   - prefer the newest canonical versions of artifact-management/status/lead-control files;
   - do not overwrite newer canonical coordination with stale worker copies.
11. Confirm `git status` is clean before starting artifact implementation.
12. Record the resulting starting SHA in the first Windows worker report.

If repository authentication is required, stop only at the exact normal Git/GitHub sign-in gate and let the owner complete it. Do not create alternate credentials, tokens, or secret files.

This is a multi-artifact execution wave. Parent artifact IDs remain canonical.

## Order

### 1. SB-V03-004 repair
- move decision log/latest-decision durable writes inside the fence or re-check/commit them under the same fence;
- do not claim filesystem multi-write transactionality;
- add regression that stalls after main fenced state/effect commit, allows takeover, then proves old owner cannot write any later worker-owned durable artifact;
- implement/prove native Windows strong process lock OR deliberately use an already-installed WSL POSIX runtime and document that as the supported Windows-host path.

### 2. SB-V03-005 repair
Adopt explicit two-layer state:
- RuntimeState (shared): worker/recovery/fence/process counters, shared capture catalog.
- PersonaState (private per persona/workspace):
  - consumed/seen signal ids;
  - hypotheses;
  - working state;
  - pending decisions;
  - goals/strategy-private state.

Shared captured evidence is read-only; each persona may independently consider the same captured evidence.

Acceptance:
- same signal can be independently considered by general and cultural personas on one runtime;
- one persona's hypothesis count cannot change another persona's reasoning context;
- concurrent cycles remain fenced/serialized for shared writes;
- no private state bleed.

### 3. SB-V03-006
Regenerate the complete V0.3 acceptance bundle only after 004/005 pass.

### 4. SB-V04-001 / SB-V04-002 real adaptive provider
Use:
- REASONING_PROPOSAL_SCHEMA.md
- CLAUDE_REASONING_ROUTE_RESEARCH.md

Windows-host proof:
- record boolean only for ANTHROPIC_API_KEY presence;
- if present, FAIL CLOSED for subscription-route test; never print key;
- use existing authenticated Claude Code subscription only;
- bounded non-interactive JSON call, no tools/effects;
- provider/auth/quota/parse failures -> BLOCKED;
- production adaptive-required posture default for V0.4 worker;
- baseline/contextual modes remain explicit debug/test only.

### 5. SB-CTL-006 CI
Add GitHub Actions unit/regression + artifact JSON validation, no secrets/network/model calls.

### 6. SB-V07-WIN-001
Prove actual recurring worker on Windows/WSL supported path:
- two separate invocations;
- real heartbeats/receipts;
- lock/fence;
- clean exit/restart/no-overlap.

## Reporting

One worker report per artifact under `worker-reports/windows-core/`.
Do not mutate canonical artifact state.
