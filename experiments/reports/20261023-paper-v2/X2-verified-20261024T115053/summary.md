# Synthetic experiment report

Campaign: paper-x2-tiny-part01
Status: NOT_EXECUTED_RESOURCE_LIMIT; attempted 486 / planned 800; not executed 314.
Held-out protocol: kfold, folds per repetition 10, repetitions = seeds [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].
Campaign: paper-x2-tiny-part02
Status: COMPLETED; attempted 400 / planned 400; not executed 0.
Held-out protocol: kfold, folds per repetition 10, repetitions = seeds [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].
Campaign: paper-x2-small
Status: NOT_EXECUTED_RESOURCE_LIMIT; attempted 397 / planned 600; not executed 203.
Held-out protocol: kfold, folds per repetition 10, repetitions = seeds [1, 2, 3, 4, 5].

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E18 | small_f4_s101 | baseline | 50/50 | 4.682479999996722 | 17.880579300830668 |
| E18 | small_f4_s101 | feedback | 50/50 | 50.12062000001315 | 17.497152620523856 |
| E18 | small_f4_s101 | multistart | 50/50 | 8.9349599999981 | 17.881460036535263 |
| E18 | small_f4_s101 | seq_milp | 50/50 | 4.896919999995735 | 17.881460036535263 |
| E18 | small_f4_s202 | baseline | 50/50 | 5.885299999995623 | 18.335060115206353 |
| E18 | small_f4_s202 | feedback | 47/47 | 49.615468085097014 | 17.43068660542031 |
| E18 | small_f4_s202 | multistart | 50/50 | 9.169419999995734 | 18.333831220200075 |
| E18 | small_f4_s202 | seq_milp | 50/50 | 5.070280000010971 | 18.333831220200075 |
| E18 | tiny_f6_s101 | baseline | 100/100 | 2.1668199999968056 | 9.341928209757976 |
| E18 | tiny_f6_s101 | feedback | 100/100 | 23.136520000001184 | 6.647999638329406 |
| E18 | tiny_f6_s101 | multistart | 99/100 | 3.266859999996377 | 9.33950216358193 |
| E18 | tiny_f6_s101 | seq_milp | 100/100 | 2.1692199999978765 | 9.341928209757976 |
| E18 | tiny_f6_s202 | baseline | 86/86 | 2.3057325581389176 | 9.419316083512129 |
| E18 | tiny_f6_s303 | baseline | 100/100 | 2.171449999996694 | 8.57853535261512 |
| E18 | tiny_f6_s303 | feedback | 100/100 | 22.18889000000432 | 6.200678209757977 |
| E18 | tiny_f6_s303 | multistart | 100/100 | 3.1731299999984914 | 8.57853535261512 |
| E18 | tiny_f6_s303 | seq_milp | 100/100 | 2.17314000000013 | 8.57853535261512 |

## Assumptions and limitations
- Exploratory paired tests; no population-level efficacy claim
- Pairing unit is (seed, cv_fold); repeated identical units are averaged, not counted as independent
- Repeated k-fold units share training orders: use nadeau_bengio_p, not the naive t-test, for cross-validated comparisons
- Wilcoxon signed-rank drops zero differences; A12 = P(treatment > baseline) + 0.5 P(tie)
- Median-difference CI: percentile bootstrap, 2000 resamples, seed 20261023
- Friedman/Nemenyi rank 1 = smallest value; dataset_means blocks are the inferential level, units blocks are exploratory
- Failure rates include all attempted jobs; solution metrics only exist for valid results
- Completion rate is not a proof of feasibility/infeasibility for unsolved cases
- Holm adjustment is applied separately to each reported test family
- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.
- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.
- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.
