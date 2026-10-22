# Final release report — 2026-10-22

**RELEASE_READY_WITH_EXTERNAL_BLOCKERS**: Windows long-path support and real local
MongoDB/Docker Compose verification pass. Atlas lacks an authorized connection
URI; no Atlas live success is claimed. Remote CI and live UNC share verification
were not executed. Local release checkpoint details are in the Git audit receipt.

## Windows long paths

Root cause reproduced from pre-edit source: StageCache normalized os.link only;
temporary write failed at 286 characters under an existing 244-character root.
Shared filesystem normalization now covers roots before mkdir, exists, read,
temporary write, link, replace and cleanup. Windows drive/UNC syntax and Unicode
are preserved; POSIX paths stay native. Logical campaign path identity remains
unchanged. No numerical algorithms or cache/scientific checksum formats changed.

Changed boundaries: infrastructure/filesystem.py and stage_cache.py; worker
artifacts/progress/spawn; experiment storage/campaign/HTTP/report/replay; independent
certificate CLI. Immutable publication completes the temporary file before the
atomic no-overwrite link. Unsupported links fail explicitly; no overwrite fallback.

Six new regression cases cover actual deep unprefixed Unicode paths, repeat reads,
checksum tampering, existing cache, concurrent writers, cleanup, failed link,
subprocess spawn and syntax conversion. Final long suite: **171 passed**, zero
failed/skipped, 350-character logical base. Short contrast: **171 passed**, zero
failed/skipped, 50-character base. Both reported HTTP failures passed in each of
three independent deep-path runs. Live UNC I/O is NOT_APPLICABLE without a share;
UNC syntax is covered. See [root cause](WINDOWS_LONG_PATH.md) and
[commands/timestamps/exits](evidence/20261022-longpath-03/verification.json).

## Installed tools and Docker Compose

Installed Docker Desktop **4.96.1**, Docker CLI/engine **29.9.2**, Compose **v5.6.0**
and WSL **2.7.13.0** through official pinned WinGet packages. WSL required elevated
WinGet/UAC. Engine started without reboot or BIOS changes. `yaml@2.8.1` is isolated
under ignored var/release-tools for static inspection. Initial installer attempts
and the rejected direct command are historical in
[tool receipt](evidence/tool-installation.json); safe package-manager installation
subsequently completed successfully.

Command: `powershell -NoProfile -ExecutionPolicy Bypass -File
scripts/verify_mongodb_compose.ps1 -Output docs/release/evidence/20261022-compose-06`.

**PASS on real Docker**: Compose config, image builds, authenticated MongoDB,
readiness/indexes, API/worker/frontend, seven input groups, T1–T4 result/report/SHA,
restart persistence, queued cancellation and expired-worker recovery. UUID test
project/database, random test credentials, free loopback ports, independent named
volumes and network were used. docker inspect independently confirmed isolation
and no published MongoDB port. Test services stopped; volumes and sanitized logs
retained. No down -v, production DB reuse or unrelated container deletion.

Final receipt: [Compose](evidence/20261022-compose-06/verification.json),
[actual isolation](evidence/compose-isolation.json).
Earlier failed attempts remain with their reasons; final suffix-06 supersedes them.
See [deployment setup](DEPLOYMENT_VERIFICATION.md).

## Atlas

**BLOCKED_ATLAS_CREDENTIALS**. No MONGODB_ATLAS_URI was supplied. The verifier
requires SRV and validated TLS and creates a fresh UUID test namespace. Its live
path covers CRUD/revision CAS/indexes/queue/spawned worker/result SHA/reconnect and
deletes only documents it created. Code readiness and secret controls do not imply
Atlas authentication/CRUD/queue PASS. Receipt:
[Atlas](evidence/20261022-atlas-01/verification.json).

Run scripts/verify_atlas_connection.ps1 after configuring the URI privately, a
database user with test permissions and the client network allowlist. No production
migration to Atlas was attempted. Account/credentials cannot be supplied by software
installation. The Atlas live path remains unverified until such access is available.

## Software quality and numerical regression

| Current-source verification | Result |
|---|---|
| Full backend long/short | 171 PASS in each; zero failures/skips |
| Final release backend | 171 PASS |
| Ruff / mypy | PASS, 98 Python modules checked |
| pip check / npm audit | PASS |
| ESLint / frontend build | PASS |
| Vitest | 4 PASS |
| Playwright on isolated real MongoDB | 9 PASS |
| MongoDB health / owned services | PASS, worker online |
| New sequential + feedback + exact campaign | 3/3 SUCCEEDED, independent witnesses PASS |
| New replay / scientific input+result SHA | 3/3 identical, numeric comparison PASS |
| Independent certificate CLI | PASS |

Commands and outcomes: [quality receipt](evidence/20261022-release-quality-01/verification.json),
[independent proof](evidence/20261022-proof-command.json),
[scientific comparison](../../experiments/reports/20261022-release-joint-comparison-01.json).
Final backend identity matches quality receipt, both new campaign identities and
the current source. One Starlette/httpx deprecation warning remains. Historical
165/164-test receipts describe earlier source; they are not new-source validation.

Campaign/report outputs use new names. Finite-instance proof does not establish
general global optimality or field effectiveness. No large historical study was
rerun merely to inflate the test count.

## Research/data preservation

Original MongoDB data still matches verified restored data: **16 projects / 8 runs**.
All **32 original artifact hashes** remain identical. Representative historical
scientific manifests verify unchanged. SQL bytes/scripts were already retired by
the user's prior instruction; their verified external backup and decoded MongoDB
history remain available. No SQL fallback was restored.

Large generated outputs are retained locally and additionally archived externally:
**57,693 files / 1,447,827,887 original bytes**, with every ZIP member SHA readback.
Archive and external manifest identity:
[research preservation](evidence/research-preservation.json).
This retains research evidence without putting the raw output tree into Git.
Local reconciliation: [data/science](evidence/local-data-and-science.json).

## Git and reproducible handoff

Initial branch main, HEAD 85add59f11ca48265e7613c9f09747b80eaaec3b. Existing dirty
changes were the authorized MongoDB-only retirement. Source/tests/contracts/configs,
reports and acceptance evidence are reviewed together with that prerequisite.
Generated experiment outputs and private runtime stores remain ignored and intact.
No broad ignore of experiments or docs. Secret scan runs before and after staging.

See [source inventory](GIT_SOURCE_INVENTORY.md), concrete git check-ignore assertions
and staged blob audit under evidence/git-audit-01. The previous explicit Git
authorization permits local checkpointing; the new prompt forbids GitHub push.
No remote push, reset, clean, amend or history rewrite is performed.

Clean Windows setup is documented in README: install pinned Python dependencies,
backend editable package, native MongoDB or private URI, then setup/start scripts.
Docker setup now also has an exercised isolated verification script. Raw scientific
artifacts have explicit external retention and checksums. Final matrix and full
machine-readable gate fields: [acceptance](FINAL_RELEASE_ACCEPTANCE.md).

Source checkpoint: `cbe15bb9dc5fcb4d1de1f3949ee4855159699b9c`. A git archive of
that tracked source was extracted to a new local directory; API startup, project
creation and MongoDB health passed in a fresh isolated namespace using the pinned
existing Python environment. [Clean-source receipt](evidence/clean-source-checkout.json).
This validates source completeness, not a separate fresh dependency installation.
Final matrix totals: **37 PASS, 0 FAIL, 5 BLOCKED**, all five live Atlas gates.

Remaining required external work: provide Atlas test access, then run its live
verifier. Optional additional validation: remote CI and a real UNC share. Current
application is running at http://127.0.0.1:5173/#research with MongoDB worker online.
