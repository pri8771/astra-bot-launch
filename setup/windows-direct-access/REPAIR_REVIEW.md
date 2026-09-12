# Host-key permission repair review

September 12, 2026. Parent-observed host metadata showed SYSTEM and Administrators full control plus an explicit `Priyansh Chordia` Modify entry on the owned host private key. The administrator's configuration checks passed; service startup had failed. No successful recovery is claimed here.

`Repair-HostKeyACL.ps1` removes only explicit allow entries for the recorded current user SID. It verifies unchanged key bytes, owner, other permissions, and the approved configuration; it starts the recorded service behind the retained guard and checks the sole Tailscale listener before opening the Mac-only rule. It never changes the service ImagePath, configuration, or original setup/rollback scripts. Failures contain the service and retain the guard.

Independent same-model agent `/root/windows_direct_access/ssh_script_review` rereviewed the final source: passed, no remaining material source blocker found. This was not a distinct-model review. Neither implementation nor review agent executed the repair.

Run the Windows parser before execution. Actual service startup, Mac authentication, restriction checks, and later rollback remain runtime verification requirements. If startup still fails, inspect service logs before another change.
