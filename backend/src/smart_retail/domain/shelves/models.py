"""Business models for shelves. No HTTP or ORM dependencies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ShelfLevel:
    id: str
    width_m: float
    depth_m: float
    height_m: float
    max_load_kg: float | None = None


@dataclass(frozen=True)
class Shelf:
    id: str
    width_m: float
    depth_m: float
    height_m: float
    levels: tuple[ShelfLevel, ...]
    x: float | None = None
    y: float | None = None
    rotation: int = 0
    faces: int = 1
    kind: str = "gondola"
    locked: bool = False
