# MongoDB operations and migration

The main API, durable queue and experiment worker use synchronous PyMongo.
No SQL persistence adapter, driver or importer remains in the project.
Engines and domain objects have no database dependency.

## Verified local Windows environment

MongoDB Community Server 8.0.16 runs as a private, owned process with authentication,
bound to 127.0.0.1:27017. Its persistent directory is `var/mongodb/data`.
The portable archive was verified against its published SHA-256:
`34eb6795860e29bdf8e5cc9cb4cbba2c73295a25c60204667029d5f3614fe807`.
Nothing was installed as a Windows service. Do not remove `var/mongodb` when
cleaning generated files: it now contains the primary database and private keys.

```powershell
# Existing checkout: credentials are already in ignored var/mongodb/private.json.
powershell -ExecutionPolicy Bypass -File scripts/start_mongodb.ps1
.venv/Scripts/python.exe -m smart_retail.infrastructure.mongodb.health --cutover-check
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
# Stop only the recorded application processes; retain the MongoDB process.
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1
# For maintenance, stop the owned local MongoDB process as well.
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1 -StopMongoDB
```

On a new Windows checkout, create `.venv`, install `backend/requirements-lock.txt`
and `pip install -e backend --no-deps`, then run
`scripts/start_mongodb.ps1 -InstallPortable` and `scripts/setup.ps1`.
The helper downloads the pinned official Windows archive and checks its hash.
Credentials are randomly generated and stored only in ignored
`var/mongodb/private.json`; treat that file as private. The current local helper
user has admin rights so isolated integration databases and restart tests work.
Use a deployment-specific restricted account for shared deployments.

For an independently managed server or Atlas, supply `MONGODB_URI` privately and
`MONGODB_DATABASE`. A `mongodb+srv` URI uses native PyMongo DNS/TLS support;
Atlas connectivity has not been exercised here. `SMART_RETAIL_ARTIFACTS` controls
filesystem run artifacts. The Windows scripts do not load `.env` automatically:
set environment variables in the shell or service manager. An explicit URI takes
precedence over the local private-file fallback. Never copy an authenticated URI
into source, screenshots or evidence.

## Existing data and deployment receipts

Main data uses `smart_retail`. Historical SQL campaign rows were decoded and
checksummed into `smart_retail_history` before removing in-checkout SQL files.
The 34 archived databases have table counts, source hashes and MongoDB readback
checks. This archive is separate from the live queue. Scientific JSON remains.
Windows startup validates an existing cutover receipt against MongoDB metadata;
it no longer requires or inspects any SQL file. There is no SQL import command
or fallback. Use native BSON backup/restore for current recovery operations.

## Persistence semantics

Projects embed seven validated input groups and revision. A single-document
compare-and-swap publishes the entire aggregate, incrementing revision once.
Invalid references produce 422, missing projects 404, stale revision 409.
Project BSON aggregates are capped at 8 MiB with an explicit 413 response.

Runs preserve their immutable snapshot. Claims atomically select the oldest
QUEUED job, attach a unique lease token and expire after 30 seconds unless renewed.
Every worker publication checks worker ID, original token, active status and
unexpired lease. An old owner cannot publish using a newly read owner's record.
A final cancellation wins the publication race. Expired RUNNING work becomes
TIMED_OUT/WORKER_LOST; expired cancellation becomes CANCELLED. Recovery does not
silently enqueue the same ID again. Retry creates a new run under the normal
replay/source identity checks. There are no TTL indexes on research data.

Large snapshot/result JSON, or values outside BSON int64, use checksummed GridFS
payloads. Parent documents reference only a completely published blob. JSON
preserves arbitrary-size scientific integers; readback verifies bytes and SHA.
Each inline payload stays below 4 MiB, leaving room for snapshot and result in
one BSON document. No truncation is performed. Failed CAS/publication may leave
an unreferenced completed blob; automatic deletion is intentionally absent.
This design uses single-document atomics and majority+journal writes, with no
multi-document transactions or replica-set assumption.

## Compose and backups

`docker-compose.yml` defines authenticated MongoDB, persistent `mongodb_data`,
idempotent index initialization, API/worker artifact volumes and loopback-only
web/API ports. MongoDB has no published host port. Supply private root credentials
and an authenticated URI using the Compose hostname `database`, not localhost.
Docker/Compose and Atlas have **not** been run on this machine. Do not use
`docker compose down -v` in routine operation.

Preserve MongoDB data together with GridFS collections and filesystem artifacts.
For ongoing deployments use a separately verified backup procedure appropriate
to that deployment. See [native backup/restore](MONGODB_BACKUP_RESTORE.md).
