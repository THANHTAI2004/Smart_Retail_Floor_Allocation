> Historical checkpoint: 2026-10-21. For the current 2026-10-22 implementation, use [model scope](MODEL_SCOPE_20261022.md), [ER readiness](EXPERIMENT_READINESS_MATRIX.md), and [actual results](RESULTS_20261022.md). The historical gates and limits below are not the current synthetic-readiness assessment.

# Ablation study

E07 compares four candidates with wait_weight=0 and wait_weight=1, retaining travel_weight=1. Both arms have mean distance 13.1886 m and mean wait 0.0242 s. This fixture provides no evidence for a benefit from wait weighting.

E05 contrasts one versus four candidates. There is no full ablation of capacity feedback, persistent cache, routing policy or all integrated components. A future congestion-rich dataset and prospectively defined design are required; do not modify fixtures after observing results to manufacture an effect.
