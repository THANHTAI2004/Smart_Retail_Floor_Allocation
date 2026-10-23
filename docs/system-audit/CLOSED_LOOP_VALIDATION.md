# Closed-loop feedback and recomputation

> Bản tóm lược được biên tập ngày 23/10/2026. Kết quả dưới đây thuộc lần kiểm chứng ngày 22/10/2026, không phải lần chạy mới. Báo cáo nguyên bản và định vị bản lưu: [hồ sơ lưu trữ](../architecture/HISTORICAL_ARCHIVE.md).

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Audit baseline Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; original report retained in the external historical archive.

Source: application/feedback/{coordinator,evaluator,neighborhood,diagnostics,state}. Fresh probe command: `.venv/Scripts/python.exe scripts/system_audit_probes.py --output var/system-audit/20261022-afbb7971/final/numerical --prefix sr_system_audit_afbb7971_`, exit 0; logs E/numerical-probes.stdout.log and numerical-probes.stderr.log.

E/numerical/feedback-summary.json proves actual T1_MOVE, T2_REASSIGN and T3_FACE decisions change their respective decision hashes and pass full validation. T1 invalidates all four stages; T2 invalidates T2/T3/T4; T3 invalidates T3/T4. Exact before/after decisions and stage data are retained in feedback-action-T*.json. Evaluated action examples include worse candidates; evaluation is not acceptance. The coordinator only accepts a valid strict improvement and cannot mutate the incumbent on rejected proposals.

The separate multi-loop execution accepted **5** improvements across iterations [1, 2, 3, 4, 5], score **0.07707106781186548 -> 0.007071067811865476**, ending **EVALUATION_LIMIT** after 60 evaluations. Every accepted step is checked for strict descent. Weights and common random seeds remain fixed. E/numerical/feedback-multiloop.json retains the full trace. A distinct T3-only local-trap run ends CONVERGED_LOCAL without claiming global optimality.

Fresh unit tests also cover invalid proposal rollback, immutable snapshot independence, changed T4 routing identity, initial T3 infeasibility causing a real T2 feasibility repair, cancel between iterations retaining the verified best snapshot, and hybrid held-out evaluation. Joint campaigns execute feedback on two seeds and export traces; E/joint-replay confirms reproducible scientific hashes. Limits: the improvement shown is a constructed finite synthetic case; no universal performance-improvement guarantee follows from it.
