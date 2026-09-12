#Requires -Version 5.1
#Requires -RunAsAdministrator
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:ProgramData 'AstraDirectSSH'
$statePath = Join-Path $root 'state.json'
$hostKey = Join-Path $root 'ssh_host_ed25519_key'
$config = Join-Path $root 'sshd_config'
$sshd = Join-Path $env:WINDIR 'System32\OpenSSH\sshd.exe'
$keygen = Join-Path $env:WINDIR 'System32\OpenSSH\ssh-keygen.exe'
$expectedImage = '"' + $sshd + '" -f "' + $config + '"'
$guard = 'AstraDirectSSH-InstallGuard'
$allow = 'AstraDirectSSH-MacOnly-2222'
$windowsIP = '100.89.44.91'
$macIP = '100.124.207.87'
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$sidType = [Security.Principal.SecurityIdentifier]

function Write-AtomicJson($Value, [string]$Path) {
    $temporary = $Path + '.tmp'
    $Value | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $temporary -Encoding UTF8
    if (Test-Path -LiteralPath $Path) { [IO.File]::Replace($temporary, $Path, [NullString]::Value) }
    else { [IO.File]::Move($temporary, $Path) }
}
function Assert-Listener {
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        if (Get-NetTCPConnection -State Listen -LocalAddress $windowsIP -LocalPort 2222 -ErrorAction SilentlyContinue) { break }
        Start-Sleep -Milliseconds 250
    }
    $current = Get-CimInstance Win32_Service -Filter "Name='sshd'"
    if ($current.State -ne 'Running' -or $current.ProcessId -eq 0) { throw 'Owned service is not running.' }
    $listeners = @(Get-NetTCPConnection -State Listen -OwningProcess $current.ProcessId -ErrorAction SilentlyContinue)
    if ($listeners.Count -ne 1 -or $listeners[0].LocalAddress -ne $windowsIP -or $listeners[0].LocalPort -ne 2222) {
        throw 'Owned service does not listen exclusively on the expected address and port.'
    }
}
function Other-AccessRules($Acl) {
    @($Acl.GetAccessRules($true, $true, $sidType) | Where-Object { $_.IdentityReference.Value -ne $state.AccountSID } |
        ForEach-Object { "$($_.IdentityReference.Value)|$($_.AccessControlType)|$($_.FileSystemRights)|$($_.InheritanceFlags)|$($_.PropagationFlags)|$($_.IsInherited)" } | Sort-Object) -join "`n"
}

# No mutation until the recorded service, user, keys, and firewall boundary agree.
if ($env:COMPUTERNAME -ine 'DESKTOP-H5S6H41' -or -not [Environment]::Is64BitProcess -or
    $state.Schema -ne 1 -or $state.Computer -ine $env:COMPUTERNAME -or $state.Root -ine $root -or
    $state.SshdBefore -ne 'Absent' -or -not $state.ServiceClaimed -or $state.ImagePath -ne $expectedImage -or
    $state.WindowsIP -ne $windowsIP -or $state.MacIP -ne $macIP -or $state.Port -ne 2222) { throw 'Setup ownership/state does not match this repair.' }
$user = Get-LocalUser -Name 'Priyansh Chordia'
if ($user.SID.Value -ne $state.AccountSID -or [Security.Principal.WindowsIdentity]::GetCurrent().User.Value -ne $state.AccountSID) {
    throw 'Run elevated as the same recorded local user; no other SID will be removed.'
}
$service = Get-CimInstance Win32_Service -Filter "Name='sshd'"
if (-not $service -or $service.PathName -ne $expectedImage -or $service.StartName -ne 'LocalSystem' -or $service.State -ne 'Stopped') {
    throw 'Expected owned LocalSystem service must be stopped with its original command.'
}
foreach ($path in @($root, $hostKey, $config, $statePath)) {
    if ((Get-Item -LiteralPath $path).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing a reparse point: $path" }
}
$guardRule = @(Get-NetFirewallRule -PolicyStore ActiveStore -Name $guard)
if ($guardRule.Count -ne 1 -or [string]$guardRule[0].Enabled -ne 'True' -or [string]$guardRule[0].PrimaryStatus -ne 'OK' -or
    [string]$guardRule[0].Action -ne 'Block' -or [string]$guardRule[0].Direction -ne 'Inbound' -or
    ($guardRule[0] | Get-NetFirewallApplicationFilter).Program -ine $sshd) { throw 'Expected active native-sshd guard is missing.' }
$allowRule = Get-NetFirewallRule -PolicyStore ActiveStore -Name $allow
$ports = $allowRule | Get-NetFirewallPortFilter
$addresses = $allowRule | Get-NetFirewallAddressFilter
if ([string]$allowRule.Action -ne 'Allow' -or [string]$allowRule.Direction -ne 'Inbound' -or [string]$allowRule.Enabled -ne 'False' -or [string]$allowRule.PrimaryStatus -ne 'Inactive' -or
    [string]$ports.Protocol -ne 'TCP' -or [string]$ports.LocalPort -ne '2222' -or
    (@($addresses.LocalAddress) -join ',') -ne $windowsIP -or (@($addresses.RemoteAddress) -join ',') -ne $macIP -or
    ($allowRule | Get-NetFirewallApplicationFilter).Program -ine $sshd) { throw 'Scoped allow rule differs from the recorded setup.' }
if ((Get-Service Tailscale).Status -ne 'Running' -or -not (Get-NetIPAddress -AddressFamily IPv4 -IPAddress $windowsIP -ErrorAction SilentlyContinue)) { throw 'Expected Tailscale address is not ready.' }
if (Get-NetTCPConnection -State Listen -LocalPort 2222 -ErrorAction SilentlyContinue) { throw 'Port 2222 is occupied.' }
$acl = Get-Acl -LiteralPath $hostKey
$ownerBefore = $acl.GetOwner($sidType).Value
if ($ownerBefore -notin @('S-1-5-18', 'S-1-5-32-544')) { throw 'Unexpected private-key owner; owner will not be changed.' }
$rules = @($acl.GetAccessRules($true, $true, $sidType))
if (@($rules | Where-Object { $_.IdentityReference.Value -notin @('S-1-5-18', 'S-1-5-32-544', $state.AccountSID) }).Count) { throw 'Unexpected private-key ACE; inspect without modifying it.' }
foreach ($trustedSID in @('S-1-5-18', 'S-1-5-32-544')) {
    if (-not @($rules | Where-Object { $_.IdentityReference.Value -eq $trustedSID -and [string]$_.AccessControlType -eq 'Allow' -and ($_.FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -eq [Security.AccessControl.FileSystemRights]::FullControl }).Count) { throw 'SYSTEM/Administrators full-control entry is missing.' }
}
$extra = @($rules | Where-Object { $_.IdentityReference.Value -eq $state.AccountSID })
if (@($extra | Where-Object { $_.IsInherited -or [string]$_.AccessControlType -ne 'Allow' }).Count) { throw 'User permission is not the expected explicit allow ACE.' }
$bytesBefore = (Get-FileHash -LiteralPath $hostKey -Algorithm SHA256).Hash
$otherRulesBefore = Other-AccessRules $acl
$protectedBefore = $acl.AreAccessRulesProtected
$configHash = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
# Failed setup had not yet persisted its hash. Require its exact approved settings.
$approvedConfig = @(
    'Port 2222', 'AddressFamily inet', "ListenAddress $windowsIP",
    ('HostKey "' + $hostKey.Replace('\', '/') + '"'),
    ('AuthorizedKeysFile "' + (Join-Path $root 'authorized_keys').Replace('\', '/') + '"'),
    ('AllowUsers "priyansh chordia@' + $macIP + '"'),
    'AuthenticationMethods publickey', 'PubkeyAuthentication yes', 'PasswordAuthentication no',
    'DisableForwarding yes', 'AllowTcpForwarding no', 'AllowAgentForwarding no', 'GatewayPorts no',
    'PermitEmptyPasswords no', 'MaxAuthTries 3', 'LoginGraceTime 30', 'LogLevel VERBOSE', 'Subsystem sftp sftp-server.exe'
) -join "`n"
if ((Get-Content -LiteralPath $config -Raw).Replace("`r`n", "`n").Trim() -cne $approvedConfig) { throw 'Configuration differs from the approved setup; inspect without enabling access.' }
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')
$receiptPath = Join-Path $root ("repair-hostkey-$stamp.json")
$receipt = [ordered]@{ StartedUtc = [DateTime]::UtcNow.ToString('o'); Status = 'Prepared'; AccountSID = $state.AccountSID; OwnerBefore = $ownerBefore; RemovedExplicitACEs = $extra.Count; OriginalImagePath = $expectedImage; OriginalACL = $acl.Sddl }
Write-AtomicJson $receipt $receiptPath

try {
    foreach ($entry in $extra) { $acl.RemoveAccessRuleSpecific($entry) }
    if ($extra.Count) { Set-Acl -LiteralPath $hostKey -AclObject $acl }
    $after = Get-Acl -LiteralPath $hostKey
    if ($after.GetOwner($sidType).Value -ne $ownerBefore -or (Other-AccessRules $after) -ne $otherRulesBefore -or
        $after.AreAccessRulesProtected -ne $protectedBefore -or
        @($after.GetAccessRules($true, $true, $sidType) | Where-Object { $_.IdentityReference.Value -eq $state.AccountSID }).Count -ne 0 -or
        (Get-FileHash -LiteralPath $hostKey -Algorithm SHA256).Hash -ne $bytesBefore) { throw 'Permission repair did not preserve the expected key/owner/other permissions.' }
    & $sshd -t -f $config
    if ($LASTEXITCODE -ne 0) { throw 'sshd configuration validation failed.' }
    $receipt.Status = 'ACL repaired; service verification pending'; Write-AtomicJson $receipt $receiptPath
    Set-Service sshd -StartupType Automatic
    Start-Service sshd
    Assert-Listener
    if ((Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash -ne $configHash) { throw 'Configuration changed during repair.' }
    $fingerprint = (& $keygen -lf ($hostKey + '.pub') 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read the host public-key fingerprint.' }
    Enable-NetFirewallRule -Name $allow | Out-Null
    $enabledRule = Get-NetFirewallRule -PolicyStore ActiveStore -Name $allow
    if ([string]$enabledRule.Enabled -ne 'True' -or [string]$enabledRule.PrimaryStatus -ne 'OK') { throw 'Scoped allow rule did not become healthy and active.' }
    $receipt.Status = 'Local repair verified; Mac authentication pending'; $receipt['HostKeyBytesUnchanged'] = $true; $receipt['HostKeyFingerprint'] = $fingerprint
    Write-AtomicJson $receipt $receiptPath
    $state.Status = 'Listening - Mac authentication still requires verification'
    $state | Add-Member -NotePropertyName HostKeyFingerprint -NotePropertyValue $fingerprint -Force
    $state | Add-Member -NotePropertyName ConfigSHA256 -NotePropertyValue $configHash -Force
    $state | Add-Member -NotePropertyName HostKeyACLRepairReceipt -NotePropertyValue $receiptPath -Force
    Write-AtomicJson $state $statePath
    Remove-NetFirewallRule -Name $guard
    Write-Output "READY for Mac authentication: $windowsIP port 2222"
    Write-Output "HOST KEY: $fingerprint"
    Write-Output "Repair receipt: $receiptPath"
} catch {
    $failure = $_
    try { Set-Service sshd -StartupType Disabled; Stop-Service sshd -ErrorAction Stop } catch { Write-Warning "Inspect service containment: $($_.Exception.Message)" }
    try { Disable-NetFirewallRule -Name $allow | Out-Null } catch { Write-Warning "Inspect allow-rule containment: $($_.Exception.Message)" }
    $receipt.Status = 'Failed - guard retained; inspect service'; $receipt['Failure'] = $failure.Exception.Message
    try { Write-AtomicJson $receipt $receiptPath } catch { Write-Warning 'Could not save the repair failure receipt.' }
    Write-Warning 'Service command was not changed. Inspect OpenSSH event logs if startup still fails; the firewall guard remains.'
    throw $failure
}
