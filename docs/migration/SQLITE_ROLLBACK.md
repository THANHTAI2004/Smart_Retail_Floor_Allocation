# SQLite recovery at the migration boundary

The original `var/smart_retail.db` and original artifacts have been retained.
No automatic fallback is included in the MongoDB runtime. Recovery is an explicit
operator action using an external SQL application bundle, leaving the MongoDB
store intact for investigation and later reconciliation.

External recovery root:
`C:/Users/admin/Documents/SmartRetailBackups/20261022-mongodb-01`.

| Item | Purpose |
|---|---|
| `runtime.db` | Verified consistent SQLite backup from initial intake |
| `sqlite-recovery/` | Separate working SQL recovery application with copied DB |
| `sqlite-recovery-manifest.json` | SHA-256 for the reconstructed recovery bundle |
| `original-artifacts.zip`, `artifact-manifest.json` | Original 32 artifacts, verified member hashes |
| `source.zip`, `manifest.json`, `VERIFIED.json` | Mixed-time source copy; individual member integrity only |

**Source archive limitation:** the first source archive was captured while edits
were beginning. Its checksums prove the captured bytes, not an exact pre-migration
source tree. It must not be advertised as an unchanged source rollback image.
The separate `sqlite-recovery` bundle reconstructs the SQL adapters from the
verified joint snapshot and retains current numerical engines. Its actual FastAPI
smoke test loaded SQLite health, 16 projects and 8 runs successfully; see
`sqlite-recovery-verification.json`. It is a recovery bundle, not a claim that the
entire old release was freshly regression-tested again.

The final frozen database is separately preserved at
`C:/Users/admin/Documents/SmartRetailBackups/20261022-mongodb-cutover-01/sqlite-backup.db`.
Its SHA-256 is
`8d562fb0607d047668bedf16d07d93115f25c9a11637a455ddc0a04de2ad3d55`.
Its `VERIFIED.json` records `PRAGMA integrity_check=ok`.

## Procedure

1. Freeze application writes and wait for active numerical runs to finish or
   cancel them explicitly. Run `scripts/stop.ps1` to stop only recorded services.
   Preserve MongoDB data, GridFS and all artifacts; do not drop or re-import over
   the target. Record any MongoDB changes since cutover for later reconciliation.
2. Verify the external bundle files against `sqlite-recovery-manifest.json`, and
   the chosen SQLite backup against its VERIFIED hash. Work on copies in a new
   external recovery directory. Never overwrite the retained originals.
3. Use the SQL bundle's pinned `requirements-lock.txt` in a separate Python 3.12
   venv and install its `backend` package. That lock retains SQLAlchemy/Alembic;
   the current MongoDB application's lock deliberately does not include them.
4. Set `SMART_RETAIL_HOME` to the recovery bundle root and
   `SMART_RETAIL_DATABASE_URL` to the copied SQLite path. Set
   `SMART_RETAIL_ARTIFACTS` to a separately extracted copy of original artifacts.
   Start the SQL API on an unused port and verify projects, runs and reports
   before directing the frontend to it. Keep the recovery working tree separate
   from this checkout and its MongoDB packages.

Example read-only smoke of the existing verified bundle from this checkout
(the current local venv still has the legacy SQL dependencies installed):

```powershell
$env:SMART_RETAIL_HOME = 'C:/Users/admin/Documents/SmartRetailBackups/20261022-mongodb-01/sqlite-recovery'
$env:SMART_RETAIL_DATABASE_URL = 'sqlite+pysqlite:///C:/Users/admin/Documents/SmartRetailBackups/20261022-mongodb-01/sqlite-recovery/var/smart_retail.db'
$env:PYTHONPATH = "$env:SMART_RETAIL_HOME/backend/src"
.venv/Scripts/python.exe -m uvicorn smart_retail.api.main:app --host 127.0.0.1 --port 8020
```

Use a separate shell for this recovery command. The SQLite snapshot does not
contain later MongoDB-only work. Returning to SQLite after new production writes
requires explicit reconciliation; this procedure does not promise automatic
reverse migration. Returning to MongoDB uses the primary checkout and its normal
environment/`scripts/start.ps1`, without deleting the recovery bundle.
