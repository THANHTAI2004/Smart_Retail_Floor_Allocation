"""Bounded deterministic repacking of one shelf after a first-fit dead end.

The assignment, fixed facings and maximum stacking policy remain unchanged.
Failure to find a witness inside these bounds never proves infeasibility.
"""

import math
import time
from collections.abc import Callable

from smart_retail.domain.models import EngineError, Product, Shelf

MAX_REPAIR_NODES = 20000
MAX_REPAIR_PRODUCTS = 64


def repack(
    shelf: Shelf,
    products: tuple[Product, ...],
    *,
    deadline: float,
    cancelled: Callable[[], bool],
    max_nodes: int = MAX_REPAIR_NODES,
) -> list[dict] | None:
    if len(products) > MAX_REPAIR_PRODUCTS:
        return None
    if any(p.allowed_shelf_kinds and shelf.kind not in p.allowed_shelf_kinds for p in products):
        return None
    ordered = sorted(products, key=lambda p: (
        -p.facings * min((p.width_m if a == 0 else p.depth_m) + p.clearance_m
                         for a in p.orientations), -p.height_m, -p.demand, p.sku
    ))
    slots = [(face, i) for face in range(shelf.faces) for i in range(len(shelf.levels))]
    used = [0.0] * len(slots)
    loads = [0.0] * len(shelf.levels)
    rows: list[dict] = []
    visited: set[tuple] = set()
    nodes = 0

    def search(index: int) -> bool:
        nonlocal nodes
        if cancelled():
            raise EngineError("CANCELLED", "T3 shelf repair cancelled")
        if time.monotonic() >= deadline:
            raise EngineError("TIMEOUT", "T3 shelf repair budget exhausted")
        if nodes >= max_nodes:
            return False
        nodes += 1
        if index == len(ordered):
            return True
        state = (index, tuple(used), tuple(loads))
        if state in visited:
            return False
        visited.add(state)
        product = ordered[index]
        for slot_index, (face, level_index) in enumerate(slots):
            level = shelf.levels[level_index]
            for angle in product.orientations:
                width, depth = ((product.width_m, product.depth_m) if angle == 0
                                else (product.depth_m, product.width_m))
                clearance = product.clearance_m
                total_width = product.facings * (width + clearance)
                layers = min(product.stack_layers, math.floor(
                    (level.height_m + 1e-9) / (product.height_m + clearance)
                ))
                deep = math.floor((level.depth_m + 1e-9) / (depth + clearance))
                capacity = product.facings * layers * deep
                load = capacity * product.weight_kg
                if layers < 1 or deep < 1 or used[slot_index] + total_width > level.width_m + 1e-9:
                    continue
                if level.max_load_kg is not None and loads[level_index] + load > level.max_load_kg + 1e-9:
                    continue
                start, previous_load = used[slot_index], loads[level_index]
                rows.append({"sku": product.sku, "shelf_id": shelf.id,
                             "level_id": level.id, "face": face, "x_m": start,
                             "width_m": total_width, "orientation": angle,
                             "facings": product.facings, "layers": layers,
                             "depth_units": deep, "capacity_units": capacity, "load_kg": load})
                used[slot_index], loads[level_index] = start + total_width, previous_load + load
                if search(index + 1):
                    return True
                rows.pop()
                used[slot_index], loads[level_index] = start, previous_load
                if nodes >= max_nodes:
                    return False
        return False

    return rows if search(0) else None
