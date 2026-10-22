"""Independent planogram replay from physical inputs, without solver matrices."""

import math
from collections import defaultdict

from smart_retail.domain.models import Product, Shelf


def violations(
    shelves: tuple[Shelf, ...],
    products: tuple[Product, ...],
    assignment: dict[str, str],
    placements: tuple[dict, ...],
) -> list[str]:
    errors: list[str] = []
    catalogue = {p.sku: p for p in products}
    fixtures = {s.id: s for s in shelves}
    seen: set[str] = set()
    occupied: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    loads: dict[tuple, float] = defaultdict(float)
    for row in placements:
        try:
            sku, sid = row["sku"], row["shelf_id"]
            if sku in seen or sku not in catalogue or sid not in fixtures:
                errors.append("Unknown or duplicate SKU/shelf")
                continue
            seen.add(sku)
            p, shelf = catalogue[sku], fixtures[sid]
            level = next(x for x in shelf.levels if x.id == row["level_id"])
            if assignment.get(p.category_id) != sid:
                errors.append(f"{sku}: category assignment mismatch")
            if p.allowed_shelf_kinds and shelf.kind not in p.allowed_shelf_kinds:
                errors.append(f"{sku}: incompatible shelf kind")
            for field in (
                "face",
                "facings",
                "layers",
                "depth_units",
                "capacity_units",
                "orientation",
            ):
                if type(row[field]) is not int:
                    raise ValueError(f"{field} must be integer")
            face, layers, deep = row["face"], row["layers"], row["depth_units"]
            if not 0 <= face < shelf.faces or row["orientation"] not in p.orientations:
                errors.append(f"{sku}: invalid face/orientation")
            width, depth = (
                (p.width_m, p.depth_m) if row["orientation"] == 0 else (p.depth_m, p.width_m)
            )
            expected_width = row["facings"] * (width + p.clearance_m)
            capacity = row["facings"] * layers * deep
            load = capacity * p.weight_kg
            if (
                not (p.min_facings or p.facings) <= row["facings"] <= (p.max_facings or p.facings)
                or not 1 <= layers <= p.stack_layers
                or deep < 1
                or layers * (p.height_m + p.clearance_m) > level.height_m + 1e-8
                or deep * (depth + p.clearance_m) > level.depth_m + 1e-8
                or capacity != row["capacity_units"]
            ):
                errors.append(f"{sku}: capacity/facing/stacking mismatch")
            if any(not math.isfinite(row[k]) for k in ("x_m", "width_m", "load_kg")):
                raise ValueError("Non-finite placement")
            if abs(row["width_m"] - expected_width) > 1e-8 or abs(row["load_kg"] - load) > 1e-8:
                errors.append(f"{sku}: dimensions/load mismatch")
            start, end = row["x_m"], row["x_m"] + expected_width
            if start < -1e-8 or end > level.width_m + 1e-8:
                errors.append(f"{sku}: exceeds usable width")
            key = (sid, face, level.id)
            if any(min(end, b) - max(start, a) > 1e-8 for a, b in occupied[key]):
                errors.append(f"{sku}: overlapping placement")
            occupied[key].append((start, end))
            loads[sid, level.id] += load
        except (KeyError, ValueError, TypeError, StopIteration) as exc:
            errors.append(f"Malformed placement: {exc}")
    if seen != set(catalogue):
        errors.append("Missing product placement")
    for shelf in shelves:
        for level in shelf.levels:
            if (
                level.max_load_kg is not None
                and loads[shelf.id, level.id] > level.max_load_kg + 1e-8
            ):
                errors.append(f"{shelf.id}/{level.id}: shared load exceeded")
    return errors
