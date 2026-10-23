# API validation and surface audit

> Bản tóm lược được biên tập ngày 23/10/2026. Kết quả dưới đây thuộc lần kiểm chứng ngày 22/10/2026, không phải lần chạy mới. Báo cáo nguyên bản và định vị bản lưu: [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md).

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Audit baseline Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; original report retained in the external historical archive.

Real FastAPI requests against a separate native MongoDB database passed. E/api-surface.json includes the complete OpenAPI paths, seven JSON exports, four CSV export/import roundtrips (revision 11), 404 for missing project/unknown section and 422 for unsupported format. Command `.venv/Scripts/python.exe scripts/system_audit_surface.py`, exit 0. It performs no numerical job and never writes the primary database.

E/full-regression/checks/invalid-input-matrix.json records missing required fields where required, extra fields for all seven groups, unknown category, negative dimensions, duplicate SKU, unchanged documents after rejected writes and stale revision 409. Pydantic validation does not silently discard unknown keys. Cross-reference/contract tests cover additional malformed data. Real refused TCP connections return a bounded sanitized 503 with `DATABASE_UNAVAILABLE` and Retry-After; see BUG_REPORT.md.

| Method | OpenAPI path |
|---|---|
| GET | `/api/research/datasets` |
| GET | `/api/research/configurations` |
| GET | `/api/research/campaigns` |
| POST | `/api/research/campaigns` |
| GET | `/api/research/campaigns/{identifier}` |
| GET | `/api/research/campaigns/{identifier}/jobs/{job_key}/joint` |
| POST | `/api/research/campaigns/{identifier}/cancel` |
| POST | `/api/research/campaigns/{identifier}/resume` |
| POST | `/api/research/campaigns/{identifier}/replay` |
| GET | `/api/research/campaigns/{identifier}/report/{relative}` |
| GET | `/api/health` |
| GET | `/api/schemas` |
| GET | `/api/projects/{identifier}/inputs/{section}/export` |
| POST | `/api/projects/{identifier}/inputs/{section}/import-csv` |
| GET | `/api/projects` |
| POST | `/api/projects` |
| GET | `/api/projects/{identifier}` |
| PUT | `/api/projects/{identifier}/inputs/{section}` |
| POST | `/api/projects/{identifier}/validate` |
| POST | `/api/projects/{identifier}/runs` |
| GET | `/api/projects/{identifier}/runs` |
| GET | `/api/runs/{identifier}` |
| POST | `/api/runs/{identifier}/cancel` |
| POST | `/api/runs/{identifier}/replay` |
| GET | `/api/runs/{identifier}/report` |

Frontend ownership: services/api.ts provides project/input/run/report calls; features/research/api.ts provides research dataset/config/campaign/joint/report calls. All 16 navigation pages render in fresh Playwright runs. The schemas endpoint remains available for programmatic clients. API schemas and contract snapshots are checked by the full regression suite. Project delete and cursor pagination are absent; list limits are bounded where implemented, not a claimed complete pagination system.

Reports validate stored input/result hashes before export; unknown formats return 422. Research artifact paths are confined to their campaign report roots, with traversal rejection in integration tests. HTTP adapters enqueue work; they do not run a solver synchronously. This is a local research API; see SECURITY limitations in DATABASE_AUDIT.md and FINAL_SYSTEM_AUDIT.md.
