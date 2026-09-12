#Requires -Version 5.1
#Requires -RunAsAdministrator
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:ProgramData 'AstraDirectSSH'
$statePath = Join-Path $root 'state.json'
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
if ($state.Schema -ne 1 -or $state.Computer -ine $env:COMPUTERNAME -or $state.Root -ine $root -or $state.SshdBefore -ne 'Absent' -or $state.Capability -ne 'OpenSSH.Server~~~~0.0.1.0') { throw 'State does not describe this setup.' }
$sshd = Join-Path $env:WINDIR 'System32\OpenSSH\sshd.exe'
$service = Get-CimInstance Win32_Service -Filter "Name='sshd'"
if ($service) {
    $owned = $service.PathName -eq $state.ImagePath
    $installerOnly = $state.InstallAttempted -and ($service.PathName.Trim('"') -ieq $sshd)
    if (-not ($owned -or $installerOnly)) { throw 'sshd has a different command; manual review required before rollback.' }
    Stop-Service sshd -ErrorAction Stop
    Set-Service sshd -StartupType Disabled
    & sc.exe delete sshd
    if ($LASTEXITCODE -ne 0) { throw 'Could not remove the service; firewall guards are retained.' }
}
foreach ($name in @('AstraDirectSSH-MacOnly-2222', 'OpenSSH-Server-In-TCP')) {
    if ($name -eq 'OpenSSH-Server-In-TCP' -and -not $state.InstallAttempted) { continue }
    if (Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue) { Remove-NetFirewallRule -Name $name }
}
$removalPending = $false
if ($state.CapabilityBefore -eq 'NotPresent' -and $state.InstallAttempted) {
    $current = Get-WindowsCapability -Online -Name $state.Capability
    if ($current.State -eq 'Installed') {
        $result = Remove-WindowsCapability -Online -Name $state.Capability
        if ($result.RestartNeeded) { $removalPending = $true }
    } elseif ($current.State -ne 'NotPresent') { $removalPending = $true }
    if ((Get-WindowsCapability -Online -Name $state.Capability).State -ne 'NotPresent') { $removalPending = $true }
}
if (Get-Process sshd -ErrorAction SilentlyContinue) { throw 'An sshd process remains; guard retained for inspection.' }
if (Get-CimInstance Win32_Service -Filter "Name='sshd'") { throw 'The service is still present or pending deletion; run rollback again after reviewing/restarting Windows.' }
if (-not $removalPending -and (Get-NetFirewallRule -Name 'AstraDirectSSH-InstallGuard' -ErrorAction SilentlyContinue)) { Remove-NetFirewallRule -Name 'AstraDirectSSH-InstallGuard' }
# Retain the audit record, remove only the host and access keys created here.
foreach ($name in @('authorized_keys', 'ssh_host_ed25519_key', 'ssh_host_ed25519_key.pub')) {
    $path = Join-Path $root $name
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path }
}
$state.Status = if ($removalPending) { 'Access removed - capability removal pending restart or inspection' } else { 'Rolled back' }
$state | Add-Member -NotePropertyName RolledBackUtc -NotePropertyValue ([DateTime]::UtcNow.ToString('o')) -Force
$temporary = $statePath + '.tmp'
$state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $temporary -Encoding UTF8
[IO.File]::Replace($temporary, $statePath, [NullString]::Value)
Write-Output "$($state.Status). Retained receipt/config: $root. Preexisting SSH files and Tailscale settings were not edited."
