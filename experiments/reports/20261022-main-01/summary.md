# Synthetic experiment report

Campaign: main
Status: COMPLETED; attempted 105 / planned 105; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E01 | tiny | baseline | 5/5 | 1.7252000000094996 | None |
| E01 | tiny | local_search | 5/5 | 3.072200000018347 | None |
| E02 | tiny | baseline | 5/5 | 1.7405999999842607 | None |
| E02 | tiny | milp | 5/5 | 1.7282000000006519 | None |
| E03 | facings | baseline | 5/5 | 1.7217999999877065 | None |
| E03 | facings | milp | 5/5 | 1.7153999999980443 | None |
| E04 | tiny | baseline | 5/5 | 1.7531999999773689 | 5.707106781186548 |
| E04 | tiny | exact | 5/5 | 1.9153999999864026 | 5.707106781186548 |
| E04 | tiny | return | 5/5 | 1.7563999999896622 | 5.707106781186548 |
| E05 | tiny | baseline | 5/5 | 1.8092000000062398 | 11.707106781186548 |
| E05 | tiny | multistart | 5/5 | 2.15 | 7.707106781186548 |
| E06 | low_shelf | baseline | 5/5 | 2.5531999999890105 | 5.707106781186548 |
| E06 | low_shelf | more_pickers | 5/5 | 2.003600000008009 | 5.707106781186548 |
| E06 | tiny | baseline | 5/5 | 2.0217999999877065 | 5.707106781186548 |
| E06 | tiny | more_pickers | 5/5 | 2.3596000000019557 | 5.707106781186548 |
| E07 | tiny | baseline | 5/5 | 2.056000000005588 | 7.707106781186548 |
| E07 | tiny | wait_weight | 5/5 | 2.106199999991804 | 7.707106781186548 |
| E08 | large | baseline | 5/5 | 1.1690000000060536 | None |
| E08 | medium | baseline | 5/5 | 0.4186000000103377 | None |
| E08 | small | baseline | 5/5 | 0.2876000000047497 | None |
| E08 | tiny | baseline | 5/5 | 1.8592000000062399 | None |

## Assumptions and limitations
- Exploratory Student-t intervals and paired tests; no population-level efficacy claim
- Repeated identical seeds are averaged before pairing, not counted as independent replications
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment covers every reported nondegenerate paired metric comparison
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
