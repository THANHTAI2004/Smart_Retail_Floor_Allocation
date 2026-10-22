# Statistical analysis

summary.json reports actual n, mean, sample standard deviation and two-sided 95% Student-t intervals. A singleton has no SD/CI. Failed arms have no solution metrics; all failures remain in runs.json.

analysis.json pairs successful runs by seed and reports treatment minus baseline. Constant paired differences receive no t-test inference: E05 decreases exactly 1 m for all seeds, with a degenerate seed-only interval [-1,-1]. This does not imply certainty on other stores. Nonzero-variance comparisons receive exploratory paired t p-values and Holm adjustment over the calculated family. P-values do not certify research readiness.

Five seeds constitute a smoke study. Independent random streams on one floorplan are not five independent stores. No power analysis, validated distribution assumption or practical-effect threshold exists. GATE 10 remains FAIL for the full requested scope. Unit tests cover singleton uncertainty, failures, constant differences, finite CI and Holm behavior.
