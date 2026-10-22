# Synthetic experiment report

Campaign: pilot
Status: COMPLETED; attempted 19 / planned 19; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E01 | tiny | baseline | 1/1 | 1.7189999999827705 | None |
| E01 | tiny | local_search | 1/1 | 3.047000000020489 | None |
| E02 | tiny | baseline | 1/1 | 1.6880000000237487 | None |
| E02 | tiny | milp | 1/1 | 1.702999999979511 | None |
| E03 | facings | baseline | 1/1 | 1.7190000000409782 | None |
| E03 | facings | milp | 1/1 | 1.8119999999762513 | None |
| E04 | tiny | baseline | 1/1 | 1.7809999999590218 | 5.707106781186548 |
| E04 | tiny | exact | 1/1 | 1.7339999999967404 | 5.707106781186548 |
| E04 | tiny | return | 1/1 | 1.7339999999967404 | 5.707106781186548 |
| E05 | tiny | baseline | 1/1 | 1.7809999999590218 | 11.707106781186548 |
| E05 | tiny | multistart | 1/1 | 1.9380000000237487 | 7.707106781186548 |
| E06 | low_shelf | baseline | 1/1 | 2.1089999999967404 | 5.707106781186548 |
| E06 | low_shelf | more_pickers | 1/1 | 2.9839999999967404 | 5.707106781186548 |
| E06 | tiny | baseline | 1/1 | 1.7190000000409782 | 5.707106781186548 |
| E06 | tiny | more_pickers | 1/1 | 2.125 | 5.707106781186548 |
| E07 | tiny | baseline | 1/1 | 2.0160000000032596 | 7.707106781186548 |
| E07 | tiny | wait_weight | 1/1 | 2.0 | 7.707106781186548 |
| E08 | small | baseline | 1/1 | 0.25 | None |
| E08 | tiny | baseline | 1/1 | 1.6560000000172295 | None |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
