<#
.SYNOPSIS
    Registers a Windows Task Scheduler task that runs bin/worker_once.py
    once per firing, on a repeating interval.

.DESCRIPTION
    SB-V07-001 authorized-host installer. This substitutes the placeholder
    tokens in SocialBotsWorkerOnce.xml (__PYTHON_EXE__, __REPO_ROOT__,
    __LANE__, __BRANCH__, __USER_ID__, __INTERVAL_MINUTES__,
    __SBOTS_HOME__) with real values, then registers the result with
    Register-ScheduledTask.

    Idempotent: an existing task with the same -TaskName is unregistered
    first, so re-running this script updates the task in place instead of
    creating a duplicate.

    Registering the task does not, by itself, prove a worker ever ran. See
    ..\README.md (Honesty boundary) and ..\RUNBOOK.md for how to verify a
    real invocation happened.

.PARAMETER RepoRoot
    Path to the git checkout root (the directory that contains the
    social-bots\ subdirectory). Not the social-bots directory itself.

.PARAMETER Lane
    Worker lane, e.g. windows-core.

.PARAMETER Branch
    Branch worker_once.py should work against.

.PARAMETER IntervalMinutes
    Minutes between firings. Default 30.

.PARAMETER PythonExe
    Path to python.exe. Default: resolved via Get-Command python.

.PARAMETER SbotsHome
    Runtime data root (leases, receipts, invocation records). Default:
    <RepoRoot>\social-bots. Task Scheduler XML cannot set environment
    variables, so this is passed to worker_once.py as --home instead of as
    SBOTS_HOME; the systemd and launchd units set the env var directly.

.PARAMETER TaskName
    Scheduled task name. Default SocialBotsWorkerOnce.

.EXAMPLE
    .\Install-WorkerOnceTask.ps1 -RepoRoot C:\code\astra-bot-launch `
        -Lane windows-core -Branch claude/windows-core-host
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$Lane,
    [Parameter(Mandatory = $true)][string]$Branch,
    [int]$IntervalMinutes = 30,
    [string]$PythonExe,
    [string]$SbotsHome,
    [string]$TaskName = "SocialBotsWorkerOnce"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- Resolve and validate inputs before touching the scheduler. ---

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$entrypoint = Join-Path $RepoRoot "social-bots\bin\worker_once.py"
if (-not (Test-Path -LiteralPath $entrypoint)) {
    throw "Entrypoint not found at '$entrypoint'. -RepoRoot must be the git checkout root (it must contain social-bots\bin\worker_once.py)."
}

if (-not $PythonExe) {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "No -PythonExe given and 'python' was not found on PATH. Pass an explicit interpreter path."
    }
    $PythonExe = $cmd.Source
}
if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "PythonExe '$PythonExe' does not exist."
}

if ($IntervalMinutes -lt 1) {
    throw "-IntervalMinutes must be a positive integer."
}

if (-not $SbotsHome) {
    $SbotsHome = Join-Path $RepoRoot "social-bots"
}
# Created here rather than left to the first firing, so a bad path fails at
# install time instead of silently in a scheduled run nobody is watching.
if (-not (Test-Path -LiteralPath $SbotsHome)) {
    New-Item -ItemType Directory -Path $SbotsHome -Force | Out-Null
}
$SbotsHome = (Resolve-Path -LiteralPath $SbotsHome).Path

$userId = "$env:USERDOMAIN\$env:USERNAME"

# --- Build the task XML from the template. ---

$templatePath = Join-Path $PSScriptRoot "SocialBotsWorkerOnce.xml"
if (-not (Test-Path -LiteralPath $templatePath)) {
    throw "Template not found: $templatePath"
}

$xml = Get-Content -LiteralPath $templatePath -Raw
$xml = $xml.Replace("__PYTHON_EXE__", $PythonExe)
$xml = $xml.Replace("__REPO_ROOT__", $RepoRoot)
$xml = $xml.Replace("__LANE__", $Lane)
$xml = $xml.Replace("__BRANCH__", $Branch)
$xml = $xml.Replace("__USER_ID__", $userId)
$xml = $xml.Replace("__INTERVAL_MINUTES__", [string]$IntervalMinutes)
$xml = $xml.Replace("__SBOTS_HOME__", $SbotsHome)

$tempXmlPath = Join-Path ([System.IO.Path]::GetTempPath()) "$TaskName.xml"
Set-Content -LiteralPath $tempXmlPath -Value $xml -Encoding UTF8

# --- Idempotent (re)registration. Never store credentials: the task runs ---
# --- as the interactive user via InteractiveToken logon, no password.    ---

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Unregistering existing task '$TaskName' before reinstall."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$resolvedXml = Get-Content -LiteralPath $tempXmlPath -Raw
$registered = Register-ScheduledTask -TaskName $TaskName -Xml $resolvedXml -User $userId

Write-Host "Registered task:"
$registered | Format-List TaskName, State

Write-Host "Runtime data root (--home): $SbotsHome"
Write-Host "Inspect run history with:"
Write-Host "  Get-ScheduledTaskInfo -TaskName $TaskName"
Write-Host "See ..\RUNBOOK.md to verify a real invocation happened (heartbeat log + invocation receipt growth), not just that this task is registered."

Remove-Item -LiteralPath $tempXmlPath -ErrorAction SilentlyContinue
