# Observed Windows installation and repair

Date: September 12, 2026. These observations were reported by the coordinator operating the Windows host. This implementation agent did not run remote commands. This record is separate from source review and does not establish that a later revised installer was executed.

1. Original `Setup-DirectSSH.ps1` SHA256 `1965b21cf2c3e4f2a0c78380ece78ff2e910ad413a35bb8824b9db788cdc37a9` passed Windows parsing and source verification. Installation reached successful `sshd -t`/`sshd -T` checks, then `Start-Service sshd` failed. Containment stopped/disabled the service and retained the firewall guard.
2. Live host-private-key ACL metadata showed `BUILTIN\Administrators:(F)`, `NT AUTHORITY\SYSTEM:(F)`, and `DESKTOP-H5S6H41\Priyansh Chordia:(M)`. The explicit user grant was the defect addressed by the repair.
3. First `Repair-HostKeyACL.ps1` SHA256 `b2df4560c345afe890f561c0a6aa418f5b6403e26ce723e95a2f15061fda2d9e` passed Windows parsing/source verification, then stopped before mutation at the firewall check. Live filters matched the intended scope, but the disabled rule reported `Enabled=False, PrimaryStatus=Inactive`.
4. Corrected repair SHA256 `040dcce336ea2d89e4d5e49699afa0ffbbf338a95c0e525f63936d7b45e427e5` subsequently reported `READY` for `100.89.44.91:2222`. The repair validates the exact PID-owned listener before enabling the scoped rule and removing the guard.
5. Windows reported host fingerprint `SHA256:OLQENXmXaQ8kMHRThuuCsXJeru+YVkbXtOcrrc0nW8g`. Independent comparison against the Mac's connection, login identity, and file-transfer outcomes were still being verified by the coordinator when this record was written; those results belong in `LIVE_STATUS.md`.

The later preventive edit to the installer is a source change only. Do not attribute this repair's live outcome to that revised installer. Reboot persistence and rollback were not verified by this implementation agent.
