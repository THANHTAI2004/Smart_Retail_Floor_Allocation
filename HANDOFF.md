# Current handoff - Windows long paths and release verification, 2026-10-22

Windows filesystem fix verified: only os.link had extended paths previously.
Replayed old cache source from verified backup: root 244 characters, temporary
write at 286 characters fails FileNotFoundError. New infrastructure/filesystem.py
normalizes owned artifact roots for all derived I/O; drive/UNC syntax, Unicode,
logical campaign identity and atomic no-overwrite hard-link semantics preserved.
Cache format/scientific checksums and numerical engines unchanged.

Updated cache, worker, experiment storage/campaign/HTTP/report/replay/certificate
I/O boundaries. Added six deep-path regression cases including spawned process,
32 concurrent writers, failed-link cleanup, immutable JSON and checksum detection.
Fresh final long-path receipt: docs/release/evidence/20261022-longpath-03/verification.json:
171 pytest PASS at logical base 350 chars, 171 PASS at 50 chars; both previously
reported HTTP tests PASS on three independent deep-path repeats. No MongoDB skips.
Earlier attempts retained as superseded harness/test-development evidence.

Fresh full quality receipt: docs/release/evidence/20261022-release-quality-01/verification.json:
171 pytest, 4 Vitest, 9 Playwright and Ruff/mypy/pip check/ESLint/build/npm audit/
architecture PASS. Final source identity matches new three-job sequential/feedback/
exact campaign and replay; 3/3 identical input/result SHA/numeric comparison.
Independent certificate CLI PASS: evidence/20261022-proof-replay.json.
Campaigns: experiments/results/20261022-release-joint{-replay}-01;
reports: experiments/reports/20261022-release-joint-01 and comparison-01.json.

Compose ports now parameterized for isolated project testing; private env/keys
excluded from Docker context. Added scripts/verify_mongodb_compose.ps1 and
verify_atlas_connection.ps1 with UUID namespaces, sanitized receipts and explicit
BLOCKED exit codes. Real isolated Compose PASS: config/build/auth/indices, API/worker/
frontend, seven inputs, T1-T4/result/report/SHA, restart persistence, cancellation
and expired worker recovery. Receipt: evidence/20261022-compose-06/verification.json.
Actual volume/network/port isolation inspected (compose-isolation.json). Atlas
remains BLOCKED_ATLAS_CREDENTIALS; no live Atlas success is claimed.
The user explicitly authorized installing missing tools. WinGet per-user Docker
attempt returned No applicable installer found; direct official installer command
was rejected before execution (blocked by policy). A safer pinned WinGet user-mode installation subsequently succeeded. Docker
Desktop 4.96.1, CLI/engine 29.9.2, Compose v5.6.0 and WSL 2.7.13 installed;
WSL needed elevated WinGet/UAC. Engine started with no reboot or BIOS changes.
Real Compose config validation PASS; isolated build/runtime verification follows
the final release receipt. Earlier BLOCKED attempts are retained as history.
Installed yaml@2.8.1 in ignored var/release-tools for static validation. WSL missing;
hypervisor present; original shell not elevated. Atlas credentials not supplied.

Original 16 projects, 8 runs, 32 artifact hashes unchanged; representative historical
scientific manifests PASS. Main API/worker/frontend restarted on current source:
http://127.0.0.1:5173/#research. External pre-edit source backup verified at
C:/Users/admin/Documents/SmartRetailBackups/20261022-longpath-061451.
Large generated result retention archive/manifest recorded in release evidence.

Git policy: ignore generated experiments/results subdirectories only, preserve
configs/source/reports/docs. Stage audited source/evidence including prior explicit
MongoDB-only removals. User's prior commit authorization permits a local checkpoint;
the new master prompt expressly forbids GitHub push. No push, reset, clean, amend
or research deletion. See final Git audit/release report for checkpoint status.

Release report: docs/release/FINAL_RELEASE_REPORT.md. Acceptance:
docs/release/FINAL_RELEASE_ACCEPTANCE.md. Target is RELEASE_READY_WITH_EXTERNAL_BLOCKERS
after local checkpoint; only Atlas credentials and remote CI remain external
verification limits. Docker and WSL installation/runtime succeeded. Live UNC share not available (syntax and local deep paths tested).

# Historical handoff - MongoDB-only retirement before long-path release

The user explicitly requested removal of the remaining SQL implementation after
the published migration. Native MongoDB is now the only persistence and recovery
path in this checkout. SQL importer/tests, Alembic scripts, PostgreSQL verifier,
local SQLite stores and SQL driver packages have been retired. No new Git staging,
commit or push is part of this removal milestone.

Before removal, verified external archive:
C:/Users/admin/Documents/SmartRetailBackups/20261022-mongodb-only-01.
522 original database/source/cache files were archived and read back by SHA-256.
34 legacy application/campaign databases were decoded into smart_retail_history,
with per-table counts/checksums and readback before removing SQL bytes locally.
Scientific JSON/manifests/results remain unchanged. Old SQL backups remain outside
the checkout as recovery evidence and are never loaded by the application.

Both project and older experiment Python venvs had SQLAlchemy/Alembic/SQL driver
packages removed. Mypy now uses filesystem caching. Standard Python installation
is untouched; no application source imports its sqlite3 module. Future setup
removes retired persistence packages from the project venv before installing locks.

Native BSON backup/restore now includes documents, IDs, indexes and GridFS, with
checksums, exclusive backup creation and refusal to overwrite existing databases.
Requires all writers stopped; does not claim an online distributed snapshot.
Actual primary backup/restore verified 16 projects/8 runs and every collection
document equal in an isolated target. Receipt: docs/migration/mongodb-only-native-restore.json.
Retirement manifest: docs/migration/mongodb-only-removal.json.
Operations: docs/migration/MONGODB_BACKUP_RESTORE.md.
**MONGODB_ONLY_VERIFIED.** Fresh final release:
docs/migration/evidence/20261022-mongodb-only-release-01/verification.json.
165 pytest, 4 Vitest, 9 Playwright PASS, no integration skips. Ruff/mypy/pip
check/ESLint/build/npm audit/architecture PASS. Pilot and replay each ran 19/19
jobs with identical input/result SHA and numerical values. Current runtime
identity matches the final release and both campaigns. Primary BSON restore
compared every collection document; history restore verified all 34 source
databases / 206 archived tables. Read-created WAL/SHM were also archived/removed.
No in-checkout SQLite database remains; original scientific JSON unchanged.
API/worker/frontend restarted successfully at http://127.0.0.1:5173/#research.
Acceptance: docs/migration/MONGODB_ONLY_ACCEPTANCE.md.
Closeout: docs/migration/mongodb-only-closeout.json. Docker/Atlas/remote CI remain
unexecuted. This retirement is not staged, committed or pushed. Previous 164/4/9
counts below are historical source evidence, not verification of this retirement.

# Historical handoff - MongoDB migration verified before SQL retirement

Publication checkpoint: the user explicitly authorized commit and push to their
existing GitHub account on 2026-10-22. Publish the current source, tests, contracts,
configuration, reports and acceptance evidence to origin/main. Raw generated
experiments/results (approximately 1.4 GiB), local MongoDB/SQLite stores, secrets,
environments and external backups remain local. The no-publication statements
below describe the migration verification milestone before this authorization.

**MONGODB_MIGRATION_VERIFIED** on real authenticated MongoDB Community 8.0.16,
Windows/Python 3.12, synchronous PyMongo 4.18.2. App remains in root frontend/backend.
No engine/domain/feedback numerical algorithm was changed for this migration.
No Git reset, clean, stage, commit or push; inherited dirty/untracked work retained.

Current local API/worker/frontend are running against `smart_retail` MongoDB:
http://127.0.0.1:5173/#research and http://127.0.0.1:8010/docs.
MongoDB binds loopback only with auth, persistent data `var/mongodb/data`.
Private credentials remain in ignored `var/mongodb/private.json`; never publish.

Implemented project aggregate CAS/404/409, native repository interfaces, atomic
claim/lease/heartbeat/fencing/cancel recovery, GridFS overflow and precise large
integers, checksummed immutable run snapshots/results, idempotent indexes, offline
SQLite migration, cutover receipt checks, Windows scripts and Compose definitions.
Primary runtime imports no SQLite/SQLAlchemy; legacy source and SQL recovery
dependencies are retained for recovery only. No multi-document transactions.

Reconciled source/target: 16 projects, 24 product keys, 12 orders, 24 order lines,
8 original SUCCEEDED runs, 9 MIGRATED_OFFLINE worker observations. IDs, revisions,
timestamps, input/result SHA and embedded relationships preserved. Final rerun
inserts zero records; original SQLite and all 32 original artifacts remain intact.
Receipts: docs/migration/mongodb-migration-report.json,
mongodb-idempotency-report.json, mongodb-final-readback.json,
mongodb-live-service.json. Snapshot and result digests validated on MongoDB readback.

Fresh final release: docs/migration/evidence/20261022-mongodb-release-02/verification.json.
**164 pytest, 4 Vitest, 9 Playwright PASS**, no integration skips; Ruff/mypy/pip
check/ESLint/build/npm audit/architecture PASS. Exact commands/times/exits recorded.
Final backend source SHA: 086d643db8a5a6fa7142c6206cb0446ff9f18fd4f3af8e885f4a7e2c59cd1a96.
One Starlette/httpx deprecation warning remains. Release-01 is an intermediate check.

Fresh campaigns under experiments/results and corresponding reports:
20261022-mongodb-pilot-02 19/19; mongodb-certification-02 15/15;
mongodb-holdout-02 6/6. Pilot/certification replay runs 34/34, identical input SHA,
scientific result SHA and numerical values. Comparison receipts are under
experiments/reports/20261022-mongodb-{pilot,certification}-comparison-02.json.
Historical-science-preservation receipt checks 50,628 original engine/domain/
feedback/result/report files, all unchanged. Old source identity guards remain;
historical SQL-era replay is not falsely relabeled as current-source verification.

Actual MongoDB restart: docs/migration/mongodb-restart-verification-02.json,
PID 22196 -> 6492, 16/8 original rows and >17 MiB GridFS result unchanged. The first
restart receipt is explicitly INVALID_RESTART_EVIDENCE: UTC guard refused shutdown
and no PID change was established; only suffix-02 is accepted. Integration covers
concurrent claims/revision saves, expired old-owner writes, cancel race, corrupt
payloads, worker recovery, migration conflicts/orphans/active policy and large ints.

External recovery: C:/Users/admin/Documents/SmartRetailBackups/20261022-mongodb-01.
SQLite/artifact backups verified. Initial source.zip is mixed-time (copy overlapped
early edits), not an exact pre-migration source restore. Separate reconstructed
sqlite-recovery bundle loaded 16 projects/8 runs using the copied SQL database;
docs/migration/sqlite-recovery-verification.json. Final frozen SQLite backup:
../20261022-mongodb-cutover-01/sqlite-backup.db, SHA
8d562fb0607d047668bedf16d07d93115f25c9a11637a455ddc0a04de2ad3d55.

Acceptance: docs/migration/MONGODB_MIGRATION_ACCEPTANCE.md.
Operations: docs/migration/MONGODB_OPERATIONS.md.
Rollback: docs/migration/SQLITE_ROLLBACK.md (no automatic reverse migration of
post-cutover writes). Start: scripts/start.ps1. Stop app: scripts/stop.ps1;
optional -StopMongoDB stops the owned local daemon while preserving files.
Do not remove var/mongodb, external recovery assets, original SQLite or artifacts.

Remaining deployment verification: Docker/Compose runtime unavailable; Compose,
Atlas/TLS connection and remote GitHub Actions configured but not executed.
Local MongoDB acceptance does not assert deployment/field validation. Next optional
deployment milestone is real Compose/Atlas verification on the chosen target plus
ongoing MongoDB backup/restore drills. No remaining blocker for this local migration.

# Historical handoff - joint T1-T4 completed before MongoDB migration

**CLOSED_LOOP_FEEDBACK_READY**
**JOINT_EXACT_SMALL_INSTANCE_CERTIFIED** (declared four-state / 128-state models)
**JOINT_GENERAL_OPTIMALITY_NOT_PROVEN**

JO01-JO18 PASS: docs/research/evidence/20261022-joint-readiness-02.json.
Final release: docs/research/evidence/20261022-joint-release-03/verification.json.
155 pytest, 4 Vitest, 9 Playwright and all static/build/dependency/architecture
checks PASS. Source identity matches all final suffix-02 campaigns and replays.
Current model/limits: docs/research/JOINT_OPTIMIZATION_FORMULATION.md.
Guide: docs/research/HOW_TO_RUN_JOINT_OPTIMIZATION.md.
Results: docs/research/JOINT_OPTIMIZATION_RESULTS_20261022.md.
Acceptance: docs/research/JOINT_OPTIMIZATION_ACCEPTANCE.md.

## Final executed campaigns (experiments/results and matching reports)

| Directory suffix | Outcome | Actual child wall total s |
|---|---|---:|
| 20261022-joint-effectiveness-02 | 9/9 completed; unexecuted 0 | 55.640 |
| 20261022-joint-ablation-02 | 15/15 completed; unexecuted 0 | 81.780 |
| 20261022-joint-certification-02 | 15/15 completed; unexecuted 0 | 54.187 |
| 20261022-joint-scalability-02 | 18/18 completed; unexecuted 0 | 192.750 |
| 20261022-joint-holdout-02 | 6/6 completed; unexecuted 0 | 35.610 |
| 20261022-joint-certification-128-02 | 6/6 completed; unexecuted 0 | 119.061 |

All 69 main jobs succeeded with independent witness validation PASS. Failure
controls are separate: experiments/results/20261022-joint-failure-controls-02
contains one FAILED/SEARCH_EXHAUSTED and one INFEASIBLE/INFEASIBLE_PROVEN;
complete result/certificate artifacts remain present. Partial search is not
called infeasible. Holdout exhaustion preserves training incumbent and explicitly
records missing holdout objective. Suffix-01 is preliminary historical source.

Proof: all 12 main exact/hybrid jobs independently verified. Every 128-state job
checks 128 leaves (32 feasible / 96 invalid); no heuristic pruning. Four-state
objective 0.1026698103 beats feedback's local plateau 0.1526698103 on the declared
scenarios. 128-state optimum 0.0955269532 is restricted to its explicitly listed
domain, and does not bound broader feedback moves outside that domain.

E11 improves 0.1026698103 -> 0.0598126675 through three actual iterations. E12
attributes the demonstrated benefit to T1; T2/T3-only have no improvement on
this fixture. E14 Small has no demonstrated improvement. E15 holdout benefit
persists on the published unseen synthetic scenarios; no field validation.

Separate pinned venv replays: E13 15/15 and improving E11 9/9 have identical input
SHA, scientific result SHA and numerical results. Receipts:
experiments/reports/20261022-joint-clean-comparison-02.json and
experiments/reports/20261022-joint-feedback-clean-comparison-02.json.
CLI proof replay: evidence/20261022-joint-proof-cli-02.json and
20261022-joint-proof-cli-128-02.json. Full commands are in the guide and command
receipts; release collector records exact arguments, timestamps and exit codes.

Local final API/worker/frontend are running: http://127.0.0.1:5173/#research.
Final demonstration campaign 8c4030e6-4760-474e-975b-b3a554812c62 completed 5/5
modes with expected independent proof statuses. Receipt:
docs/research/evidence/20261022-joint-live-service-02.json. The frontend now also
shows actual normalized-objective component KPIs and no-incumbent jobs.

Original five business tables still match the external initial SQLite backup:
16 projects, 24 product keys, 12 orders, 24 lines, 8 runs. No root business job
was running when restarting the owned services. Verified 6,684-file external
snapshot: C:/Users/admin/Documents/SmartRetailBackups/20261022-joint-01; consistent
runtime.db, pre-joint-restart.db and final-source-runtime.db retained there.
HEAD remains 3a53f0ea12318fd939d68bece92ee71ada97074f, staged diff empty. No reset,
clean, stash, stage, commit, push or artifact deletion. Inherited work preserved.

Remaining limits: explicit finite numerical domains and fixed simulation samples;
no continuous/general optimum, full global Pareto set, strong LP/MIP lower bound,
LNS/annealing, Large integrated scaling, real calibration, cross-OS proof or field
validation. Docker/PostgreSQL/remote CI remain unverified and outside this task's
local synthetic acceptance. Next research: independent physical instances, isolated
layer-sensitive fixtures, broader holdout seeds and larger bounded studies, then
licensed real data/calibration/deployment validation.

---
# Joint implementation execution history (superseded intermediate pointers)

# Current joint optimization execution - 2026-10-22

Task: real closed-loop T1/T2/T3 feedback, exact finite joint solver, independent
certificates, hybrid mode, E11-E15 and research dashboard integration.
Status: IN_PROGRESS; JO acceptance not yet claimed.

Fresh baseline before changes: 133 pytest passed, one dependency deprecation warning.
Inherited dirty/untracked work was inventoried and retained; no Git staging/reset/
clean/stash/commit/push. Verified external snapshot of 6,684 repository files:
C:/Users/admin/Documents/SmartRetailBackups/20261022-joint-01. Every ZIP member SHA
was checked, workflow.py was restored/read back, and runtime.db is a consistent
SQLite backup. Prior campaigns are immutable historical evidence, not verification
of this new source.

Milestone: implemented real feedback decision edits in each upstream layer and
reused official stage/physical/route validation. A manually authored local plateau
fixture distinguishes CONVERGED_LOCAL from complete finite optimum. Focused tests:
16 passed. Initial full regression: 147 passed, 2 schema/sample synchronization
failures; updating generated schema and normalized sample, not changing assertions.
Next: complete E15 and 128-state E13, synchronize reports and assess JO01-JO18.

Fresh final-source release collector:
`.venv/Scripts/python.exe scripts/verify_experiment_release.py --output docs/research/evidence/20261022-joint-release-01`
All ten commands PASS: 152 pytest, 4 Vitest, 9 Playwright, Ruff, mypy (85 modules),
pip check, ESLint, build, npm audit and static architecture (85 Python/40 frontend).
Two additional control tests were added after collection; the full focused joint
suite subsequently passed 20/20 with XML/logs in evidence/20261022-joint-controls-01.
No backend production source changed after campaign/release source freeze.

E13 four-state campaign 15/15 succeeded; exact/hybrid certificate verification PASS.
Independent CLI verifier replayed four states successfully. Separate pinned venv
replay completed 15/15 with exact input/result SHA and numerical match in
experiments/reports/20261022-joint-clean-comparison-01.json.
E11 9/9, E12 15/15 and E14 18/18 completed without unexecuted jobs. E11 improves
over three actual iterations; E12 improvement is attributable to T1 on this
fixture, with no demonstrated T2/T3-only advantage. Do not claim all layers improve.
The first joint UI attempt collided with the preceding replay's still-publishing
supervisor (409); a real completion wait fixed the test sequencing. Failed evidence
is preserved in var/e2e-20261022-110605; final nine browser cases all pass.

Final edge-case audit found and fixed: a joint result without an incumbent must
not become SUCCEEDED in the durable worker. Real two-job control now records
FAILED/SEARCH_EXHAUSTED for incomplete search and INFEASIBLE for independently
proved empty finite domain; result/certificate artifacts remain retained. Holdout
budget exhaustion now preserves the verified training incumbent with an explicit
not-completed holdout status. This changed production source identity. Therefore
campaign/report suffix -01 and release-01 remain preserved preliminary receipts;
current final verification is release-02 (155 pytest passed so far) and all six
campaigns are being rerun into suffix -02, with fresh replay/proof checks.
Current JO assessment must be recomputed against those final source identities.

---
# Previous synthetic-platform milestone (historical source)

# Current execution pointer - 2026-10-22

Task: implement the complete synthetic experiment platform requested on 2026-10-22.
Status: **EXPERIMENT_READY_SYNTHETIC / ER01-ER15 PASS**.
Scope: controlled local Windows/Python 3.12/SQLite synthetic experiments.
Current results: docs/research/RESULTS_20261022.md.
Current model: docs/research/MODEL_SCOPE_20261022.md.

This file was absent at inspection; it is a new current handoff, not a restoration
of the removed historical file. Historical research artifacts remain unchanged.
Repository main at 3a53f0ea12318fd939d68bece92ee71ada97074f was clean at start.
Do not reset, clean, stash, stage, commit or push without explicit authorization.

Baseline: 85 passed, 1 cancellation-test failure caused by a transient Windows
progress-file sharing violation; Ruff reported 10 I001 errors. These are fresh
results, not the previous checkpoint's 86-pass claim. Initial corrections use the
existing transient-safe progress reader in the cancellation test and explicitly
declare smart_retail as a first-party import for stable Ruff behavior.

External snapshot: C:\Users\admin\Documents\SmartRetailBackups\20261022-experiment-platform-01.
Archive readback verified all 629 files against SHA-256; sample recovery verified.
VERIFIED.json records original HEAD/index fingerprint. No stage/reset/clean,
commit/push or inherited-business-data replacement was performed.

## Completed milestones and fresh verification

1. Expanded seven-section contracts to 1.1, explicit provenance and immutable
   migration; regenerated schemas/sample and published a new manifest v2 without
   rewriting the historical v1 manifest. CSV import/export preserves metadata.
2. Implemented T1 local search/topology, T2 soft-affinity MILP, T3 facing ranges
   and compatibility, T4 finite pickers/piecewise arrivals/three route policies.
   Independent reference enumeration and physical/route replay cover these models.
3. Integrated bounded candidates, content-keyed persistent stage cache, standalone
   stages, immutable per-stage artifacts, actual OS child memory/CPU measurement,
   startup-inclusive wall budget, killable timeout/cancel and bounded crash retry.
4. Implemented typed campaign CLI/API, four scales/five scenarios, import hashes,
   checkpoint/resume, failure retention, seed-aware statistics, Matplotlib figures,
   manifests/replay/compare and real research dashboard. React shell now composes
   page components/hooks rather than owning all application logic.
5. Collected a fresh complete release using:
   `.venv/Scripts/python.exe scripts/verify_experiment_release.py --output docs/research/evidence/20261022-release-01`
   Result: **133 pytest, 4 Vitest, 8 Playwright PASS**; Ruff, mypy (68 modules),
   ESLint, TypeScript/Vite build, pip check, npm audit (0 vulnerabilities), import
   architecture audit (68 Python/39 frontend, no detected cycles/legacy imports).
   Exact arguments, timings, stdout/stderr and identities are in verification.json.
   Browser checks include research/CSV roundtrip, accessibility, editor undo/redo,
   workflow/persistence/replay/export, invalid/empty/offline and mobile states.
6. Final campaigns (each `run --config experiments/configs/<name>.json --output
   experiments/results/<directory>`, followed by `analyze` to corresponding report):

| Config | Final directory | Observed outcomes |
|---|---|---|
| pilot | 20261022-pilot-04 | 19/19 succeeded; 41.001 s child wall |
| main | 20261022-main-02 | 105/105 succeeded; 304.922 s; independent replay PASS |
| robustness | 20261022-robustness-01 | 20/20 succeeded; 55.594 s |
| reproducibility | 20261022-reproducibility-01 | 4/4 succeeded; 9.657 s |
| failure_controls | 20261022-failure-controls-02 | 2 SEARCH_EXHAUSTED failures, 2 MILP INFEASIBLE; 9.328 s |

All planned jobs were attempted in those campaigns. Failure controls intentionally
remain failures/infeasible, not successful solutions. Earlier campaign outputs
are preserved; main-01 predates the corrected startup-inclusive clock and is not
the final runtime benchmark.

7. Created `var/clean-python-20261022` from a fresh venv, installed the pinned lock
   and editable backend with --no-deps; pip check passed. Replayed final pilot to
   `experiments/results/20261022-clean-replay-02` (19/19 succeeded, 60.406 s).
   `compare` output `experiments/reports/20261022-clean-comparison-02.json` confirms
   19/19 same input SHA, exact scientific result SHA and numeric equivalence.
   This is a clean Python environment on the same OS, not clean-OS validation.
8. Executed readiness collector with release-01, main-02, pilot-04, clean
   comparison-02 and main-02 report: `docs/research/evidence/20261022-readiness.json`
   gives EXPERIMENT_READY_SYNTHETIC; all ER01-ER15 PASS. See readiness matrix for
   executable command using a fresh output path. No backend source changed after
   final campaigns. Additional plots use frozen main-02 rows and hash their inputs.

## Local service and data preservation

Before restart all eight original optimization runs were SUCCEEDED; no queued or
running business jobs. Compared all five business tables with the initial
consistent backup: projects 16, product_keys 24, orders 12, order_lines 24,
optimization_runs 8, with identical complete rows. Created another consistent
external SQLite backup `pre-restart-runtime.db` (SHA-256
09d41691a8d5f953a1f50cd8a7c4923531d767fe16bc1080e64c7311ee577e1d).
Used `scripts/stop.ps1` and `scripts/start.ps1` to restart only recorded services.
Health returned SQLite/worker_online true with the final source identity;
frontend HTTP 200, four research datasets and nine configurations were available.
Live-service receipt: docs/research/evidence/20261022-live-service.json.
Final live API smoke campaign c8732748-0515-4373-9ce6-1d1997d22263 completed
2/2 E02 jobs with independent validation PASS, and all 11 report file hashes
matched the report manifest. The dashboard can display this actual campaign.
After documentation synchronization, readiness was executed again to
docs/research/evidence/20261022-readiness-final.json: all ER01-ER15 still PASS.
E09/E10/failure-control integrity checks respectively verified 227/49/37 files.
UTF-8/suspicious-character scan and representative Vietnamese strings passed;
current-document Markdown links resolved. Final source imports/checks remain as
recorded in the release receipt; subsequent changes were docs/CI/plotting only.
HEAD remains the initial commit, with no staged diff. Git status refreshed index
stat-cache bytes; staged entries and tracked blob identities were not altered.
Open http://127.0.0.1:5173/#research. API http://127.0.0.1:8010/docs.

## Limits and next research work

Synthetic scope only. No real survey/behavior calibration or REAL_WORLD_VALIDATED.
Exact routing covers at most ten service points as a closed tour, followed by exit
choice. T2 assigns each category to one shelf; T3 one SKU block/level/face. Finite
candidate selection is not global optimization. Large executed scalability is
T1-only, not a full large integrated solve. E06 changes arrival rate and picker
count together; E02/E07/E09 do not demonstrate treatment improvement. Runtime/RSS
are measurements on this machine; polling can miss short memory spikes.

Docker/psql are absent from PATH; PostgreSQL/Compose remain unverified. A Windows
GitHub Actions workflow was authored, with browser installation; it was not pushed
or run remotely. These do not block the declared SQLite synthetic target.
Next research: collect licensed real inputs/calibration, isolate sensitivity
factors, broaden independent instances/seeds, test integrated large cases within
declared budgets, and verify deployment/parallel scheduling when required.
