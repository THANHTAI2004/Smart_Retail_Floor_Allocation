import copy
import math
from dataclasses import replace

import pytest
from shapely.geometry import LineString, Polygon

from smart_retail.application.workflow import execute
from smart_retail.contracts.inputs import to_domain
from smart_retail.engines.t1_layout.engine import footprint
from smart_retail.engines.t2_allocation.validation import replay


def test_integrated_candidates_replay_determinism_and_selection(sample):
    sample["optimization"].update(candidate_count=4, slotting_algorithm="milp")
    original = copy.deepcopy(sample)
    a, b = execute(sample), execute(sample)
    assert a == b
    assert original == sample
    integrated = a["integrated"]
    feasible = [r for r in integrated["candidates"] if r["status"] == "FEASIBLE"]
    assert len(feasible) == 4
    selected = next(r for r in feasible if r["candidate"] == integrated["selected_candidate"])
    assert selected["score"] == min(r["score"] for r in feasible)
    assert a["stages"] == selected["stages"]
    assert selected["candidate"] in integrated["pareto_candidates"]
    assert not integrated["global_optimality_proven"]


def test_routes_replay_geometry_distance_elapsed_and_quantities(sample):
    sample["demand"]["customers"] = 0
    result = execute(sample)
    metrics = result["stages"]["T4"]["metrics"]
    assert len(metrics["journeys"]) == len(metrics["routes"]) == 1
    journey, route = metrics["journeys"][0], metrics["routes"][0]
    assert {p["sku"]: p["quantity"] for p in journey["picks"]} == {"WATER": 3, "RICE": 2}
    points = route["points_m"]
    assert points[0] == points[-1] == tuple(sample["floorplan"]["entrance"])
    total = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
    assert journey["distance_m"] == pytest.approx(total)
    assert journey["wait_s"] == 0
    assert journey["elapsed_s"] == pytest.approx(total / 1.2 + 5 * 4)
    d = to_domain(sample)
    shelves = tuple(
        replace(s, **{k: row[k] for k in ("x", "y", "rotation")})
        for s, row in zip(d.shelves, result["stages"]["T1"]["shelves"])
    )
    for left, right in zip(points, points[1:]):
        if left == right:
            continue
        line = LineString([left, right])
        assert Polygon(d.floorplan.boundary).covers(line)
        assert all(not line.intersects(footprint(s)) for s in shelves)
        assert all(not line.intersects(Polygon(o)) for o in d.floorplan.obstacles)


def test_t2_independent_replay_detects_tampered_capacity_fixed_and_separation(sample):
    from smart_retail.engines.t1_layout.engine import solve

    d = to_domain(sample)
    shelves = solve(d.floorplan, d.shelves, d.layout_mode).shelves
    cats = (
        replace(d.categories[0], fixed_shelf_id="S02", separate=("FOOD",), distance_m=99),
        d.categories[1],
    )
    errors, _ = replay(d.floorplan, shelves, cats, {"DRINK": "S01", "FOOD": "S01"})
    assert any("capacity" in e for e in errors)
    assert any("fixed" in e for e in errors)
    assert any("proximity" in e for e in errors)


def test_cache_reuses_only_identical_dependencies_and_invalidates_products(sample):
    import time

    from smart_retail.application.workflow import _candidate

    cache = {}
    deadline = time.monotonic() + 10
    first = _candidate(sample, deadline=deadline, cache=cache)
    second = _candidate(sample, deadline=deadline, cache=cache)
    assert all(row["hit"] for row in second["stage_cache"].values())
    assert first["stages"] == second["stages"]
    sample["products"]["items"][0]["demand"] += 1
    changed = _candidate(sample, deadline=deadline, cache=cache)
    assert changed["stage_cache"]["T1"]["hit"]
    assert changed["stage_cache"]["T2"]["hit"]
    assert not changed["stage_cache"]["T3"]["hit"]
    assert not changed["stage_cache"]["T4"]["hit"]
