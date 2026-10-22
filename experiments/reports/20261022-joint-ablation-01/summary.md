# Synthetic experiment report

Campaign: joint_ablation
Status: COMPLETED; attempted 15 / planned 15; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E12 | two_shelves | baseline | 3/3 | 2.010333333319674 | 7.707106781186549 |
| E12 | two_shelves | combined | 3/3 | 6.2079999999841675 | 1.7071067811865477 |
| E12 | two_shelves | t1 | 3/3 | 3.760333333319674 | 1.7071067811865477 |
| E12 | two_shelves | t2 | 3/3 | 2.526333333342336 | 7.707106781186549 |
| E12 | two_shelves | t3 | 3/3 | 2.604333333360652 | 7.707106781186549 |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
