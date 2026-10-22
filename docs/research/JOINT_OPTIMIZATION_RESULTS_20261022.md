# Executed joint optimization results - 2026-10-22

Scope: synthetic Windows/SQLite experiments with the fixed numerical model in
[the formulation](JOINT_OPTIMIZATION_FORMULATION.md). Status is assessed from
[JO01-JO18](JOINT_OPTIMIZATION_ACCEPTANCE.md), not inferred from successful plots.

## Reproducible source and verification

The final release receipt is
`docs/research/evidence/20261022-joint-release-03/verification.json`: all ten checks
passed, including **155 pytest, 4 Vitest and 9 Playwright**. Ruff/mypy, ESLint,
TypeScript/Vite build, pip consistency, npm audit and static import architecture
passed. Architecture covers 85 Python and 40 frontend modules, with no detected
cycles or retired dependency. No backend production source changed during the
final suffix-02 campaigns and separate-environment replay. Release-03 also verifies
the final T4 KPI and no-incumbent job inspection UI.

A final edge-case audit corrected the durable worker's handling of a result with
no incumbent and preserved the training incumbent when holdout time runs out.
Therefore suffix-01 campaigns/releases remain preliminary receipts; final
scientific evidence uses suffix-02. The two-job failure control confirms
FAILED/SEARCH_EXHAUSTED versus independently proved INFEASIBLE, with artifacts
retained and no false success. This is in addition to the 69 main jobs.

The first browser attempt received HTTP 409 because the preceding replay's report
supervisor was still finishing. Its output remains under `var/e2e-20261022-110605`.
Waiting for that real supervisor before launching the next campaign fixed test
sequencing; no browser assertions were disabled. All nine final cases passed.
Screenshots for exact/feedback decision inspection are in the release browser/ui.

## Designs and outcomes

Each campaign uses three independent job seeds (11/23/37) with two common training
scenario offsets (0/101). Each arm has the same 60 s hard child process budget,
fixed normalization and scenario set. Algorithms may stop before consuming their
budget. Scenario randomness is varied on fixed physical fixtures; this is not
independent store sampling. Reports retain all attempted failures and resource
outcomes, and do not infer population efficacy from fixture completion.

Campaign directories are `experiments/results/20261022-joint-<name>-02`; reports
use the corresponding names under `experiments/reports/`.

| Experiment | Name | Planned jobs | Design |
|---|---|---:|---|
| E11 | effectiveness | 9 | Sequential, bounded multistart, feedback on two shelves |
| E12 | ablation | 15 | No feedback, T1-only, T2-only, T3-only, combined |
| E13 | certification | 15 | Five modes on four-state local-trap model |
| E13 | certification-128 | 6 | Exact/hybrid on explicit 128-state joint model |
| E14 | scalability | 18 | Two baselines over local-trap, two-shelf and generated Small |
| E15 | holdout | 6 | Sequential/feedback with disjoint test scenario offsets |

The executed source, input files, config and dependencies are fingerprinted for
each campaign. Raw stage telemetry, process receipts, all scenario evaluations,
content-sealed JOINT_STATE snapshots and JOINT_EVENT traces remain available.
Report manifests hash every exported CSV/JSON/Markdown/PNG/SVG/certificate.

## Feedback effectiveness and ablation

E11 means over three job seeds:

| Treatment | Joint objective | Mean training route m | Child wall s | Evaluations |
|---|---:|---:|---:|---:|
| Sequential | 0.1026698103 | 7.7071067812 | 2.448 | 1 |
| Multistart | 0.1026698103 | 7.7071067812 | 2.922 | 3 |
| Feedback | 0.0598126675 | 1.7071067812 | 7.250 | 41 |

Feedback improves the common weighted objective by about **41.74%** on this
fixture. The selected solution improves through three actual feedback iterations,
using the same demand/orders and fixed weights/scales. These are bounded,
validated improvements without a global proof for the feedback neighborhood.

E12 T1-only reaches the same objective as combined feedback (0.0598126675), using
14 rather than 41 evaluations on average. T2-only and T3-only remain at baseline
0.1026698103. Valid T2/T3 edits are exercised and replayed in tests and traces,
but this ablation demonstrates **no incremental T2/T3 objective benefit** on this
fixture. It is not evidence that those layers never matter in other instances.

## Exact finite certification and the local plateau

On E13 local-trap with the published training seeds, sequential, multistart and
feedback have objective **0.1526698103**. Strict descent feedback stops at
CONVERGED_LOCAL: a single face edit does not pass the configured improvement
tolerance. Exhaustive search evaluates all **four** declared face combinations
and exact/hybrid achieve **0.1026698103**, with LB=UB and absolute gap zero.
The better solution moves both SKU blocks to the other shelf face.

The actual simulation can yield tiny seed-specific floating differences; different
training seed sets can change the path taken by strict descent. The evidence is
for the declared scenarios, not a universal local minimum across all seeds.

The certificate verifier separately enumerates each point, recomputes the official
simulations and rational selection score, verifies physical feasibility and checks
proof completeness. Tampering tests cover a resealed objective, bound, solution,
finite domain, omitted leaf, relative gap and input identity. A separate CLI replay
has receipt `evidence/20261022-joint-proof-cli-02.json`.

The 128-state model also allows an unlocked shelf pose choice, category assignments
and explicit per-SKU shelf/face placements. This is a full Cartesian joint search;
invalid combinations are counted and rejected by the official validators, with no
heuristic pruning. The exact/hybrid report states how many leaves are feasible and
whether independent verification completes within budget. Certification applies
only when the proof status and independent verification both pass.

All six published exact/hybrid jobs completed and verified **128/128** leaves;
32 leaves per job were feasible and 96 failed declared physical/assignment
constraints. Every job has LB=UB, absolute gap zero and verification PASS.
The optimum is **0.0955269532**. This finite optimum can be worse than the
unrestricted feedback result (0.0598126675): the feedback neighborhood permits
other poses/orientations outside this exact domain. This distinction is why
the certificate explicitly binds the domain rather than claiming a universal
global optimum. No state was pruned by a heuristic.

## Bounded scalability and synthetic holdout

E14 Small has 12 shelves, 6 categories, 48 SKU and 100 orders. Sequential and feedback
both have mean objective **0.1212794967**, with mean route **8.5 m**. Mean child wall
time is about **3.724 s** sequential versus **29.750 s** feedback, with 25 evaluated
decisions for feedback. This shows overhead and no observed improvement for the
examined bounded neighborhood. It does not establish Large-instance performance.
Resource measurements are actual OS samples on this concurrently used machine;
short memory peaks may be missed. No speedup claim is inferred.

E15 holds out offsets 10001/20003, disjoint from the optimization scenarios:

| Treatment | Training objective | Holdout objective |
|---|---:|---:|
| Sequential | 0.1026698103 | 0.1028053956 |
| Feedback | 0.0598126675 | 0.0599482528 |

The benefit persists on these unseen synthetic scenarios. This is a bounded
simulation holdout observation, not evidence of field effectiveness or robustness
across real stores. Statistics retain mean/median/SD/t intervals and paired effects
where nondegenerate; repeated identical seeds do not count as independent samples.
Identical differences do not receive invented p-values.

## Scientific replay and remaining limits

The separate pinned Python environment `var/clean-python-20261022` passed pip check
and replayed all 15 E13 jobs. Input SHA, exact scientific result SHA and numerical
equivalence match **15/15** in
`experiments/reports/20261022-joint-clean-comparison-02.json`. Runtime/cache-hit data
remain outside scientific hashes. This checks a separate Python environment on
the same Windows machine, not a clean OS or cross-solver guarantee.

The exact solver's valid partial-search lower bound is zero, usually weak. It
does not implement a strong LP relaxation or branch-and-bound acceleration.
No simulated annealing/LNS, continuous exact geometry, category splitting,
realistic aisle crowd model, broad Large integrated study, real-data calibration,
or complete global Pareto frontier is claimed. Physical/route validators use
their published numerical tolerances; the certificate certifies their accepted
finite numerical model, not exact physical real arithmetic.

The following states must remain separate:
**CLOSED_LOOP_FEEDBACK_READY**, **JOINT_EXACT_SMALL_INSTANCE_CERTIFIED** for the
published verified finite models, and **JOINT_GENERAL_OPTIMALITY_NOT_PROVEN**.
Commands and dashboard instructions:
[HOW_TO_RUN_JOINT_OPTIMIZATION.md](HOW_TO_RUN_JOINT_OPTIMIZATION.md).

The final E11 improving-feedback replay also matches all nine input SHA/scientific
result SHA/numerical comparisons in
`experiments/reports/20261022-joint-feedback-clean-comparison-02.json`, including
all action/state traces. It complements the 15-job E13 replay. No real-world
validation is inferred from either reproduction check.
