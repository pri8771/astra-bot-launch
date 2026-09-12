#Requires -Version 5.1
#Requires -RunAsAdministrator
[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$PublicKeyPath)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:ProgramData 'AstraDirectSSH'
$statePath = Join-Path $root 'state.json'
$configPath = Join-Path $root 'sshd_config'
$keyPath = Join-Path $root 'authorized_keys'
$hostKeyPath = Join-Path $root 'ssh_host_ed25519_key'
$sshd = Join-Path $env:WINDIR 'System32\OpenSSH\sshd.exe'
$keygen = Join-Path $env:WINDIR 'System32\OpenSSH\ssh-keygen.exe'
$capability = 'OpenSSH.Server~~~~0.0.1.0'
$ruleName = 'AstraDirectSSH-MacOnly-2222'
$guardName = 'AstraDirectSSH-InstallGuard'
$defaultRule = 'OpenSSH-Server-In-TCP'
$windowsIP = '100.89.44.91'
$macIP = '100.124.207.87'
$accountName = 'Priyansh Chordia'
$imagePath = '"' + $sshd + '" -f "' + $configPath + '"'

function Save-State {
    $temporary = $statePath + '.tmp'
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $temporary -Encoding UTF8
    if (Test-Path -LiteralPath $statePath) { [IO.File]::Replace($temporary, $statePath, [NullString]::Value) }
    else { [IO.File]::Move($temporary, $statePath) }
}
function Invoke-Checked([string]$File, [string[]]$Arguments) {
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$File exited with code $LASTEXITCODE" }
}
function Protect-File([string]$Path, [switch]$UserRead) {
    $grants = @('*S-1-5-18:F', '*S-1-5-32-544:F')
    if ($UserRead) { $grants += "*$($user.SID.Value):R" }
    Invoke-Checked icacls.exe (@($Path, '/inheritance:r', '/grant:r') + $grants)
    Invoke-Checked icacls.exe @($Path, '/setowner', '*S-1-5-32-544')
}

# All checks below precede any mutation. Never adopt an existing sshd service.
if ($env:COMPUTERNAME -ine 'DESKTOP-H5S6H41') { throw 'Wrong Windows computer.' }
if (-not [Environment]::Is64BitProcess) { throw 'Use 64-bit Windows PowerShell.' }
if (Test-Path -LiteralPath $root) { throw "$root already exists; inspect or roll back before retrying." }
if (Get-Service sshd -ErrorAction SilentlyContinue) { throw 'An sshd service already exists; it will not be changed.' }
if (Get-Process sshd -ErrorAction SilentlyContinue) { throw 'An sshd process already exists; it will not be changed.' }
foreach ($name in @($ruleName, $guardName, $defaultRule)) {
    if (Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue) { throw "Existing firewall rule $name; inspect before continuing." }
}
if (Get-NetTCPConnection -State Listen -LocalPort 2222 -ErrorAction SilentlyContinue) { throw 'Port 2222 is in use.' }
$tailscale = Get-Service Tailscale
if ($tailscale.Status -ne 'Running') { throw 'Tailscale must already be running.' }
$ip = @(Get-NetIPAddress -AddressFamily IPv4 -IPAddress $windowsIP -ErrorAction SilentlyContinue)
if ($ip.Count -ne 1) { throw 'Expected Tailscale address is not assigned locally.' }
$adapter = Get-NetAdapter -InterfaceIndex $ip[0].InterfaceIndex
if ($adapter.InterfaceDescription -notmatch 'Tailscale') { throw 'Expected address is not on a Tailscale adapter.' }
if (@(Get-NetFirewallProfile -PolicyStore ActiveStore | Where-Object { -not $_.Enabled }).Count) {
    throw 'Windows Firewall must already be enabled for every profile; no profile settings will be changed.'
}
if (@(Get-NetFirewallProfile -PolicyStore ActiveStore | Where-Object { [string]$_.AllowLocalFirewallRules -eq 'False' }).Count) {
    throw 'Policy disables local firewall rules; a local setup cannot establish its firewall boundary.'
}
$user = Get-LocalUser -Name $accountName
if (-not $user.Enabled) { throw 'The existing Windows account is disabled.' }
$publicKey = (Get-Content -LiteralPath $PublicKeyPath -Raw).Trim()
if ($publicKey -notmatch '^ssh-ed25519 [A-Za-z0-9+/]+={0,2}(?: [^\r\n]*)?$') {
    throw 'Supply exactly one plain ssh-ed25519 PUBLIC key, without authorized_keys options.'
}
$publicKey = ($publicKey -split ' ', 3)[0..1] -join ' '
$before = Get-WindowsCapability -Online -Name $capability
if ($before.State -notin @('Installed', 'NotPresent')) { throw "Capability state $($before.State) requires inspection." }
if ($before.State -eq 'NotPresent' -and (Get-NetTCPConnection -State Listen -LocalPort 22 -ErrorAction SilentlyContinue)) {
    throw 'Another server listens on port 22. Windows installation could transiently broaden its firewall access; inspect separately.'
}
$adminSIDs = @(Get-LocalGroupMember -SID 'S-1-5-32-544' | ForEach-Object { $_.SID.Value })

New-Item -ItemType Directory -Path $root | Out-Null
Invoke-Checked icacls.exe @($root, '/inheritance:r', '/grant:r', '*S-1-5-18:(OI)(CI)F', '*S-1-5-32-544:(OI)(CI)F', "*$($user.SID.Value):(RX)")
$state = [ordered]@{
    Schema = 1; Computer = $env:COMPUTERNAME; CreatedUtc = [DateTime]::UtcNow.ToString('o')
    Root = $root; Capability = $capability; CapabilityBefore = [string]$before.State
    SshdBefore = 'Absent'; DefaultFirewallRuleBefore = 'Absent'; InstallAttempted = $false
    ServiceClaimed = $false; ImagePath = $imagePath; Account = $user.Name; AccountSID = $user.SID.Value
    AccountWasAdministrator = ($adminSIDs -contains $user.SID.Value)
    WindowsIP = $windowsIP; MacIP = $macIP; Port = 2222; Status = 'Preparing'
}
Save-State

try {
    # Cover the installer interval: Windows may create an enabled port-22 rule.
    # This block applies only to the native sshd binary, not another server on 22.
    New-NetFirewallRule -Name $guardName -DisplayName $guardName -Direction Inbound -Action Block -Program $sshd -Profile Any | Out-Null
    $activeGuard = @(Get-NetFirewallRule -PolicyStore ActiveStore -Name $guardName)
    if ($activeGuard.Count -ne 1 -or [string]$activeGuard[0].Enabled -ne 'True' -or [string]$activeGuard[0].PrimaryStatus -ne 'OK') {
        throw 'Installer guard is not healthy and enabled in the active firewall policy.'
    }
    if (Get-Service sshd -ErrorAction SilentlyContinue) { throw 'sshd appeared after preflight; refusing to adopt it.' }
    if ($before.State -eq 'NotPresent') {
        $state.InstallAttempted = $true; Save-State
        $result = Add-WindowsCapability -Online -Name $capability
        if (Get-NetFirewallRule -Name $defaultRule -ErrorAction SilentlyContinue) {
            Disable-NetFirewallRule -Name $defaultRule | Out-Null
        }
        if ($result.RestartNeeded) { throw 'Windows requests a restart; keep the guard, roll back, then reassess.' }
    }
    if (-not (Test-Path -LiteralPath $sshd)) { throw 'The official Windows sshd binary is missing.' }
    if (-not (Test-Path -LiteralPath $keygen)) { throw 'The official Windows ssh-keygen binary is missing.' }
    $installedService = Get-CimInstance Win32_Service -Filter "Name='sshd'"
    if ($installedService) {
        if (-not $state.InstallAttempted) { throw 'Unexpected preexisting sshd appeared; refusing to adopt it.' }
        if ($installedService.PathName.Trim('"') -ine $sshd -or $installedService.StartName -notin @('LocalSystem', 'LocalSystemAccount')) {
            throw 'The installer-created service does not match the expected native binary and LocalSystem identity.'
        }
        Stop-Service sshd -ErrorAction Stop
        Set-Service sshd -StartupType Disabled
    }
    if (Get-NetFirewallRule -Name $defaultRule -ErrorAction SilentlyContinue) {
        Disable-NetFirewallRule -Name $defaultRule | Out-Null
    }
    # A second key-level source restriction remains effective despite unrelated firewall rules.
    ('from="' + $macIP + '",no-agent-forwarding,no-port-forwarding,no-X11-forwarding ' + $publicKey) |
        Set-Content -LiteralPath $keyPath -Encoding ASCII
    Protect-File $keyPath -UserRead
    $keyFingerprint = (& $keygen -lf $keyPath 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'ssh-keygen rejected the supplied public key.' }
    # ArgumentList is a complete native argument string so the empty passphrase survives PS 5.1.
    $generated = Start-Process -FilePath $keygen -ArgumentList ('-q -t ed25519 -f "' + $hostKeyPath + '" -N ""') -Wait -PassThru -NoNewWindow
    if ($generated.ExitCode -ne 0) { throw 'Host-key generation failed.' }
    Protect-File $hostKeyPath
    # ssh-keygen adds an explicit creator ACE; /grant:r does not remove it.
    $creatorSID = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    if ($creatorSID -notin @('S-1-5-18', 'S-1-5-32-544')) {
        Invoke-Checked icacls.exe @($hostKeyPath, '/remove:g', ('*' + $creatorSID))
    }
    $hostKeyRules = (Get-Acl -LiteralPath $hostKeyPath).GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])
    if (@($hostKeyRules | Where-Object { $_.IdentityReference.Value -notin @('S-1-5-18', 'S-1-5-32-544') }).Count) {
        throw 'Host private key has an unexpected access entry; service will not be started.'
    }
    Protect-File ($hostKeyPath + '.pub')
    $config = @"
Port 2222
AddressFamily inet
ListenAddress $windowsIP
HostKey "$($hostKeyPath.Replace('\', '/'))"
AuthorizedKeysFile "$($keyPath.Replace('\', '/'))"
AllowUsers "$($accountName.ToLowerInvariant())@$macIP"
AuthenticationMethods publickey
PubkeyAuthentication yes
PasswordAuthentication no
DisableForwarding yes
AllowTcpForwarding no
AllowAgentForwarding no
GatewayPorts no
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30
LogLevel VERBOSE
Subsystem sftp sftp-server.exe
"@
    $config | Set-Content -LiteralPath $configPath -Encoding ASCII
    Protect-File $configPath
    Invoke-Checked $sshd @('-t', '-f', $configPath)
    $effective = & $sshd -T -f $configPath 2>&1
    if ($LASTEXITCODE -ne 0) { throw 'Could not validate effective sshd settings.' }
    $effective | Set-Content -LiteralPath (Join-Path $root 'effective-config.txt') -Encoding UTF8
    if ($installedService) {
        $changed = Invoke-CimMethod -InputObject $installedService -MethodName Change -Arguments @{ PathName = $imagePath; StartMode = 'Automatic'; ServiceDependencies = @('Tailscale') }
        if ($changed.ReturnValue -ne 0) { throw "Service configuration failed with code $($changed.ReturnValue)." }
    } else {
        New-Service -Name sshd -DisplayName 'OpenSSH SSH Server' -BinaryPathName $imagePath -StartupType Automatic -DependsOn Tailscale | Out-Null
    }
    $state.ServiceClaimed = $true; Save-State
    # Tailscale is a startup prerequisite. No existing Tailscale settings are changed.
    New-NetFirewallRule -Name $ruleName -DisplayName $ruleName -Direction Inbound -Action Allow -Protocol TCP -LocalPort 2222 -LocalAddress $windowsIP -RemoteAddress $macIP -InterfaceAlias $adapter.Name -Program $sshd -Profile Any | Out-Null
    $activeRule = @(Get-NetFirewallRule -PolicyStore ActiveStore -Name $ruleName)
    if ($activeRule.Count -ne 1 -or [string]$activeRule[0].Enabled -ne 'True' -or [string]$activeRule[0].PrimaryStatus -ne 'OK') {
        throw 'Scoped allow rule is not healthy and enabled in the active firewall policy.'
    }
    Start-Service sshd
    # Service Running can precede socket readiness; wait at most five seconds.
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        if (Get-NetTCPConnection -State Listen -LocalAddress $windowsIP -LocalPort 2222 -ErrorAction SilentlyContinue) { break }
        Start-Sleep -Milliseconds 250
    }
    $service = Get-CimInstance Win32_Service -Filter "Name='sshd'"
    $listeners = @(Get-NetTCPConnection -State Listen -OwningProcess $service.ProcessId -ErrorAction SilentlyContinue)
    if ($service.State -ne 'Running' -or $listeners.Count -ne 1 -or $listeners[0].LocalPort -ne 2222 -or $listeners[0].LocalAddress -ne $windowsIP) {
        throw 'Service did not listen exclusively on the expected Tailscale address and port.'
    }
    $hostFingerprint = (& $keygen -lf ($hostKeyPath + '.pub') 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read host-key fingerprint.' }
    $state['PublicKeyFingerprint'] = $keyFingerprint
    $state['HostKeyFingerprint'] = $hostFingerprint
    $state['ConfigSHA256'] = (Get-FileHash -LiteralPath $configPath -Algorithm SHA256).Hash
    $state.Status = 'Listening - Mac authentication still requires verification'; Save-State
    # The service stays inaccessible until every local check above has passed.
    Remove-NetFirewallRule -Name $guardName
    Write-Output "READY for Mac verification: $windowsIP port 2222; account $($user.Name)"
    Write-Output "HOST KEY: $hostFingerprint"
    Write-Output "Evidence: $statePath"
    Write-Output "Existing administrator membership: $($state.AccountWasAdministrator) (unchanged)"
} catch {
    $failure = $_
    # Containment precedes receipt writes, including when the original error was disk I/O.
    try {
        $current = Get-CimInstance Win32_Service -Filter "Name='sshd'"
        if ($current -and (($current.PathName -eq $imagePath) -or ($state.InstallAttempted -and $current.PathName.Trim('"') -ieq $sshd))) {
            Stop-Service sshd -ErrorAction Stop
            Set-Service sshd -StartupType Disabled -ErrorAction Stop
        }
    } catch { Write-Warning "Service containment needs inspection: $($_.Exception.Message)" }
    foreach ($name in @($ruleName, $defaultRule)) {
        if ($name -eq $defaultRule -and -not $state.InstallAttempted) { continue }
        try {
            if (Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue) { Disable-NetFirewallRule -Name $name | Out-Null }
        } catch { Write-Warning "Firewall containment needs inspection for ${name}: $($_.Exception.Message)" }
    }
    $state.Status = 'Failed - inspect service and retained firewall guard'; $state['Failure'] = $failure.Exception.Message
    try { Save-State } catch { Write-Warning "Could not persist failure receipt: $($_.Exception.Message)" }
    throw $failure
}
