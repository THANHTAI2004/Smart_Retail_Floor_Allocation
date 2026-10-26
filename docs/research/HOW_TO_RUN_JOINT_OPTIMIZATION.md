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
feedback, exact or hybrid. Multistart and random_search evaluate seeded random walks
of geometry-valid shelf-pose edits (T2/T3 re-optimized); random_search continues until
`max_evaluations`. Annealing samples the feedback neighborhood uniformly and accepts
worse moves by the Metropolis rule (`annealing_initial_temperature` relative to the
initial score, geometric cooling to `annealing_final_ratio`) until `max_evaluations`.
Every joint result reports `incumbent_curve` and `evaluations_to_best`.
Feedback implements deterministic first- or best-improvement strict descent.
Use `layers` to ablate T1/T2/T3; optional T4 changes routing policy. Configure
`max_iterations`, `max_evaluations`, `max_actions`, `patience`, `target`,
`tolerance`, `scenario_seeds`, `holdout_seeds` and the common objective.

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
