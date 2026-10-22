# Objectives and hypotheses

- H1: every accepted witness satisfies independent geometry, allocation, packing and route replay. Acceptance requires zero violations rather than relying on solver status.
- H2: T2 MILP matches independent exhaustive enumeration on a small fixture; greedy is a baseline, not assumed inferior.
- H3: T3 MIP can recover some first-fit failures. The load witness has independently enumerated optimum 14. Its designed nature prevents interpreting success frequency as a population estimate.
- H4: bounded complete-candidate evaluation can reduce route distance on identical data and seeds. E05 probes this without inventing an improvement threshold.
- H5: demand, arrival rate and wait weighting can affect results; zero treatment effects in E06/E07 remain valid outcomes.

Correctness thresholds are zero violations and objective agreement within the explicit floating tolerances in tests. No practical-effect threshold, power calculation or preregistered population efficacy claim has been established.
