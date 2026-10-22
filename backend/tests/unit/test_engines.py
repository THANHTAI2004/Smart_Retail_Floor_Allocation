import itertools
import math
import time
from dataclasses import replace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError, Product, Shelf, ShelfLevel
from smart_retail.engines.t1_layout.engine import footprint, violations
from smart_retail.engines.t1_layout.engine import solve as layout
from smart_retail.engines.t2_allocation.engine import solve as allocate
from smart_retail.engines.t3_slotting.engine import solve as slot
from smart_retail.engines.t4_simulation.engine import navigation
from smart_retail.engines.t4_simulation.engine import solve as simulate


def test_t1_is_deterministic_and_constraint_checked(sample):
    d = to_domain(sample)
    a = layout(d.floorplan, d.shelves, "optimizable")
    b = layout(d.floorplan, d.shelves, "optimizable")
    assert a == b
    assert not violations(d.floorplan, a.shelves)
    assert footprint(a.shelves[0]).distance(footprint(a.shelves[1])) >= d.floorplan.min_aisle_m


@pytest.mark.parametrize("positions", [((-1, 1), (4, 1)), ((1, 1), (1, 1)), ((1, 1), (3.2, 1))])
def test_t1_rejects_outside_overlap_and_narrow_aisles(sample, positions):
    d = to_domain(sample)
    shelves = tuple(replace(s, x=p[0], y=p[1]) for s, p in zip(d.shelves, positions))
    with pytest.raises(EngineError, match="outside|aisle|overlap"):
        layout(d.floorplan, shelves, "fixed")


def test_t1_timeout_and_cancel_and_search_limit(sample):
    d = to_domain(sample)
    with pytest.raises(EngineError) as timeout:
        layout(d.floorplan, d.shelves, "optimizable", deadline=time.monotonic() - 1)
    assert timeout.value.code == "TIMEOUT"
    with pytest.raises(EngineError) as cancel:
        layout(d.floorplan, d.shelves, "optimizable", cancelled=lambda: True)
    assert cancel.value.code == "CANCELLED"
    with pytest.raises(EngineError) as limit:
        layout(d.floorplan, d.shelves, "optimizable", max_iterations=1)
    assert limit.value.code == "SEARCH_EXHAUSTED"


def test_t2_matches_independent_enumeration(sample):
    d = to_domain(sample)
    shelves = layout(d.floorplan, d.shelves, "optimizable").shelves
    result = allocate(d.floorplan, shelves, d.categories)
    diagonal = max(math.dist(a, b) for a in d.floorplan.boundary for b in d.floorplan.boundary)
    total = sum(c.demand * c.priority for c in d.categories)
    feasible = []
    for permutation in itertools.product(range(len(shelves)), repeat=len(d.categories)):
        if any(
            sum(c.required_width_m for c, k in zip(d.categories, permutation) if k == j)
            > sum(level.width_m for level in shelf.levels) * shelf.faces
            for j, shelf in enumerate(shelves)
        ):
            continue
        cost = sum(
            c.demand
            * c.priority
            / total
            * math.dist(
                d.floorplan.entrance,
                (footprint(shelves[k]).centroid.x, footprint(shelves[k]).centroid.y),
            )
            / diagonal
            for c, k in zip(d.categories, permutation)
        )
        feasible.append(cost)
    assert result["status"] == "OPTIMAL"
    assert result["objective"] == pytest.approx(min(feasible))
    weighted = allocate(d.floorplan, shelves, d.categories, distance_weight=2)
    assert weighted["assignment"] == result["assignment"]
    assert weighted["objective"] == pytest.approx(2 * result["objective"])
    assert (
        allocate(d.floorplan, shelves, d.categories, algorithm="greedy")["status"]
        == "FEASIBLE_GREEDY"
    )


def test_t2_proves_infeasible_and_honors_fixed_and_proximity(sample):
    d = to_domain(sample)
    shelves = layout(d.floorplan, d.shelves, "optimizable").shelves
    impossible = tuple(replace(c, required_width_m=9999) for c in d.categories)
    with pytest.raises(EngineError) as exc:
        allocate(d.floorplan, shelves, impossible)
    assert exc.value.code == "INFEASIBLE"
    constrained = (replace(d.categories[0], fixed_shelf_id="S02"), d.categories[1])
    assert allocate(d.floorplan, shelves, constrained)["assignment"]["DRINK"] == "S02"
    too_close = (replace(d.categories[0], near=("FOOD",), distance_m=0.1), d.categories[1])
    with pytest.raises(EngineError) as exc:
        allocate(d.floorplan, shelves, too_close)
    assert exc.value.code == "INFEASIBLE"


def test_t3_capacity_and_unfittable_product(sample):
    d = to_domain(sample)
    plan = slot(d.shelves, d.products, {"DRINK": "S01", "FOOD": "S02"})
    assert {p["sku"]: p["capacity_units"] for p in plan.placements} == {"WATER": 24, "RICE": 12}
    with pytest.raises(EngineError) as exc:
        slot(d.shelves, (replace(d.products[0], height_m=99),), {"DRINK": "S01"})
    assert exc.value.code == "SLOTTING_FAILED"
    with pytest.raises(EngineError):
        slot(d.shelves, (replace(d.products[0], weight_kg=1000),), {"DRINK": "S01"})


@given(
    width=st.floats(min_value=0.05, max_value=0.4, allow_nan=False),
    depth=st.floats(min_value=0.05, max_value=0.4, allow_nan=False),
    facing=st.integers(1, 4),
)
@settings(max_examples=40, deadline=None)
def test_t3_physical_capacity_property(width, depth, facing):
    level = ShelfLevel("L1", 2, 0.6, 0.5, 200)
    shelf = Shelf("S", 2, 0.6, 1.8, (level,))
    product = Product("P", "Product", "C", width, depth, 0.2, facings=facing, stack_layers=2)
    plan = slot((shelf,), (product,), {"C": "S"})
    p = plan.placements[0]
    assert p["x_m"] + p["width_m"] <= level.width_m + 1e-9
    assert p["depth_units"] * (depth + product.clearance_m) <= level.depth_m + 1e-9
    assert p["layers"] * (product.height_m + product.clearance_m) <= level.height_m + 1e-9
    assert p["capacity_units"] == facing * p["depth_units"] * p["layers"]


def test_t4_routes_reproducible_and_pass_no_solids(sample):
    from shapely.geometry import LineString, Polygon

    d = to_domain(sample)
    shelves = layout(d.floorplan, d.shelves, "optimizable").shelves
    assignment = allocate(d.floorplan, shelves, d.categories)["assignment"]
    a = simulate(d, shelves, assignment)
    b = simulate(d, shelves, assignment)
    assert a == b
    assert a.metrics["completed"] > 1
    assert a.metrics["mean_distance_m"] > 0
    graph, start, targets = navigation(d, shelves)
    assert start in graph and len(targets) == 2
    for left, right in graph.edges:
        segment = LineString([graph.nodes[left]["point"], graph.nodes[right]["point"]])
        assert all(not segment.intersects(footprint(s)) for s in shelves)
        assert all(not segment.intersects(Polygon(p)) for p in d.floorplan.obstacles)
