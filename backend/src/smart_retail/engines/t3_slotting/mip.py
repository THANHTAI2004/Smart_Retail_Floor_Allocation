"""Exact finite strip-packing model with fixed facings and variable stock depth/layers.

One rectangular SKU block per product, full assigned shelf, shared level load.
No vertical interleaving, mixed SKU depth lanes or demand satisfaction assumption.
"""

import math
import time
from collections.abc import Callable

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

from smart_retail.domain.models import EngineError, Planogram, Product, Shelf
from smart_retail.engines.t3_slotting.validation import violations


def solve(
    shelves: tuple[Shelf, ...],
    products: tuple[Product, ...],
    assignment: dict[str, str],
    *,
    deadline: float = math.inf,
    max_options: int = 20000,
    cancelled: Callable[[], bool] = lambda: False,
) -> Planogram:
    options: list[dict] = []
    slots = [(s.id, face, level) for s in shelves for face in range(s.faces) for level in s.levels]
    shared = [(s.id, level) for s in shelves for level in s.levels]
    product_index = {p.sku: i for i, p in enumerate(products)}
    for p in products:
        for sid, face, level in slots:
            shelf = next(s for s in shelves if s.id == sid)
            if p.allowed_shelf_kinds and shelf.kind not in p.allowed_shelf_kinds:
                continue
            if sid != assignment.get(p.category_id):
                continue
            for angle in sorted(set(p.orientations)):
                width, depth = (p.width_m, p.depth_m) if angle == 0 else (p.depth_m, p.width_m)
                for facings in range(p.min_facings or p.facings, (p.max_facings or p.facings) + 1):
                    block_width = facings * (width + p.clearance_m)
                    if block_width > level.width_m + 1e-9:
                        continue
                    max_layers = min(
                        p.stack_layers,
                        math.floor((level.height_m + 1e-9) / (p.height_m + p.clearance_m)),
                    )
                    max_deep = math.floor((level.depth_m + 1e-9) / (depth + p.clearance_m))
                    for layers in range(1, max_layers + 1):
                        for deep in range(1, max_deep + 1):
                            if cancelled():
                                raise EngineError("CANCELLED", "T3 cancelled")
                            if time.monotonic() >= deadline:
                                raise EngineError(
                                    "TIMEOUT", "T3 candidate generation budget exhausted"
                                )
                            capacity = facings * layers * deep
                            load = capacity * p.weight_kg
                            if level.max_load_kg is not None and load > level.max_load_kg + 1e-9:
                                continue
                            options.append(
                                dict(
                                    sku=p.sku,
                                    shelf_id=sid,
                                    face=face,
                                    level_id=level.id,
                                    x_m=0.0,
                                    width_m=block_width,
                                    orientation=angle,
                                    facings=facings,
                                    layers=layers,
                                    depth_units=deep,
                                    capacity_units=capacity,
                                    load_kg=load,
                                )
                            )
                            if len(options) > max_options:
                                raise EngineError(
                                    "PROBLEM_LIMIT",
                                    "T3 exceeds finite candidate budget; no infeasibility claim",
                                )
    if any(not any(o["sku"] == p.sku for o in options) for p in products):
        raise EngineError(
            "INFEASIBLE", "No physical candidate for a SKU in fixed-facing strip model"
        )
    if not products:
        return Planogram((), "OPTIMAL", "milp", mip_gap=0.0)
    matrix = lil_matrix((len(products) + len(slots) + len(shared), len(options)))
    lower = np.full(matrix.shape[0], -np.inf)
    upper = np.zeros(matrix.shape[0])
    lower[: len(products)] = upper[: len(products)] = 1
    costs = []
    by_sku = {p.sku: p for p in products}
    for j, option in enumerate(options):
        matrix[product_index[option["sku"]], j] = 1
        for i, (sid, face, level) in enumerate(slots, len(products)):
            upper[i] = level.width_m
            if (sid, face, level.id) == (option["shelf_id"], option["face"], option["level_id"]):
                matrix[i, j] = option["width_m"]
        for i, (sid, level) in enumerate(shared, len(products) + len(slots)):
            upper[i] = level.max_load_kg if level.max_load_kg is not None else np.inf
            if (sid, level.id) == (option["shelf_id"], option["level_id"]):
                matrix[i, j] = option["load_kg"]
        costs.append(-by_sku[option["sku"]].demand * option["capacity_units"])
    if time.monotonic() >= deadline:
        raise EngineError("TIMEOUT", "T3 model construction budget exhausted")
    result = milp(
        np.array(costs),
        integrality=np.ones(len(options)),
        bounds=Bounds(0, 1),
        constraints=LinearConstraint(matrix.tocsr(), lower, upper),
        options={"time_limit": min(300.0, deadline - time.monotonic()), "mip_rel_gap": 0.0},
    )
    if result.status == 2:
        raise EngineError("INFEASIBLE", "HiGHS proved fixed-facing strip model infeasible")
    if result.x is None:
        raise EngineError("TIMEOUT" if result.status == 1 else "SOLVER_ERROR", str(result.message))
    placements = []
    used: dict[tuple, float] = {}
    for option, chosen in zip(options, result.x):
        if chosen > 0.5:
            key = (option["shelf_id"], option["face"], option["level_id"])
            row = {**option, "x_m": used.get(key, 0.0)}
            used[key] = row["x_m"] + row["width_m"]
            placements.append(row)
    errors = violations(shelves, products, assignment, tuple(placements))
    if errors:
        raise EngineError("INVALID_SOLUTION", "; ".join(errors))
    objective = sum(by_sku[p["sku"]].demand * p["capacity_units"] for p in placements)
    return Planogram(
        tuple(placements),
        "OPTIMAL" if result.status == 0 else "FEASIBLE_TIME_LIMIT",
        "milp",
        objective,
        mip_gap=float(result.mip_gap),
    )
