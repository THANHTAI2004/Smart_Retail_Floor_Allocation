# Bugs, fixes and unsuccessful audit attempts

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Starting Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; changes remain uncommitted by instruction.
MongoDB Atlas: **OUT_OF_SCOPE**, never a failed or blocked gate. The parent attempt directory retains superseded receipts and before-fix logs; E/../ denotes that parent.

## BUG-01: MongoDB connection loss escapes the API

Severity: operational API failure (fixed). Root cause: HTTP adapters had handlers for service/validation errors but no PyMongo connection-failure handler. After startup, an actual refused TCP connection caused an uncaught ServerSelectionTimeoutError instead of a stable response. Correct reproduction: ../outage-before-02/stdout.log. ../outage-before was an earlier incorrect store-injection attempt that returned 200 and is not accepted as bug proof.

Fix: api/main.py handles PyMongo ConnectionFailure with HTTP 503, `DATABASE_UNAVAILABLE`, generic detail and Retry-After: 1; logs exception type only. It does not expose URI/password or convert arbitrary integrity/model errors into connectivity errors. New integration test `test_actual_database_disconnect_is_sanitized_503` replaces only the isolated API store's driver with a real refused loopback endpoint, checks elapsed <5 s and absence of URI. E/full-regression/checks/database-disconnect.json is the after receipt. Both full178-test Windows runs pass. Docker later stops its isolated DB container and verifies the same response, then recovers connectivity.

## BUG-02: imported datasets fail from an installed Docker package

Severity: research workflow blocked in Docker (fixed). The first real Compose attempt passed T1-T4 but its joint campaign failed with `ValueError: Imported dataset must be inside the repository datasets directory`. Before evidence is in the parent attempt's compose/research-readback/.requests directory and dataset-before.log. Root cause: generators.py derived DATASET_ROOT from five parent directories above __file__; that describes a source checkout but not site-packages.

Fix: resolve the datasets directory and relative import paths from application ROOT (SMART_RETAIL_HOME or the application working directory), then resolve/constrain the path before reading and checking its original SHA. No checksum or path-confinement check was removed. The new unit regression relocates the actual module into a site-packages-shaped directory, imports the real bundled dataset, and verifies an outside path is still refused. It fails before and passes after the fix. The final full suite has 178 tests; the final fresh Compose attempt additionally runs actual feedback/exact/hybrid campaigns from the installed package. Earlier 177-test/campaign evidence is retained but superseded for final-source acceptance.

## Audit harness corrections

The E2E output parameter originally joined an absolute path a second time. scripts/verify_e2e.ps1 now accepts absolute/relative paths; ../e2e-01 logs retain the failed attempt. The new UI test's direct-PyMongo helper initially used frontend as its cwd and could not load the ignored root private URI; ../e2e-02 retains 9 passed/1 failed. It now uses repository-root cwd; ../e2e-03 and E/e2e-final pass all 10 tests. These failures are not product numerical failures and are not erased.

Test/campaign prefix environment settings isolate all new audit DBs while preserving existing defaults. Long-path verifier accepts an audit-local temporary parent. Compose supports isolated audit DB prefixes and actual feedback/exact/hybrid/outage probes. No numerical algorithms/objectives were modified to improve benchmark outcomes.

Remaining warnings: one Starlette TestClient httpx deprecation warning in each backend suite; no failing/skipped backend tests. It concerns the test-client dependency transition, not a runtime result discrepancy. Python coverage was not measured. No open numerical-correctness bug was observed within the executed scope; see explicit model, security and endurance limits rather than interpreting that as a proof of bug absence.
