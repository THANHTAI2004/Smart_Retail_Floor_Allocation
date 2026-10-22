import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from smart_retail.contracts.inputs import SECTIONS, FloorplanInput, OrdersInput, to_domain


@pytest.mark.parametrize("section", list(SECTIONS))
def test_valid_fixture_and_schema(section, sample):
    model = SECTIONS[section].model_validate(sample[section])
    assert model.model_dump(mode="json")
    assert SECTIONS[section].model_json_schema()["type"] == "object"


@pytest.mark.parametrize(
    "section,path,value",
    [
        ("floorplan", "grid_m", -1),
        ("shelves", "layout_mode", "unknown"),
        ("demand", "customers", -1),
        ("optimization", "time_limit_s", 0),
        ("optimization", "capacity_weight", 1),
    ],
)
def test_invalid_groups(section, path, value, sample):
    sample[section][path] = value
    with pytest.raises(ValidationError):
        SECTIONS[section].model_validate(sample[section])


def test_bowtie_and_bad_obstacle(sample):
    floor = copy.deepcopy(sample["floorplan"])
    floor["boundary"] = [[0, 0], [4, 4], [0, 4], [4, 0]]
    with pytest.raises(ValidationError, match="simple polygon"):
        FloorplanInput.model_validate(floor)
    floor = copy.deepcopy(sample["floorplan"])
    floor["obstacles"] = [[[11, 8], [14, 8], [14, 10]]]
    with pytest.raises(ValidationError, match="inside"):
        FloorplanInput.model_validate(floor)


def test_duplicate_and_reference_integrity(sample):
    sample["orders"]["order_lines"].append(sample["orders"]["order_lines"][0])
    with pytest.raises(ValidationError, match="Duplicate"):
        OrdersInput.model_validate(sample["orders"])


def test_domain_conversion_does_not_mutate_input(sample):
    original = copy.deepcopy(sample)
    dataset = to_domain(sample)
    assert dataset.shelves[0].x is None
    assert dataset.products[0].sku == "WATER"
    assert sample == original


def test_wrong_foreign_key(sample):
    sample["products"]["items"][0]["category_id"] = "UNKNOWN"
    with pytest.raises(ValueError, match="unknown category"):
        to_domain(sample)


def test_all_groups_reject_unknown_fields(sample):
    for key, model in SECTIONS.items():
        with pytest.raises(ValidationError):
            model.model_validate({**sample[key], "unrecognized": True})


@pytest.mark.parametrize("section", list(SECTIONS))
def test_generated_schema_is_synchronized(section):
    root = Path(__file__).resolve().parents[3]
    saved = json.loads((root / f"datasets/schemas/{section}.schema.json").read_text(encoding="utf-8"))
    assert saved == SECTIONS[section].model_json_schema()


@pytest.mark.parametrize("section", list(SECTIONS))
def test_invalid_dataset_fixture_rejected(section):
    root = Path(__file__).resolve().parents[3]
    invalid = json.loads((root / "datasets/samples/invalid_inputs.json").read_text(encoding="utf-8"))
    with pytest.raises(ValidationError):
        SECTIONS[section].model_validate(invalid[section])


@pytest.mark.parametrize("patch", [
    {"candidate_count": 0}, {"candidate_count": 9}, {"slotting_algorithm": "unknown"},
    {"travel_weight": 0, "stock_weight": 0, "wait_weight": 0}, {"wait_weight": -1},
])
def test_research_configuration_rejects_invalid_budget_and_objectives(sample, patch):
    with pytest.raises(ValidationError):
        SECTIONS["optimization"].model_validate({**sample["optimization"], **patch})
