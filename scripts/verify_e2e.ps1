$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$runRoot = Join-Path $projectRoot ('var/e2e-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (Test-Path -LiteralPath $runRoot) { throw 'Verification directory already exists' }
foreach ($port in 8011,5174) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) { throw "Verification port $port is occupied" }
}
New-Item -ItemType Directory -Path $runRoot | Out-Null
$envNames = @('SMART_RETAIL_DATABASE_URL','SMART_RETAIL_ARTIFACTS','SMART_RETAIL_API_URL','SMART_RETAIL_E2E_URL','SMART_RETAIL_E2E_OUTPUT')
$savedEnvironment = @{}
foreach ($envName in $envNames) { $savedEnvironment[$envName] = [Environment]::GetEnvironmentVariable($envName,'Process') }
$processes = @()
try {
    $env:SMART_RETAIL_DATABASE_URL = 'sqlite:///' + (Join-Path $runRoot 'e2e.db').Replace('\','/')
    $env:SMART_RETAIL_ARTIFACTS = Join-Path $runRoot 'artifacts'
    $env:SMART_RETAIL_API_URL = 'http://127.0.0.1:8011'
    $env:SMART_RETAIL_E2E_URL = 'http://127.0.0.1:5174'
    $env:SMART_RETAIL_E2E_OUTPUT = (Join-Path $runRoot 'browser').Replace('\','/')
    $pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
    & $pythonPath -m alembic -c backend/alembic.ini upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Migration failed' }
    $processes += Start-Process $pythonPath -ArgumentList @('-m','uvicorn','smart_retail.api.main:app','--host','127.0.0.1','--port','8011') -WindowStyle Hidden -WorkingDirectory $projectRoot -RedirectStandardOutput (Join-Path $runRoot 'api.out.log') -RedirectStandardError (Join-Path $runRoot 'api.err.log') -PassThru
    $processes += Start-Process $pythonPath -ArgumentList @('-m','smart_retail.workers.runner') -WindowStyle Hidden -WorkingDirectory $projectRoot -RedirectStandardOutput (Join-Path $runRoot 'worker.out.log') -RedirectStandardError (Join-Path $runRoot 'worker.err.log') -PassThru
    $vitePath = Join-Path $projectRoot 'frontend/node_modules/vite/bin/vite.js'
    $processes += Start-Process (Get-Command node.exe).Source -ArgumentList @($vitePath,'--host','127.0.0.1','--port','5174','--strictPort') -WindowStyle Hidden -WorkingDirectory (Join-Path $projectRoot 'frontend') -RedirectStandardOutput (Join-Path $runRoot 'web.out.log') -RedirectStandardError (Join-Path $runRoot 'web.err.log') -PassThru
    $healthy = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        Start-Sleep -Milliseconds 500
        try {
            $health = Invoke-RestMethod 'http://127.0.0.1:8011/api/health'
            $response = Invoke-WebRequest 'http://127.0.0.1:5174' -UseBasicParsing
            if ($health.worker_online -and $response.StatusCode -eq 200) { $healthy = $true; break }
        } catch {}
    }
    if (-not $healthy) { throw 'Verification services did not become healthy' }
    $health | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $runRoot 'health.json') -Encoding UTF8
    Push-Location frontend
    try {
        & npm.cmd run test:e2e
        if ($LASTEXITCODE -ne 0) { throw 'Playwright failed; inspect the isolated browser report' }
    } finally { Pop-Location }
    Write-Output "E2E evidence: $runRoot"
} finally {
    foreach ($ownedProcess in $processes) {
        $liveProcess = Get-Process -Id $ownedProcess.Id -ErrorAction SilentlyContinue
        if ($liveProcess -and $liveProcess.StartTime -eq $ownedProcess.StartTime) { & taskkill.exe /PID $ownedProcess.Id /T /F | Out-Null }
    }
    foreach ($envName in $envNames) { [Environment]::SetEnvironmentVariable($envName,$savedEnvironment[$envName],'Process') }
}
