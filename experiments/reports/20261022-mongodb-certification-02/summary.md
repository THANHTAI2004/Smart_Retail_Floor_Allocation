# Synthetic experiment report

Campaign: joint_certification
Status: COMPLETED; attempted 15 / planned 15; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E13 | local_trap | baseline | 3/3 | 2.4789999999920838 | 14.70710678118655 |
| E13 | local_trap | exact | 3/3 | 3.1513333333229334 | 7.707106781186549 |
| E13 | local_trap | feedback | 3/3 | 3.3176666666792394 | 14.70710678118655 |
| E13 | local_trap | hybrid | 3/3 | 4.229333333341249 | 7.707106781186549 |
| E13 | local_trap | multistart | 3/3 | 2.8959999999885135 | 14.70710678118655 |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
