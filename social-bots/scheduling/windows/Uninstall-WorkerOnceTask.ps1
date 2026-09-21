<#
.SYNOPSIS
    Removes the scheduled task created by Install-WorkerOnceTask.ps1.

.DESCRIPTION
    Idempotent: succeeds quietly if the task does not exist. Does not touch
    any durable evidence (heartbeat log, invocation receipts) -- those live
    under social-bots/worker-reports and $SBOTS_HOME regardless of whether
    the scheduled task is installed.

.PARAMETER TaskName
    Scheduled task name to remove. Default SocialBotsWorkerOnce.
#>
[CmdletBinding()]
param(
    [string]$TaskName = "SocialBotsWorkerOnce"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "No task named '$TaskName' is registered. Nothing to do."
    exit 0
}

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Host "Unregistered task '$TaskName'."
