# Synthetic experiment report

Campaign: main
Status: COMPLETED; attempted 105 / planned 105; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E01 | tiny | baseline | 5/5 | 2.125 | None |
| E01 | tiny | local_search | 5/5 | 4.059399999992456 | None |
| E02 | tiny | baseline | 5/5 | 2.2371999999857506 | None |
| E02 | tiny | milp | 5/5 | 3.1246000000159255 | None |
| E03 | facings | baseline | 5/5 | 2.746999999997206 | None |
| E03 | facings | milp | 5/5 | 2.7093999999924563 | None |
| E04 | routing | baseline | 5/5 | 2.037799999990966 | 14.547106781186548 |
| E04 | routing | exact | 5/5 | 2.0562000000034457 | 14.213773447853212 |
| E04 | routing | return | 5/5 | 2.1373999999952504 | 20.013773447853215 |
| E05 | tiny | baseline | 5/5 | 2.0655999999959023 | 11.707106781186548 |
| E05 | tiny | multistart | 5/5 | 2.3658000000054016 | 7.707106781186548 |
| E06 | low_shelf | baseline | 5/5 | 1.9658000000054017 | 5.707106781186548 |
| E06 | low_shelf | more_pickers | 5/5 | 2.0871999999857507 | 5.707106781186548 |
| E06 | tiny | baseline | 5/5 | 2.0970000000088476 | 5.707106781186548 |
| E06 | tiny | more_pickers | 5/5 | 2.071999999997206 | 5.707106781186548 |
| E07 | tiny | baseline | 5/5 | 2.05 | 7.707106781186548 |
| E07 | tiny | wait_weight | 5/5 | 2.03760000000475 | 7.707106781186548 |
| E08 | large | baseline | 5/5 | 2.387400000006892 | None |
| E08 | medium | baseline | 5/5 | 1.8844000000157393 | None |
| E08 | small | baseline | 5/5 | 1.7779999999911524 | None |
| E08 | tiny | baseline | 5/5 | 1.8061999999918044 | None |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
