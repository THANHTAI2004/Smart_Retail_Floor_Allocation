param([string]$Output = ('var/windows-long-path-' + (Get-Date -Format 'yyyyMMdd-HHmmss')))
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& '.venv/Scripts/python.exe' scripts/verify_windows_long_path.py --output $Output
exit $LASTEXITCODE
