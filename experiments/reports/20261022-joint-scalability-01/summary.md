# Synthetic experiment report

Campaign: joint_scalability
Status: COMPLETED; attempted 18 / planned 18; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E14 | local_trap | baseline | 3/3 | 2.370000000014746 | 14.70710678118655 |
| E14 | local_trap | feedback | 3/3 | 2.72400000000683 | 14.70710678118655 |
| E14 | small | baseline | 3/3 | 4.094000000002173 | 8.5 |
| E14 | small | feedback | 3/3 | 28.08866666664835 | 8.5 |
| E14 | two_shelves | baseline | 3/3 | 2.234666666656267 | 7.707106781186549 |
| E14 | two_shelves | feedback | 3/3 | 6.233999999977338 | 1.7071067811865477 |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
