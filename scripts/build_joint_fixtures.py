"""Author tiny declared-domain synthetic fixtures; never derive an oracle from a solver."""

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fixture(two=False):
    envelope = {"schema_version": "1.1", "data_origin": "SYNTHETIC"}
    sections = {
        name: dict(envelope)
        for name in (
            "floorplan",
            "shelves",
            "categories",
            "products",
            "demand",
            "orders",
            "optimization",
        )
    }
    sections["floorplan"].update(
        units="m",
        boundary=[[0, 0], [8, 0], [8, 8], [0, 8]],
        entrance=[0, 4] if two else [3, 8],
        grid_m=0.5,
        min_aisle_m=0.5,
    )
    shelf = {
        "id": "S1",
        "width_m": 2,
        "depth_m": 1,
        "height_m": 1,
        "x": 2,
        "y": 3,
        "rotation": 0,
        "faces": 2,
        "locked": not two,
        "levels": [
            {
                "id": "L1",
                "width_m": 2,
                "depth_m": 0.2,
                "height_m": 0.5,
                "max_load_kg": 10,
            }
        ],
    }
    sections["shelves"].update(layout_mode="fixed", items=[shelf])
    if two:
        other = copy.deepcopy(shelf)
        other.update(id="S2", x=5, y=3, locked=True)
        sections["shelves"]["items"].append(other)
    sections["categories"]["items"] = [
        {"id": c, "name": c, "required_width_m": 0.4}
        for c in (["A", "B"] if two else ["A"])
    ]
    sections["products"]["items"] = [
        {
            "sku": sku,
            "name": sku,
            "category_id": c,
            "width_m": 0.2,
            "depth_m": 0.2,
            "height_m": 0.2,
            "weight_kg": 1,
            "demand": 3,
            "facings": 1,
            "min_facings": 1,
            "max_facings": 1,
            "clearance_m": 0,
            "orientations": [0],
        }
        for sku, c in [("P1", "A"), ("P2", "B" if two else "A")]
    ]
    sections["demand"].update(
        customers=4,
        horizon_s=600,
        arrivals_per_hour=100,
        baskets=[["P1", "P2"]],
        behavior={"speed_m_s": 1, "dwell_s": 1},
        picker_count=1,
    )
    sections["orders"].update(
        orders=[{"id": "O1", "placed_at": "2026-10-22T00:00:00+00:00", "due_s": 100}],
        order_lines=[
            {"order_id": "O1", "sku": sku, "quantity": 1} for sku in ["P1", "P2"]
        ],
    )
    sections["optimization"].update(
        seed=11, time_limit_s=60, algorithm="greedy", candidate_count=1
    )
    placements = {}
    for i, sku in enumerate(["P1", "P2"]):
        placements[sku] = [
            {
                "sku": sku,
                "shelf_id": sid,
                "level_id": "L1",
                "face": face,
                "x_m": i * 0.2,
                "width_m": 0.2,
                "orientation": 0,
                "facings": 1,
                "layers": 1,
                "depth_units": 1,
                "capacity_units": 1,
                "load_kg": 1,
            }
            for sid in (["S1", "S2"] if two else ["S1"])
            for face in [0, 1]
        ]
    space = {
        "poses": {"S1": [[2, 3, 0], [2, 5, 0]] if two else [[2, 3, 0]]},
        "assignments": {
            c: ["S1", "S2"] if two else ["S1"] for c in (["A", "B"] if two else ["A"])
        },
        "placements": placements,
        "routing_policies": ["nearest"],
        "max_states": 256,
    }
    if two:
        space["poses"]["S2"] = [[5, 3, 0]]
    return sections, space


def main():
    out = ROOT / "datasets/joint"
    out.mkdir(exist_ok=False)
    hashes = {}
    for name, two in [("local-trap", False), ("two-shelves", True)]:
        sections, space = fixture(two)
        for suffix, value in [("", sections), ("-space", space)]:
            path = out / f"{name}{suffix}.json"
            path.write_text(json.dumps(value, indent=2), encoding="utf-8")
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (out / "manifest.json").write_text(
        json.dumps(
            {
                "version": "1",
                "data_origin": "SYNTHETIC",
                "description": "Manually declared finite domains, not solver-generated optima",
                "files": hashes,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
