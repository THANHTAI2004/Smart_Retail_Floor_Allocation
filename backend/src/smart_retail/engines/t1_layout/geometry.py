"""Independent physical geometry replay for rectangular shelf footprints."""

from shapely.geometry import Point, Polygon, box

from smart_retail.domain.models import EngineError, Floorplan, Shelf


def footprint(shelf: Shelf) -> Polygon:
    if shelf.x is None or shelf.y is None:
        raise EngineError("MISSING_POSITION", f"Shelf {shelf.id} has no coordinates")
    width, depth = shelf.width_m, shelf.depth_m
    if shelf.rotation == 90:
        width, depth = depth, width
    return box(shelf.x, shelf.y, shelf.x + width, shelf.y + depth)


def violations(floor: Floorplan, shelves: tuple[Shelf, ...]) -> list[str]:
    boundary = Polygon(floor.boundary)
    obstacles = [Polygon(p) for p in floor.obstacles] + [Polygon(z.boundary) for z in floor.zones]
    errors = []
    shapes: list[tuple[str, Polygon]] = []
    for shelf in shelves:
        shape = footprint(shelf)
        if not boundary.covers(shape):
            errors.append(f"Shelf {shelf.id} is outside boundary")
        if shape.distance(boundary.boundary) < floor.min_aisle_m - 1e-8:
            errors.append(f"Shelf {shelf.id}: perimeter aisle is too narrow")
        if shape.distance(Point(floor.entrance)) < floor.min_aisle_m - 1e-8:
            errors.append(f"Shelf {shelf.id} obstructs entrance")
        if any(
            shape.distance(Point(p)) < floor.min_aisle_m - 1e-8
            for p in floor.exits + floor.pickup_points
        ):
            errors.append(f"Shelf {shelf.id} obstructs exit/pickup")
        if any(
            shape.intersects(o) or shape.distance(o) < floor.min_aisle_m - 1e-8 for o in obstacles
        ):
            errors.append(f"Shelf {shelf.id}: obstacle clearance is too narrow")
        for previous, other in shapes:
            if shape.intersects(other) or shape.distance(other) < floor.min_aisle_m - 1e-8:
                errors.append(f"Shelves {previous} and {shelf.id}: overlap or aisle violation")
        shapes.append((shelf.id, shape))
    return errors
