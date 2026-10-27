import json
from pathlib import Path

import pytest

from smart_retail.domain.models import EngineError, Product, Shelf, ShelfLevel
from smart_retail.engines.t3_slotting.engine import solve
from smart_retail.engines.t3_slotting.repair import repack
from smart_retail.engines.t3_slotting.validation import violations

CASES = json.loads((Path(__file__).resolve().parents[3] /
                    "datasets/samples/t3_first_fit_fragmentation.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_recorded_first_fit_fragmentation_recovers_without_changing_inputs(case):
    shelf = Shelf(**{**case["shelf"], "levels": tuple(
        ShelfLevel(**level) for level in case["shelf"]["levels"]
    )})
    products = tuple(Product(**{**p, "orientations": tuple(p["orientations"]),
                                "allowed_shelf_kinds": tuple(p["allowed_shelf_kinds"])})
                     for p in case["products"])
    plan = solve((shelf,), products, case["assignment"])
    assert not violations((shelf,), products, case["assignment"], plan.placements)
    assert {p["sku"] for p in plan.placements} == {p.sku for p in products}
    assert plan.status == "FEASIBLE_FIRST_FIT_REPAIRED"


def test_repair_is_bounded_and_honors_cancellation_and_deadline():
    import math

    shelf = Shelf("S", 1, 0.5, 1, (ShelfLevel("L", 1, 0.5, 0.5),))
    products = (Product("P", "P", "C", 0.2, 0.2, 0.2),)
    assert repack(shelf, products, deadline=math.inf, cancelled=lambda: False, max_nodes=1) is None
    with pytest.raises(EngineError) as cancelled:
        repack(shelf, products, deadline=math.inf, cancelled=lambda: True)
    assert cancelled.value.code == "CANCELLED"
    with pytest.raises(EngineError) as timeout:
        repack(shelf, products, deadline=0, cancelled=lambda: False)
    assert timeout.value.code == "TIMEOUT"


def test_successful_first_fit_is_unchanged_by_repair():
    shelf = Shelf("S", 1, 0.5, 1, (ShelfLevel("L", 1, 0.5, 0.5),))
    product = Product("P", "P", "C", 0.2, 0.2, 0.2)
    plan = solve((shelf,), (product,), {"C": "S"})
    assert plan.status == "FEASIBLE_FIRST_FIT"
    assert plan.placements[0]["x_m"] == 0


def test_shared_load_stays_enforced_across_faces_during_repair():
    shelf = Shelf("S", 1, 0.2, 1, (ShelfLevel("L", 1, 0.2, 0.2, 1),), faces=2)
    products = (Product("A", "A", "C", 0.6, 0.2, 0.2, weight_kg=1, clearance_m=0),
                Product("B", "B", "C", 0.6, 0.2, 0.2, weight_kg=1, clearance_m=0))
    with pytest.raises(EngineError) as failed:
        solve((shelf,), products, {"C": "S"})
    assert failed.value.code == "SLOTTING_FAILED"
    sufficient_load = Shelf("S", 1, 0.2, 1, (ShelfLevel("L", 1, 0.2, 0.2, 2),), faces=2)
    plan = solve((sufficient_load,), products, {"C": "S"})
    assert {p["face"] for p in plan.placements} == {0, 1}
    assert not violations((sufficient_load,), products, {"C": "S"}, plan.placements)
