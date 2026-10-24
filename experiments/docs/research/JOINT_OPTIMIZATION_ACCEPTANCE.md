# Joint optimization acceptance

Status: **JO01-JO18 PASS** for the declared bounded synthetic/local scope. Assessed from actual release/campaign/proof receipts; no general optimality proof is claimed.

**CLOSED_LOOP_FEEDBACK_READY**

**JOINT_EXACT_SMALL_INSTANCE_CERTIFIED** (explicit four-state and 128-state numerical models)

**JOINT_GENERAL_OPTIMALITY_NOT_PROVEN**

| Gate | Criteria | Status | Evidence command / required evidence |
|---|---|---|---|
| JO01 | Explicit joint decisions, finite scope, scenarios and common objective | PASS | Explicit finite domains and fixed scenario objective; formulation; contract/reference proofs |
| JO02 | Immutable state snapshots and lineage trace | PASS | Frozen content-sealed snapshot and mutation/rollback regression; JOINT_STATE artifacts |
| JO03 | T4 diagnostics use only modeled observations | PASS | Real simulated visits/picks/queue diagnostics with declared attribution proxies |
| JO04 | Actual valid unlocked T1 edits | PASS | Real valid T1 edits and independent constraint replay; action traces |
| JO05 | Actual valid category reassignment/swap | PASS | Real valid T2 edits and independent constraint replay; action traces |
| JO06 | Actual valid physical planogram edits | PASS | Real valid T3 edits and independent constraint replay; action traces |
| JO07 | Dependency-sensitive cache reuse/invalidation | PASS | Observed unchanged upstream and changed downstream content keys for actual T1/T2/T3/T4 edits |
| JO08 | Multiple bounded feedback iterations | PASS | Multiple actual improving E11 iterations and strict-descent tests |
| JO09 | Rollback, cancellation, resource/evaluation budgets | PASS | Rollback, iteration/evaluation limits, actual process cancellation/RSS/wall supervision regressions |
| JO10 | Independent joint witness replay | PASS | Every successful recorded job independently replays official physical and route witnesses |
| JO11 | Complete exact finite search | PASS | Hand-authored four-state oracle, 128-state model, one-state/tie/infeasible tests |
| JO12 | Valid UB/LB and complete proof evidence | PASS | Complete certificates, validated UB and valid zero LB for partial search; timeout tests |
| JO13 | Separate verifier rejects tampering | PASS | Resealed tampering rejection plus independent offline verifier receipt |
| JO14 | Feedback local plateau distinguished from finite optimum | PASS | Local plateau distinguished from strictly better exact finite solution in E13 |
| JO15 | Real E11-E15 campaigns with failure retention/holdout | PASS | Executed E11-E15, immutable identities, report hashes and failure-preserving records |
| JO16 | Real dashboard, convergence, decision views and exports | PASS | Real browser campaign/proof/convergence/decision views and trace/certificate exports |
| JO17 | Full regression on final source | PASS | Fresh full release commands, source identity, immutable receipt hashes |
| JO18 | Reproducible final identities/results | PASS | 15/15 E13 and 9/9 improving E11 exact scientific-result and input hashes in separate pinned Python environment |

Final assessment must cite the actual fresh command receipts, accepted finite
scope, unexecuted cases and limitations. Previous ER01-ER15 receipts describe the
previous source and remain historical evidence.

## Executed commands and source scope

- Release: `.venv/Scripts/python.exe scripts/verify_experiment_release.py --output docs/research/evidence/20261022-joint-release-03`.
- Full post-control regression: `python -m pytest backend/tests -q --basetemp var/pytest-joint-final-154 --junitxml docs/research/evidence/20261022-joint-final-regression/pytest.xml` (command receipt records actual executable).
- Focused 20-case controls: `python -m pytest backend/tests/unit/test_joint_optimization.py -q`; XML/logs under evidence/20261022-joint-controls-01.
- Campaigns: `python -m smart_retail.application.experiments.cli run --config experiments/configs/joint_<design>.json --output experiments/results/20261022-joint-<design>-02`, then analyze to corresponding reports. Six designs: effectiveness, ablation, certification, certification_128, scalability, holdout. Exact paths in the readiness receipt.
- Independent proof CLI: command in HOW_TO_RUN_JOINT_OPTIMIZATION.md; actual PASS receipt evidence/20261022-joint-proof-cli-02.json.
- Separate pinned venv: replay final E13 to experiments/results/20261022-joint-clean-replay-02; compare receipt experiments/reports/20261022-joint-clean-comparison-02.json has 15/15 input/result SHA and numeric matches.
- Evaluator: `.venv/Scripts/python.exe scripts/check_joint_readiness.py --release docs/research/evidence/20261022-joint-release-03 --output var/my-joint-readiness.json` (output must be new).

Machine-readable assessment: [20261022-joint-readiness-02.json](evidence/20261022-joint-readiness-02.json).
The evaluator verifies release/report/campaign hashes, current source/dependency
identity, named executed tests, independent certificate statuses and replay results.

## Limits retained with PASS

- JO08: Local convergence only within examined, possibly truncated neighborhood.
- JO11: Finite explicitly listed decision domains only.
- JO12: Exact comparison of serialized numerical simulation observations, not real arithmetic.
- JO13: Verifier shares official model physics/simulation; separately enumerates and selects minimum.
- JO15: E14 bounded Small-scale sweep; E15 synthetic holdout only; three independent job seeds per arm.
- JO18: Same Windows machine; no cross-platform/real-store validation.

No branch-and-bound acceleration, continuous geometry proof, complete global
Pareto set, Large full integrated scalability, cross-OS certification or actual
store validation is asserted. Local descent can stop on plateaus. T2/T3 actions
are valid and tested but did not improve the published E12 fixture. A solver's
unverified raw complete-search status never authorizes the UI global proof label.
For final measurements see JOINT_OPTIMIZATION_RESULTS_20261022.md.

Final source: release-03 has 155 pytest / 4 Vitest / 9 Playwright PASS.
All six suffix-02 campaigns completed (69/69 successful jobs); two separate
no-incumbent controls remain FAILED/INFEASIBLE with no false success. All 12
main exact/hybrid certificates independently verified; 4-state and 128-state
offline CLI proof replay also passed. The improving E11 replay matches 9/9 in
addition to the E13 15/15 comparison. No current backend source drift was detected.
