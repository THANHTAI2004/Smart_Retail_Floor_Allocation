# Synthetic experiment report

Campaign: robustness
Status: COMPLETED; attempted 20 / planned 20; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E09 | uneven | baseline | 5/5 | 2.396999999997206 | 5.707106781186548 |
| E09 | uneven | exact | 5/5 | 2.3343999999924563 | 5.707106781186548 |
| E09 | volatile | baseline | 5/5 | 2.255999999982305 | 5.707106781186548 |
| E09 | volatile | exact | 5/5 | 2.018800000008196 | 5.707106781186548 |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
