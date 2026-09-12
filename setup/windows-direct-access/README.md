# Windows direct command access

Updated September 12, 2026. The original installation plus the separate host-key repair reached Windows `READY` at `100.89.44.91:2222`. The coordinator subsequently verified Mac authentication, hostname/user, an SFTP round trip, exact private listener and password-only rejection; see `LIVE_STATUS.json`. The installer now contains a preventive source change that has not been executed on Windows.

The setup is fixed to `DESKTOP-H5S6H41`, Windows Tailscale address `100.89.44.91`, Mac source `100.124.207.87`, TCP port `2222`, and the existing local account `Priyansh Chordia`. It installs Microsoft's Windows OpenSSH Server capability only if absent. It creates no account and grants no administrator membership. If the selected account is already an administrator, SSH retains that account's existing authority; this is not a sandbox or a standard-account boundary. A dedicated standard account can be considered separately.

It refuses an existing `sshd` service/process, occupied port 2222, existing setup folder, existing named firewall rules, a wrong host/Tailscale address, or disabled Windows Firewall profiles. If the capability needs installation, any existing port-22 listener also causes a stop because Windows creates a broad port-22 rule during installation. The package owns `C:\ProgramData\AstraDirectSSH`, its new `sshd` service, and named firewall rules. Existing SSH configurations, keys, other users, Tailscale settings, and other services on port 22 are not edited.

The service uses its own `-f` configuration, host key, and authorized-key file. Source restrictions exist at the network binding, firewall, allowed user, and public key. Password authentication and SSH forwarding are disabled. The temporary installer guard blocks only the native `sshd.exe`; the installer's newly created broad port-22 rule is disabled. The guard is removed only after local service/listener checks succeed. Failures retain the guard and the receipt.

## What happened and what to do next

The original installer passed Windows parsing and `sshd -t`/`sshd -T`, but service startup failed. `ssh-keygen` had added an explicit `Priyansh Chordia:(M)` permission to the host private key; the protection step retained it alongside SYSTEM and Administrators. The separate repair removes that user entry while checking that key bytes, owner, other permissions, configuration, and service command are preserved.

The first repair attempt stopped before mutation because Windows labels the disabled allow rule `Inactive`. The corrected repair accepts `False/Inactive` before starting, then requires `True/OK` after enabling. It reached `READY` with the exact Tailscale listener. See `INSTALL_OBSERVATIONS.md` for the observed sequence and original artifact hashes; `REPAIR_REVIEW.md` records the source review.

Expected existing host fingerprint observed on Windows:

```text
SHA256:OLQENXmXaQ8kMHRThuuCsXJeru+YVkbXtOcrrc0nW8g
```

The coordinator matched that fingerprint through TeamViewer before creating the Mac trust file. Identity, file-transfer and local restriction checks passed. Use the verified Mac alias `ssh astra-windows` for commands and `scp`/`sftp` with that alias for files. Other-source rejection has not been probed from another host. Reboot persistence and rollback are still separate verification steps. Do not rerun the installer on the already installed host; its ownership preflight intentionally refuses an existing service/folder.

## Installation on a fresh target state

First transfer these two scripts plus the Mac's single **public** Ed25519 key to the PC using the existing authorized channel. Never transfer its private key. Review the scripts and verify the intended PC identity before accepting Windows UAC.

```powershell
& 'C:\path\Setup-DirectSSH.ps1' -PublicKeyPath 'C:\path\astra-windows.pub'
```

The Mac key must be a new purpose-specific key. The script prints the Windows host-key SHA256 fingerprint and records local evidence in `C:\ProgramData\AstraDirectSSH\state.json`. Compare this fingerprint with the Mac's SSH host-key prompt over the independently observed TeamViewer session before accepting the key. Do not bypass host-key checking. No password or private key is written into these source files.

## Everyday command and file access

Connect from the Mac using the actual private-key path; the private key remains on the Mac:

```sh
ssh -p 2222 -i /absolute/path/to/astra-windows -o IdentitiesOnly=yes -o PreferredAuthentications=publickey -o PasswordAuthentication=no -l 'priyansh chordia' 100.89.44.91 whoami
```

Use the same key for an interactive file-transfer session, working only in an agreed Windows folder:

```sh
sftp -P 2222 -i /absolute/path/to/astra-windows -o IdentitiesOnly=yes 'priyansh chordia@100.89.44.91'
```

Verify the returned identity and hostname, then a bounded file write/read/delete in an agreed work folder. Confirm password-only authentication is rejected. If a second authorized tailnet device is available, confirm that it cannot connect. Local `Listening` status alone is not completion. Retain the host identity, fingerprint comparison, successful key authentication, and restriction-check results before dispatching work.

`sshd` starts automatically and depends on the existing Tailscale service. Reboot and reconnect testing is still required: service startup can race address readiness. This package changes no sleep, login, Tailscale expiry, tailnet policy, or reboot settings. A later Tailscale address change requires a reviewed config update. Tailnet grants can additionally limit the Mac-to-PC flow; this package does not alter existing network policy.

## Roll back from elevated Windows PowerShell

```powershell
& 'C:\path\Rollback-DirectSSH.ps1'
```

Rollback checks ownership, stops/removes the newly created service, removes this setup's firewall rules and keys, and uninstalls the server capability only when this setup installed it. A capability already installed at preflight is preserved. It retains the configuration and receipt for review, so another setup run will deliberately stop until that folder is reviewed and archived. It does not remove preexisting Windows SSH folders or files. Do not run setup/rollback concurrently with another SSH administrator.

## Sources

- [Microsoft: install the Windows OpenSSH capability](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
- [Microsoft: SSH server configuration and user restrictions](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration)
- [Microsoft: public-key authentication and Windows permissions](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)
- [Tailscale: unattended Windows access](https://tailscale.com/docs/solutions/access-remote-desktops-using-windows-rdp)

The preventive installer change removes the key creator's explicit grant only from the newly generated host private key and rejects unexpected remaining key permissions. The general file-protection function and other files are unchanged. That revised installer has source-only validation; the observed Windows recovery used the separate repair script. Current authentication/transfer results belong in the coordinator's `LIVE_STATUS.json`.
