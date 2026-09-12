# Source review receipt

Date: September 12, 2026

Independent reviewer: `/root/windows_direct_access/ssh_script_review`, a separate agent inheriting the same model configuration as the implementation agent. This was an independent agent review, not a distinct-model review.

Final disposition: source review passed; no remaining material blocker found. No script was executed or published by the implementation or review agent.

Findings addressed:

- Native service-command quoting was replaced by `Win32_Service.Change` with a checked return value.
- Capability installation refuses another port-22 listener, and a temporary program-specific block protects the native server during installation.
- Firewall rules must be healthy and enabled in the active policy; profiles that disallow local rules cause a stop.
- Failure containment precedes receipt writes. Receipts use atomic replacement and the PowerShell 5.1-compatible `[NullString]::Value` argument.
- Rollback verifies service/process absence and capability state, reporting pending removal rather than claiming completion when a restart or inspection remains.
- The exact existing account, its unchanged privileges, a quoted lowercase allowed username, Mac source restrictions, isolated keys/configuration, and fail-closed service ownership checks were reviewed.

Preparation checks: files were read back and checked for trailing whitespace. No PowerShell runtime was available on the preparation Mac.

Still required on the target: Windows PowerShell parsing, `sshd -t`/`sshd -T`, independently verified host-key fingerprint, actual Mac key authentication and identity, rejected password authentication, source restriction verification, reboot persistence, and eventual rollback verification. The setup script includes local configuration/listener checks; those checks have not yet run.

This receipt does not establish a live connection or successful setup.
