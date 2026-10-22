"""T2 capacitated category allocation: HiGHS MILP and deterministic greedy baseline."""

import math

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

from smart_retail.domain.models import Category, EngineError, Floorplan, Shelf
from smart_retail.engines.t1_layout.engine import footprint
from smart_retail.engines.t2_allocation.validation import replay


def solve(
    floor: Floorplan,
    shelves: tuple[Shelf, ...],
    categories: tuple[Category, ...],
    *,
    algorithm: str = "milp",
    time_limit_s: float = 30,
    distance_weight: float = 1,
    affinity_weight: float = 1,
) -> dict:
    if algorithm not in ("milp", "greedy"):
        raise EngineError("INVALID_INPUT", f"Unknown allocation algorithm {algorithm}")
    n, m = len(categories), len(shelves)
    if n * m > 20000:
        raise EngineError("PROBLEM_LIMIT", "T2 baseline supports at most 20,000 binary variables")
    centers = [footprint(s).centroid for s in shelves]
    diag = max(math.dist(a, b) for a in floor.boundary for b in floor.boundary)
    total_demand = sum(c.demand * c.priority for c in categories) or 1
    costs = np.array(
        [
            c.demand * c.priority / total_demand * math.dist(floor.entrance, (p.x, p.y)) / diag
            for c in categories
            for p in centers
        ]
    )
    costs *= distance_weight
    capacities = [sum(level.width_m for level in s.levels) * s.faces for s in shelves]
    shelf_ids = [s.id for s in shelves]
    if any(c.fixed_shelf_id and c.fixed_shelf_id not in shelf_ids for c in categories):
        raise EngineError("INVALID_REFERENCE", "Unknown fixed shelf")
    pairs = []
    for i, c in enumerate(categories):
        for j, other in enumerate(categories):
            if other.id in c.near + c.separate:
                for k, p in enumerate(centers):
                    for other_index, q in enumerate(centers):
                        distance = p.distance(q)
                        bad = (other.id in c.near and distance > c.distance_m) or (
                            other.id in c.separate and distance < c.distance_m
                        )
                        if bad:
                            pairs.append((i * m + k, j * m + other_index))
                            if len(pairs) > 200000:
                                raise EngineError(
                                    "PROBLEM_LIMIT", "Too many proximity constraints for baseline"
                                )
    affinity = []
    category_index = {c.id: i for i, c in enumerate(categories)}
    total_affinity = sum(weight for c in categories for _, weight in c.affinity) or 1
    for i, c in enumerate(categories):
        for other_id, weight in c.affinity:
            if other_id not in category_index:
                raise EngineError("INVALID_REFERENCE", "Unknown affinity category")
            for a in range(m):
                for b in range(m):
                    affinity.append(
                        (
                            i * m + a,
                            category_index[other_id] * m + b,
                            affinity_weight
                            * weight
                            / total_affinity
                            * centers[a].distance(centers[b])
                            / diag,
                        )
                    )
                    if n * m + len(affinity) > 20000:
                        raise EngineError(
                            "PROBLEM_LIMIT", "T2 affinity linearization exceeds 20,000 variables"
                        )
    variables = n * m + len(affinity)
    if variables > 20000:
        raise EngineError("PROBLEM_LIMIT", "T2 affinity linearization exceeds 20,000 variables")
    costs = np.concatenate([costs, np.array([penalty for _, _, penalty in affinity])])
    matrix = lil_matrix((n + m + len(pairs) + 3 * len(affinity), variables), dtype=float)
    lower = np.full(matrix.shape[0], -np.inf)
    upper = np.full(matrix.shape[0], np.inf)
    bounds_upper = np.ones(variables)
    for i, c in enumerate(categories):
        matrix[i, i * m : (i + 1) * m] = 1
        lower[i] = upper[i] = 1
        for k, shelf in enumerate(shelves):
            matrix[n + k, i * m + k] = c.required_width_m
            if c.fixed_shelf_id and shelf.id != c.fixed_shelf_id:
                bounds_upper[i * m + k] = 0
    upper[n : n + m] = capacities
    for row, (a, b) in enumerate(pairs, n + m):
        matrix[row, a] = 1
        matrix[row, b] = 1
        upper[row] = 1
    for index, (a, b, _) in enumerate(affinity):
        y = n * m + index
        row = n + m + len(pairs) + index * 3
        matrix[row, y], matrix[row, a], upper[row] = 1, -1, 0
        matrix[row + 1, y], matrix[row + 1, b], upper[row + 1] = 1, -1, 0
        matrix[row + 2, a], matrix[row + 2, b], matrix[row + 2, y], upper[row + 2] = 1, 1, -1, 1

    def refresh_affinity(vector):
        for index, (a, b, _) in enumerate(affinity):
            vector[n * m + index] = vector[a] * vector[b]

    if algorithm == "greedy":
        x = np.zeros(variables)
        for i in sorted(
            range(n),
            key=lambda i: (-categories[i].priority * categories[i].demand, categories[i].id),
        ):

            def rank(k):
                trial = x.copy()
                trial[i * m + k] = 1
                refresh_affinity(trial)
                return (float(costs @ trial), shelves[k].id)

            for k in sorted(range(m), key=rank):
                idx = i * m + k
                if not bounds_upper[idx]:
                    continue
                x[idx] = 1
                refresh_affinity(x)
                if np.all(matrix @ x <= upper + 1e-7):
                    break
                x[idx] = 0
                refresh_affinity(x)
            else:
                raise EngineError(
                    "SEARCH_EXHAUSTED",
                    "Greedy category assignment failed; infeasibility is not proven",
                )
        status = "FEASIBLE_GREEDY"
    else:
        result = milp(
            costs,
            integrality=np.ones(variables),
            bounds=Bounds(np.zeros(variables), bounds_upper),
            constraints=LinearConstraint(matrix.tocsr(), lower, upper),
            options={"time_limit": max(0.001, time_limit_s), "mip_rel_gap": 0.0, "presolve": True},
        )
        if result.status == 2:
            raise EngineError("INFEASIBLE", "HiGHS proved category allocation infeasible")
        if result.x is None:
            raise EngineError(
                "TIMEOUT" if result.status == 1 else "SOLVER_ERROR", str(result.message)
            )
        x = np.rint(result.x)
        status = "OPTIMAL" if result.status == 0 else "FEASIBLE_TIME_LIMIT"
    values = matrix @ x
    if not (
        np.all(values >= lower - 1e-6)
        and np.all(values <= upper + 1e-6)
        and np.all(x <= bounds_upper)
    ):
        raise EngineError("INVALID_SOLUTION", "Independent assignment constraint replay failed")
    assignment = {
        c.id: shelves[int(np.argmax(x[i * m : (i + 1) * m]))].id for i, c in enumerate(categories)
    }
    errors, objective = replay(
        floor, shelves, categories, assignment, distance_weight, affinity_weight
    )
    if errors or abs(objective - float(costs @ x)) > 1e-7:
        raise EngineError("INVALID_SOLUTION", "; ".join(errors) or "Objective replay mismatch")
    return {
        "status": status,
        "assignment": assignment,
        "objective": float(costs @ x),
        "objective_units": "dimensionless demand-weighted entrance distance / floor diagonal",
        "algorithm": algorithm,
        "mip_gap": float(result.mip_gap) if algorithm == "milp" else None,
    }
