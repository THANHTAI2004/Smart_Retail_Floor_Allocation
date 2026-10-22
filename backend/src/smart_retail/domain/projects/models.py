"""Business models for projects. No HTTP or ORM dependencies."""

from dataclasses import dataclass

from smart_retail.domain.floorplan.models import Floorplan


@dataclass(frozen=True)
class Project:
    id: str
    name: str


@dataclass(frozen=True)
class Store:
    id: str
    project_id: str
    name: str


@dataclass(frozen=True)
class DisplayArea:
    id: str
    store_id: str
    floorplan: Floorplan
