import copy
import itertools
import math
from dataclasses import replace

import pytest
from pydantic import ValidationError

from smart_retail.application.workflow import execute
from smart_retail.contracts.inputs import SECTIONS, to_domain
from smart_retail.contracts.migration import normalize
from smart_retail.contracts.tabular import export_csv, import_csv
from smart_retail.domain.models import EngineError, Product, Shelf, ShelfLevel
from smart_retail.engines.t1_layout.engine import solve as layout
from smart_retail.engines.t1_layout.search import objective
from smart_retail.engines.t3_slotting.engine import solve as slot
from smart_retail.engines.t3_slotting.validation import violations
from smart_retail.engines.t4_simulation.routing import order


def test_version_migration_is_non_destructive_and_explicit(sample):
    old = copy.deepcopy(sample)
    for section in old.values():
        section.pop("schema_version")
    before = copy.deepcopy(old)
    migrated, trace = normalize(old)
    assert old == before and len(trace) == 7
    assert all(section["schema_version"] == "1.1" for section in migrated.values())
    assert normalize(migrated)[1] == []
    old["floorplan"]["schema_version"] = "99"
    with pytest.raises(ValueError, match="Unsupported"):
        normalize(old)


@pytest.mark.parametrize("section", ["shelves", "categories", "products", "orders"])
def test_lossless_csv_including_nested_values(section, sample):
    encoded = export_csv(section, sample[section])
    assert import_csv(section, encoded) == SECTIONS[section].model_validate(
        sample[section]
    ).model_dump(mode="json")
    with pytest.raises(ValueError):
        import_csv(section, "width_m\n1\n")


def test_csv_api_transaction_and_reference_validation(client, saved_project):
    pid = saved_project["id"]
    exported = client.get(f"/api/projects/{pid}/inputs/products/export?format=csv")
    assert exported.status_code == 200
    imported = client.post(
        f"/api/projects/{pid}/inputs/products/import-csv",
        json={"text": exported.text, "expected_revision": 7},
    )
    assert imported.status_code == 200
    assert imported.json()["revision"] == 8
    assert (
        client.post(
            f"/api/projects/{pid}/inputs/products/import-csv",
            json={"text": exported.text, "expected_revision": 7},
        ).status_code
        == 409
    )


def test_local_search_improves_feasible_layout(sample):
    d = to_domain(sample)
    baseline = layout(d.floorplan, d.shelves, d.layout_mode)
    improved = layout(
        d.floorplan, d.shelves, d.layout_mode, algorithm="local_search", max_iterations=2000
    )
    assert improved.status == "FEASIBLE_LOCAL_SEARCH"
    assert improved.objective == pytest.approx(objective(d.floorplan, improved.shelves))
    assert improved.objective < objective(d.floorplan, baseline.shelves)


def test_full_walkable_topology_rejects_disconnected_components(sample):
    d = to_domain(sample)
    floor = replace(
        d.floorplan,
        obstacles=(((5, 0), (5.5, 0), (5.5, 9), (5, 9)),),
        require_connected_aisles=True,
    )
    with pytest.raises(EngineError) as error:
        layout(floor, (), "fixed")
    assert error.value.code == "DISCONNECTED_AISLES"


def test_mip_facing_range_and_shelf_compatibility():
    shelves = (Shelf("S", 1, 0.5, 1, (ShelfLevel("L", 1, 0.5, 0.4),)),)
    product = Product("P", "P", "C", 0.2, 0.2, 0.2, clearance_m=0, min_facings=1, max_facings=3)
    plan = slot(shelves, (product,), {"C": "S"}, algorithm="milp")
    assert plan.placements[0]["facings"] == 3
    assert not violations(shelves, (product,), {"C": "S"}, plan.placements)
    with pytest.raises(EngineError) as error:
        slot(
            shelves,
            (replace(product, allowed_shelf_kinds=("chilled",)),),
            {"C": "S"},
            algorithm="milp",
        )
    assert error.value.code == "INFEASIBLE"


def test_exact_routing_matches_permutation_oracle():
    start = (0, 0)
    points = {"A": (2, 1), "B": (1, 4), "C": (5, 2), "D": (4, 5)}
    distance = math.dist

    def cost(keys):
        route = [start, *(points[k] for k in keys), start]
        return sum(distance(a, b) for a, b in itertools.pairwise(route))

    chosen = order("exact", points, start, distance)
    assert cost(chosen) == pytest.approx(min(cost(keys) for keys in itertools.permutations(points)))
    assert cost(chosen) <= cost(order("nearest", points, start, distance)) + 1e-9


def test_soft_affinity_milp_matches_independent_enumeration(sample):
    from smart_retail.engines.t2_allocation.engine import solve as allocate
    from smart_retail.engines.t2_allocation.validation import replay

    d = to_domain(sample)
    shelves = layout(d.floorplan, d.shelves, d.layout_mode).shelves
    categories = (
        replace(d.categories[0], required_width_m=2, affinity=((d.categories[1].id, 1.0),)),
        replace(d.categories[1], required_width_m=2),
    )
    result = allocate(d.floorplan, shelves, categories, affinity_weight=2)
    references = []
    for chosen in itertools.product([s.id for s in shelves], repeat=2):
        assignment = {c.id: sid for c, sid in zip(categories, chosen)}
        errors, value = replay(d.floorplan, shelves, categories, assignment, 1, 2)
        if not errors:
            references.append(value)
    assert result["objective"] == pytest.approx(min(references))
    assert result["mip_gap"] == 0


def test_piecewise_arrivals_and_finite_picker_metrics(sample):
    sample["demand"].update(
        customers=4,
        horizon_s=100,
        periods=[{"start_s": 10, "end_s": 20, "arrivals_per_hour": 100000}],
        picker_count=1,
    )
    original = sample["orders"]["orders"][0]
    sample["orders"]["orders"] = [{**original, "id": f"O{i}"} for i in range(3)]
    sample["orders"]["order_lines"] = [
        {"order_id": f"O{i}", "sku": "WATER", "quantity": 2} for i in range(3)
    ]
    metrics = execute(sample)["stages"]["T4"]["metrics"]
    assert all(10 <= j["arrival_s"] < 20 for j in metrics["journeys"] if j["kind"] == "customer")
    pickers = [j for j in metrics["journeys"] if j["kind"] == "picker"]
    assert len(pickers) == 3 and max(j["picker_wait_s"] for j in pickers) > 0
    assert 0 < metrics["picker_utilization"] <= 1 + 1e-9
    for journey in metrics["journeys"]:
        assert journey["elapsed_s"] == pytest.approx(
            journey["travel_s"] + journey["picking_s"] + journey["wait_s"]
        )


def test_reject_invalid_periods_facings_and_origin(sample):
    for section, patch in (
        ("demand", {"periods": [{"start_s": 20, "end_s": 10, "arrivals_per_hour": 10}]}),
        ("floorplan", {"schema_version": "2.0"}),
        ("floorplan", {"data_origin": "real"}),
    ):
        with pytest.raises(ValidationError):
            SECTIONS[section].model_validate({**sample[section], **patch})


def test_customer_exit_and_required_aisle_replay(sample):
    from smart_retail.application.experiments.validation import verify

    sample["floorplan"]["exits"] = [[12, 4.5]]
    sample["floorplan"]["zones"] = [
        {"id": "WALK", "kind": "required_aisle", "boundary": [[0, 3], [12, 3], [12, 3.5], [0, 3.5]]}
    ]
    sample["demand"].update(customers=2, arrivals_per_hour=100000, horizon_s=100)
    sample["orders"] = {"orders": [], "order_lines": []}
    result = execute(sample)
    assert all(
        tuple(r["points_m"][-1]) == (12, 4.5) for r in result["stages"]["T4"]["metrics"]["routes"]
    )
    assert verify(sample, result)["status"] == "PASS"


def test_invalid_exit_obstacle_and_required_zone_are_rejected(sample):
    floor = sample["floorplan"]
    with pytest.raises(ValidationError):
        SECTIONS["floorplan"].model_validate({**floor, "exits": [[9.5, 6.5]]})
    with pytest.raises(ValidationError):
        SECTIONS["floorplan"].model_validate(
            {
                **floor,
                "zones": [
                    {
                        "id": "blocked",
                        "kind": "required_aisle",
                        "boundary": [[9, 6], [10, 6], [10, 7], [9, 7]],
                    }
                ],
            }
        )
