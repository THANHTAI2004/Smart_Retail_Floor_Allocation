# Synthetic experiment report

Campaign: pilot_cv
Status: COMPLETED; attempted 80 / planned 80; not executed 0.
Held-out protocol: kfold, folds per repetition 10, repetitions = seeds [1].

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E16 | small_f4 | baseline | 10/10 | 4.803199999999743 | 17.808333333333334 |
| E16 | small_f4 | feedback | 7/10 | 49.3483000000002 | 17.10297619047619 |
| E16 | small_f4 | multistart | 10/10 | 8.534400000000279 | 17.808333333333334 |
| E16 | small_f4 | seq_milp | 10/10 | 4.789000000000124 | 17.808333333333334 |
| E16 | tiny_f6 | baseline | 10/10 | 2.536000000000058 | 9.473178209757975 |
| E16 | tiny_f6 | feedback | 10/10 | 16.69680000000026 | 6.689249638329406 |
| E16 | tiny_f6 | multistart | 10/10 | 2.749999999999818 | 9.473178209757975 |
| E16 | tiny_f6 | seq_milp | 10/10 | 2.368800000000192 | 9.473178209757975 |

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
