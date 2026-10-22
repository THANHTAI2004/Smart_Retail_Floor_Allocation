"""T1 deterministic grid construction and independently callable geometry checks."""

import math
import random
import time
from collections.abc import Callable
from dataclasses import replace

from shapely.geometry import Point, Polygon

from smart_retail.domain.models import EngineError, Floorplan, LayoutSolution, Shelf
from smart_retail.engines.t1_layout.geometry import footprint, violations


def solve(
    floor: Floorplan,
    shelves: tuple[Shelf, ...],
    mode: str,
    *,
    deadline: float = math.inf,
    max_iterations: int = 10000,
    cancelled: Callable[[], bool] = lambda: False,
    variant: int = 0,
    algorithm: str = "grid",
) -> LayoutSolution:
    if algorithm not in ("grid", "local_search"):
        raise EngineError("INVALID_INPUT", "Unknown layout algorithm")
    if mode == "fixed":
        errors = violations(floor, shelves)
        if errors:
            raise EngineError("INVALID_LAYOUT", "; ".join(errors))
        from smart_retail.engines.navigation import validate_topology

        validate_topology(floor, shelves, deadline)
        from smart_retail.engines.t1_layout.search import objective

        return LayoutSolution(shelves, "VALID_FIXED", "fixed", objective(floor, shelves))
    placed = tuple(s for s in shelves if s.locked)
    errors = violations(floor, placed)
    if errors:
        raise EngineError("INVALID_LOCKED_LAYOUT", "; ".join(errors))
    boundary = Polygon(floor.boundary)
    minx, miny, maxx, maxy = boundary.bounds
    boundary_line = boundary.boundary
    obstacle_shapes = [Polygon(p) for p in floor.obstacles] + [
        Polygon(z.boundary) for z in floor.zones
    ]
    placed_shapes = [footprint(s) for s in placed]
    entrance = Point(floor.entrance)
    clearance = floor.min_aisle_m - 1e-8
    iterations = 0
    ordered = sorted(
        (s for s in shelves if not s.locked), key=lambda s: (-s.width_m * s.depth_m, s.id)
    )
    if variant:
        random.Random(variant).shuffle(ordered)
    ys = list(range(math.ceil((maxy - miny) / floor.grid_m) + 1))
    xs = list(range(math.ceil((maxx - minx) / floor.grid_m) + 1))
    if variant & 1:
        xs.reverse()
    if variant & 2:
        ys.reverse()
    for shelf in ordered:
        found = None
        for iy in ys:
            if found:
                break
            for ix in xs:
                for rotation in (90, 0) if variant & 4 else (0, 90):
                    if cancelled():
                        raise EngineError("CANCELLED", "Run was cancelled")
                    if time.monotonic() >= deadline:
                        raise EngineError("TIMEOUT", "T1 time limit reached")
                    iterations += 1
                    if iterations > max_iterations:
                        raise EngineError(
                            "SEARCH_EXHAUSTED",
                            "T1 grid candidate limit reached; infeasibility is not proven",
                        )
                    candidate = replace(
                        shelf,
                        x=round(minx + ix * floor.grid_m, 8),
                        y=round(miny + iy * floor.grid_m, 8),
                        rotation=rotation,
                    )
                    shape = footprint(candidate)
                    valid = (
                        boundary.covers(shape)
                        and shape.distance(boundary_line) >= clearance
                        and shape.distance(entrance) >= clearance
                        and all(
                            not shape.intersects(o) and shape.distance(o) >= clearance
                            for o in obstacle_shapes
                        )
                        and all(
                            not shape.intersects(other) and shape.distance(other) >= clearance
                            for other in placed_shapes
                        )
                    )
                    if valid:
                        found = candidate
                        break
                if found:
                    break
        if found is None:
            raise EngineError(
                "SEARCH_EXHAUSTED",
                f"No grid placement found for {shelf.id}; infeasibility is not proven",
            )
        placed += (found,)
        placed_shapes.append(footprint(found))
    by_id = {s.id: s for s in placed}
    solution = tuple(by_id[s.id] for s in shelves)
    errors = violations(floor, solution)
    if errors:
        raise EngineError("INVALID_SOLUTION", "; ".join(errors))
    from smart_retail.engines.navigation import validate_topology

    validate_topology(floor, solution, deadline)
    if algorithm == "local_search":
        from smart_retail.engines.t1_layout.search import improve

        return improve(floor, solution, deadline, max(0, max_iterations - iterations), cancelled)
    from smart_retail.engines.t1_layout.search import objective

    return LayoutSolution(solution, "FEASIBLE_GRID_BASELINE", "grid", objective(floor, solution))
