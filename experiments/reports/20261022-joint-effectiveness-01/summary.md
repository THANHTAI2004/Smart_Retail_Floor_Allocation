# Synthetic experiment report

Campaign: joint_effectiveness
Status: COMPLETED; attempted 9 / planned 9; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E11 | two_shelves | baseline | 3/3 | 2.1250000000194027 | 7.707106781186549 |
| E11 | two_shelves | feedback | 3/3 | 5.9369999999956535 | 1.7071067811865477 |
| E11 | two_shelves | multistart | 3/3 | 2.5779999999989136 | 7.707106781186549 |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
