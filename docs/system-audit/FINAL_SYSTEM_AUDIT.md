# Final system audit

> Bản tóm lược được biên tập ngày 23/10/2026. Kết quả dưới đây thuộc lần kiểm chứng ngày 22/10/2026, không phải lần chạy mới. Báo cáo nguyên bản và định vị bản lưu: [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md).

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Audit baseline Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; original report retained in the external historical archive.

**SYSTEM_VERIFIED_WITH_LIMITATIONS**

The defined synthetic research path is freshly verified: INPUT -> FRONTEND -> API -> MONGODB -> WORKER -> T1 -> T2 -> T3 -> T4 -> FEEDBACK/EXACT/HYBRID -> RESULT -> DATABASE -> FRONTEND -> REPORT -> REPLAY. See [the 24-gate matrix](END_TO_END_ACCEPTANCE.md) for exact criteria, actual results, sources and limitations.

Two product bugs were reproduced and fixed: installed-package dataset roots now resolve against application home, and MongoDB connection loss now returns sanitized HTTP503 rather than an uncaught driver exception. No engine algorithm/objective was changed. New tests cover seven direct readbacks, invalid input atomicity, oversized project rejection, real refused connection, bounded API sampling, real T4 worker process death and 16-page browser traversal. Audit namespace and output controls keep all new tests outside the main DB.

| Fresh backend run | Tests | Failures | Errors | Skipped | Seconds |
|---|---:|---:|---:|---:|---:|
| full-long | 178 | 0 | 0 | 0 | 59.526 |
| full-short | 178 | 0 | 0 | 0 | 59.099 |
| http-repeat-1 | 2 | 0 | 0 | 0 | 16.605 |
| http-repeat-2 | 2 | 0 | 0 | 0 | 16.709 |
| http-repeat-3 | 2 | 0 | 0 | 0 | 16.703 |

Additional fresh checks: Ruff, mypy, pip check, ESLint, 4 Vitest tests, frontend build, npm audit, architecture, actual Docker Compose build/start/workflow/joint/restart/outage, and 10 Playwright tests. The full suites emit one Starlette TestClient/httpx deprecation warning per run. There is no measured coverage percentage. Exact argv, timestamps, exit codes and logs are E/commands/journal.json and supplemental-journal.json; long-path commands are nested in E/long-path/verification.json. Supplemental probes are documented in their topic reports.

Experiments: 38 new pilot jobs (pause after 3, resume), 10 joint jobs (five modes x two seeds), then 48 fresh replay jobs and checksum comparisons. All 48 original and 48 replay jobs SUCCEEDED; negative/failure behavior is exercised separately by regression tests. All 16 configurations validate; this does not claim all full E01-E15 campaigns have been rerun. Reports are generated in new audit directories. Feedback probe shows 5 accepted iterations and independently checked dependency recomputation; exact unit oracle covers all four finite states and eight proof attacks.

Primary data preservation: unchanged 17 projects/8 runs and business SHA, 32 original artifact checksums, all 57,693 historical research file checksums (1,447,827,887 bytes), external legacy backup SHA and Git index/HEAD. During that audit: no main MongoDB/app restart, data replacement or historical result overwrite. E/preservation.json retains the readback evidence; E/final-change-manifest.json and audited-source-changes.zip preserve the final uncommitted change set. The original main services can still have the prior modules loaded because this task deliberately did not restart them; audited code was loaded by isolated test services and Compose. A future normal app restart is needed to serve the new 503 handler in the user's existing main process.

Limits preventing a stronger status:

- Synthetic T4 assumptions, shelf queues and finite routing/optimization scopes; no empirical store-trajectory calibration or unrestricted continuous global proof.
- Two-seed audit campaigns are execution/replay checks, not statistically powered comparative research; full E01-E15 matrices were not executed.
- Bounded Tiny/Small/Medium and local ASGI measurements; no sustained leak/queue-starvation/load-capacity guarantee or Large benchmark.
- Local research application security scope; no multi-user API authorization/public deployment acceptance or replica failover test.
- Desktop browser scope; no exhaustive device/accessibility/browser matrix and no line/branch coverage measurement.

These limits do not block running the defined synthetic experiments. No observed serious remaining fault corrupted results, lost primary data or blocked that workflow. All large artifacts/logs remain in ignored var; the 13 topic reports are versionable source documents. No historical release document has been overwritten. The audit baseline Git HEAD names the baseline only; the source SHA above and E/preservation.json capture the audited uncommitted change set.

Reproduction: use README environment setup and existing MongoDB; choose a **new** audit ID/prefix/output for every run. Run scripts/verify_system_audit.py with a new state JSON; scripts/system_audit_probes.py and system_audit_surface.py produce supplementary receipts. Do not reuse basetemp/output directories containing evidence. The controller runs expensive phases sequentially. Never point audit writes at smart_retail or replace historical result files.
