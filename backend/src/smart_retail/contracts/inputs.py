"""The seven versioned input groups, also used for files and JSON Schema."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator
from shapely.geometry import Point as ShapePoint
from shapely.geometry import Polygon

from smart_retail.contracts.feedback import JointConfig
from smart_retail.domain import models as d

Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
NonNegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Identifier = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9_.-]+$")]
Coordinate = tuple[
    Annotated[float, Field(allow_inf_nan=False)], Annotated[float, Field(allow_inf_nan=False)]
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class SectionContract(Contract):
    schema_version: Literal["1.1"] = "1.1"
    data_origin: Literal[
        "SYNTHETIC", "REAL_VERIFIED", "REAL_UNVERIFIED", "ASSUMED", "DERIVED", "UNSPECIFIED"
    ] = "UNSPECIFIED"


class ZoneInput(Contract):
    id: Identifier
    kind: Literal["no_shelf", "required_aisle"]
    boundary: list[Coordinate] = Field(min_length=3, max_length=1000)


class FloorplanInput(SectionContract):
    units: Literal["m"] = "m"
    boundary: list[Coordinate] = Field(min_length=3, max_length=1000)
    entrance: Coordinate
    obstacles: list[list[Coordinate]] = Field(default_factory=list, max_length=100)
    min_aisle_m: Positive = 0.8
    grid_m: Annotated[float, Field(ge=0.1, le=2)] = 0.25
    exits: list[Coordinate] = Field(default_factory=list, max_length=20)
    pickup_points: list[Coordinate] = Field(default_factory=list, max_length=500)
    zones: list[ZoneInput] = Field(default_factory=list, max_length=100)
    require_connected_aisles: bool = False

    @model_validator(mode="after")
    def geometry(self) -> Self:
        polygon = Polygon(self.boundary)
        if not polygon.is_valid or polygon.area <= 0:
            raise ValueError("Boundary must be a simple polygon with positive area")
        if polygon.area > 10000:
            raise ValueError("Baseline supports display areas up to 10,000 m²")
        if not polygon.covers(ShapePoint(self.entrance)):
            raise ValueError("Entrance must be on or inside the display area")
        unique_ids(self.zones)
        for point in self.exits + self.pickup_points:
            if not polygon.covers(ShapePoint(point)):
                raise ValueError("Exit/pickup point must be inside boundary")
        for zone in self.zones:
            shape = Polygon(zone.boundary)
            if not shape.is_valid or shape.area <= 0 or not polygon.covers(shape):
                raise ValueError("Functional zone must be a valid polygon inside boundary")
        for points in self.obstacles:
            obstacle = Polygon(points)
            if not obstacle.is_valid or obstacle.area <= 0 or not polygon.covers(obstacle):
                raise ValueError("Each obstacle must be a valid polygon inside the display area")
            if obstacle.covers(ShapePoint(self.entrance)):
                raise ValueError("Entrance cannot be inside an obstacle")
            if any(obstacle.covers(ShapePoint(p)) for p in self.exits + self.pickup_points):
                raise ValueError("Exit/pickup cannot be inside an obstacle")
            if any(
                z.kind == "required_aisle" and obstacle.intersects(Polygon(z.boundary))
                for z in self.zones
            ):
                raise ValueError("Required aisle cannot intersect an obstacle")
        return self


class LevelInput(Contract):
    id: Identifier
    width_m: Positive
    depth_m: Positive
    height_m: Positive
    max_load_kg: Positive | None = None


class ShelfInput(Contract):
    id: Identifier
    kind: str = Field(default="gondola", min_length=1, max_length=120)
    width_m: Positive
    depth_m: Positive
    height_m: Positive
    levels: list[LevelInput] = Field(min_length=1, max_length=50)
    x: Annotated[float, Field(allow_inf_nan=False)] | None = None
    y: Annotated[float, Field(allow_inf_nan=False)] | None = None
    rotation: Literal[0, 90] = 0
    faces: Literal[1, 2] = 1
    locked: bool = False

    @model_validator(mode="after")
    def physical(self) -> Self:
        if (self.x is None) != (self.y is None):
            raise ValueError("Supply both x and y, or leave both empty")
        if self.locked and self.x is None:
            raise ValueError("A locked shelf requires coordinates")
        if len({x.id for x in self.levels}) != len(self.levels):
            raise ValueError("Level IDs must be unique within a shelf")
        for level in self.levels:
            if level.width_m > self.width_m or level.depth_m > self.depth_m:
                raise ValueError("Usable level dimensions exceed physical shelf dimensions")
        if sum(x.height_m for x in self.levels) > self.height_m + 1e-9:
            raise ValueError("Sum of usable level heights exceeds shelf height")
        return self


class ShelvesInput(SectionContract):
    layout_mode: Literal["fixed", "optimizable"] = "optimizable"
    items: list[ShelfInput] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def unique(self) -> Self:
        unique_ids(self.items)
        if self.layout_mode == "fixed" and any(s.x is None for s in self.items):
            raise ValueError("Fixed layout requires coordinates for every shelf")
        return self


class CategoryInput(Contract):
    id: Identifier
    name: str = Field(min_length=1, max_length=200)
    priority: Positive = 1
    demand: NonNegative = 1
    required_width_m: Positive
    fixed_shelf_id: Identifier | None = None
    near: list[Identifier] = Field(default_factory=list)
    separate: list[Identifier] = Field(default_factory=list)
    distance_m: Positive = 3
    affinity: dict[Identifier, Positive] = Field(default_factory=dict, max_length=200)


class CategoriesInput(SectionContract):
    items: list[CategoryInput] = Field(default_factory=list, max_length=200)

    @model_validator(mode="after")
    def unique(self) -> Self:
        unique_ids(self.items)
        ids = {c.id for c in self.items}
        for c in self.items:
            if c.id in c.affinity or not c.affinity.keys() <= ids:
                raise ValueError("Affinity references unknown category or itself")
            if set(c.near) & set(c.separate) or c.id in c.near + c.separate:
                raise ValueError("Category proximity constraints contradict each other")
            if not set(c.near + c.separate) <= ids:
                raise ValueError("Proximity constraint references an unknown category")
        return self


class ProductInput(Contract):
    sku: Identifier
    name: str = Field(min_length=1, max_length=200)
    category_id: Identifier
    width_m: Positive
    depth_m: Positive
    height_m: Positive
    weight_kg: NonNegative = 0
    demand: NonNegative = 1
    facings: Annotated[int, Field(ge=1, le=1000)] = 1
    orientations: list[Literal[0, 90]] = Field(default=[0], min_length=1)
    stack_layers: Annotated[int, Field(ge=1, le=100)] = 1
    clearance_m: NonNegative = 0.01
    min_facings: Annotated[int, Field(ge=1, le=1000)] | None = None
    max_facings: Annotated[int, Field(ge=1, le=1000)] | None = None
    allowed_shelf_kinds: list[str] = Field(default_factory=list, max_length=50)

    @model_validator(mode="after")
    def facing_bounds(self) -> Self:
        lo = self.min_facings if self.min_facings is not None else self.facings
        hi = self.max_facings if self.max_facings is not None else self.facings
        if not lo <= self.facings <= hi:
            raise ValueError("Require min_facings <= facings <= max_facings")
        return self


class ProductsInput(SectionContract):
    items: list[ProductInput] = Field(default_factory=list, max_length=10000)

    @model_validator(mode="after")
    def unique(self) -> Self:
        unique_ids(self.items, "sku")
        return self


class BehaviorInput(Contract):
    model: Literal["synthetic_basket"] = "synthetic_basket"
    speed_m_s: Positive = 1.2
    dwell_s: NonNegative = 5


class ArrivalPeriodInput(Contract):
    start_s: NonNegative
    end_s: Positive
    arrivals_per_hour: NonNegative


class DemandInput(SectionContract):
    arrivals_per_hour: Positive = 20
    horizon_s: Annotated[float, Field(gt=0, le=86400)] = 3600
    customers: Annotated[int, Field(ge=0, le=10000)] = 20
    baskets: list[list[Identifier]] = Field(default_factory=list)
    behavior: BehaviorInput = Field(default_factory=BehaviorInput)
    periods: list[ArrivalPeriodInput] = Field(default_factory=list, max_length=168)
    picker_count: Annotated[int, Field(ge=1, le=100)] = 1
    routing_policy: Literal["nearest", "return", "exact"] = "nearest"

    @model_validator(mode="after")
    def intervals(self) -> Self:
        previous = 0.0
        for p in self.periods:
            if p.start_s < previous or not p.start_s < p.end_s <= self.horizon_s:
                raise ValueError(
                    "Demand periods must be ordered, non-overlapping and within horizon"
                )
            previous = p.end_s
        return self


class OrderInput(Contract):
    id: Identifier
    placed_at: datetime
    kind: Literal["online", "in_store"] = "online"
    due_s: Positive = 3600

    @model_validator(mode="after")
    def timezone_required(self) -> Self:
        if self.placed_at.tzinfo is None:
            raise ValueError("Order timestamp must include a timezone")
        return self


class OrderLineInput(Contract):
    order_id: Identifier
    sku: Identifier
    quantity: Annotated[int, Field(gt=0, le=100000)]


class OrdersInput(SectionContract):
    orders: list[OrderInput] = Field(default_factory=list, max_length=10000)
    order_lines: list[OrderLineInput] = Field(default_factory=list, max_length=100000)

    @model_validator(mode="after")
    def integrity(self) -> Self:
        unique_ids(self.orders)
        ids = {o.id for o in self.orders}
        keys = {(x.order_id, x.sku) for x in self.order_lines}
        if len(keys) != len(self.order_lines):
            raise ValueError("Duplicate (order_id, sku) order line")
        if any(x.order_id not in ids for x in self.order_lines):
            raise ValueError("Order line references an unknown order")
        covered_orders = {line.order_id for line in self.order_lines}
        if ids - covered_orders:
            raise ValueError("Each order must have at least one order line")
        return self


class HeldOutEvaluationInput(Contract):
    """Held-out orders scored after optimization; engines never receive them."""

    split: Literal["kfold", "temporal_holdout"]
    fold: Annotated[int, Field(ge=0, le=99)]
    budget_fraction: Annotated[float, Field(ge=0.05, le=0.5)] = 0.25
    population_orders: Annotated[int, Field(ge=2, le=20000)]
    orders: OrdersInput

    @model_validator(mode="after")
    def nonempty(self) -> Self:
        if not self.orders.orders:
            raise ValueError("Held-out evaluation requires at least one order")
        return self


class OptimizationInput(SectionContract):
    joint: JointConfig | None = None
    evaluation: HeldOutEvaluationInput | None = None
    seed: Annotated[int, Field(ge=0, le=2147483647)] = 42
    time_limit_s: Annotated[float, Field(gt=0, le=3600)] = 30
    max_iterations: Annotated[int, Field(ge=1, le=1000000)] = 10000
    algorithm: Literal["milp", "greedy"] = "milp"
    distance_weight: Positive = 1
    affinity_weight: NonNegative = 1
    capacity_weight: Literal[0] = 0
    slotting_algorithm: Literal["first_fit", "milp"] = "first_fit"
    candidate_count: Annotated[int, Field(ge=1, le=8)] = 1
    travel_weight: NonNegative = 1
    wait_weight: NonNegative = 0
    stock_weight: NonNegative = 0
    layout_algorithm: Literal["grid", "local_search"] = "grid"
    stop_after_stage: Literal["T1", "T2", "T3", "T4"] = "T4"
    memory_limit_mb: Annotated[int, Field(ge=128, le=8192)] | None = 2048

    @model_validator(mode="after")
    def objective_weights(self) -> Self:
        if self.travel_weight + self.wait_weight + self.stock_weight <= 0:
            raise ValueError("At least one integrated objective weight must be positive")
        return self

    @model_serializer(mode="wrap")
    def omit_absent_evaluation(self, handler):
        # Inputs without held-out orders keep their pre-existing canonical form.
        data = handler(self)
        if data.get("evaluation") is None:
            data.pop("evaluation", None)
        return data


def unique_ids(items: list, key: str = "id") -> None:
    if len({getattr(x, key) for x in items}) != len(items):
        raise ValueError(f"Duplicate {key}")


SECTIONS: dict[str, type[Contract]] = {
    "floorplan": FloorplanInput,
    "shelves": ShelvesInput,
    "categories": CategoriesInput,
    "products": ProductsInput,
    "demand": DemandInput,
    "orders": OrdersInput,
    "optimization": OptimizationInput,
}


def validate_references(sections: dict) -> list[str]:
    errors = []
    shelves = {x["id"] for x in sections.get("shelves", {}).get("items", [])}
    cats = {x["id"] for x in sections.get("categories", {}).get("items", [])}
    skus = {x["sku"] for x in sections.get("products", {}).get("items", [])}
    for c in sections.get("categories", {}).get("items", []):
        if c.get("fixed_shelf_id") and c["fixed_shelf_id"] not in shelves:
            errors.append(f"Category {c['id']}: unknown fixed shelf {c['fixed_shelf_id']}")
    for p in sections.get("products", {}).get("items", []):
        if p["category_id"] not in cats:
            errors.append(f"Product {p['sku']}: unknown category {p['category_id']}")
    for basket in sections.get("demand", {}).get("baskets", []):
        if not set(basket) <= skus:
            errors.append("Demand basket references unknown SKU")
    for line in sections.get("orders", {}).get("order_lines", []):
        if line["sku"] not in skus:
            errors.append(f"Order {line['order_id']}: unknown SKU {line['sku']}")
    held_out = (sections.get("optimization", {}).get("evaluation") or {}).get("orders")
    if held_out:
        training = {o["id"] for o in sections.get("orders", {}).get("orders", [])}
        if training & {o["id"] for o in held_out["orders"]}:
            errors.append("Held-out orders overlap training orders")
        if any(line["sku"] not in skus for line in held_out["order_lines"]):
            errors.append("Held-out order references an unknown SKU")
    return errors


def to_domain(sections: dict) -> d.RetailDataset:
    missing = set(SECTIONS) - sections.keys()
    if missing:
        raise ValueError("Missing input groups: " + ", ".join(sorted(missing)))
    parsed = {key: cls.model_validate(sections[key]) for key, cls in SECTIONS.items()}
    values = {key: value.model_dump(mode="json") for key, value in parsed.items()}
    errors = validate_references(values)
    if errors:
        raise ValueError("; ".join(errors))
    for value in values.values():
        value.pop("schema_version")
        value.pop("data_origin")
    floor = values["floorplan"]
    floor.pop("units")
    floor["boundary"] = tuple(map(tuple, floor["boundary"]))
    floor["entrance"] = tuple(floor["entrance"])
    floor["obstacles"] = tuple(tuple(map(tuple, p)) for p in floor["obstacles"])
    floor["exits"] = tuple(map(tuple, floor["exits"]))
    floor["pickup_points"] = tuple(map(tuple, floor["pickup_points"]))
    from smart_retail.domain.floorplan.models import FunctionalZone

    floor["zones"] = tuple(
        FunctionalZone(z["id"], z["kind"], tuple(map(tuple, z["boundary"]))) for z in floor["zones"]
    )
    shelves = []
    for shelf in values["shelves"]["items"]:
        shelf["levels"] = tuple(d.ShelfLevel(**level) for level in shelf["levels"])
        shelves.append(d.Shelf(**shelf))
    categories = []
    for category in values["categories"]["items"]:
        category["near"] = tuple(category["near"])
        category["separate"] = tuple(category["separate"])
        category["affinity"] = tuple(sorted(category["affinity"].items()))
        categories.append(d.Category(**category))
    products = []
    for product in values["products"]["items"]:
        product["orientations"] = tuple(product["orientations"])
        product["allowed_shelf_kinds"] = tuple(product["allowed_shelf_kinds"])
        products.append(d.Product(**product))
    demand = values["demand"]
    demand["behavior"] = d.CustomerBehavior(**demand["behavior"])
    demand["baskets"] = tuple(map(tuple, demand["baskets"]))
    from smart_retail.domain.demand.models import ArrivalPeriod

    demand["periods"] = tuple(ArrivalPeriod(**p) for p in demand["periods"])
    if not shelves or not categories or not products:
        raise ValueError("A run requires at least one shelf, category and product")
    # Held-out orders are application evaluation data, never an engine input.
    values["optimization"].pop("evaluation", None)
    if values["optimization"]["joint"] is not None:
        import json

        values["optimization"]["joint"] = json.dumps(values["optimization"]["joint"], sort_keys=True)
    return d.RetailDataset(
        floorplan=d.Floorplan(**floor),
        shelves=tuple(shelves),
        categories=tuple(categories),
        products=tuple(products),
        demand=d.DemandProfile(**demand),
        orders=tuple(d.Order(**o) for o in values["orders"]["orders"]),
        order_lines=tuple(d.OrderLine(**o) for o in values["orders"]["order_lines"]),
        config=d.OptimizationConfig(**values["optimization"]),
        layout_mode=values["shelves"]["layout_mode"],
    )
