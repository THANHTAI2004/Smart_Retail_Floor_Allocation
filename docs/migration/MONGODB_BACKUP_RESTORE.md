# Native MongoDB backup and restore

The application has one persistence backend: MongoDB. SQL importers, SQL migration
files, legacy driver packages and in-checkout SQL databases have been removed.
Restore uses native BSON including GridFS chunks/metadata, IDs, documents and
indexes. No SQL driver or SQL recovery application is involved.

Stop **all** API, worker, campaign and external writers before backup. Keep the
database process running. This is a quiesced backup, not an online point-in-time
or cross-collection snapshot. Back up filesystem artifacts and experiment output
alongside the database; they are not included in the BSON archive. Choose a new
external destination. Treat backups as private data.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1
.venv/Scripts/python.exe -m smart_retail.infrastructure.mongodb.backup backup C:/Users/admin/Documents/SmartRetailBackups/my-new-backup.zip --database smart_retail --writers-stopped
```

Backup uses exclusive-create, per-collection SHA-256/document counts and archive
readback. Restore validates all checksums/BSON streams before the first insertion
and refuses a target with any existing collections. It never drops or overwrites
an existing target. A connection failure mid-restore may leave a partial **new**
database: retain it for diagnosis and retry to a different new database.

```powershell
.venv/Scripts/python.exe -m smart_retail.infrastructure.mongodb.backup restore C:/Users/admin/Documents/SmartRetailBackups/my-new-backup.zip --database smart_retail_restore_new
```

Verify projects, result SHA, GridFS, indexes and artifact directories before
switching services. The local cutover receipt checks its recorded database when
startup uses `--cutover-check`; do not reuse a receipt for another deployment.
A new restored deployment requires reviewed receipt/configuration. Plain health
checks require only native MongoDB connectivity and indexes.

The actual primary database was backed up and restored to an isolated target on
2026-10-22: see `mongodb-only-native-restore.json`. It had 16 projects and 8 runs.
Tests also cover GridFS payloads, exact scientific JSON integers, indexes, corrupt
archive rejection and refusing existing targets.

Old SQL recovery copies remain externally as historical evidence. They are not
used by the application. See `mongodb-only-removal.json` for the archive manifest.
