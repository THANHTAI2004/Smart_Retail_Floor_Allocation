$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
New-Item -ItemType Directory -Path var/logs -Force | Out-Null
if (Test-Path -LiteralPath 'var/services.json') {
    $previous = Get-Content -LiteralPath 'var/services.json' -Raw | ConvertFrom-Json
    $live = @($previous | Where-Object { Get-Process -Id $_.pid -ErrorAction SilentlyContinue })
    if ($live.Count -gt 0) { throw 'Recorded services are still running. Use scripts/stop.ps1 first.' }
}
foreach ($port in 8010,5173) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) { throw "Port $port is occupied" }
}
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
& $pythonPath -m alembic -c backend/alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Migration failed' }
$services = @()
try {
    $apiProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m','uvicorn','smart_retail.api.main:app','--host','127.0.0.1','--port','8010') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput 'var/logs/api.out.log' -RedirectStandardError 'var/logs/api.err.log' -PassThru
    $services += @{name='api';pid=$apiProcess.Id;start=$apiProcess.StartTime.ToUniversalTime().ToString('o')}
    $workerProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m','smart_retail.workers.runner') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput 'var/logs/worker.out.log' -RedirectStandardError 'var/logs/worker.err.log' -PassThru
    $services += @{name='worker';pid=$workerProcess.Id;start=$workerProcess.StartTime.ToUniversalTime().ToString('o')}
    $nodePath = (Get-Command node.exe).Source
    $vitePath = Join-Path $projectRoot 'frontend/node_modules/vite/bin/vite.js'
    $webProcess = Start-Process -FilePath $nodePath -ArgumentList @($vitePath,'--host','127.0.0.1','--port','5173','--strictPort') -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectRoot 'var/logs/frontend.out.log') -RedirectStandardError (Join-Path $projectRoot 'var/logs/frontend.err.log') -PassThru
    $services += @{name='frontend';pid=$webProcess.Id;start=$webProcess.StartTime.ToUniversalTime().ToString('o')}
    $services | ConvertTo-Json | Set-Content -LiteralPath 'var/services.json' -Encoding UTF8
    $healthy = $false
    for ($attempt=0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Milliseconds 500
        try { $health = Invoke-RestMethod 'http://127.0.0.1:8010/api/health'; $web = Invoke-WebRequest 'http://127.0.0.1:5173' -UseBasicParsing; if ($health.worker_online -and $web.StatusCode -eq 200) { $healthy=$true; break } } catch {}
    }
    if (-not $healthy) { throw 'Services did not become healthy. Inspect var/logs.' }
    Write-Output 'Smart Retail ready: http://127.0.0.1:5173'
} catch {
    foreach ($service in $services) { Stop-Process -Id $service.pid -ErrorAction SilentlyContinue }
    throw
}
