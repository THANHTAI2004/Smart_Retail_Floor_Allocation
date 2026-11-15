# Vai trò: Mô hình domain cho mặt bằng và nghiệm bố trí.
# Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
"""Business models for floorplan. No HTTP or ORM dependencies."""

from dataclasses import dataclass

from smart_retail.domain.primitives import Point
from smart_retail.domain.shelves.models import Shelf


@dataclass(frozen=True)
class FunctionalZone:
    id: str
    kind: str
    boundary: tuple[Point, ...]


@dataclass(frozen=True)
class Floorplan:
    boundary: tuple[Point, ...]
    entrance: Point
    obstacles: tuple[tuple[Point, ...], ...] = ()
    min_aisle_m: float = 0.8
    grid_m: float = 0.25
    exits: tuple[Point, ...] = ()
    pickup_points: tuple[Point, ...] = ()
    zones: tuple[FunctionalZone, ...] = ()
    require_connected_aisles: bool = False


@dataclass(frozen=True)
class LayoutSolution:
    shelves: tuple[Shelf, ...]
    status: str
    algorithm: str = "grid"
    objective: float = 0
