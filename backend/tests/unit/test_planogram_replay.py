import itertools
import time
from dataclasses import replace

import pytest
from smart_retail.domain.models import EngineError, Product, Shelf, ShelfLevel
from smart_retail.engines.t3_slotting.engine import solve
from smart_retail.engines.t3_slotting.validation import violations


def fixture():
    shelf = Shelf("S", 1, 0.6, 1, (ShelfLevel("L", 1, 0.6, 0.5, 6),))
    products = (
        Product("A", "A", "C", 0.3, 0.2, 0.2, weight_kg=1, demand=3, stack_layers=2, clearance_m=0),
        Product("B", "B", "C", 0.3, 0.2, 0.2, weight_kg=1, demand=1, stack_layers=2, clearance_m=0),
    )
    return (shelf,), products, {"C": "S"}


def test_mip_matches_independent_exhaustive_stock_enumeration():
    shelves, products, assignment = fixture()
    plan = solve(shelves, products, assignment, algorithm="milp")
    # Each SKU fits 1..2 layers and 1..3 units deep; at least one unit per SKU.
    stocks = [layers * deep for layers, deep in itertools.product(range(1, 3), range(1, 4))]
    exact = max(3 * a + b for a, b in itertools.product(stocks, repeat=2) if a + b <= 6)
    assert plan.status == "OPTIMAL"
    assert plan.objective == exact == 14
    assert plan.mip_gap == 0
    assert not violations(shelves, products, assignment, plan.placements)
    with pytest.raises(EngineError) as error:
        solve(shelves, products, assignment)
    assert error.value.code == "SLOTTING_FAILED"


def test_mip_recovers_from_first_fit_level_choice():
    shelf = Shelf(
        "S", 1, 0.5, 1, (ShelfLevel("tall", 1, 0.5, 0.7), ShelfLevel("short", 1, 0.5, 0.3))
    )
    products = (
        Product("A", "A", "C", 0.6, 0.2, 0.2, demand=2, clearance_m=0),
        Product("B", "B", "C", 0.6, 0.2, 0.6, clearance_m=0),
    )
    with pytest.raises(EngineError):
        solve((shelf,), products, {"C": "S"})
    plan = solve((shelf,), products, {"C": "S"}, algorithm="milp")
    assert {p["sku"]: p["level_id"] for p in plan.placements} == {"A": "short", "B": "tall"}


@pytest.mark.parametrize(
    "patch",
    [
        {"capacity_units": 999},
        {"load_kg": 0},
        {"width_m": 0},
        {"x_m": -1},
        {"orientation": 45},
        {"face": 2},
        {"layers": 99},
        {"facings": 99},
        {"depth_units": 99},
        {"x_m": float("nan")},
        {"layers": 1.5},
        {"shelf_id": "missing"},
    ],
)
def test_independent_replay_rejects_tampering(patch):
    shelves, products, assignment = fixture()
    plan = solve(shelves, products, assignment, algorithm="milp")
    rows = ({**plan.placements[0], **patch}, *plan.placements[1:])
    assert violations(shelves, products, assignment, rows)


def test_replay_detects_overlap_missing_duplicate_and_shared_load():
    shelves, products, assignment = fixture()
    plan = solve(shelves, products, assignment, algorithm="milp")
    assert violations(shelves, products, assignment, plan.placements[:1])
    assert violations(shelves, products, assignment, plan.placements + plan.placements[:1])
    overlap = (plan.placements[0], {**plan.placements[1], "x_m": 0})
    assert any("overlapping" in e for e in violations(shelves, products, assignment, overlap))
    light_shelves = (replace(shelves[0], levels=(replace(shelves[0].levels[0], max_load_kg=1),)),)
    assert any(
        "shared load" in e for e in violations(light_shelves, products, assignment, plan.placements)
    )


def test_infeasible_timeout_cancel_and_limit_are_distinct():
    shelves, products, assignment = fixture()
    for kwargs, code in [
        ({"deadline": time.monotonic() - 1}, "TIMEOUT"),
        ({"cancelled": lambda: True}, "CANCELLED"),
    ]:
        with pytest.raises(EngineError) as error:
            solve(shelves, products, assignment, algorithm="milp", **kwargs)
        assert error.value.code == code
    with pytest.raises(EngineError) as error:
        solve(shelves, (replace(products[0], height_m=10),), assignment, algorithm="milp")
    assert error.value.code == "INFEASIBLE"
    from smart_retail.engines.t3_slotting.mip import solve as mip

    with pytest.raises(EngineError) as error:
        mip(shelves, products, assignment, max_options=1)
    assert error.value.code == "PROBLEM_LIMIT"
