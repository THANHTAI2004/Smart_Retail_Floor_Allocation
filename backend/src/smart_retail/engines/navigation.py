"""Shared walkability graph and independent service/topology validation."""

import math
import time

import networkx as nx
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from smart_retail.domain.models import EngineError, Floorplan, Shelf
from smart_retail.engines.t1_layout.geometry import footprint


def navigation(
    floor: Floorplan,
    shelves: tuple[Shelf, ...],
    deadline: float = math.inf,
    required_faces: dict[str, set[int]] | None = None,
) -> tuple[nx.Graph, tuple[int, int], dict[str, tuple[int, int]]]:
    boundary = Polygon(floor.boundary)
    solids = unary_union([*(footprint(s) for s in shelves), *(Polygon(o) for o in floor.obstacles)])
    minx, miny, maxx, maxy = boundary.bounds
    step = floor.grid_m
    nx_cells, ny_cells = math.ceil((maxx - minx) / step), math.ceil((maxy - miny) / step)
    if nx_cells * ny_cells > 40000:
        raise EngineError("PROBLEM_LIMIT", "T4 grid exceeds 40,000 cells; increase grid_m")
    graph: nx.Graph = nx.Graph()
    for i in range(nx_cells):
        if time.monotonic() >= deadline:
            raise EngineError("TIMEOUT", "T4 navigation time limit")
        for j in range(ny_cells):
            point = Point(minx + (i + 0.5) * step, miny + (j + 0.5) * step)
            if boundary.covers(point) and not solids.intersects(point):
                graph.add_node((i, j), point=(point.x, point.y))
                for other in ((i - 1, j), (i, j - 1)):
                    if other in graph:
                        segment = LineString([graph.nodes[other]["point"], (point.x, point.y)])
                        if boundary.covers(segment) and not solids.intersects(segment):
                            graph.add_edge((i, j), other, weight=step)
    if not graph:
        raise EngineError("UNREACHABLE", "No walkable cells")
    entrance = Point(floor.entrance)
    candidates = [
        node
        for node in graph
        if boundary.covers(LineString([floor.entrance, graph.nodes[node]["point"]]))
        and not solids.intersects(LineString([floor.entrance, graph.nodes[node]["point"]]))
    ]
    if not candidates:
        raise EngineError("UNREACHABLE", "Entrance has no walkable connection")
    start = min(candidates, key=lambda node: entrance.distance(Point(graph.nodes[node]["point"])))
    connected = nx.node_connected_component(graph, start)
    for zone in floor.zones:
        if zone.kind == "required_aisle":
            shape = Polygon(zone.boundary)
            required = [n for n in graph if shape.covers(Point(graph.nodes[n]["point"]))]
            if not required or any(n not in connected for n in required):
                raise EngineError(
                    "UNREACHABLE", f"Required aisle {zone.id} has no complete grid connection"
                )
    if floor.require_connected_aisles and len(connected) != len(graph):
        raise EngineError(
            "DISCONNECTED_AISLES", "Walkable grid is not connected at the declared resolution"
        )
    for point in floor.exits + floor.pickup_points:
        nodes = [
            node
            for node in connected
            if boundary.covers(LineString([point, graph.nodes[node]["point"]]))
            and not solids.intersects(LineString([point, graph.nodes[node]["point"]]))
        ]
        if not nodes:
            raise EngineError("UNREACHABLE", "Exit/pickup has no connection to entrance component")
    targets = {}
    for shelf in shelves:
        shape = footprint(shelf)
        # Service on a long face, never from the end of a gondola.
        x, y, xx, yy = shape.bounds
        if shelf.rotation == 0:
            faces = [LineString([(x, y), (xx, y)])]
            if shelf.faces == 2:
                faces.append(LineString([(x, yy), (xx, yy)]))
        else:
            faces = [LineString([(x, y), (x, yy)])]
            if shelf.faces == 2:
                faces.append(LineString([(xx, y), (xx, yy)]))
        requested = required_faces.get(shelf.id, set()) if required_faces is not None else {0}
        for index in sorted(requested):
            face = faces[index]
            nodes = []
            for node in connected:
                px, py = graph.nodes[node]["point"]
                on_service_side = (
                    x <= px <= xx and (py <= y if index == 0 else py >= yy)
                    if shelf.rotation == 0
                    else y <= py <= yy and (px <= x if index == 0 else px >= xx)
                )
                if on_service_side and face.distance(Point(px, py)) <= step * 1.5:
                    nodes.append(node)
            if not nodes:
                raise EngineError(
                    "UNREACHABLE", f"Shelf {shelf.id} face {index} has no reachable pickup"
                )
            key = f"{shelf.id}:{index}" if required_faces is not None else shelf.id
            targets[key] = min(
                nodes,
                key=lambda node: (shape.centroid.distance(Point(graph.nodes[node]["point"])), node),
            )
    return graph, start, targets


def validate_topology(
    floor: Floorplan, shelves: tuple[Shelf, ...], deadline: float = math.inf
) -> None:
    navigation(floor, shelves, deadline, {s.id: set(range(s.faces)) for s in shelves})
