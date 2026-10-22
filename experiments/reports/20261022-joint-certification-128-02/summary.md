# Synthetic experiment report

Campaign: joint_certification_128
Status: COMPLETED; attempted 6 / planned 6; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E13 | two_shelves | exact | 3/3 | 9.432666666669926 | 6.707106781186548 |
| E13 | two_shelves | hybrid | 3/3 | 13.104333333321847 | 6.707106781186548 |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
