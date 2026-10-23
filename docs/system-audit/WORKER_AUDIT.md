# Durable queue and worker audit

> Bản tóm lược được biên tập ngày 23/10/2026. Kết quả dưới đây thuộc lần kiểm chứng ngày 22/10/2026, không phải lần chạy mới. Báo cáo nguyên bản và định vị bản lưu: [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md).

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Audit baseline Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; original report retained in the external historical archive.

Source: workers/runner.py and infrastructure/mongodb/{run_repository,worker_repository}. Application enqueue writes a frozen complete snapshot with project revision, source/dependency identity and checksum. The worker atomically claims a queued row and supervises a spawned numerical process. Stage artifacts and final receipt record input/result hashes, timings, child exit, sampled CPU/RSS, budget, status and errors.

Fresh full regression includes integration/test_worker_control.py, test_worker_wall_time.py, test_system_audit.py and test_mongodb_persistence.py. Evidence: E/long-path/full-long.xml and full-short.xml; E/full-regression/checks/real-worker-crash.json (exact receipt name can also be found in checks/). Tests cover success, user cancellation, hard wall timeout during T4, memory/process supervision, expired leases, concurrent claims, immutable input, source drift and stale worker publication fencing. No successful result is published after timeout/cancel or by an expired owner.

The new crash test launches a real isolated CLI worker, observes T4, kills only the recorded owned PID tree, expires that run's lease and starts recovery. Expected/actual: TIMED_OUT with WORKER_LOST, no result; the former owner cannot publish. Main service PIDs and DB are untouched. This is process-crash recovery, not a mock exception. Compose separately restarts only audit API/worker containers and verifies stored result SHA and recovery.

Long numerical work is killable; API requests return queued rows promptly. Feedback evaluation/iteration/action budgets and exact finite-state budgets stop repeated search. A missing progress sample is tolerated rather than interrupting supervision. Cache is content-addressed and correctness is tested across changed inputs; no assertion of unlimited-run cache storage reclamation is made. Queue admission is not a multi-tenant quota system. Long-duration queue saturation/resource starvation and operating-system failure injection are not certified by this bounded run.
