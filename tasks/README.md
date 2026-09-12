# IDE task directory entrypoint

These are **actual planning folders**, not installed executors, a Jira synchronizer or a cross-host claim service. Start in the selected folder with `TASKS.md` and `queue.json`, then read [roadmaps](../BOT_ROADMAPS.md), [task contract](../TASK_DIRECTORY_CONTRACT.md) and the assigned worker packet.

Priority folders: [OPO](one-person-ops/TASKS.md), [WHB](wait-how-big/TASKS.md), [CommerceLint](commercelint/TASKS.md). [BidetFit](bidetfit/TASKS.md) and [Guru](guru/TASKS.md) are deferred, not canceled. Kai/Pri are services, not additional business folders.

All task IDs are internal; every status is proposed and needs actual Jira mapping. Null keys are unknown, never requests to clear native fields. Estimates are deliberately absent: preserve existing estimates/actuals through writer readback. Check/reuse writer task `6046ab83-8402-47e3-b832-f4fe478da7f1`; no competing writer.

Required gates: valid fully populated Jira contract before execution, verified source/spec hashes, dependencies, exclusive path/action ownership, current capability and bounded review/repair. Preparation for Jira may continue while execution is unadmitted. Definition changes invalidate prior admission. Maximum two targeted repairs per task.

Paths are relative to each folder; `packet_root` resolves the wave directory. For cloud/other-host checkouts, set `source_root_override` in the admission receipt and bind verified repository/ref/path mappings. Never treat a Mac path or historical receipt as current remote source or permission.

Each task's evidence belongs in its eventual admitted `runs/<run-id>/` directory. This preparation creates none. Preserve actual results, unknowns and rejected/failed attempts. Independent review and receiving-system receipts determine acceptance; no fake adoption/revenue. Ongoing businesses proceed through separately admitted experiments, not an infinite queue. Atomic claims/fencing still require implementation and qualification under the contract.
