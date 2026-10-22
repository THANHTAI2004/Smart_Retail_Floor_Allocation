"""Bounded deterministic best-improvement local search of feasible grid poses."""

import math
import time
from collections.abc import Callable
from dataclasses import replace

from smart_retail.domain.models import EngineError, Floorplan, LayoutSolution, Shelf
from smart_retail.engines.navigation import validate_topology
from smart_retail.engines.t1_layout.geometry import footprint, violations


def objective(floor: Floorplan, shelves: tuple[Shelf, ...]) -> float:
    return sum(
        math.dist(floor.entrance, (footprint(s).centroid.x, footprint(s).centroid.y))
        for s in shelves
    )


def improve(
    floor: Floorplan,
    shelves: tuple[Shelf, ...],
    deadline: float,
    budget: int,
    cancelled: Callable[[], bool],
) -> LayoutSolution:
    incumbent, score = shelves, objective(floor, shelves)
    used = 0
    while used < budget and time.monotonic() < deadline:
        best, value = incumbent, score
        for i, shelf in enumerate(incumbent):
            if shelf.locked:
                continue
            for dx, dy, rotation in (
                (-floor.grid_m, 0, shelf.rotation),
                (floor.grid_m, 0, shelf.rotation),
                (0, -floor.grid_m, shelf.rotation),
                (0, floor.grid_m, shelf.rotation),
                (0, 0, 90 - shelf.rotation),
            ):
                if cancelled():
                    raise EngineError("CANCELLED", "T1 local search cancelled")
                if used >= budget or time.monotonic() >= deadline:
                    break
                used += 1
                moved = replace(
                    shelf, x=(shelf.x or 0) + dx, y=(shelf.y or 0) + dy, rotation=rotation
                )
                candidate = incumbent[:i] + (moved,) + incumbent[i + 1 :]
                if violations(floor, candidate):
                    continue
                cost = objective(floor, candidate)
                if cost < value - 1e-9:
                    try:
                        validate_topology(floor, candidate, deadline)
                    except EngineError as exc:
                        if exc.code == "TIMEOUT":
                            break
                        continue
                    best, value = candidate, cost
        if value >= score - 1e-9:
            break
        incumbent, score = best, value
    return LayoutSolution(incumbent, "FEASIBLE_LOCAL_SEARCH", "local_search", score)
