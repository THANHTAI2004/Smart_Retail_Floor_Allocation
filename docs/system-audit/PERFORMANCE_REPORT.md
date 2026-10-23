# Bounded performance and resource observations

> Bản tóm lược được biên tập ngày 23/10/2026. Kết quả dưới đây thuộc lần kiểm chứng ngày 22/10/2026, không phải lần chạy mới. Báo cáo nguyên bản và định vị bản lưu: [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md).

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Audit baseline Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; original report retained in the external historical archive.

Three actual queued worker jobs complete sequentially. Full measurements, including per-stage cache_hit/elapsed_s, enqueue/query times, CPU/RSS sampling and artifact size, are in E/numerical/performance.json and numerical/performance-artifacts. Wall times include child startup and publication. CPU/RSS are sampled child observations, not a continuous profiler; short stage times can quantize to zero on the Windows timer.

| Scale | Shelves/SKUs/orders | Wall s | Peak sampled child MiB | Sampled CPU s | Artifact bytes |
|---|---|---:|---:|---:|---:|
| tiny | 4/12/20 | 1.563 | 105.41 | 1.203 | 285298 |
| small | 12/48/100 | 1.687 | 109.82 | 1.156 | 1333546 |
| medium | 36/180/500 | 2.688 | 135.96 | 1.906 | 8013836 |

Queue delay (created timestamp to atomic claim epoch) and enqueue latency are retained separately. For each job 20 direct MongoDB project reads are timed, and stage receipts expose T1/T2/T3/T4 elapsed times and cache use. E/full-regression/checks/api-latency.json records 30 sequential ASGI requests with real MongoDB: mean 2.850 ms, p50 2.759 ms, p95 3.496 ms and max 3.572 ms. These are local ASGI measurements, not network-latency or concurrent-load benchmarks. RSS before/after is retained without inferring a long-duration leak verdict.

Feedback: 5 accepted changes, 60 evaluations, bounded termination. Exact/hybrid elapsed/resource fields are in joint campaign records. Queue timeout/cancel/crash tests and isolated Compose outage tests demonstrate bounded termination and recovery; 9 MiB project rejection and GridFS tests address BSON limits. Cache tests demonstrate reuse/invalidation consistency, not indefinite storage reclamation.

**Limits:** No uncontrolled Large run, long-duration leak test, sustained queue saturation, unlimited cache growth study, multi-user throughput or resource-starvation stress was performed. The bounded Tiny/Small/Medium results and functional termination checks PASS. Large and endurance claims are **NOT_APPLICABLE to this bounded audit**, not asserted successful. These limits do not prevent the explicitly defined synthetic campaigns from running; they prevent a general production capacity claim.
