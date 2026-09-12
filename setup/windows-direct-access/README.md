# Windows direct command access

Prepared September 12, 2026. These files are a proposed setup, not evidence of a working connection.

The setup is fixed to `DESKTOP-H5S6H41`, Windows Tailscale address `100.89.44.91`, Mac source `100.124.207.87`, TCP port `2222`, and the existing local account `Priyansh Chordia`. It installs Microsoft's Windows OpenSSH Server capability only if absent. It creates no account and grants no administrator membership. If the selected account is already an administrator, SSH retains that account's existing authority; this is not a sandbox or a standard-account boundary. A dedicated standard account can be considered separately.

It refuses an existing `sshd` service/process, occupied port 2222, existing setup folder, existing named firewall rules, a wrong host/Tailscale address, or disabled Windows Firewall profiles. If the capability needs installation, any existing port-22 listener also causes a stop because Windows creates a broad port-22 rule during installation. The package owns `C:\ProgramData\AstraDirectSSH`, its new `sshd` service, and named firewall rules. Existing SSH configurations, keys, other users, Tailscale settings, and other services on port 22 are not edited.

The service uses its own `-f` configuration, host key, and authorized-key file. Source restrictions exist at the network binding, firewall, allowed user, and public key. Password authentication and SSH forwarding are disabled. The temporary installer guard blocks only the native `sshd.exe`; the installer's newly created broad port-22 rule is disabled. The guard is removed only after local service/listener checks succeed. Failures retain the guard and the receipt.

## Run once from an elevated 64-bit Windows PowerShell

First transfer these two scripts plus the Mac's single **public** Ed25519 key to the PC using the existing authorized channel. Never transfer its private key. Review the scripts and verify the intended PC identity before accepting Windows UAC.

```powershell
& 'C:\path\Setup-DirectSSH.ps1' -PublicKeyPath 'C:\path\astra-windows.pub'
```

The Mac key must be a new purpose-specific key. The script prints the Windows host-key SHA256 fingerprint and records local evidence in `C:\ProgramData\AstraDirectSSH\state.json`. Compare this fingerprint with the Mac's SSH host-key prompt over the independently observed TeamViewer session before accepting the key. Do not bypass host-key checking. No password or private key is written into these source files.

Connect from the Mac using the actual private-key path:

```sh
ssh -p 2222 -i /absolute/path/to/astra-windows -o IdentitiesOnly=yes -o PreferredAuthentications=publickey -o PasswordAuthentication=no -l 'priyansh chordia' 100.89.44.91 whoami
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

Validation at preparation: source review only until a Windows PowerShell parser and the installed `sshd -t`/`sshd -T` execute on the target. Runtime, authentication, service startup, and rollback must not be claimed as tested based on source review.
