# Experiment readiness matrix — 22/10/2026

**Current status: EXPERIMENT_READY_SYNTHETIC; 15/15 ER gates PASS.**

Status is evaluated by `scripts/check_experiment_readiness.py` against the release
receipt, main/pilot manifests, independent validation, clean-environment replay
and actual reports. The JSON receipt is authoritative; this table is synchronized
from that evaluation. Target scope is controlled local Windows/Python 3.12/SQLite
synthetic experiments. It excludes production and real-world validation.

| Gate | Status | Acceptance condition and related implementation | Verification and evidence |
|---|---|---|---|
| ER01 | PASS | Modular source/dependencies; no forbidden imports/cycles; React shell/pages/state hooks | Release Ruff/mypy/architecture logs and architecture.json |
| ER02 | PASS | Seven versioned inputs, unit/FK validation, migration, JSON and lossless table CSV | Contract/regression tests; synchronized datasets/schemas; input CSV E2E |
| ER03 | PASS | T1 baseline/local search, independent geometry/topology/service replay | E01 main witnesses; exact geometry and disconnected-aisle regressions |
| ER04 | PASS | T2 greedy/MILP, hard constraints/soft affinity and independent enumeration | E02 main; allocation/affinity reference tests |
| ER05 | PASS | T3 first-fit/MIP, facing/orientation/load/packing replay and exact reference | E03 main; facing range/compatibility/stock enumeration tests |
| ER06 | PASS | T4 valid grid routes, exit connectors, finite pickers, periods and route policies | E04 main; exact-tour oracle, time/quantity/exit regressions |
| ER07 | PASS | Bounded integration, stage artifacts, dependency cache/rerun, timeout/cancel/retry | E05 main; cache tamper/invalidation and real process-failure retry tests |
| ER08 | PASS | Deterministic labeled generator, four published scales, scenario fingerprints | Generator property/contract checks; Tiny/Small/Medium/Large manifests |
| ER09 | PASS | Manifest-driven durable runner, checkpoint/resume without rewriting valid outcomes | Campaign main checkpoint; real resume/worker tests |
| ER10 | PASS | Failure-preserving summary, appropriate paired analysis, uncertainty and correction | statistics.json; duplicate-seed, singleton and degenerate-sample tests |
| ER11 | PASS | Current source/dependencies, hashes, scientific replay in clean compatible environment | Clean replay comparison; exact hashes vs atol=1e-8/rtol=1e-9 |
| ER12 | PASS | Fresh backend/frontend/E2E/static/dependency checks | docs/research/evidence/20261022-release-01/verification.json |
| ER13 | PASS | Actual CSV/JSON/Markdown, Matplotlib PNG/SVG and validated report hashes | experiments/reports/20261022-main-02/manifest.json |
| ER14 | PASS | Current scope, mathematics, protocol, guide, provenance, limitations and handoff | HOW_TO_RUN_EXPERIMENTS; CURRENT_STATE; DEPENDENCY_MAP; versioned model notes |
| ER15 | PASS | CLI pilot/main and dashboard connected to real runner, exports and replay | Release browser results, research screenshot and CLI campaign records |

Reproduce the evaluation after running the verification/campaign commands:

```powershell
.venv\Scripts\python.exe scripts/check_experiment_readiness.py --evidence docs/research/evidence/20261022-release-01 --campaign experiments/results/20261022-main-02 --pilot experiments/results/20261022-pilot-04 --comparison experiments/reports/20261022-clean-comparison-02.json --report experiments/reports/20261022-main-02 --output var/my-readiness.json
```

An ER PASS does not change the historical, broader research acceptance gates
from 21/10/2026. PostgreSQL/Docker remain unverified and S05/S06/S07 real survey,
licensing and calibration evidence is absent. No REAL_WORLD_VALIDATED claim.
