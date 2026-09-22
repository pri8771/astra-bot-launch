# Heartbeats: project-specific, not one copied cadence

Sources were freshly read at the pinned commits in PROJECTS.json. Recheck each project's current instruction before operating. This file does not start a watcher or change its policy.

| Project | Verified rule | Codex behavior |
|---|---|---|
| Social Bots | One SESSION_ONCE per genuinely fresh worker session; none repeated on resume; no periodic loop | Check existing session record, emit only the new worker's allowed start receipt after handoff, preserve historical entries. Invocation results and lease renewal are separate. |
| Jobs | One owned local five-minute worker heartbeat; FIVE_MIN_2026_09_21 / ACTIVE_5M; lead hourly sync is separate | Discover current owner/process and reuse the established stream after clean handoff. Do not add a second watcher because Codex is coordinating. |
| SwarmAI | One implementation session and one local five-minute producer; retain CURSOR-V17-SINGLE stream with explicit takeover/epoch | Check actual host/process and relinquished ownership. Preserve last real activity separately from publication/tick time. |

## One Codex conversation is not one shared worker identity

The coordinator may keep one compact session checkpoint referencing three project records. That is not a heartbeat proving three workers are running. Do not emit implementation heartbeats for Fable, impersonate its session or backfill its missing intervals.

If Codex is only coordinating/reviewing, reference existing implementation heartbeats and record its own role as coordinator. If Codex is explicitly handed implementation ownership, create the required per-project worker identity/epoch and follow that repo's cadence. This does not require three chat windows. It also does not authorize three duplicate timer processes. One existing producer per applicable repository is the current rule; Bots has no timer producer.

While switching projects, keep truthful ACTIVE, WAITING_REVIEW, BLOCKED, PAUSED or STOPPED state using the local schema. Do not keep a timer saying active implementation while the model has exited. A long-running real test can be tracked by its process/run receipt, not by invented edits. Do not kill another host's watcher from a local PID lookup.

## Safe takeover sequence

1. Read current canonical assignment and the real current worker report/heartbeat.
2. Verify repo/branch/host/process/session and whether the previous owner has relinquished the work.
3. Preserve local changes and exact last source/evidence refs. Coordinate the handoff before editing shared files.
4. Record a new owner/epoch only if actually taking over. Distinguish lead instruction delivery from worker acknowledgement.
5. Reuse or replace the established watcher only where the local policy and permissions allow; never operate both.
6. Run the smallest bounded assigned action and write truthful completion/blocked evidence.
7. On exit, stop or accurately mark any watcher owned by the ended implementation session. Never stop a separately authorized application service merely because development ends.

No changes to ChatGPT automations or their schedules are made by this handoff. Local five-minute heartbeat producers are not ChatGPT scheduled tasks. Do not try to implement five-minute work using a tool that cannot support that cadence. Verify an actual authorized lead-review transport before claiming an automatic lead/worker cycle exists.

Critical historical distinction: a branch ACK was often authored by the lead to deliver instructions. It is not independent worker work, current liveness or proof that a repair ran. A missing periodic Bots update is normal under SESSION_ONCE, not evidence to restart a lane.
