# Synthetic experiment report

Campaign: paper-x4-tiny
Status: COMPLETED; attempted 60 / planned 60; not executed 0.
Campaign: paper-x4-small
Status: CANCELLED; attempted 23 / planned 60; not executed 37.

| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |
|---|---|---|---:|---:|---:|
| E21 | small_f4_s101 | baseline | 5/5 | 3.7719999999506397 | 18.08760353999887 |
| E21 | small_f4_s101 | feedback | 5/5 | 63.82800000002608 | 17.230079442885295 |
| E21 | small_f4_s101 | multistart | 5/5 | 7.743999999994412 | 18.08760353999887 |
| E21 | small_f4_s101 | seq_milp | 5/5 | 3.784000000031665 | 18.08760353999887 |
| E21 | small_f4_s202 | baseline | 3/3 | 3.922333333369655 | 18.64498490312444 |
| E21 | tiny_f6_s101 | baseline | 5/5 | 2.1345999999903142 | 10.223773447853214 |
| E21 | tiny_f6_s101 | feedback | 5/5 | 13.03139999997802 | 7.197106781186547 |
| E21 | tiny_f6_s101 | multistart | 5/5 | 2.43159999998752 | 10.223773447853214 |
| E21 | tiny_f6_s101 | seq_milp | 5/5 | 2.1906000000191854 | 10.223773447853214 |
| E21 | tiny_f6_s202 | baseline | 5/5 | 2.009400000004098 | 9.407106781186547 |
| E21 | tiny_f6_s202 | feedback | 5/5 | 14.109599999990314 | 6.843773447853214 |
| E21 | tiny_f6_s202 | multistart | 5/5 | 2.2811999999685213 | 9.407106781186547 |
| E21 | tiny_f6_s202 | seq_milp | 5/5 | 1.9472000000067056 | 9.407106781186547 |
| E21 | tiny_f6_s303 | baseline | 5/5 | 2.081199999968521 | 8.79044011451988 |
| E21 | tiny_f6_s303 | feedback | 5/5 | 13.903200000012294 | 6.277106781186547 |
| E21 | tiny_f6_s303 | multistart | 5/5 | 2.415399999986403 | 8.79044011451988 |
| E21 | tiny_f6_s303 | seq_milp | 5/5 | 2.1158000000054016 | 8.79044011451988 |

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
