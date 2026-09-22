# SwarmAI — source-verified route for the shared Codex session

Repository: `pri8771/swarmai`.
Canonical instructions: `coordination/swarm-control`, observed at `817821d0bab6c68ae1b92671b115f8be98590ebc`.
Application source: `cursor/v17-single-session`, observed at `ab958d7a4b4d6198b143e7e79ecf69ff367cb10e`.

Use a separate coordination worktree or git show. Do NOT merge stale application files from the coordination snapshot into the actual app branch. Local paths are discovered, not inferred from earlier Downloads-folder conversations.

## Mandatory current controls

Read current root AGENTS.md, `docs/coordination/SESSION_START.md`, `FABLE_DELIVERY_CONTRACT.md`, `EXECUTION_CONTROL.json` and the relevant latest review. The last two short names are relative to docs/coordination.

EXECUTION_CONTROL pins `goal_version=1.7`, `allowed_phases=[v17]`, one implementation session and one heartbeat producer. V1.8–V3 implementation AND further planning are parked. An accepted V1.7 does not auto-unlock another phase. Historical metadata saying V3 is not execution authority.

Read `docs/coordination/V17_RECOVERY_PACKET_QUEUE.json` and only the next genuinely permitted packet. Run the native scope guard `docs/coordination/tools/execution_guard.py` for phase v17 before selection. Its structural pass cannot waive live prerequisites or review holds. `preflight_only` means a read-only capability probe, not a mutation.

## Observed worker report — not independent completion evidence

At the pinned coordination ref, `docs/coordination/status/CURSOR-V17-SINGLE.md` reports Fable takeover epoch `fable-v17-20260922-01`, source `ab958d7...`, update `2026-09-22T00:33:34Z`, packet OPS-CI-01 / ART-OPS-HEARTBEAT, next action R27a durable action receipts. Its block list includes EXT-ACTIONS-BILLING, EXT-V14-LEAD-REVIEW, EXT-G13-*, EXT-G12-REMOTE-ROUTES and EXT-V15-SECOND-HOST. These are worker-reported snapshot facts; refresh current source, actual processes and evidence before action. Do not pay to resolve a billing blocker without authorization.

The matching heartbeat under `docs/coordination/heartbeats/CURSOR-V17-SINGLE.json` records the takeover and distinct last meaningful activity. This is the verified path; a root-level `status/CURSOR-V17-SINGLE.md` was not found on the app branch in this notes pass. Resolve paths relative to the coordination docs instead of treating that lookup as missing project evidence.

No checkpoint was newly accepted and no runtime test was executed by this handoff.

## Active finish line

Deliver a private/local running application the owner can actually access: exact pushed candidate SHA, genuine missions, worker recovery, knowledge/action-session receipts, a real external GitHub checkpoint through SwarmAI, integrated checkpoint matrix and independently reviewable evidence. Show real URL/port, process/log location and start/restart/stop instructions with honest reachability limits. A health endpoint alone or fixture mission is not live V1.7.

Native startup priority: CI/heartbeat hygiene -> durable effects/approval safety -> actual worker/knowledge/tool wiring -> genuine CP1/CP3/CP4/CP5 -> R33c real external checkpoint -> integrated CP6. Lower-version prerequisite evidence remains binding. Use exact packet definitions for meanings and requirements, not guessed checkpoint labels.

The current control explicitly gates R07/R10/R11 on Windows/sealed-digest/remote-route proof; R33c requires EXT-V17-REALWORLD-GITHUB. Review holds include R27e after R27c and R28a after R27e. Empty reviewed/frozen maps do not approve the work. Do not clear a gate merely because a structural validator or one worker says ready.

## Use existing implementation

Swarm's native AGENTS directs reuse of PostgreSQL/SQLAlchemy/Alembic, FastAPI/httpx/Pydantic, the existing broker, ToolGateway, scheduler, worker system, outbox, eval/review and self-development infrastructure. Do not replace these with Bots' file/JSON storage because the same Codex session sees both. No second scheduler, authority DB or orchestration framework without a demonstrated reviewed gap.

Swarm remains a reusable product, not the mandatory host for Bots or Jobs. Cross-project coordination does not require a cross-project Swarm mission or shared product memory. No self-development privilege escalation, self-acceptance or unreviewed public/main deployment.

## Ownership and heartbeat

Fable is the single implementation worker after a verified local handoff. Retain historical CURSOR-V17-SINGLE stream with explicit engine/epoch rather than creating a competing Fable/Codex watcher. The local producer is five-minute. A timer tick is not proof the model is working; preserve actual activity/test process and intentional wait/stopped state.

Codex coordinates/reviews without becoming a second implementation owner. If handed implementation, verify release of prior local ownership and preserve work. Do not kill remote/local processes based only on an old report. No unconditional watcher takeover.

## Authority and exit

Existing GitHub account use for R33c requires a fresh read-only probe on the actual host plus exact action approvals. This chat's GitHub connector access does not prove local gh auth or that SwarmAI executed an action. Model/provider/account capacities are verified, not assumed. No paid fallback, secret logging, main merge/public release or destructive production action without actual owner approval.

Return READY_FOR_LEAD_REVIEW or precise BLOCKED_FRONTIER. Continue other permitted V1.7 work behind independent external blockers, never invent missing results or bypass a review hold. Stop development at V1.7; keep only otherwise-authorized application operation running safely.

## Pinned sources

https://github.com/pri8771/swarmai/blob/817821d0bab6c68ae1b92671b115f8be98590ebc/docs/coordination/SESSION_START.md
https://github.com/pri8771/swarmai/blob/817821d0bab6c68ae1b92671b115f8be98590ebc/docs/coordination/EXECUTION_CONTROL.json
https://github.com/pri8771/swarmai/blob/817821d0bab6c68ae1b92671b115f8be98590ebc/AGENTS.md
