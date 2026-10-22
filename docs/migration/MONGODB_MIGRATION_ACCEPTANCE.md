# MongoDB migration acceptance â€” 2026-10-22

Current MongoDB-only checkpoint: SQL adapters, SQL databases and drivers have been removed. See [MongoDB-only acceptance](MONGODB_ONLY_ACCEPTANCE.md). The following migration details are historical.

Status: **MONGODB_MIGRATION_VERIFIED**. All final local release and replay checks
below completed successfully. Local runtime: real authenticated MongoDB Community 8.0.16,
Windows, Python 3.12, synchronous PyMongo 4.18.2. No fake Mongo driver was used.

The primary database is `smart_retail`. HTTP routes and frontend request/response
contracts remain compatible. The main application does not load SQLite or
SQLAlchemy. Retired SQL migrations remain historical source; only the explicit
offline importer uses stdlib sqlite3. The current dependency lock has no ORM or
SQL driver requirement. Existing installed SQL packages remain available for
external recovery and are not imported by the primary runtime.

## Data reconciliation and recovery

| Logical data | SQLite source | Verified MongoDB readback |
|---|---:|---:|
| Projects | 16 | 16 |
| Product keys in embedded inputs | 24 | 24 |
| Orders in embedded inputs | 12 | 12 |
| Order lines in embedded inputs | 24 | 24 |
| Optimization runs | 8 | 8 |
| Historic worker observations | 9 | 9, MIGRATED_OFFLINE |

Evidence: `mongodb-migration-report.json`, `mongodb-idempotency-report.json`,
`mongodb-final-readback.json`. No active source jobs required status conversion.
All original eight runs remain SUCCEEDED with original snapshot/result SHA-256.
ID, revision, timestamps, input groups, outcomes and relationship rows were
compared on readback. Rerun inserted zero projects/runs and refused conflicts
in isolated integration controls. Target worker liveness comes from a fresh
MongoDB heartbeat, not migrated observations.

The frozen SQLite backup is external at
`C:/Users/admin/Documents/SmartRetailBackups/20261022-mongodb-cutover-01/sqlite-backup.db`,
SHA-256 `8d562fb0607d047668bedf16d07d93115f25c9a11637a455ddc0a04de2ad3d55`.
The source remains in place, read-only to migration. `mongodb-live-service.json`
compares original source rows to MongoDB and verifies all original 32 artifact
hashes. Recoverable copies are outside the checkout.

Read the externally archived SQL recovery guide before recovery: the first source
archive is a mixed-time capture and is not an exact pre-migration tree. A separate
reconstructed SQL recovery bundle was actually tested against its copied SQLite
store (16 projects / 8 runs); receipt `sqlite-recovery-verification.json`.
No current MongoDB data is dropped by rollback instructions.

## Gates and current evidence

| Gate | Evidence |
|---|---|
| Project CRUD, seven inputs, validation, SKU/order references, 404/409, atomic revision | Real MongoDB API/integration tests and browser workflow |
| Simultaneous updates | Eight saves at one revision: exactly one success, seven conflicts |
| Atomic queue, concurrent claim | 24 claims for 16 jobs, each job claimed exactly once |
| Lease, crash/restart recovery, old-owner fencing | Expired owner cannot renew/publish, including after reading a new owner's record |
| Cancel/timeout and final publication race | MongoDB worker integration and supervisor tests |
| Immutable snapshot and checksum rejection | Snapshot unchanged on publication; corrupt snapshot/result rejected |
| BSON overflow, scientific integer precision | 17 MiB result and 120-digit integers roundtrip through GridFS; corrupt chunk rejected |
| Enqueue â†’ T1 â†’ T2 â†’ T3 â†’ T4 â†’ result/report, replay, CSV/JSON | Existing full backend workflow tests and Playwright on isolated real MongoDB |
| Migration dry-run, idempotency, conflict refusal, orphan and active-run policy | Isolated real MongoDB integration controls |
| Persistence across actual MongoDB restart | `mongodb-restart-verification-02.json`: PID 22196 â†’ 6492, all main rows and large GridFS payload unchanged |
| No SQL runtime dependency / no public MongoDB bind | `mongodb-live-service.json`, static architecture audit |
| Indexes / startup cutover consistency | `mongodb-index-health.json`, receipt ID + database + source SHA gate |
| Historical engine/research bytes | `historical-science-preservation.json` |
| Full current software checks | `evidence/20261022-mongodb-release-02/verification.json` |
| Current experiment runner / scientific replay | Final campaign and comparison paths below |

The first `mongodb-restart-verification.json` is explicitly INVALID_RESTART_EVIDENCE:
a UTC guard refused shutdown, so no actual PID change was established in that
attempt. Only the second receipt establishes restart. Release-01 and certification-01
are intermediate checks before the final orphan-reference validation change;
release-02 and campaign suffix-02 are the final source receipts.

## Fresh numerical regression on MongoDB

Final software verification: **164 pytest, 4 Vitest, 9 Playwright PASS**; Ruff,
mypy, pip check, ESLint, frontend build, npm audit and static architecture PASS.
No MongoDB integration test was skipped. Pilot 19/19, joint certification 15/15
and holdout 6/6 jobs completed successfully. Pilot/certification replay completed
34/34 jobs with identical input and scientific result SHA-256 and equivalent
numerical outcomes. Current source/dependency identity matches every final
campaign and the final release. Historical preservation verified **50,628 files**:
20 domain, 20 engine, 8 feedback, 50,116 result and 464 report files, all unchanged.

All results have explicit immutable output directories under `experiments/results`;
matching analysis lives under `experiments/reports`.

| Campaign directory | Purpose |
|---|---|
| `20261022-mongodb-pilot-02` | 19-job T1â€“T4/E01â€“E08 pilot |
| `20261022-mongodb-pilot-replay-02` | New execution of the same pilot |
| `20261022-mongodb-certification-02` | 15-job sequential/multistart/feedback/exact/hybrid comparison |
| `20261022-mongodb-certification-replay-02` | New execution with independent certificate checks |
| `20261022-mongodb-holdout-02` | Six-job joint holdout regression |

Comparison receipts: `experiments/reports/20261022-mongodb-pilot-comparison-02.json`
and `experiments/reports/20261022-mongodb-certification-comparison-02.json`.
Scientific results exclude runtime telemetry; exact input/result hashes and
numerical comparison are reported separately. Current source/dependency identity
naturally differs from SQLite-era identity. Old snapshots/certificates remain
unchanged and readable; replay must still enforce the original identity guard.
Historical evidence is not counted as new-source test success. Finite-instance
optimality does not imply general global optimality or real-store effectiveness.

Executed commands (full release collector arguments/times/exit codes in its receipt):

```powershell
.venv/Scripts/python.exe scripts/verify_experiment_release.py --output docs/migration/evidence/20261022-mongodb-release-02
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/pilot.json --output experiments/results/20261022-mongodb-pilot-02
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli replay experiments/results/20261022-mongodb-pilot-02 --output experiments/results/20261022-mongodb-pilot-replay-02
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli compare experiments/results/20261022-mongodb-pilot-02 experiments/results/20261022-mongodb-pilot-replay-02 --output experiments/reports/20261022-mongodb-pilot-comparison-02.json
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/joint_certification.json --output experiments/results/20261022-mongodb-certification-02
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli replay experiments/results/20261022-mongodb-certification-02 --output experiments/results/20261022-mongodb-certification-replay-02
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli compare experiments/results/20261022-mongodb-certification-02 experiments/results/20261022-mongodb-certification-replay-02 --output experiments/reports/20261022-mongodb-certification-comparison-02.json
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/joint_holdout.json --output experiments/results/20261022-mongodb-holdout-02
```

## Scope and operational limits

Docker/Compose, Atlas/TLS connection and remote GitHub Actions were configured but
not executed here (Docker runtime unavailable). Authentication, majority/journal
writes, local connection/index setup, worker operation and real daemon restart
were exercised on standalone MongoDB. No transaction support is assumed.
There is no automatic reverse migration of post-cutover MongoDB edits. Completed
unreferenced GridFS blobs may remain after failed CAS; no research data is deleted
automatically. Test databases and original research output are retained.

See [operations](MONGODB_OPERATIONS.md) for environment configuration, startup,
shutdown, data size limits and deployment procedures. Git index/HEAD and inherited
work are preserved. No reset, clean, commit, push, original data/artifact deletion
or research result overwrite is part of this migration.
