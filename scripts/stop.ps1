$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$statePath = Join-Path $projectRoot 'var/services.json'
if (-not (Test-Path -LiteralPath $statePath)) { Write-Output 'No recorded services'; exit }
$services = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
foreach ($service in $services) {
    $process = Get-Process -Id $service.pid -ErrorAction SilentlyContinue
    if ($process -and $process.StartTime.ToUniversalTime().ToString('o') -eq $service.start) {
        # Kill only the recorded service and its owned children (including an active job).
        & taskkill.exe /PID $service.pid /T /F | Out-Null
    }
}
Remove-Item -LiteralPath $statePath
Write-Output 'Recorded Smart Retail services stopped'
