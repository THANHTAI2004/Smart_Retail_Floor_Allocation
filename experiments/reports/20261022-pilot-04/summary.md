# Synthetic experiment report

Campaign: pilot
Status: COMPLETED; attempted 19 / planned 19; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E01 | tiny | baseline | 1/1 | 1.547000000020489 | None |
| E01 | tiny | local_search | 1/1 | 2.797000000020489 | None |
| E02 | tiny | baseline | 1/1 | 1.5310000000172295 | None |
| E02 | tiny | milp | 1/1 | 1.5780000000377186 | None |
| E03 | facings | baseline | 1/1 | 1.547000000020489 | None |
| E03 | facings | milp | 1/1 | 1.922000000020489 | None |
| E04 | routing | baseline | 1/1 | 2.375 | 14.373773447853214 |
| E04 | routing | exact | 1/1 | 1.8439999999827705 | 14.040440114519878 |
| E04 | routing | return | 1/1 | 1.7969999999622814 | 19.84044011451988 |
| E05 | tiny | baseline | 1/1 | 1.687999999965541 | 11.707106781186548 |
| E05 | tiny | multistart | 1/1 | 2.0320000000065193 | 7.707106781186548 |
| E06 | low_shelf | baseline | 1/1 | 1.7189999999827705 | 5.707106781186548 |
| E06 | low_shelf | more_pickers | 1/1 | 1.8280000000377186 | 5.707106781186548 |
| E06 | tiny | baseline | 1/1 | 1.6880000000237487 | 5.707106781186548 |
| E06 | tiny | more_pickers | 1/1 | 1.7179999999934807 | 5.707106781186548 |
| E07 | tiny | baseline | 1/1 | 1.9059999999590218 | 7.707106781186548 |
| E07 | tiny | wait_weight | 1/1 | 1.9380000000237487 | 7.707106781186548 |
| E08 | small | baseline | 1/1 | 1.6560000000172295 | None |
| E08 | tiny | baseline | 1/1 | 1.6719999999622814 | None |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
