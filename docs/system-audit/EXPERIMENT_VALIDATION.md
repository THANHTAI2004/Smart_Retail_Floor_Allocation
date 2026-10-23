# Research campaigns, reports and replay

> Bản tóm lược được biên tập ngày 23/10/2026. Kết quả dưới đây thuộc lần kiểm chứng ngày 22/10/2026, không phải lần chạy mới. Báo cáo nguyên bản và định vị bản lưu: [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md).

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Audit baseline Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; original report retained in the external historical archive.

New campaigns were executed sequentially against isolated MongoDB databases under this audit. Seeds are **11 and 23**. Evidence is new and is not copied from prior release counts.

| Campaign | Actual job records | Actual statuses | Experiments |
|---|---:|---|---|
| pilot | 38 | {'SUCCEEDED': 38} | E01, E02, E03, E04, E05, E06, E07, E08 |
| joint | 10 | {'SUCCEEDED': 10} | E13 |

The pilot first stops after 3 jobs (PAUSED_PARTIAL), then resumes to 38/38 completed with no jobs omitted; E/pilot-pause-proof.json proves the intermediate state. Resume uses persistent checkpoints/attempt identities rather than silently starting a new unrelated campaign. Replay executes all 38 pilot jobs and all 10 joint jobs afresh, then CLI compare produces E/pilot-comparison.json and joint-comparison.json. Scientific checksums exclude wall-clock/cache telemetry. Failed/infeasible instances are retained and compared by status/reason; they are not manufactured into success or dropped from report denominators.

All 16 experiment configuration JSON files are schema-validated in E/configuration-inventory.json. This is configuration validation, not a claim that all full E01-E15 scale/seed matrices were executed. Pilot execution covers its explicitly configured subset; joint execution covers joint certification. Published historical benchmark results are unchanged. Small two-seed audit campaigns demonstrate execution/replay, not statistically powered scientific superiority.

E/pilot-report and E/joint-report contain freshly generated artifacts. HTTP/browser tests run a real research child and fetch audited report files, certificate/trace views and exports. Safe-path tests refuse traversal. A result hash is checked before report export. Pause/resume/replay/report commands and exact argv, UTC timestamps, exit codes and logs are in E/commands/journal.json. CLI and HTTP paths use the same campaign/application implementation.

Dataset generators tag synthetic origin and retain generated input artifacts. Independent validation replays geometry, allocation, physical packing, route/time/order semantics for successful candidate runs. Records contain run ID, input/result SHA, seed, treatment, status, stage errors and resource metrics. No field is populated with a mock numerical result.
