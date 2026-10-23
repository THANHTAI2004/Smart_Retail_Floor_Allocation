# End-to-end system acceptance matrix

> Bản tóm lược được biên tập ngày 23/10/2026. Kết quả dưới đây thuộc lần kiểm chứng ngày 22/10/2026, không phải lần chạy mới. Báo cáo nguyên bản và định vị bản lưu: [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md).

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Audit baseline Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; original report retained in the external historical archive.

All gates below PASS against the **stated bounded acceptance criteria**. Each limitation is part of the conclusion; this does not assert general production readiness. Overall status: **SYSTEM_VERIFIED_WITH_LIMITATIONS**.

| Gate | Area | Status |
|---|---|---|
| SYS01 | Architecture | PASS |
| SYS02 | Frontend UI | PASS |
| SYS03 | Seven input groups | PASS |
| SYS04 | API validation | PASS |
| SYS05 | MongoDB | PASS |
| SYS06 | Worker queue | PASS |
| SYS07 | T1 | PASS |
| SYS08 | T2 | PASS |
| SYS09 | T3 | PASS |
| SYS10 | T4 | PASS |
| SYS11 | T1-T4 integration | PASS |
| SYS12 | Recomputation | PASS |
| SYS13 | Feedback | PASS |
| SYS14 | Exact | PASS |
| SYS15 | Hybrid | PASS |
| SYS16 | Research runner | PASS |
| SYS17 | Reports/export | PASS |
| SYS18 | Replay | PASS |
| SYS19 | Failures | PASS |
| SYS20 | Compose | PASS |
| SYS21 | Security/isolation | PASS |
| SYS22 | Performance | PASS |
| SYS23 | Regression | PASS |
| SYS24 | Git/reproducibility | PASS |

## SYS01: Architecture — PASS

- Acceptance criterion / expected: No forbidden dependency/cycles or retired application execution.
- Test performed: Static graph + architecture unit tests.
- Actual result: 98 Python/40 frontend modules; no local cycles/forbidden imports.
- Source files: `scripts/verify_architecture.py; domain; engines` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/architecture.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Dynamic/external internals not proven.

## SYS02: Frontend UI — PASS

- Acceptance criterion / expected: Actual pages connected to real backend and rendered.
- Test performed: Playwright all 16 routes, result views and research workflow.
- Actual result: 10 browser tests pass; 16 page screenshots, no page errors/HTTP500.
- Source files: `frontend/src/app, pages, features` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/e2e-final/browser/results.json; e2e-final/browser/system-pages.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Desktop test viewport; not every browser/device/accessibility matrix.

## SYS03: Seven input groups — PASS

- Acceptance criterion / expected: Persist/reload all seven groups without silent changes.
- Test performed: UI/API saves + direct Mongo reads after each revision.
- Actual result: All seven groups MATCH after reload.
- Source files: `contracts/inputs.py; application/projects.py; frontend/src/features` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/full-regression/checks/seven-input-readback.json; e2e-final/browser/system-pages/verification.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Four tabular CSV groups; other groups JSON.

## SYS04: API validation — PASS

- Acceptance criterion / expected: Reject malformed/extra/cross-reference/stale input atomically.
- Test performed: Invalid matrix, schema/export probes.
- Actual result: 422/409/404 as defined; rejected document unchanged.
- Source files: `api/main.py; contracts` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/api-surface.json; full-regression/checks/invalid-input-matrix.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: No delete/cursor pagination API.

## SYS05: MongoDB — PASS

- Acceptance criterion / expected: Native auth persistence, CAS/index/overflow and restore.
- Test performed: Real native tests + container restart.
- Actual result: Roundtrip, indexes, backup corruption refusal PASS.
- Source files: `infrastructure/mongodb` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/long-path/full-short.xml; compose/verification.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: No replica failover test.

## SYS06: Worker queue — PASS

- Acceptance criterion / expected: Atomic ownership; bounded process; crash/cancel recovery.
- Test performed: Real worker crash during T4, lease recovery and stale publish rejection.
- Actual result: Timeout/cancel/lost-worker states and no invalid result PASS.
- Source files: `workers/runner.py; mongodb/run_repository.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/full-regression/checks; long-path/full-short.xml.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: No prolonged queue saturation.

## SYS07: T1 — PASS

- Acceptance criterion / expected: Geometry/access replay and immutable fixed shelves.
- Test performed: Five fixtures + invalid geometry tests.
- Actual result: Valid fixtures replay; oversized case classified honestly.
- Source files: `engines/t1_layout` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/numerical/t1-fixtures.json; long-path/full-short.xml.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Heuristic exhaustion is not infeasibility proof.

## SYS08: T2 — PASS

- Acceptance criterion / expected: Allocation/objective consistency with independent oracle.
- Test performed: Enumeration, fixed/proximity/capacity tests.
- Actual result: Oracle and assignment replay agree.
- Source files: `engines/t2_allocation` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/long-path/full-short.xml; pilot-campaign/records.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: MILP scope only.

## SYS09: T3 — PASS

- Acceptance criterion / expected: Physical packing/load/stock consistency.
- Test performed: Independent enumeration, tamper/property tests.
- Actual result: Valid packing agrees; corruption rejected.
- Source files: `engines/t3_slotting` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/long-path/full-short.xml; pilot-campaign/records.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: First-fit is heuristic.

## SYS10: T4 — PASS

- Acceptance criterion / expected: Route/order/time semantics independently reproduce.
- Test performed: Polyline arithmetic + quantity/time replay.
- Actual result: 16.7071067812 m and 33.9225889843 s manual reference agrees.
- Source files: `engines/t4_simulation` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/numerical/manual-route.json; long-path/full-short.xml.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Shelf queues, synthetic arrivals; no corridor dynamics.

## SYS11: T1-T4 integration — PASS

- Acceptance criterion / expected: Real upstream outputs feed downstream stages.
- Test performed: Worker baseline/integrated + independent campaign validation.
- Actual result: Real snapshots, stage artifacts, validated results and UI output.
- Source files: `application/workflow.py; stage_workflow.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/pilot-campaign; e2e-final/browser/results.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Finite declared workflow/model.

## SYS12: Recomputation — PASS

- Acceptance criterion / expected: Invalidate only dependencies; changed decisions cannot reuse stale result.
- Test performed: Actual T1/T2/T3 actions + routing key/reuse checks.
- Actual result: All required downstream stages invalidated; identities recorded.
- Source files: `application/feedback/evaluator.py; infrastructure/stage_cache.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/numerical/feedback-action-T1.json; feedback-summary.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: No infinite cache-retention study.

## SYS13: Feedback — PASS

- Acceptance criterion / expected: Multiple actual strict improvements, bounded stop and rollback.
- Test performed: 5 accepted iterations, invalid proposals and local trap.
- Actual result: Score 0.0770710678 -> 0.0070710678; stop at 60 evaluations.
- Source files: `application/feedback` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/numerical/feedback-multiloop.json; feedback-summary.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: No global claim or universal improvement guarantee.

## SYS14: Exact — PASS

- Acceptance criterion / expected: Finite proof verified independently; false certificates rejected.
- Test performed: Four-state oracle, ties/infeasibility/partial search and 8 attacks.
- Actual result: Complete certificate gap zero; all attacks rejected.
- Source files: `engines/joint_exact` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/long-path/full-short.xml; joint-campaign.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Only declared finite SAA space/objective.

## SYS15: Hybrid — PASS

- Acceptance criterion / expected: Valid incumbent/bounds/budgets and holdout semantics.
- Test performed: Hybrid fresh two-seed jobs + HTTP/Docker + unit limits.
- Actual result: Bound/certificate statuses retained and verified.
- Source files: `application/feedback/coordinator.py; joint_exact` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/joint-campaign; compose/verification.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Finite certification only if complete.

## SYS16: Research runner — PASS

- Acceptance criterion / expected: New seeded campaign, real worker/checkpoint/resume.
- Test performed: 38 pilot + 10 joint jobs; pause after 3 and resume.
- Actual result: 48 original records retained; classifications explicit.
- Source files: `application/experiments` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/pilot-pause-proof.json; pilot-campaign; joint-campaign.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Not all full E01-E15 matrices executed.

## SYS17: Reports/export — PASS

- Acceptance criterion / expected: Real reports/downloads with verified hashes.
- Test performed: CLI analyze + HTTP/browser export + input roundtrips.
- Actual result: Fresh reports, CSV/JSON and path safety PASS.
- Source files: `reporting; application/experiments/reports.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/pilot-report; joint-report; api-surface.json; e2e-final.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Statistical power limited by two seeds.

## SYS18: Replay — PASS

- Acceptance criterion / expected: Fresh execution produces same scientific checksums/status.
- Test performed: 38 pilot + 10 joint replay jobs and comparisons.
- Actual result: Compare commands exit 0; stored snapshot identity enforced.
- Source files: `application/experiments/campaign.py; api/main.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/pilot-comparison.json; joint-comparison.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Different source identity deliberately rejected.

## SYS19: Failures — PASS

- Acceptance criterion / expected: Named bounded errors, no corrupt successful publish.
- Test performed: DB refused TCP/container outage, process crash, cancel/timeout, corrupt data.
- Actual result: Sanitized503 and validated failure states PASS.
- Source files: `api/main.py; workers/runner.py; serializers.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/full-regression/checks; compose/verification.json; long-path/full-short.xml.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: No OS-wide failure/replica election.

## SYS20: Compose — PASS

- Acceptance criterion / expected: Real isolated build/start/run/joint/restart/outage workflow.
- Test performed: Fresh compose verifier with unique project/database.
- Actual result: Real containers and all specified smoke checks PASS.
- Source files: `docker-compose.yml; scripts/verify_mongodb_deployment.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/compose/verification.json; commands/compose.stdout.log.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Local Docker Desktop; not public deployment.

## SYS21: Security/isolation — PASS

- Acceptance criterion / expected: No primary mutation, secrets or unsafe artifact paths.
- Test performed: Primary/artifact/index SHA readback, auth, path rejection, npm audit.
- Actual result: Business SHA/index intact; private files ignored.
- Source files: `mongodb/settings.py; experiments/service.py; .gitignore` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/preservation.json; commands/npm-audit.stdout.log.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: No application multi-user auth/public penetration audit.

## SYS22: Performance — PASS

- Acceptance criterion / expected: Bounded Tiny/Small/Medium, metrics and timeout behavior.
- Test performed: Three queued jobs + 30 real-Mongo ASGI reads + budget tests.
- Actual result: All three SUCCEEDED; CPU/RSS/stages/query/artifacts recorded.
- Source files: `workers/resources.py; scripts/system_audit_probes.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/numerical/performance.json; full-regression/checks/api-latency.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: No Large/endurance/leak/load-capacity certification.

## SYS23: Regression — PASS

- Acceptance criterion / expected: Fresh checks with no failures/skips.
- Test performed: Ruff/mypy/pip/lint/Vitest/build/audit; full pytest twice; HTTP repeats; E2E.
- Actual result: 178 passed twice, 4 Vitest, 10 browser; all commands exit0.
- Source files: `backend/tests; frontend/tests; scripts` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/commands/journal.json; long-path; e2e-final/browser/results.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: One TestClient deprecation warning; coverage not measured.

## SYS24: Git/reproducibility — PASS

- Acceptance criterion / expected: Preserve HEAD/index, record exact uncommitted identity and commands.
- Test performed: Index/head SHA, runtime SHA and patch/file manifest.
- Actual result: HEAD/index unchanged; uncommitted audited changes documented.
- Source files: `infrastructure/provenance.py; scripts/verify_system_audit.py` (under backend/src/smart_retail unless otherwise qualified).
- Evidence: E/preservation.json; verification.json; final-change-manifest.json; commands/journal.json.
- Exit code: 0 for the associated completed verification commands (E/commands/journal.json and supplemental E receipts); per-job failed/infeasible scientific outcomes remain in campaign records.
- Remaining limitation: Audit state not committed/pushed by explicit instruction.
