# Smart Retail Floor Allocation

The retail research application uses React/TypeScript, FastAPI/Pydantic and
**MongoDB with synchronous PyMongo**. MongoDB is the only application and campaign
database. No SQL persistence adapter, SQL driver, Alembic or SQL importer remains.

Current release hardens Windows long paths for caches, worker artifacts, campaign
reports and replay. Fresh verification: **171 pytest at both long and short temp
roots; 4 Vitest; 9 Playwright PASS**. Isolated Docker Compose verification PASS; Atlas remains blocked by missing credentials.
See [final release report](docs/release/FINAL_RELEASE_REPORT.md) and
[acceptance matrix](docs/release/FINAL_RELEASE_ACCEPTANCE.md).

## Windows startup

Requires Python 3.12, Node >=22.12 and MongoDB. This checkout has authenticated
MongoDB Community 8.0.16 bound to loopback.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Application: **http://127.0.0.1:5173**; research dashboard:
**http://127.0.0.1:5173/#research**; API: **http://127.0.0.1:8010/docs**.

On a new machine create `.venv`, install `backend/requirements-lock.txt`, install
`backend` with `pip install -e backend --no-deps`, then run
`scripts/start_mongodb.ps1 -InstallPortable` before `setup.ps1`. The helper checks
the pinned official Windows archive SHA-256.

```powershell
# Stop API/worker/frontend, retain MongoDB data and process.
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1
# Stop the owned local MongoDB process too, retaining its files.
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1 -StopMongoDB
```

Configure `MONGODB_URI`, `MONGODB_DATABASE`, `SMART_RETAIL_ARTIFACTS` in the shell.
Windows scripts do not automatically load `.env`. When URI is unset, the local
checkout uses ignored `var/mongodb/private.json`. Never publish credentials.
Primary data lives in `var/mongodb/data`; run artifacts live in `var/artifacts`.
These are persistent data directories, not disposable caches.

## Research workflows

Create a project, save seven input groups, validate SKU/order relations, enqueue
and inspect T1 Layout -> T2 Allocation -> T3 Slotting -> T4 Simulation and report.
Project revisions use atomic CAS. The queue uses atomic claims, leases, heartbeat,
owner fencing and cancellation. Immutable snapshots/results retain checksums.
Large payloads and scientific integers beyond BSON int64 use lossless GridFS JSON.

The dashboard supports Sequential, Multistart, Closed-Loop Feedback, Exact Joint
and Hybrid. Finite-domain certificates do not prove general global optimality.
Synthetic experimental results do not constitute real-store effectiveness.

```powershell
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/pilot.json --output experiments/results/my-pilot
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli replay experiments/results/my-pilot --output experiments/results/my-replay
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli compare experiments/results/my-pilot experiments/results/my-replay --output experiments/reports/my-comparison.json
.venv/Scripts/python.exe -m smart_retail.application.experiments.cli analyze experiments/results/my-pilot --output experiments/reports/my-pilot
```

Output paths must be new. Campaigns have isolated native MongoDB databases;
immutable scientific manifests, JSON/CSV, figures and checkpoints stay on disk.
Historical campaign data is preserved in `smart_retail_history`; raw SQL files
have been retired to verified external backups, outside this checkout.

## Verification and recovery

```powershell
.venv/Scripts/python.exe scripts/verify_experiment_release.py --output var/my-release-check
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_windows_long_path.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_mongodb_compose.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_atlas_connection.ps1
```

The collector runs pytest, Ruff, mypy, pip check, ESLint, Vitest, build, dependency
audit, architecture checks and Playwright on isolated real MongoDB databases.
MongoDB integration evidence is never supplied by a fake driver.
Deployment verifiers return exit 2 and an explicit BLOCKED receipt when runtime or
credentials are absent; they do not substitute local MongoDB for Docker/Atlas.
See [deployment setup and tool-installation outcome](docs/release/DEPLOYMENT_VERIFICATION.md).

- [Current handoff and fresh verification](HANDOFF.md)
- [MongoDB operations](docs/migration/MONGODB_OPERATIONS.md)
- [Native BSON/GridFS backup and restore](docs/migration/MONGODB_BACKUP_RESTORE.md)
- [MongoDB-only acceptance](docs/migration/MONGODB_ONLY_ACCEPTANCE.md)
- [Joint formulation and certificate scope](docs/research/JOINT_OPTIMIZATION_FORMULATION.md)
- [Joint workflow guide](docs/research/HOW_TO_RUN_JOINT_OPTIMIZATION.md)
- [Published numerical results](docs/research/JOINT_OPTIMIZATION_RESULTS_20261022.md)

Compose defines authenticated MongoDB, persistent volumes, health checks and
API/worker services. MongoDB has no public host port. Isolated Compose config/build/auth/workflow/restart/cancellation/recovery checks
have passed on Docker Desktop. Atlas/TLS and remote CI have not been executed. Never use `docker compose down -v` in routine
operation. Historical receipts may refer to SQL-era verification; current runtime
has no SQL fallback or dependency.
