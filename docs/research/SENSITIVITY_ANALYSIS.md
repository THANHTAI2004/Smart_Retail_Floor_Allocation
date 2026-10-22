> Historical checkpoint: 2026-10-21. For the current 2026-10-22 implementation, use [model scope](MODEL_SCOPE_20261022.md), [ER readiness](EXPERIMENT_READINESS_MATRIX.md), and [actual results](RESULTS_20261022.md). The historical gates and limits below are not the current synthetic-readiness assessment.

# Sensitivity analysis

E06 doubles product demand and arrivals_per_hour together. Mean wait changes from 0.0242 s to 0.0410 s and mean distance from 14.1886 m to 14.2321 m on the supplied fixture/seeds.

The T3 objective doubles from 2640 to 5280 because its demand coefficients double; physical capacity has not doubled. Customers are capped by horizon and maximum count.

A factorial design varying each factor separately, number of levels, complete weight sweeps, picker count and perturbation distributions is still missing. GATE 09 remains FAIL. See [actual summary](../../experiments/results/20261021-research-02/summary.json).
