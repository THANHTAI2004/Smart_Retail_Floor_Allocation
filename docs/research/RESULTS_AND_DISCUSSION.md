> Historical checkpoint: 2026-10-21. For the current 2026-10-22 implementation, use [model scope](MODEL_SCOPE_20261022.md), [ER readiness](EXPERIMENT_READINESS_MATRIX.md), and [actual results](RESULTS_20261022.md). The historical gates and limits below are not the current synthetic-readiness assessment.

# Actual results: 2026-10-21

| Experiment | Arm | Succeeded | Mean route m | Mean wait s | T3 objective |
|---|---|---:|---:|---:|---:|
| E01 | baseline | 5/5 | 14.1886 | 0.0242 | 2640.0000 |
| E01 | treatment | 5/5 | 14.1886 | 0.0242 | 2640.0000 |
| E02 | baseline | 5/5 | 14.1886 | 0.0242 | 2640.0000 |
| E02 | treatment | 5/5 | 14.1886 | 0.0242 | 2640.0000 |
| E03 | baseline | 0/5 | no solution | no solution | no solution |
| E03 | treatment | 5/5 | 9.7071 | 0.0875 | 14.0000 |
| E04 | baseline | 5/5 | 9.3491 | 0.0242 | 2640.0000 |
| E04 | treatment | 5/5 | 21.3491 | 0.0242 | 2640.0000 |
| E05 | baseline | 5/5 | 14.1886 | 0.0242 | 2640.0000 |
| E05 | treatment | 5/5 | 13.1886 | 0.0242 | 2640.0000 |
| E06 | baseline | 5/5 | 14.1886 | 0.0242 | 2640.0000 |
| E06 | treatment | 5/5 | 14.2321 | 0.0410 | 5280.0000 |
| E07 | baseline | 5/5 | 13.1886 | 0.0242 | 2640.0000 |
| E07 | treatment | 5/5 | 13.1886 | 0.0242 | 2640.0000 |
| E08 | baseline | 5/5 | 14.1886 | 0.0242 | 2640.0000 |
| E08 | treatment | 5/5 | 7.6083 | 0.0242 | 14160.0000 |

All 80 jobs are retained: 75 succeed. The five FAILED E03 baseline jobs report expected SLOTTING_FAILED; they are not failing software tests. Independent audit validates all snapshots/receipts, all feasible candidate geometry/allocation/packing, and every route segment of all 75 successful runs. A new replay has identical hashes.

E05 reduces distance by exactly 1 m on all five seeds (about 7.05% for this fixture), while T2 centroid objective rises from 0.3134 to 0.3182. This demonstrates that the T2 proxy does not substitute for operational evaluation. E02 has no objective gain and E07 has no observed weighting effect. E08 changes SKU/demand composition and is only an execution-scale smoke, not evidence for effectiveness or large-scale scalability.

Raw evidence: [completed campaign](../../experiments/results/20261021-research-02/). No SOFTWARE_RESEARCH_READY or REAL_WORLD_VALIDATED claim. research-01 was interrupted by a Windows progress-file sharing violation and is preserved; regression and research-02 verify the correction.
