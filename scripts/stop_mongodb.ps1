$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath 'var/mongodb/process.json')) { throw 'No recorded local MongoDB process; external deployments are not stopped' }
$owned = Get-Content -LiteralPath 'var/mongodb/process.json' -Raw | ConvertFrom-Json
$live = Get-Process -Id $owned.pid -ErrorAction SilentlyContinue
if (-not $live) { Write-Output 'Recorded MongoDB process is already stopped'; return }
if ([Math]::Abs(($live.StartTime.ToUniversalTime() - ([datetimeoffset]::Parse($owned.start)).UtcDateTime).TotalSeconds) -gt 1) { throw 'Recorded MongoDB PID was reused; refusing shutdown' }
@'
from pymongo.errors import AutoReconnect
from smart_retail.infrastructure.mongodb.client import connect
owner,_=connect()
try:
    owner.client.admin.command('shutdown',force=False)
except AutoReconnect:
    pass
finally:
    owner.dispose()
print('Owned local MongoDB shutdown requested; persistent files preserved')
'@ | & '.venv/Scripts/python.exe' -
if ($LASTEXITCODE -ne 0) { throw 'MongoDB graceful shutdown failed' }
$live.WaitForExit(15000) | Out-Null
