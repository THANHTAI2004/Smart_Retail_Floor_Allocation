"""Deterministic synthetic instance generator with explicit provenance."""

import hashlib
import json
import math
import random
from pathlib import Path

from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.experiments import DatasetSpec
from smart_retail.contracts.inputs import SECTIONS, to_domain
from smart_retail.contracts.migration import normalize
from smart_retail.infrastructure.database import ROOT

DATASET_ROOT = ROOT / "datasets"

SIZES = {
    "tiny": (4, 3, 12, 20),
    "small": (12, 6, 48, 100),
    "medium": (36, 12, 180, 500),
    "large": (80, 25, 500, 2000),
}


def generate(spec: DatasetSpec) -> tuple[dict, dict]:
    if spec.input_path:
        supplied = Path(spec.input_path)
        path = (supplied if supplied.is_absolute() else ROOT / supplied).resolve()
        if not path.is_relative_to(DATASET_ROOT.resolve()):
            raise ValueError("Imported dataset must be inside the repository datasets directory")
        raw = path.read_bytes()
        if len(raw) > 20_000_000 or hashlib.sha256(raw).hexdigest() != spec.input_file_sha256:
            raise ValueError("Imported dataset size/checksum mismatch")
        original = json.loads(raw.decode("utf-8"))
        if set(original) != set(SECTIONS):
            raise ValueError("Imported dataset must contain exactly the seven input groups")
        imported, migrations = normalize(original)
        if any(section["data_origin"] != "SYNTHETIC" for section in imported.values()):
            raise ValueError("This campaign scope accepts explicitly SYNTHETIC input groups only")
        domain = to_domain(imported)
        return imported, {
            "dataset_id": spec.id,
            "version": "1.0",
            "data_origin": "SYNTHETIC",
            "source": str(path),
            "input_file_sha256": spec.input_file_sha256,
            "sha256": canonical_hash(imported),
            "migrations": migrations,
            "generator": "imported-seven-section-bundle",
            "counts": {
                "shelves": len(domain.shelves),
                "categories": len(domain.categories),
                "products": len(domain.products),
                "orders": len(domain.orders),
            },
            "units": {"length": "m", "mass": "kg", "time": "s"},
            "rights": "User-supplied synthetic bundle; no field validation or external licensing assertion",
        }
    rng = random.Random(spec.seed)
    shelf_count, category_count, sku_count, order_count = SIZES[spec.scale]
    cols = math.ceil(math.sqrt(shelf_count))
    rows = math.ceil(shelf_count / cols)
    width, height = cols * 3 + 4, rows * 2.5 + 4
    shelves = [
        {
            "id": f"S{i}",
            "width_m": 2,
            "depth_m": 0.6,
            "height_m": (0.5 * spec.levels + 0.2) * spec.height_scale,
            "levels": [
                {
                    "id": f"L{j}",
                    "width_m": 1.9,
                    "depth_m": 0.5,
                    "height_m": 0.5 * spec.height_scale,
                    "max_load_kg": 80,
                }
                for j in range(spec.levels)
            ],
            "x": 2 + (i % cols) * 3,
            "y": 2 + (i // cols) * 2.5,
            "locked": False,
        }
        for i in range(shelf_count)
    ]
    products: list[dict] = [
        {
            "sku": f"P{i}",
            "name": f"Synthetic product {i}",
            "category_id": f"C{i % category_count}",
            "width_m": round(rng.uniform(0.04, 0.08), 4),
            "depth_m": 0.12,
            "height_m": rng.choice([0.15, 0.2]),
            "weight_kg": 0.2,
            "demand": rng.randint(1, 30) * (5 if spec.scenario == "uneven" and i % 5 == 0 else 1),
            "facings": 1,
            "stack_layers": 1,
            "clearance_m": 0.005,
        }
        for i in range(sku_count)
    ]
    if spec.variable_facings:
        for product in products:
            product.update(min_facings=1, max_facings=3)
    categories: list[dict] = [
        {
            "id": f"C{i}",
            "name": f"Synthetic category {i}",
            "required_width_m": round(
                sum(
                    p["width_m"] + p["clearance_m"] for p in products if p["category_id"] == f"C{i}"
                ),
                5,
            ),
            "fixed_shelf_id": f"S{i}",
            "demand": sum(p["demand"] for p in products if p["category_id"] == f"C{i}"),
        }
        for i in range(category_count)
    ]
    if spec.category_assignment == "free":
        for category in categories:
            category.pop("fixed_shelf_id")
    orders = [
        {"id": f"O{i}", "placed_at": f"2026-10-22T00:{i % 60:02d}:00+00:00", "due_s": 600}
        for i in range(order_count)
    ]
    lines = [
        {"order_id": order["id"], "sku": sku, "quantity": rng.randint(1, 3)}
        for order in orders
        for sku in rng.sample([p["sku"] for p in products], min(3, sku_count))
    ]
    data: dict = {
        "floorplan": {
            "boundary": [[0, 0], [width, 0], [width, height], [0, height]],
            "entrance": [0, height / 2],
            "grid_m": 0.5,
            "min_aisle_m": 0.5,
            "require_connected_aisles": True,
        },
        "shelves": {"layout_mode": "fixed", "items": shelves},
        "categories": {"items": categories},
        "products": {"items": products},
        "demand": {
            "customers": 10 if spec.scale == "tiny" else 30,
            "horizon_s": 3600,
            "arrivals_per_hour": 30,
            "picker_count": 2,
            "behavior": {"speed_m_s": 1.2, "dwell_s": 2},
        },
        "orders": {"orders": orders, "order_lines": lines},
        "optimization": {"seed": spec.seed, "time_limit_s": 15, "max_iterations": 50000},
    }
    if spec.scenario == "infeasible":
        data["categories"]["items"][0]["required_width_m"] = 1_000_000
    if spec.scenario == "high_load":
        data["demand"].update(arrivals_per_hour=600, customers=100, picker_count=1)
    if spec.scenario == "volatile":
        data["demand"]["periods"] = [
            {"start_s": 0, "end_s": 1800, "arrivals_per_hour": 10},
            {"start_s": 1800, "end_s": 3600, "arrivals_per_hour": 120},
        ]
    for value in data.values():
        value["data_origin"] = "SYNTHETIC"
    data, _ = normalize(data)
    to_domain(data)
    manifest = {
        "dataset_id": spec.id,
        "version": "1.0",
        "data_origin": "SYNTHETIC",
        "generator": "structured_store_v1",
        "spec": spec.model_dump(),
        "sha256": canonical_hash(data),
        "counts": {
            "shelves": shelf_count,
            "categories": category_count,
            "products": sku_count,
            "orders": order_count,
        },
        "units": {"length": "m", "mass": "kg", "time": "s"},
        "rights": "Locally generated synthetic research data",
        "created_on": "2026-10-22",
        "source": "Deterministic Python random generator, no field observations",
        "limitations": [
            "Not representative of a real store",
            "Feasibility subject to solver model and budget",
            f"Category assignment mode: {spec.category_assignment}",
        ],
    }
    return data, manifest


def merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        result[key] = (
            merge(base.get(key, {}), value)
            if isinstance(value, dict) and isinstance(base.get(key, {}), dict)
            else value
        )
    return result
