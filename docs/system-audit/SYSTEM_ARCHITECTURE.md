# System architecture audit

> Bản tóm lược được biên tập ngày 23/10/2026. Kết quả dưới đây thuộc lần kiểm chứng ngày 22/10/2026, không phải lần chạy mới. Báo cáo nguyên bản và định vị bản lưu: [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md).

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Audit baseline Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; original report retained in the external historical archive.

The application is the modular monolith in `frontend/` and `backend/`. No retired application is executed. Static analysis found 98 Python modules and 40 frontend modules, no local import cycles, no prohibited domain/engine imports and no retired-tree dependency. Evidence: E/architecture.json; command `architecture`, exit 0.

| Responsibility | Source | Input and output |
|---|---|---|
| Workspace UI | frontend/src/app, pages, features | Validated form state -> API; persisted project/run/report -> rendered pages |
| HTTP adapter | backend/src/smart_retail/api/main.py, research.py | Pydantic requests -> application services; named HTTP errors |
| Project application | application/projects.py | Sections/revisions -> cross-reference validation, immutable queued snapshots |
| Workflow coordinator | application/workflow.py, stage_workflow.py | Snapshot -> T1/T2/T3/T4 candidates and independent replay |
| Feedback coordinator | application/feedback | Diagnostics/actions -> validated complete decision candidates |
| Exact engine | engines/joint_exact | Declared finite decision space -> exhaustive certificate; separate verifier |
| Persistence | infrastructure/mongodb | Native PyMongo documents, atomic claims/revision CAS, GridFS payloads |
| Durable worker | workers/runner.py | MongoDB queue -> killable spawned child -> fenced result publish |
| Experiments/reporting | application/experiments, reporting | Seeded dataset/config -> checkpoint, independent validation, report and replay |

The static graph is an application import analysis, not a proof about external package internals or arbitrary dynamic imports. Unit architecture checks additionally enforce engine isolation. Independent validators intentionally repeat constraints without trusting optimizer output; this is useful independent validation, not accidental duplicate workflow orchestration. API routes delegate numerical work; engines neither import MongoDB/FastAPI nor select the end-to-end workflow.

UI wiring was executed, not inferred from source alone: E/e2e-final/browser/system-pages/verification.json records 16 routes and actual MongoDB readback; fresh research HTTP and browser suites run child processes and download reports. `GET /api/schemas` is a programmatic schema endpoint, not consumed by current UI forms. Delete-project and cursor pagination routes are not implemented and are not claimed as tested UI features. No unused-code deletion was attempted: public schema/export helpers and independent validators must not be removed on a keyword-only inference.

Boundary limits: local application imports and the defined synthetic research workflow are verified. This is not a general proof that every branch is reachable or a full dead-code certification. No coverage percentage was measured.
