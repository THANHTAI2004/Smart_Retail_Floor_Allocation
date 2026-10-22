"""T3 physical, deterministic first-fit baseline with orientations and load checks."""

import math
import time
from collections.abc import Callable
from typing import TypedDict

from smart_retail.domain.models import EngineError, Planogram, Product, Shelf, ShelfLevel
from smart_retail.engines.t3_slotting.validation import violations


class SlotState(TypedDict):
    level: ShelfLevel
    used: float


def solve(
    shelves: tuple[Shelf, ...],
    products: tuple[Product, ...],
    assignment: dict[str, str],
    *,
    algorithm: str = "first_fit",
    deadline: float = math.inf,
    cancelled: Callable[[], bool] = lambda: False,
) -> Planogram:
    if algorithm == "milp":
        from smart_retail.engines.t3_slotting.mip import solve as optimize

        return optimize(shelves, products, assignment, deadline=deadline, cancelled=cancelled)
    if algorithm != "first_fit":
        raise EngineError("INVALID_INPUT", f"Unknown slotting algorithm {algorithm}")
    slots: dict[tuple[str, int, str], SlotState] = {
        (s.id, face, level.id): {"level": level, "used": 0.0}
        for s in shelves
        for face in range(s.faces)
        for level in s.levels
    }
    shared_load = {(s.id, level.id): 0.0 for s in shelves for level in s.levels}
    placements: list[dict] = []
    for product in sorted(products, key=lambda p: (-p.demand, p.sku)):
        if cancelled():
            raise EngineError("CANCELLED", "T3 cancelled")
        if time.monotonic() >= deadline:
            raise EngineError("TIMEOUT", "T3 first-fit budget exhausted")
        shelf_id = assignment.get(product.category_id)
        placed = False
        for (sid, face, lid), slot in slots.items():
            if sid != shelf_id:
                continue
            shelf = next(s for s in shelves if s.id == sid)
            if product.allowed_shelf_kinds and shelf.kind not in product.allowed_shelf_kinds:
                continue
            level = slot["level"]
            for angle in product.orientations:
                width, depth = (
                    (product.width_m, product.depth_m)
                    if angle == 0
                    else (product.depth_m, product.width_m)
                )
                clearance = product.clearance_m
                total_width = product.facings * (width + clearance)
                layers = min(
                    product.stack_layers,
                    math.floor((level.height_m + 1e-9) / (product.height_m + clearance)),
                )
                deep = math.floor((level.depth_m + 1e-9) / (depth + clearance))
                capacity = product.facings * layers * deep
                load = capacity * product.weight_kg
                if layers < 1 or deep < 1 or slot["used"] + total_width > level.width_m + 1e-9:
                    continue
                if (
                    level.max_load_kg is not None
                    and shared_load[(sid, lid)] + load > level.max_load_kg + 1e-9
                ):
                    continue
                placements.append(
                    {
                        "sku": product.sku,
                        "shelf_id": sid,
                        "level_id": lid,
                        "face": face,
                        "x_m": slot["used"],
                        "width_m": total_width,
                        "orientation": angle,
                        "facings": product.facings,
                        "layers": layers,
                        "depth_units": deep,
                        "capacity_units": capacity,
                        "load_kg": load,
                    }
                )
                slot["used"] += total_width
                shared_load[(sid, lid)] += load
                placed = True
                break
            if placed:
                break
        if not placed:
            raise EngineError(
                "SLOTTING_FAILED",
                f"SKU {product.sku} cannot be placed by first-fit within dimensions, facings and load limits; infeasibility is not proven",
            )
    errors = violations(shelves, products, assignment, tuple(placements))
    if errors:
        raise EngineError("INVALID_SOLUTION", "; ".join(errors))
    by_sku = {p.sku: p for p in products}
    return Planogram(
        tuple(placements),
        "FEASIBLE_FIRST_FIT",
        objective=sum(by_sku[p["sku"]].demand * p["capacity_units"] for p in placements),
    )
