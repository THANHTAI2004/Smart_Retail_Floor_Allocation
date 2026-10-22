# Executed model and evidence scope - 2026-10-22

Joint extension: [JOINT_OPTIMIZATION_FORMULATION.md](JOINT_OPTIMIZATION_FORMULATION.md)
defines the new closed-loop and finite exact modes. Baseline limitations below
remain applicable except for the explicitly extended feedback/certificate scope.

Status: EXPERIMENT_READY_SYNTHETIC for the published local Windows/SQLite scope.
The earlier broad acceptance matrix remains historical; the user explicitly
defined a separate synthetic experiment target and permitted SQLite acceptance.

## Input version and provenance

Seven root envelopes use schema_version 1.1 and an explicit data_origin. Nested
entities remain strict Pydantic contracts. Unknown fields/versions, unsupported
algorithm names, invalid physical units/dimensions and references are rejected.
Versionless current-application data can be explicitly normalized from 1.0 to
1.1 when creating a new immutable snapshot; original saved aggregates are not
rewritten. The snapshot records every migrated section.

The campaign version is 1.0. CSV tables preserve parent metadata and nested JSON
cells, including empty tables. This is a lossless research interchange format,
not a promise to infer arbitrary third-party spreadsheets. A custom synthetic
seven-group JSON bundle can be selected with input_path and input_file_sha256 in
a DatasetSpec; the file must be under datasets/ and every group must explicitly
declare SYNTHETIC. Both raw-file and normalized-bundle fingerprints are retained.

## T1

Grid construction and deterministic multistart are baselines. Local search moves
an unlocked shelf by one grid step or swaps its 0/90 orientation, retaining only
geometrically and topologically valid improvements. The geometric objective is
the sum of shelf-centroid distances from entrance, in m. It is a proxy rather
than a customer route objective. All accepted layouts replay boundary, clearance,
obstacles, reserved zones, exit/pickup access and service faces. Full free-grid
connectivity is enforced when requested. Every required-aisle zone must connect
to the entrance component. Resolution is explicit; no continuous egress or
global-optimality proof is asserted.

## T2

One category chooses one shelf; several categories can share a shelf. Fixed,
capacity, near and separate restrictions are hard. Soft affinity contributes a
normalized weighted centroid-distance penalty. The MILP linearizes each binary
assignment product with three constraints; greedy evaluates affinity against
already selected assignments. The total model is capped at 20,000 variables.
Independent dictionary replay recomputes constraints and objective, including
affinity. Category splitting is outside this declared model.

## T3

Finite options now include every allowed facing count between min/max (falling
back to the declared fixed facings), orientation, depth count and stack count.
Shelf-kind compatibility is enforced. Per face/level summed widths and shared
level load constrain the options; blocks concatenate along x. Objective maximizes
demand-weighted capacity. No multiple blocks per SKU or mixed-SKU depth/vertical
interleaving. Per-face usable depth is a model convention requiring validation
against actual fixture specifications before field use. Face 0 is min-y at
orientation 0 and min-x at orientation 90; face 1 is the opposite service side.
OPTIMAL/INFEASIBLE are scoped to this finite model. PROBLEM_LIMIT does not prove
infeasibility.

## T4

Nearest-next, return-per-stop and exact closed small-tour policies use the same
valid grid shortest paths. Exact covers at most ten distinct service locations.
Customers finish at the least-cost declared exit connector; pickers return to
entrance. Exact tour ordering with subsequent exit choice is not an exact open
multi-exit TSP. Orders seize a finite picker resource until completion. Elapsed
time includes picker-pool wait, travel, per-unit dwell and shelf-queue wait.
Piecewise arrival periods override the global rate, and gaps produce no arrivals.
Admitted journeys drain after the arrival horizon. Queues are at shelves, not
pedestrian corridor dynamics; inventory is not depleted or replenished.

## Execution, resources and cache

Each job is a killable spawned process. The supervisor measures wall time from
before process creation, samples the child's OS peak working set/CPU and enforces
the configured RSS cap and wall limit. Sampling is discrete; it is not a
continuous per-allocation memory trace. One worker executes a campaign at a time.
The plan has a hard 1,000-job ceiling and stores compact descriptors/fingerprints
rather than duplicating a large input bundle per seed. No unbounded search or
retry is used. Only WORKER_CRASH/WORKER_LOST receive bounded retries.

Stage JSON artifacts include inputs, content key, output hash, cache-hit telemetry
and elapsed time. Persistent cache keys bind source/dependency/model identities,
inputs, algorithm settings and budget. Benchmark campaigns default to isolated
per-job caches; reuse is explicit. Normal project workflows use cross-run cache
to recompute affected stages only. Scientific result bytes omit variable
telemetry; receipts/stage artifacts preserve it. Exact result-byte equality and
numeric equivalence (atol 1e-8, rtol 1e-9) are reported separately.

## Scientific limits

Five seeds on controlled examples do not establish general store-population
efficacy. E06 changes arrival rate and picker count together; its effects cannot
be attributed to either factor alone. E07 can legitimately have zero effect.
E08 executes T1 on four scales; Large full T1-T4/MIP scaling is not established.
Production/PostgreSQL/Compose, observed shopper behavior, calibration, real data
rights and S05/S06/S07 field evidence remain unverified. No REAL_WORLD_VALIDATED,
global integrated optimum or full crowd-dynamics claim.
