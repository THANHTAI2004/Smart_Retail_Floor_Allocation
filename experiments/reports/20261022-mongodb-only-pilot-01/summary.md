# Synthetic experiment report

Campaign: pilot
Status: COMPLETED; attempted 19 / planned 19; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E01 | tiny | baseline | 1/1 | 2.110000000044238 | None |
| E01 | tiny | local_search | 1/1 | 3.452999999979511 | None |
| E02 | tiny | baseline | 1/1 | 1.9070000000065193 | None |
| E02 | tiny | milp | 1/1 | 2.01500000001397 | None |
| E03 | facings | baseline | 1/1 | 1.875 | None |
| E03 | facings | milp | 1/1 | 1.9530000000377186 | None |
| E04 | routing | baseline | 1/1 | 1.9839999999967404 | 14.373773447853214 |
| E04 | routing | exact | 1/1 | 2.125 | 14.040440114519878 |
| E04 | routing | return | 1/1 | 1.937000000034459 | 19.84044011451988 |
| E05 | tiny | baseline | 1/1 | 2.047000000020489 | 11.707106781186548 |
| E05 | tiny | multistart | 1/1 | 2.452999999979511 | 7.707106781186548 |
| E06 | low_shelf | baseline | 1/1 | 1.9849999999860302 | 5.707106781186548 |
| E06 | low_shelf | more_pickers | 1/1 | 1.9679999999934807 | 5.707106781186548 |
| E06 | tiny | baseline | 1/1 | 2.047000000020489 | 5.707106781186548 |
| E06 | tiny | more_pickers | 1/1 | 2.062999999965541 | 5.707106781186548 |
| E07 | tiny | baseline | 1/1 | 2.23499999998603 | 7.707106781186548 |
| E07 | tiny | wait_weight | 1/1 | 2.327999999979511 | 7.707106781186548 |
| E08 | small | baseline | 1/1 | 1.8589999999967404 | None |
| E08 | tiny | baseline | 1/1 | 1.9059999999590218 | None |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
