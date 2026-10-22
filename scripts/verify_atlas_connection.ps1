param([string]$Output = ('var/atlas-verification-' + (Get-Date -Format 'yyyyMMdd-HHmmss')))
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& '.venv/Scripts/python.exe' scripts/verify_mongodb_deployment.py atlas --output $Output
exit $LASTEXITCODE
