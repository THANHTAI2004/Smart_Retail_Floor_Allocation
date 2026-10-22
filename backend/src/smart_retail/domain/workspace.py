from dataclasses import dataclass
from typing import Literal

from smart_retail.domain.categories.models import Category
from smart_retail.domain.demand.models import DemandProfile
from smart_retail.domain.floorplan.models import Floorplan
from smart_retail.domain.optimization.models import OptimizationConfig
from smart_retail.domain.orders.models import Order, OrderLine
from smart_retail.domain.products.models import Product
from smart_retail.domain.shelves.models import Shelf


@dataclass(frozen=True)
class RetailDataset:
    floorplan: Floorplan
    shelves: tuple[Shelf, ...]
    categories: tuple[Category, ...]
    products: tuple[Product, ...]
    demand: DemandProfile
    orders: tuple[Order, ...]
    order_lines: tuple[OrderLine, ...]
    config: OptimizationConfig
    layout_mode: Literal["fixed", "optimizable"] = "optimizable"
