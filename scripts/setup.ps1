$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { python -m venv .venv }
& '.venv\Scripts\python.exe' -m pip install -r backend/requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependencies failed' }
& '.venv\Scripts\python.exe' -m pip install -e backend --no-deps
if ($LASTEXITCODE -ne 0) { throw 'Backend install failed' }
New-Item -ItemType Directory -Path var -Force | Out-Null
& '.venv\Scripts\python.exe' -m alembic -c backend/alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Migration failed' }
Push-Location frontend
try { npm ci; if ($LASTEXITCODE -ne 0) { throw 'Frontend install failed' } } finally { Pop-Location }
