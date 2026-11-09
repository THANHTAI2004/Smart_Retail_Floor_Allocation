"""Synthetic generator layout families: grid default, corner entrance, wide, columns."""

import pytest
from pydantic import ValidationError

from smart_retail.application.experiments.generators import generate
from smart_retail.contracts.experiments import DatasetSpec
from smart_retail.contracts.inputs import to_domain
from smart_retail.engines.navigation import validate_topology
from smart_retail.engines.t1_layout.geometry import violations

FACINGS = {"tiny": 6, "small": 4, "medium": 3}
FAMILIES = ["grid", "corner_entrance", "wide", "columns"]
DEFAULT_HASHES = {
    "tiny": "99882f1ef49cfef118b388141d195b5cdfc1d4aeb365a1e45023bdaf5ec316c2",
    "small": "309499d765d58db7793b7591840034b4b4790ed9d7b53952db7798ec26cf22c5",
    "medium": "9aa0b7cc0541fcd70a94b5cd15ff6618418522c1dd6e6aa97a91c8c9c7da1878",
}


def make(scale: str, family: str | None = None) -> tuple[dict, dict]:
    spec = DatasetSpec(id="x", scale=scale, seed=101, facings=FACINGS[scale], layout_family=family)
    return generate(spec)


def extent(domain) -> tuple[float, float]:
    xs, ys = zip(*domain.floorplan.boundary, strict=True)
    return max(xs), max(ys)


@pytest.mark.parametrize("scale", FACINGS)
def test_default_generator_hash_unchanged(scale):
    spec = DatasetSpec(id="x", scale=scale, seed=101, facings=FACINGS[scale])
    assert generate(spec)[1]["sha256"] == DEFAULT_HASHES[scale]
    assert make(scale, None)[1]["sha256"] == DEFAULT_HASHES[scale]
    assert "layout_family" not in DatasetSpec(id="x").model_dump()
    assert "layout_family" not in generate(spec)[1]["spec"]
    assert not any("Layout family" in line for line in generate(spec)[1]["limitations"])


@pytest.mark.parametrize("scale", FACINGS)
@pytest.mark.parametrize("family", FAMILIES)
def test_layout_families_are_valid(scale, family):
    data, manifest = make(scale, family)
    domain = to_domain(data)
    assert violations(domain.floorplan, domain.shelves) == []
    validate_topology(domain.floorplan, domain.shelves)
    assert manifest["spec"]["layout_family"] == family
    assert manifest["limitations"][-1] == f"Layout family: {family}"
    assert manifest["counts"]["shelves"] == len(domain.shelves)

    default_data, _ = make(scale, None)
    default = to_domain(default_data)
    width, height = extent(domain)
    default_width, default_height = extent(default)
    if family == "grid":
        assert data == default_data
        assert manifest["sha256"] == DEFAULT_HASHES[scale]
    if family == "corner_entrance":
        assert domain.floorplan.entrance == (0, 1.0)
        assert domain.floorplan.boundary == default.floorplan.boundary
        assert [(s.x, s.y) for s in domain.shelves] == [(s.x, s.y) for s in default.shelves]
    if family == "columns":
        assert {s.rotation for s in domain.shelves} == {90}
    else:
        assert {s.rotation for s in domain.shelves} == {0}
    if family == "wide":
        assert width > default_width
        assert width / height > default_width / default_height
    if family != "corner_entrance":
        assert domain.floorplan.entrance == (0, height / 2)


@pytest.mark.parametrize("family", FAMILIES)
def test_layout_family_changes_geometry_only(family):
    data, _ = make("small", family)
    default, _ = make("small", None)
    for section in ("categories", "products", "orders", "demand", "optimization"):
        assert data[section] == default[section]


def test_layout_family_geometry_matches_design_table():
    wide = to_domain(make("tiny", "wide")[0])
    assert extent(wide) == (13, 9)
    assert [(s.x, s.y) for s in wide.shelves] == [(2, 2), (5, 2), (8, 2), (2, 4.5)]
    columns = to_domain(make("tiny", "columns")[0])
    assert extent(columns) == (9, 10)
    assert [(s.x, s.y) for s in columns.shelves] == [(2, 2), (4.5, 2), (2, 5), (4.5, 5)]


def test_layout_family_contract():
    spec = DatasetSpec(id="x", layout_family="wide")
    assert spec.model_dump()["layout_family"] == "wide"
    assert DatasetSpec.model_validate(spec.model_dump()) == spec
    with pytest.raises(ValidationError):
        DatasetSpec(id="x", layout_family="diagonal")
