"""Assignment replay independent of the MILP coefficient matrix."""

import math

from smart_retail.domain.models import Category, Floorplan, Shelf
from smart_retail.engines.t1_layout.engine import footprint


def replay(
    floor: Floorplan,
    shelves: tuple[Shelf, ...],
    categories: tuple[Category, ...],
    assignment: dict[str, str],
    distance_weight: float = 1,
    affinity_weight: float = 1,
) -> tuple[list[str], float]:
    errors = []
    by_id = {s.id: s for s in shelves}
    if (
        set(assignment) != {c.id for c in categories}
        or not set(assignment.values()) <= by_id.keys()
    ):
        return ["Assignment keys/references mismatch"], math.nan
    used = dict.fromkeys(by_id, 0.0)
    centers = {s.id: footprint(s).centroid for s in shelves}
    objective = 0.0
    diagonal = max(math.dist(a, b) for a in floor.boundary for b in floor.boundary)
    total = sum(c.demand * c.priority for c in categories) or 1
    for c in categories:
        sid = assignment[c.id]
        used[sid] += c.required_width_m
        if c.fixed_shelf_id is not None and c.fixed_shelf_id != sid:
            errors.append(f"{c.id}: fixed shelf mismatch")
        for other in c.near + c.separate:
            if other not in assignment:
                errors.append(f"{c.id}: unknown proximity reference")
                continue
            distance = centers[sid].distance(centers[assignment[other]])
            if (other in c.near and distance > c.distance_m + 1e-7) or (
                other in c.separate and distance < c.distance_m - 1e-7
            ):
                errors.append(f"{c.id}/{other}: proximity violation")
        point = centers[sid]
        objective += (
            distance_weight
            * c.demand
            * c.priority
            / total
            * math.dist(floor.entrance, (point.x, point.y))
            / diagonal
        )
    affinity_total = sum(weight for c in categories for _, weight in c.affinity) or 1
    for c in categories:
        for other, weight in c.affinity:
            if other not in assignment:
                errors.append("Unknown affinity reference")
                continue
            objective += (
                affinity_weight
                * weight
                / affinity_total
                * centers[assignment[c.id]].distance(centers[assignment[other]])
                / diagonal
            )
    for sid, amount in used.items():
        if amount > sum(level.width_m for level in by_id[sid].levels) * by_id[sid].faces + 1e-7:
            errors.append(f"{sid}: category width exceeds capacity")
    return errors, objective
