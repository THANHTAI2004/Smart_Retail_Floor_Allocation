# Synthetic experiment readiness

Target: EXPERIMENT_READY_SYNTHETIC on a compatible local Windows/Python 3.12/SQLite
environment. Final status is determined by EXPERIMENT_READINESS_MATRIX.md and
executable evidence, not by the existence of source files.

This scope permits controlled synthetic and benchmark experiments with explicit
solver limits and failure outcomes. An algorithm may fail to find a solution or
hit a resource limit without making the experiment framework invalid, provided
the outcome is recorded honestly and no invalid witness is accepted.

Scientific scope: rectangular shelf poses at 0/90 degrees; one shelf per category,
multiple categories per shelf; hard fixed/near/separate constraints and normalized
soft affinity; one SKU block per level/face with orientation/facing range and
shared load; grid walking and shelf queues with a finite picker pool. Exact route
optimization covers a closed tour of at most ten service locations. Optional
customer exit selection is evaluated after the closed-tour order and is not an
exact multi-exit TSP. No corridor crowd dynamics or calibrated shopper behavior.

Campaign scale declarations: Tiny 4 shelves/3 categories/12 SKUs/20 orders; Small
12/6/48/100; Medium 36/12/180/500; Large 80/25/500/2000. The executed stage and
instance are explicit in each plan. A Large T1 run is not evidence that a full
Large T1-T4 or large MIP solves within budget. Unexecuted jobs are explicitly
NOT_EXECUTED_RESOURCE_LIMIT and are never counted as passed experiments.

Primary acceptance: zero independently replayed constraint/route violations,
valid input/artifact hashes, bounded cancellation/timeout/resources, resumable
campaigns without rewriting valid completed jobs, full failure retention,
scientific replay comparison and actual report/dashboard evidence.

Statistics are descriptive/paired exploratory. Repeated identical seeds are
averaged before paired inference; small or degenerate samples receive no invented
p-value. Fixed data/seed observations do not establish efficacy across stores.

PostgreSQL/Docker and real S05/S06/S07 evidence are not prerequisites for this
explicit SQLite synthetic scope. They remain unverified external/deployment
limitations. REAL_WORLD_VALIDATED is never inferred from synthetic readiness.
