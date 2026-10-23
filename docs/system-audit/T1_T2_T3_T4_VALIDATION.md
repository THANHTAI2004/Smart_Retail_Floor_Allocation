# Independent T1 through T4 validation

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Starting Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; changes remain uncommitted by instruction.
MongoDB Atlas: **OUT_OF_SCOPE**, never a failed or blocked gate. The parent attempt directory retains superseded receipts and before-fix logs; E/../ denotes that parent.

All engine claims below are backed by fresh execution, not only source inspection. Source: engines/t1_layout, t2_allocation, t3_slotting, t4_simulation; application/experiments/validation.py. Full-suite tests are listed in E/long-path/*.xml.

| Stage | Independent checks and expected result | Fresh evidence and actual result |
|---|---|---|
| T1 | Boundary containment, no overlap/obstacle intersection, aisle separation, access connectivity; fixed poses unchanged | E/numerical/t1-fixtures.json: tiny, obstacle, fixed and multiple-shelf fixtures have no violations. Oversized shelf dimension reasoning is recorded separately from heuristic engine status. Unit tests exercise invalid geometry, timeout, cancellation and search limit. |
| T2 | Assignment uniqueness/coverage, compatible capacity, fixed allocation/proximity/separation; objective reconstructed against independent enumeration | unit/test_engines.py::test_t2_matches_independent_enumeration and test_t2_proves_infeasible_and_honors_fixed_and_proximity pass in both suites; campaign validator checks real stage output. |
| T3 | Independent stock enumeration and replay of dimensions, orientation, facings, depth/height, stock, overlap, load sharing and SKU coverage | unit/test_planogram_replay.py and physical capacity property tests pass; deliberate missing/duplicate/overlap/shared-load corruption is rejected. First-fit is feasible heuristic; MILP bounds only apply to its stated formulation. |
| T4 | Recompute route polyline length, obstacle/topology validity, SKU target/quantity, travel/service/queue time and order completion | E/numerical/manual-route.json: WATER 3 + RICE 2, distance 16.707106781186546 m; travel at 1.2 m/s + 20 s picking = 33.92258898432212 s, matching engine within floating tolerance. Campaign independent validator replays real journeys. |

T1 heuristic search exhaustion is never promoted to proven infeasibility. Oversized-fixture dimensional reasoning is an independent special-case proof, not a general search certificate. T2/T3 finite/MILP optimality statuses retain their formulation/budget scope. All named status and error semantics remain unchanged.

T4 assumptions are visible in simulation UI: synthetic baskets/Poisson arrivals, four-neighbor navigation, finite picker pool, one-server queues at shelves, no corridor pedestrian dynamics. Customers choose a declared exit connector; pickers return to the entrance. Arrivals stop at horizon, but accepted journeys drain to completion. Order timestamps are normalized to earliest supplied order. Exact routing covers a bounded closed tour with <=10 service locations, not unrestricted multi-exit open TSP. Pickup-fulfillment behavior is outside the implemented routing model. Numerical consistency is verified for synthetic inputs; empirical realism has not been established by observed store trajectories.

The integrated worker path consumes all preceding stage outputs. E/pilot-campaign/records and E/joint-campaign/records retain actual run IDs, input/result SHA, validations, stage outcomes and failed-stage details. Reports include failures rather than discarding unfavorable outcomes.
