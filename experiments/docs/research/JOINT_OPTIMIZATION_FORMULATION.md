# Joint T1-T4 formulation and proof scope

Version: `joint-finite-1`. Synthetic research extension of the current official
T1-T4 engines. A general optimality proof is **not** claimed.

## Decisions, data and finite domains

Let S be shelves, C categories, P products, L(s) levels, F(s) faces, O supplied
orders and K a fixed finite set of simulation seeds. The seven validated input
groups remain fixed throughout search. Demand, order contents, speeds, picker
count and arrival parameters are data, not knobs the optimizer can reduce.

An exact instance explicitly declares:

- A nonempty pose list D1(s) for every shelf: (x m, y m, rotation 0/90).
- A nonempty shelf-choice list D2(c) for every category.
- A nonempty full placement list D3(p) for every SKU: shelf/level/face, horizontal
  offset in m, orientation, facings, layers, depth units, capacity and load kg.
  Capacity/width/load fields are checked against physical dimensions; they are
  not independent free variables that can bypass validation.
- A finite list R of allowed routing policies. If R has one entry, policy is
  fixed. If it has multiple entries, every policy is evaluated. Picker count,
  scheduling rule and customer behavior remain fixed input parameters.

The joint decision domain is the Cartesian product of these lists. The solver
does not manufacture candidate lists using a heuristic and then claim coverage
of all continuous shelf locations or all strip packings. In particular, a finite
placement list restricts horizontal anchors and packing choices to those listed.
The published local-trap instance has four states; the two-shelf instance has 128.
Arbitrary continuous coordinates and unlisted slots lie outside these exact proofs.

## Joint feasibility

A point is feasible only if the official validators accept all layers:

1. T1: complete shelf identity, immutable locked shelf pose, 0/90 rotation,
   boundary, shelf overlap, clearance, obstacles, zones, entrance/exit/pickup
   access, required aisles and service-face connectivity on the declared grid.
2. T2: exactly one shelf per category, fixed assignments, aggregate usable width,
   near/separate constraints and references. Multiple categories may share a shelf;
   category splitting is outside this model.
3. T3: exactly one placement per SKU on the category-assigned shelf; kind,
   dimensions, orientation, facing bounds, depth/stack limits, usable strip,
   overlap and shared level load. This reuses independent physical replay.
4. T4: reachable valid routes and supplied order quantities under the official
   deterministic event simulator. Independent replay recomputes route segments,
   distance, time accounting, entrance/exit and picker quantities.

Unreachable/invalid decisions are rejected leaves. Unsupported resource/model
limits are not proofs of infeasibility. A complete infeasibility certificate means
no feasible point in the **declared finite domain**, not no feasible store design.

## Common objective and arithmetic

For scenario k, let t be mean journey distance (m), q mean journey wait (s),
b = sum_p max(0,demand_p-capacity_p) / max(1,sum_p demand_p), and
u = late supplied orders / max(1,number of supplied orders).
Picker wait and shelf wait are both included in q; u uses supplied due_s and the
simulator's declared elapsed-order interpretation. No actual corridor crowd
dynamics are modeled.

For nonnegative weights w with positive sum and fixed positive scales a:

`F(x) = mean_{k in K} [t/a1, q/a2, b/a3, u/a4]`

`J(x) = sum_i w_i F_i(x) / sum_i w_i`.

Scales and weights are fixed in the experiment configuration. No candidate-dependent
normalization is introduced. All four components are nonnegative, so zero is a
valid (possibly weak) global lower bound. Holdout seeds are disjoint from K and
never participate in acceptance, ranking or certification.

Simulation uses deterministic IEEE-754 computations. Serialized decimal observations,
weights and scales are converted to rational numbers for exact score comparison;
the exhaustive minimum is selected without a gap tolerance. This certifies the
minimum of the **implemented finite numerical model**, not an ideal real-arithmetic
physical system. Local-search tolerance controls strict descent only; it is not
used to manufacture an exact proof.

Global optimality of the sample-average objective on K does not imply global
optimality of the expected cost over every possible customer behavior.

## Feedback search and recomputation

The application coordinator initializes a valid solution, analyzes simulated SKU
picks, routes, shelf visits/wait and co-picked categories, and generates edits.
T1 moves/rotates/swaps unlocked shelf poses. T2 moves/swaps categories. T3 changes
face/level/offset/orientation/facings or swaps positions on the assigned shelf.
All edits are copies; validation precedes incumbent replacement. Neighborhoods
are deterministic, operational-evidence-ranked, round-robin by enabled layer and
bounded by max_actions. Full groups or continuous deformation are not operators
in this version. Diagnostics that divide journey travel/wait across picks/stops
are explicitly labeled attribution proxies, not measured per-location timings.

T1 edits invalidate downstream optimized allocation/packing/simulation; T2 edits
retain T1 and rerun T2-T4; T3 edits retain T1/T2 and rerun T3/T4. A routing edit
retains the three upstream decisions. Content keys include runtime/source/solver,
physical dependencies, all pertinent input, objective/scenario context and seeds.
An explicit decision identical to a cached official solve reuses the same artifact.
Timeout incumbents are not published as complete optimal cache entries.

Strict descent accepts only J(new) < J(current)-tolerance. Best-improvement and
first-improvement are available. The initial and best solution, candidate lineage,
before/after, constraint rejection, decisions, keys, scenarios and termination
are retained. Limits include iterations, decision evaluations, actions, patience,
target, wall time and worker RSS/cancellation. Duplicate proposals are skipped.
CONVERGED_LOCAL refers only to the actually examined, possibly truncated declared
neighborhood. The Pareto archive covers evaluated candidates only.

## Exact search, bounds, proof and hybrid

The exact engine exhaustively traverses the complete Cartesian domain, with no
heuristic pruning. It records every feasible/invalid leaf and the incumbent.
UB is the objective of a validated member of the finite domain. Before completion,
LB=0; after full enumeration LB=UB for a feasible optimum. Exhausted domains with
no feasible leaf produce INFEASIBLE_PROVEN. A timeout/limit never receives a global
proof label. No strong LP/MIP bound or branch-and-bound speed claim is made.

The certificate binds model version, input/runtime, objective, scenario hash and
finite-space hash. It contains all leaf hashes/statuses/objectives, incumbent,
rational bounds, gap, termination and completeness counts, plus a payload seal.
This checksum detects accidental edits; it is not a digital signature or proof
by itself.

The verifier never calls the search-selection routine. It separately decodes
mixed-radix ordinals, validates/evaluates every leaf using a fresh cache, checks
simulation and witness hashes, recomputes the exact minimum and bounds, validates
incumbent domain membership and rejects altered domains, scores or completeness.
Shared official physics/simulation code defines the model; the verifier is not
an independent reimplementation of SimPy or geometry. A hand-enumerated four-state
test separately checks the local plateau and the better two-face edit.

Hybrid runs feedback first, then supplies its incumbent only if that decision is
a valid member of the declared exact domain. An out-of-domain heuristic solution
is never used to certify that domain's UB. Remaining time/evaluation budget is
shared. Proof verification also shares the wall budget. A complete solver search
with unfinished verification remains FEASIBLE_NOT_PROVEN in the product proof
status, even if the raw search certificate records complete enumeration.

The independent CLI verifier can replay an exported certificate with its recorded
worker input in a compatible source/dependency environment. It refuses source
drift. The CLI is an explicit offline verification command; HTTP numerical work
continues through the killable durable worker.
