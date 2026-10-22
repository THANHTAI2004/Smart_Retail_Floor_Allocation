# Baseline comparison

T1 baseline is constructive sweep candidate 0. Bounded multistart changes scan direction, shelf order and orientation priority. T2 greedy and HiGHS optimize the same normalized centroid-distance objective. Independent exhaustive tests verify the small MILP optimum. T3 compares demand-descending first-fit against complete finite strip-option MIP under the same dimensions and fixed facings. T4 remains nearest-next routing; E04 compares layouts, not routing policies.

E02 has identical objectives in both arms: no universal MILP superiority claim. E03 first-fit fails 5/5 designed tight-load witnesses while MIP succeeds 5/5 with exact objective 14. E05 includes baseline among four evaluated candidates and finds lower walking distance on this fixture. No GA or NSGA-II was implemented; a finite nondominated set is not described as NSGA-II.
