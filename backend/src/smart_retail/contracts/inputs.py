"""The seven versioned input groups, also used for files and JSON Schema."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from shapely.geometry import Point as ShapePoint
from shapely.geometry import Polygon

from smart_retail.domain import models as d

Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
NonNegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Identifier = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9_.-]+$")]
Coordinate = tuple[
    Annotated[float, Field(allow_inf_nan=False)], Annotated[float, Field(allow_inf_nan=False)]
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class FloorplanInput(Contract):
    units: Literal["m"] = "m"
    boundary: list[Coordinate] = Field(min_length=3, max_length=1000)
    entrance: Coordinate
    obstacles: list[list[Coordinate]] = Field(default_factory=list, max_length=100)
    min_aisle_m: Positive = 0.8
    grid_m: Annotated[float, Field(ge=0.1, le=2)] = 0.25

    @model_validator(mode="after")
    def geometry(self) -> Self:
        polygon = Polygon(self.boundary)
        if not polygon.is_valid or polygon.area <= 0:
            raise ValueError("Boundary must be a simple polygon with positive area")
        if polygon.area > 10000:
            raise ValueError("Baseline supports display areas up to 10,000 m²")
        if not polygon.covers(ShapePoint(self.entrance)):
            raise ValueError("Entrance must be on or inside the display area")
        for points in self.obstacles:
            obstacle = Polygon(points)
            if not obstacle.is_valid or obstacle.area <= 0 or not polygon.covers(obstacle):
                raise ValueError("Each obstacle must be a valid polygon inside the display area")
            if obstacle.covers(ShapePoint(self.entrance)):
                raise ValueError("Entrance cannot be inside an obstacle")
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


class ShelvesInput(Contract):
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


class CategoriesInput(Contract):
    items: list[CategoryInput] = Field(default_factory=list, max_length=200)

    @model_validator(mode="after")
    def unique(self) -> Self:
        unique_ids(self.items)
        ids = {c.id for c in self.items}
        for c in self.items:
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


class ProductsInput(Contract):
    items: list[ProductInput] = Field(default_factory=list, max_length=10000)

    @model_validator(mode="after")
    def unique(self) -> Self:
        unique_ids(self.items, "sku")
        return self


class BehaviorInput(Contract):
    model: Literal["synthetic_basket"] = "synthetic_basket"
    speed_m_s: Positive = 1.2
    dwell_s: NonNegative = 5


class DemandInput(Contract):
    arrivals_per_hour: Positive = 20
    horizon_s: Annotated[float, Field(gt=0, le=86400)] = 3600
    customers: Annotated[int, Field(ge=0, le=10000)] = 20
    baskets: list[list[Identifier]] = Field(default_factory=list)
    behavior: BehaviorInput = Field(default_factory=BehaviorInput)


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


class OrdersInput(Contract):
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
        if any(not any(x.order_id == o.id for x in self.order_lines) for o in self.orders):
            raise ValueError("Each order must have at least one order line")
        return self


class OptimizationInput(Contract):
    seed: Annotated[int, Field(ge=0, le=2147483647)] = 42
    time_limit_s: Annotated[float, Field(gt=0, le=300)] = 30
    max_iterations: Annotated[int, Field(ge=1, le=1000000)] = 10000
    algorithm: Literal["milp", "greedy"] = "milp"
    distance_weight: Positive = 1
    capacity_weight: Literal[0] = 0
    slotting_algorithm: Literal["first_fit", "milp"] = "first_fit"
    candidate_count: Annotated[int, Field(ge=1, le=8)] = 1
    travel_weight: NonNegative = 1
    wait_weight: NonNegative = 0
    stock_weight: NonNegative = 0

    @model_validator(mode="after")
    def objective_weights(self) -> Self:
        if self.travel_weight + self.wait_weight + self.stock_weight <= 0:
            raise ValueError("At least one integrated objective weight must be positive")
        return self


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
    floor = values["floorplan"]
    floor.pop("units")
    floor["boundary"] = tuple(map(tuple, floor["boundary"]))
    floor["entrance"] = tuple(floor["entrance"])
    floor["obstacles"] = tuple(tuple(map(tuple, p)) for p in floor["obstacles"])
    shelves = []
    for shelf in values["shelves"]["items"]:
        shelf["levels"] = tuple(d.ShelfLevel(**level) for level in shelf["levels"])
        shelves.append(d.Shelf(**shelf))
    categories = []
    for category in values["categories"]["items"]:
        category["near"] = tuple(category["near"])
        category["separate"] = tuple(category["separate"])
        categories.append(d.Category(**category))
    products = []
    for product in values["products"]["items"]:
        product["orientations"] = tuple(product["orientations"])
        products.append(d.Product(**product))
    demand = values["demand"]
    demand["behavior"] = d.CustomerBehavior(**demand["behavior"])
    demand["baskets"] = tuple(map(tuple, demand["baskets"]))
    if not shelves or not categories or not products:
        raise ValueError("A run requires at least one shelf, category and product")
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
