param([switch]$InstallPortable)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$runtime = Join-Path $projectRoot 'var/tools/mongodb-8.0.16'
$executable = Join-Path $runtime 'mongod.exe'
if (-not (Test-Path -LiteralPath $executable)) {
    if (-not $InstallPortable) { throw 'No portable MongoDB. Use -InstallPortable or configure an external MONGODB_URI.' }
    New-Item -ItemType Directory -Path var/tools -Force | Out-Null
    $archive = Join-Path $projectRoot 'var/tools/mongodb-8.0.16.zip'
    if (-not (Test-Path -LiteralPath $archive)) {
        & curl.exe -L --fail -o $archive https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.0.16.zip
        if ($LASTEXITCODE -ne 0) { throw 'MongoDB download failed' }
    }
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne '34eb6795860e29bdf8e5cc9cb4cbba2c73295a25c60204667029d5f3614fe807') { throw 'MongoDB archive SHA-256 mismatch' }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    New-Item -ItemType Directory -Path $runtime | Out-Null
    $zip = [IO.Compression.ZipFile]::OpenRead($archive)
    try {
        foreach ($entry in $zip.Entries) {
            if ($entry.FullName -match '/bin/mongod.exe$') {
                [IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$executable,$false)
            }
        }
    } finally { $zip.Dispose() }
}
if (Get-NetTCPConnection -State Listen -LocalPort 27017 -ErrorAction SilentlyContinue) {
    & '.venv/Scripts/python.exe' -m smart_retail.infrastructure.mongodb.health
    if ($LASTEXITCODE -ne 0) { throw 'Port 27017 is occupied by an unverified MongoDB instance' }
    return
}
New-Item -ItemType Directory -Path var/mongodb/data,var/logs -Force | Out-Null
$owned = Start-Process -FilePath $executable -ArgumentList @('--dbpath',(Join-Path $projectRoot 'var/mongodb/data'),'--bind_ip','127.0.0.1','--port','27017','--auth','--logpath',(Join-Path $projectRoot 'var/logs/mongod.log'),'--logappend') -WindowStyle Hidden -PassThru
@{pid=$owned.Id;start=$owned.StartTime.ToUniversalTime().ToString('o');port=27017;version='8.0.16'} | ConvertTo-Json | Set-Content -LiteralPath 'var/mongodb/process.json' -Encoding UTF8
@'
from pathlib import Path
import json,secrets
from pymongo import MongoClient
private=Path('var/mongodb/private.json')
if not private.exists():
    client=MongoClient('mongodb://127.0.0.1:27017',serverSelectionTimeoutMS=10000)
    client.admin.command('ping')
    password=secrets.token_urlsafe(36)
    client.admin.command('createUser','smart_retail_local',pwd=password,roles=[{'role':'root','db':'admin'}])
    private.write_text(json.dumps({'uri':'mongodb://smart_retail_local:'+password+'@127.0.0.1:27017/?authSource=admin'}),encoding='utf-8')
    client.close()
print('Local MongoDB ready; credentials remain in ignored var/mongodb/private.json')
'@ | & '.venv/Scripts/python.exe' -
if ($LASTEXITCODE -ne 0) { throw 'MongoDB authentication bootstrap failed; inspect local log without publishing credentials' }
& '.venv/Scripts/python.exe' -m smart_retail.infrastructure.mongodb.health
if ($LASTEXITCODE -ne 0) { throw 'MongoDB connection check failed' }
