"""Business models for orders. No HTTP or ORM dependencies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: str
    placed_at: str
    kind: str = "online"
    due_s: float = 3600


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int
