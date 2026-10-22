"""Business models for products. No HTTP or ORM dependencies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    category_id: str
    width_m: float
    depth_m: float
    height_m: float
    weight_kg: float = 0
    demand: float = 1
    facings: int = 1
    orientations: tuple[int, ...] = (0,)
    stack_layers: int = 1
    clearance_m: float = 0.01
    min_facings: int | None = None
    max_facings: int | None = None
    allowed_shelf_kinds: tuple[str, ...] = ()


@dataclass(frozen=True)
class Planogram:
    placements: tuple[dict, ...]
    status: str
    algorithm: str = "first_fit"
    objective: float = 0
    objective_units: str = "demand-weighted capacity units"
    mip_gap: float | None = None
