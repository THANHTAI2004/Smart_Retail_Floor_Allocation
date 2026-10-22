"""Business models for floorplan. No HTTP or ORM dependencies."""

from dataclasses import dataclass

from smart_retail.domain.primitives import Point
from smart_retail.domain.shelves.models import Shelf


@dataclass(frozen=True)
class Floorplan:
    boundary: tuple[Point, ...]
    entrance: Point
    obstacles: tuple[tuple[Point, ...], ...] = ()
    min_aisle_m: float = 0.8
    grid_m: float = 0.25


@dataclass(frozen=True)
class LayoutSolution:
    shelves: tuple[Shelf, ...]
    status: str
