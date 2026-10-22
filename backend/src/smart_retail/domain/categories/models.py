"""Business models for categories. No HTTP or ORM dependencies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    id: str
    name: str
    demand: float
    required_width_m: float
    priority: float = 1
    fixed_shelf_id: str | None = None
    near: tuple[str, ...] = ()
    separate: tuple[str, ...] = ()
    distance_m: float = 3
    affinity: tuple[tuple[str, float], ...] = ()
