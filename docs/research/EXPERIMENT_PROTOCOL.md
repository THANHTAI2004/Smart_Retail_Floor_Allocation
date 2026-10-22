# E01-E08 experiment protocol

Executed 2026-10-21 on Windows; exact Python/packages in configuration.json. Seeds: 11,23,37,53,71. Each of 16 arms runs five seeds: 80 durable queue jobs with killable child processes, a dedicated SQLite database and artifacts. Each job has a 15 s wall budget and 50,000 grid-candidate ceiling; multiple integrated candidates share that budget. T3 option ceiling is 20,000. Termination is candidate exhaustion, wall deadline, cancellation or structured error.

| ID | Treatment and purpose | Baseline | Metrics and limits |
|---|---|---|---|
| E01 | Concave polygon | Rectangular polygon | Geometry feasibility; one shape pair |
| E02 | HiGHS T2 MILP | T2 greedy | Objective and feasibility; small instance |
| E03 | T3 MILP on tight load witness | First-fit | Feasibility, exact reference objective 14 |
| E04 | Fixed shelves far from entrance | Fixed shelves near entrance | Route/wait; same nearest-next routing |
| E05 | Four complete T1-T4 candidates | One candidate | Route/objective/runtime; same budget ceiling |
| E06 | Double product demand and arrival rate | Original demand/rate | Sensitivity; effects not separately identified |
| E07 | wait_weight=1 | wait_weight=0, both four candidates | Objective-component ablation only |
| E08 | Eight shelves/categories/SKUs | Two shelves | Runtime/failure smoke, not a scaling curve |

Keep all failures. Wall time includes child startup/polling; machine load is not controlled. No speedup claim follows from these times. Child peak memory is not instrumented and is null. Confidence intervals/tests explore seed variability on one synthetic instance, not store-population effects.

Outputs: runs.json, summary.json, analysis.json and artifacts/<run_id>/*.json. research-01 was interrupted by a Windows sharing violation and is preserved. research-02 is the completed corrected-source campaign.
