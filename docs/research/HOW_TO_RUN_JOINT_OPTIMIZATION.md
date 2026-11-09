# Running joint T1-T4 research

Run commands from `D:\Smart_Retail_Floor_Allocation` using the pinned environment
in README. Historical campaign directories must never be reused as new output.

## Campaign CLI

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli run --config experiments/configs/joint_effectiveness.json --output experiments/results/my-joint-effectiveness
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli analyze experiments/results/my-joint-effectiveness --output experiments/reports/my-joint-effectiveness
```

Other presets: `joint_ablation.json` (E12), `joint_certification.json` (E13,
four-state local plateau), `joint_certification_128.json` (E13, two shelves,
128 full Cartesian configurations), `joint_scalability.json` (E14), and
`joint_holdout.json` (E15). All use the existing real durable worker and immutable
run snapshots. E14's limited local-trap/two-shelf/Small sweep is not evidence of
general large-instance scalability. Each job receives an equal 60 s hard process
budget; a numerical evaluation budget is also declared. Work and report wall time
are measured, not held equal by artificial delays.

`joint_failure_controls.json` separately reproduces no-incumbent outcomes:
an incomplete search is FAILED/SEARCH_EXHAUSTED with no infeasibility assertion;
a completely enumerated empty finite domain is INFEASIBLE with independently
verified proof. Both retain result/certificate artifacts and are included in
failure tables. A successful experiment execution is not a feasible solution.

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli status experiments/results/my-joint-effectiveness
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli resume experiments/results/my-joint-effectiveness
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli verify experiments/results/my-joint-effectiveness
```

Resume requires matching source/dependency/configuration identity and intact
artifacts. Completed valid jobs remain unchanged. Stop/cancel and process RSS/time
limits follow the existing worker. The CLI `resume` is for an interrupted campaign;
a completed campaign should be analyzed or replayed instead.

## Inputs and controls

`optimization.joint` is optional. Omitting it preserves the sequential/multistart
workflow. Its `mode` selects sequential, multistart, random_search, annealing,
feedback, genetic, exact or hybrid. Multistart and random_search evaluate seeded random walks
of geometry-valid shelf-pose edits (T2/T3 re-optimized); random_search continues until
`max_evaluations`. Annealing samples the feedback neighborhood uniformly and accepts
worse moves by the Metropolis rule (`annealing_initial_temperature` relative to the
initial score, geometric cooling to `annealing_final_ratio`) until `max_evaluations`.
Every joint result reports `incumbent_curve` and `evaluations_to_best`.
Feedback implements deterministic first- or best-improvement strict descent.
Use `layers` to ablate T1/T2/T3; optional T4 changes routing policy. Configure
`max_iterations`, `max_evaluations`, `max_actions`, `patience`, `target`,
`tolerance`, `scenario_seeds`, `holdout_seeds` and the common objective.

Optional paper-v4 search controls (absent = paper-v3 behavior, omitted from the
canonical config):
- `t1_steps`: T1 move lengths in grid steps, e.g. `[1, 2, 3]` (default `[1]`).
- `geometry_prefilter`: drop T1 edits that violate boundary, entrance/exit or aisle
  clearance before they spend an evaluation. Topology is still checked on evaluation.
- `t3_scope: "objective"`: keep only T3 edits that can change the joint score. T4
  routes to the shelf face, so level, orientation and x position never change travel
  or wait; facings matter only while a SKU's capacity is below its demand.
- `layer_allocation: "adaptive"`: layers share the truncated action list by the
  smoothed success rate (accepted + 1) / (evaluated + 2) instead of round-robin. The
  weights are written to each `IMPROVING` trace event as `layer_weights`.
- `kicks`, `kick_edits`: iterated local search. On `patience` sweeps without strict
  improvement, feedback restarts descent from a random walk of `kick_edits` (default 3)
  geometry-valid T1 edits of the best plan (`ILS_KICK` trace events). The best plan
  is kept separately; kicks spend the same evaluation budget.
- `restart_max_step`: largest per-axis grid displacement of a random-walk edit for
  random_search, multistart and kicks (default 3). `1` gives the small-step control.
- `search_time_s`: equal-wall-time comparison. No new evaluation starts after this many
  seconds of search (an evaluation already running finishes); the rest of
  `time_limit_s` is left for verification and held-out scoring. Termination is
  `SEARCH_TIME_LIMIT`, and the result reports `search_time_s`.
- `screen_seeds`, `screen_margin`: two-fidelity screening. A candidate is first
  simulated on the first `screen_seeds` scenario seeds; it is fully evaluated only when
  that score is at most (1 + `screen_margin`) x the reference plan's score on the same
  seeds (feedback: descent state; annealing: current state; random_search: best plan;
  kicks and initialization are never screened). Rejections raise `SCREENED_OUT` and
  are not feasibility verdicts. `max_evaluations` then counts full-evaluation
  equivalents (seed simulations / number of scenario seeds); the last promoted candidate
  can exceed it by at most one unscreened remainder. Results report `budget_spent` and
  `screened_out`; screening is rejected for exact/hybrid. Promotion reuses the
  screened seed's stages from the cache (same declared scenario set).

Optional paper-v5 search controls (absent = paper-v4 behavior, omitted from the
canonical config; design in `EXPERIMENT_DESIGN_DEEPMG.md` section 12):

| Control | Default | Effect |
|---|---|---|
| `surrogate` | off | `walk_heat` or `walk`. Ranks T1 candidates before they are simulated: shortest walk from the entrance to each shelf's nearest pickup point on the navigation grid; categories are paired with shelves by the rearrangement inequality (hottest category on the nearest shelf). `walk_heat` weights a category by the units picked in the latest simulation plus 1, `walk` uses weight 1. Layouts without a valid topology are dropped unsimulated. The surrogate only ranks: acceptance is still strict decrease on simulation. |
| `surrogate_pool` | off; 96 when `surrogate` is set | Number of T1 candidates sampled uniformly from all shelves (moves by `t1_steps`, rotations, swaps) per descent round before ranking. Without `surrogate` the pool is shuffled with a seed and cut at `max_actions` (the "no surrogate" ablation). Used by feedback and hybrid descent only. |
| `compound_moves` | 0 | Number of seeded random walks that move 2..N shelves at once (from the current plan) added to the T1 candidate set. Active only when the descent is pooled (`surrogate` or `surrogate_pool` set, feedback and hybrid); otherwise accepted but inert. |
| `restart_samples`, `restart_evaluations` | off | Warm start: `restart_samples` seeded random walks from the initial plan (the random_search generator) are ranked by the surrogate (without a surrogate they keep generation order); the first `restart_evaluations` are simulated (trace `SURROGATE_RESTART`) and descent starts from the best plan. The phase spends the same evaluation budget. `restart_evaluations` requires `restart_samples` and must not exceed it (rejected otherwise; effective cap 2,000). `restart_samples` alone does nothing. The result reports `restart_evaluations`, the evaluations spent in the phase. |
| `search_seed_scope` | `job` | `instance`: the seed of every stochastic stream (random_search, multistart, annealing, genetic, warm start, kicks, candidate sampling) is a hash of the instance content and the job seed, so instances that share a job seed no longer share one random stream. `job` keeps the job seed. |
| `population`, `mutation_edits` | 8, 2 | Genetic mode only: population size and shelves edited per mutation. |
| `drop_identical_swaps` | off | `true`: the T1 neighbourhood (feedback, hybrid and annealing) omits the swap of two shelves that are physically identical (every shelf field except `id`, `x`, `y`, `rotation`, `locked` equal) when no category has `fixed_shelf_id` on either; in the pooled descent, compound walks whose layout only permutes identical shelves of the current plan (same multiset of pose and physical attributes, no fixed category on a moved shelf) are dropped too. Such edits only relabel shelves: the score does not change, but each would cost an evaluation. All generated paper-v5 shelves are identical, so every swap is dropped there. |

Mode `genetic`: steady-state genetic algorithm with the same `max_evaluations` budget as
the other search modes. A solution is the pose (x, y, rotation) of every shelf; T2/T3 are
re-solved on each evaluation. The initial population is the initial plan plus
(`population` - 1) random walks as in random_search. Parents come from a binary
tournament; crossover takes each shelf's pose from one parent, and a child that violates
geometry is retried up to 50 times and then only mutated. Mutation is a random walk of
`mutation_edits` shelves. Duplicate children cost no budget; a child replaces the worst
member when it is better. Trace actions are `GA_INIT` and `GA_OFFSPRING`; `surrogate` and
`restart_*` are accepted but ignored.

Declared assumptions and limits of the v5 controls:
- Restart fields are inert outside feedback (the result reports `restart_evaluations` 0) and
  active in hybrid, which shares the feedback descent.
- The warm start draws its walks from the same `(seed, variant)` stream as random_search
  (common random numbers): with the same search seed and `restart_max_step`, candidate
  walks of the two modes coincide. This is a declared experimental assumption, not
  independent sampling.
- `value()` pairs free categories with the full shelf list, fixed shelves included, so on
  instances with fixed category-to-shelf assignments it is a relaxation (slightly
  optimistic). The paper-v5 configs have no fixed assignments.
- The surrogate ignores queues, multi-shelf routes, T2 capacity and near/far constraints and
  assumes an ideal T2 assignment. A bad ranking costs search time, never correctness, and is
  not evidence of infeasibility.
- Surrogate and pool time counts toward job wall time: a pooled `actions()` round about 6 s
  on small and 22 s on medium; the warm start generates 128 walks (about 12.5 s per job on
  medium) and ranks them (about 3/6/17 s on tiny/small/medium). Once the evaluation budget is
  spent the pooled round is skipped, and walk generation stops at the search deadline
  (`SEARCH_TIME_LIMIT`, or `TIMEOUT` at the job deadline).
- `drop_identical_swaps` assumes that a relabel of identical shelves leaves the score
  unchanged; with a fixed category on a shelf the swap is kept.

`optimization.time_limit_s` and campaign `job_time_limit_s` accept up to 3,600 s
(supervisor grace max(15 s, 10%)); the worker renews its 30 s lease while a job runs.

`objective.weights` and `objective.scales` each have four entries: travel, wait,
stock shortfall and operational lateness penalty. Scales stay fixed across all
candidates and seeds. The legacy travel_weight/wait_weight/stock_weight controls
belong to the earlier workflow; joint mode uses `joint.objective` explicitly.
The full preset configuration is visible in the dashboard.

Training and holdout seed lists must be disjoint and have no duplicates.
`scenario_seed_policy: fixed` evaluates exactly those seeds. The campaign presets
use `job_seed_offsets`: each listed offset is added to the independent job seed
modulo 2^31, equally for every treatment. Actual seeds are saved in the result.
The E15 holdout is never fed to the feedback diagnostics or objective acceptance.
Distinct seeds share the same physical fixture; they do not constitute independent
real-store replications. Degenerate paired differences receive no invented p-value.

Exact/hybrid requires `finite_space`: every shelf pose list, category shelf list,
SKU full placement list, allowed routing policy list and hard state cap. Malformed
domains are rejected; invalid physical combinations are individually recorded.
Do not replace the domain by a heuristic candidate set and describe it as the
full continuous problem. See [the formulation](JOINT_OPTIMIZATION_FORMULATION.md).

## Reports, trace and offline verifier

Holdout evaluation shares the time budget. If it cannot complete, the valid
training incumbent remains available and the holdout status explicitly records
TIMEOUT/CANCELLED/NOT_EXECUTED_BUDGET; a missing holdout objective is not a zero.

In addition to regular reports, joint campaigns export `joint-comparison.csv`,
`joint-trace.csv`, `joint-examples.json`, convergence PNG/SVG and one certificate
JSON per exact/hybrid job. Per-job `stages/` contains durable JOINT_EVENT and
immutable JOINT_STATE artifacts including actual scenario simulations, lineage,
decisions, cache keys and timing. Scientific hashes exclude timing/cache-hit
telemetry; these measurements remain in worker/stage receipts.

Verify a certificate against the corresponding worker `input.json`:

```powershell
.venv\Scripts\python.exe -m smart_retail.application.feedback.cli --input experiments/results/MY-CAMPAIGN/artifacts/RUN-ID/input.json --certificate experiments/reports/MY-CAMPAIGN/certificates/JOB-KEY.json --output var/my-proof-verification.json --time-limit 120
```

The verifier separately enumerates all claimed leaves using a fresh cache and
checks bounds, objective, decision-domain identity and the incumbent. Use recorded
source/dependencies; source drift is rejected. A checksum alone is not proof.
This certifies the finite implemented numerical model and fixed scenario average,
not continuous geometry, all random behavior, or real-world optimality.

Replay and compare:

```powershell
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli replay experiments/results/MY-CAMPAIGN --output experiments/results/MY-REPLAY
.venv\Scripts\python.exe -m smart_retail.application.experiments.cli compare experiments/results/MY-CAMPAIGN experiments/results/MY-REPLAY --output experiments/reports/my-joint-comparison.json
```

## Dashboard

Start the local services with `scripts/start.ps1`, then open
http://127.0.0.1:5173/#research. Select a `joint_*` campaign and retain
**Use campaign design** to compare all declared treatment modes. Select independent
seed count and time budget, then start the campaign. An explicit mode override
applies that mode to all arms; exact/hybrid still requires a compatible finite
domain. The server rejects a second live supervisor with HTTP 409; wait for report
publication before launching another campaign.

Choose a joint job to inspect objective, termination, UB/LB/gap, proof verification,
iteration/action acceptance, convergence, initial/selected layout, category shelves
and planogram rows. **CONVERGED_LOCAL** and **FEASIBLE_NOT_PROVEN** do not display a
global certification label. Download actual trace/certificate JSON or CSV/SVG
reports. An exact certificate is shown only with its finite-model scope.
