# Synthetic experiment report

Campaign: paper-x1-exact
Status: COMPLETED; attempted 150 / planned 150; not executed 0.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E17 | local_trap | baseline | 30/30 | 1.8754666666849515 | 14.70710678118655 |
| E17 | local_trap | exact | 30/30 | 2.4879666666539078 | 7.707106781186549 |
| E17 | local_trap | feedback | 30/30 | 2.5048333333339543 | 13.30710678118655 |
| E17 | local_trap | hybrid | 30/30 | 3.2093666666808227 | 7.707106781186549 |
| E17 | local_trap | multistart | 30/30 | 2.0110666666645556 | 14.70710678118655 |

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
