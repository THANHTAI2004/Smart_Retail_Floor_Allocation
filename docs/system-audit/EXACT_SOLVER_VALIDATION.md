# Finite exact and hybrid solver validation

Audit `20261022-afbb7971`, performed on 2026-10-22. All paths below are relative to the repository unless stated otherwise.

Evidence root: `var/system-audit/20261022-afbb7971/final/` (abbreviated **E/** below).
Source SHA-256: `321d73d95a4ba9952f4af622601a02edb04f2ad95e60e5c1ddb569408e8841dc`. Starting Git HEAD: `081253604b329b4fba0a75bfe8c58755d47c3fd7`; changes remain uncommitted by instruction.
MongoDB Atlas: **OUT_OF_SCOPE**, never a failed or blocked gate. The parent attempt directory retains superseded receipts and before-fix logs; E/../ denotes that parent.

Source: engines/joint_exact/{formulation,solver,verifier}. Exact joint optimization enumerates a declared finite set of shelf poses, category assignments and physical placements, with seeded T4 evaluation and fixed score weights. Global optimality means global within that finite space and objective, not unrestricted continuous retail floor design or expected real-world behavior.

Fresh unit/test_joint_optimization.py executes an independent manually enumerated four-state reference. The local trap is strictly worse than the certified global state; the full certificate covers all four states, both products face the entrance, absolute gap zero and independent verification PASS. Separate tests cover a single state, ties, fully enumerated infeasibility, corrupt domain rows INVALID_MODEL, partial bounded-gap search and timeout before any evaluation. An incomplete search never claims OPTIMAL_CERTIFIED or global infeasibility.

Eight adversarial certificate attacks (seal, objective, lower bound, relative gap, solution, omitted leaves, altered finite space and altered input identity) are rejected, including resealed payloads. Verifier re-evaluates constraints/objective with immutable identity instead of trusting a digest alone. Raw exact score fractions preserve precision through MongoDB JSON/GridFS roundtrips.

Hybrid uses feedback as an incumbent followed by bounded exact search over the same declared space. It retains valid upper/lower bounds, scope, termination reason, evaluation budget and holdout fields. Finite certification remains limited to complete verified enumeration. Fresh E/joint-campaign has baseline, integrated, feedback, exact and hybrid on seeds 11 and 23; E/joint-replay and joint-comparison.json check scientific reproducibility. E/compose/verification.json includes real feedback/exact/hybrid HTTP campaign jobs inside Docker. No MILP result is relabeled as a certificate for an unrelated nonlinear simulation objective.

Evidence: full-long.xml/full-short.xml test_joint_optimization cases; integration/test_joint_research_http.py; test_joint_no_incumbent.py; E/joint-campaign and E/joint-report. All referenced automated commands exit 0; individual run outcomes remain explicitly classified in experiment records.
