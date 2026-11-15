# Vai trò: Chạy quy trình xác minh stack MongoDB qua Compose và ghi kết quả vào đích kiểm tra riêng.
param([string]$Output = ('var/compose-verification-' + (Get-Date -Format 'yyyyMMdd-HHmmss')))
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& '.venv/Scripts/python.exe' scripts/verify_mongodb_deployment.py compose --output $Output
exit $LASTEXITCODE
