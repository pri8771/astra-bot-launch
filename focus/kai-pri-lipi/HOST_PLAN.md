# Hosting and the mobile-Mac outage

Owner decision, 12 September 2026: the i9 Mac will remain on. The mobile Mac may be offline for roughly an hour. This updates target ownership, not deployed state.

| Machine | Target role | Current evidence / next proof |
|---|---|---|
| R730 / Unraid | Central hub for Kai and local bots: durable job/state storage, action ownership, small services and local-network endpoints | Destination confirmed by owner. Current capacity/container/storage/backup suitability requires refresh. Install Unraid applications only through the owner's required official store route. No deployment or network change in this packet. |
| Windows | Fallback hub and development/inference worker while available | Earlier RTX3060/Qwen synthetic tests passed; owner now reports Cursor Atlassian auth. Verify current tools and active jobs before delegating. No assumption of existing Mac-only files or exported credentials. |
| Intel i9 Mac | Staging computer and secondary fallback; build a portable copy here before migration | Owner reports present/left on. Hardware, OS, apps, developer tools, permissions and exact remote identity unverified. Prepare inventory first; do not assume eGPU acceleration or installed IDEs. |
| Mobile Mac | Interactive coordination and optional development | Current Kai/Pri processes were observed here. Mobile network loss can interrupt them until actual migration. This chat's continued execution is not guaranteed while its host is offline. |

R730 can own the hub while qualified workers perform inference/builds on other machines. The hub location does not require every heavy computation to run on the R730. Keep host-local Git worktrees; central shares are for approved state/artifacts/backups, not simultaneous cross-OS edits to one live checkout.

## Fast path

1. Limit i9 work to a quick inventory if remote input works; stop rather than spending time on setup with no immediate job. Use the prepared setup package when useful. Confirm its exact TeamViewer target and signed-in desktop; do not connect to an unidentified saved machine.
2. Prepare a host-local workspace and clone the private task library through existing Git authentication. Reuse installed tools; install only missing necessary vendor software after inspecting OS compatibility and existing permissions. The default scripts do not install anything.
3. Start one available IDE with a bounded staging task and a persistent return file. Verify it actually accepted/runs the task before claiming mobile-Mac-independent progress. A TeamViewer connection or pasted prompt is not execution proof.
4. Stage only the necessary source/config templates. Reconnect credentials on the chosen host through approved mechanisms; never commit runtime profiles, Google tokens, Slack credentials or private chat records. Test one small workflow before transferring service ownership.
5. Qualify R730 packaging/storage, then migrate one bot at a time. Stop/fence the old consumer before enabling the new active consumer; check both ends and retain rollback. Do not run multiple Slack listeners or schedulers as accidental failover.
6. Prove fallback explicitly: restore from a known state, acquire one owner/lease, reconcile pending side effects, process one job exactly once and record recovery. Automatic failover is future implemented behavior, not a promise from this plan.

Speed comes from independent preparation lanes (Kai acceptance, Pri packaging, Lipi live-input reconciliation and i9 inventory), small context packets, reuse of accepted tests and no competing writers. A full infrastructure rewrite is not required to run one useful staged workflow.

## Remote observation in this turn

The owner clarified that the i9 is low priority and should be used only if immediately useful. The owner connected the i9, and at about 19:21 UTC TeamViewer on the mobile Mac showed its signed-in `Priyanshs-MBP` desktop. Initial remote coordinate input failed with `noWindowsAvailable`; raising the window and sending the application-search shortcut did not visibly open Terminal. The owner reports Terminal is on, but remote input/command execution remained unverified. The owner then parked i9 setup in favor of the first-five kickoff; do not keep retrying it. This confirms a remote screen, not working remote command execution. No direct remote execution endpoint or i9 worker is verified yet. Update from receiving-host evidence after the next successful action.
