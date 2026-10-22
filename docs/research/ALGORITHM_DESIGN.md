> Historical checkpoint: 2026-10-21. For the current 2026-10-22 implementation, use [model scope](MODEL_SCOPE_20261022.md), [ER readiness](EXPERIMENT_READINESS_MATRIX.md), and [actual results](RESULTS_20261022.md). The historical gates and limits below are not the current synthetic-readiness assessment.

# Algorithm design

1. Parse seven input sections to frozen domain models. Enqueue a snapshot with runtime/source identity.
2. Atomically claim a durable job and start a killable child process. All candidates share a wall deadline.
3. For i=0..candidate_count-1 (at most 8), construct T1 with fixed locks and variant sweep/order, then replay geometry.
4. Run T2 greedy or HiGHS MILP. Independently replay the assignment dictionary and objective without reusing the solver matrix as the only oracle.
5. Run T3 first-fit or finite strip MIP. Independent replay checks orientation, facings, depth/layers, dimensions, capacity, shared load and interval overlap.
6. T4 builds valid grid edges and face-specific pickup targets, runs synthetic customers and supplied picker orders, and exports route points and pick quantities.
7. Only complete candidates participate in selection. Candidate-specific allocation infeasibility never proves whole-system infeasibility.
8. Return the selected score, finite nondominated set, all candidate witnesses/failures and termination reason.

Stage cache keys hash dependent inputs, an algorithm version and snapshot runtime. Reuse is limited to one run. Changing products invalidates T3/T4 while preserving independent T1/T2. Persistent cross-run cache, generic partial rerun and bounded retry are not implemented. A common wall budget can favor early candidates.

Sources: [workflow](../../backend/src/smart_retail/application/workflow.py), [T3 MIP](../../backend/src/smart_retail/engines/t3_slotting/mip.py), [physical replay](../../backend/src/smart_retail/engines/t3_slotting/validation.py).
