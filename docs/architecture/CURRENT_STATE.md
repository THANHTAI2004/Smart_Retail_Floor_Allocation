# Current state - 2026-10-22

## MongoDB migration, current checkpoint

Primary persistence is authenticated MongoDB Community 8.0.16 via synchronous
PyMongo. HTTP adapters use application services and repository contracts; MongoDB
implementation remains in infrastructure. Project aggregates use revision CAS;
run queue uses atomic claims, expiring leases and fencing tokens. GridFS handles
large scientific payloads without truncation or integer coercion. No SQL ORM is
loaded in the primary API/worker runtime and no multi-document transaction is
assumed. Domain/engines remain independent of PyMongo.

Status: MONGODB_MIGRATION_VERIFIED on local Windows/MongoDB. Original 16 projects,
24 product keys, 12 orders, 24 lines, 8 runs and 9 offline worker observations
were reconciled; SQLite, original 32 artifacts and research outputs are retained.
Fresh release: 164 pytest, 4 Vitest, 9 Playwright plus static/build/dependency
checks PASS. Actual MongoDB PID change and readback verified persistence. Fresh
pilot/joint replay matches 34/34 input/result hashes. Compose/Atlas and remote CI
were not executed. Full evidence and recovery caveat:
[MongoDB acceptance](../migration/MONGODB_MIGRATION_ACCEPTANCE.md).

The following sections are the historical pre-migration orientation. Their
SQLite/PostgreSQL descriptions and test counts do not describe current persistence.

## Historical experiment-platform intake

The application lives directly in frontend/ and backend/. No retired source is
imported or executed. Initial branch main, HEAD
3a53f0ea12318fd939d68bece92ee71ada97074f, clean index/worktree. HANDOFF.md was
absent at inspection; this execution created a new current handoff rather than
restoring removed historical material. No Git publication is authorized.

External snapshot: C:\Users\admin\Documents\SmartRetailBackups\20261022-experiment-platform-01.
629 files were archived, read back and verified against SHA-256; workflow.py was
restored to a separate recovery-smoke directory and its checksum verified. A
consistent SQLite backup is stored alongside the archive. Historical campaign
and research evidence is preserved.

Fresh initial baseline: 85 pytest passed, one cancellation test failed when its
own progress reader hit a transient Windows sharing violation. Ruff found 10
I001 import errors. The test now uses the existing transient-safe reader and
Ruff explicitly recognizes smart_retail as first-party. A later full milestone
ran 123 tests successfully; final receipts are recorded under research evidence.

Current capabilities: versioned seven-section contracts with explicit migration,
lossless table CSV, T1 geometry/topology and local search, T2 greedy/MILP with
soft affinity, T3 facing-range strip MIP/physical replay, finite picker pools,
piecewise demand, nearest/return/exact small-tour policies, persistent stage
cache, standalone stages, durable worker and campaign checkpoint/resume.

Research interface: application.experiments CLI and /api/research adapters share
the same manifest contract and real queue/process worker. The research dashboard
uses these adapters, never mock results. Reports are built from immutable recorded
outcomes with Matplotlib PNG/SVG, CSV/JSON, statistics and manifest hashes.

The target is EXPERIMENT_READY_SYNTHETIC for declared local Windows/SQLite
experiments. Production deployment, PostgreSQL/Compose runtime, real survey data,
real calibration and REAL_WORLD_VALIDATED are separate and are not asserted.

Final milestone: EXPERIMENT_READY_SYNTHETIC, ER01-ER15 PASS. Fresh release: 133 pytest, 4 Vitest, 8 Playwright, 68 Python/39 frontend static import audit. Exact receipts and results: ../research/evidence/20261022-release-01/verification.json and ../research/RESULTS_20261022.md. The local services were restarted onto the final source; all five business tables match the verified initial SQLite backup.
