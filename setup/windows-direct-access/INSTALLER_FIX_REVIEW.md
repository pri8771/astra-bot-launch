# Preventive installer change: source review only

Date: September 12, 2026.

Revised `Setup-DirectSSH.ps1` SHA256: `0a20eca0d2856bd9f56508ee128c60ebd6ac15a294be8ee162d3a8b65e078977`.

The change is confined to the newly generated host private key: remove the explicit creator grant unless the creator is SYSTEM/Administrators, then reject remaining access identities outside SYSTEM/Administrators. The shared protection helper, other files, service configuration, and rollback are unchanged.

Independent same-model agent `/root/windows_direct_access/ssh_script_review` reviewed the change and documentation and reported no material source blocker. This was not a distinct-model review. No remote execution or Windows parsing of this revised installer was performed by the implementation or review agent.

The original installer plus the separate repair supplied the reported live recovery. See `INSTALL_OBSERVATIONS.md` for that sequence. Do not treat the live repair as a test of this preventive installer revision. The coordinator owns subsequent authentication and transfer evidence in `LIVE_STATUS.md`.
