"""T4 grid routes + SimPy shelf-service contention. All customer behavior is synthetic."""

import math
import random
import time
from datetime import datetime
from typing import Any

import networkx as nx
import simpy
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from smart_retail.domain.models import (
    EngineError,
    Planogram,
    RetailDataset,
    Shelf,
    SimulationResult,
)
from smart_retail.engines.t1_layout.engine import footprint


def navigation(
    dataset: RetailDataset,
    shelves: tuple[Shelf, ...],
    deadline: float = math.inf,
    required_faces: dict[str, set[int]] | None = None,
) -> tuple[nx.Graph, tuple[int, int], dict[str, tuple[int, int]]]:
    floor = dataset.floorplan
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


def solve(
    dataset: RetailDataset,
    shelves: tuple[Shelf, ...],
    assignment: dict[str, str],
    deadline: float = math.inf,
    planogram: Planogram | None = None,
) -> SimulationResult:
    faces: dict[str, set[int]] | None = None
    if planogram is not None:
        faces = {s.id: set() for s in shelves}
        for p in planogram.placements:
            faces[p["shelf_id"]].add(p["face"])
    graph, start, targets = navigation(dataset, shelves, deadline, faces)
    rng = random.Random(dataset.config.seed)
    sku_shelf = {p.sku: assignment[p.category_id] for p in dataset.products}
    if planogram is not None:
        sku_shelf = {p["sku"]: f"{p['shelf_id']}:{p['face']}" for p in planogram.placements}
    env = simpy.Environment()
    resources = {s.id: simpy.Resource(env, capacity=1) for s in shelves}
    distances: dict[tuple, float] = {}

    def distance(a: tuple, b: tuple) -> float:
        if (a, b) not in distances:
            distances[(a, b)] = nx.shortest_path_length(graph, a, b, weight="weight")
        return distances[(a, b)]

    journeys: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    connector = math.dist(dataset.floorplan.entrance, graph.nodes[start]["point"])

    def journey(
        kind: str, identifier: str, arrival: float, items: list[tuple[str, int]], due_s: float
    ):
        yield env.timeout(arrival)
        begin = env.now
        node = start
        route_distance, wait = connector, 0.0
        points = [dataset.floorplan.entrance, graph.nodes[start]["point"]]
        yield env.timeout(connector / dataset.demand.behavior.speed_m_s)
        remaining: dict[str, int] = {}
        for sku, qty in items:
            sid = sku_shelf[sku]
            remaining[sid] = remaining.get(sid, 0) + qty
        visited = []
        while remaining:
            if time.monotonic() >= deadline:
                raise EngineError("TIMEOUT", "T4 simulation time limit")
            sid = min(remaining, key=lambda sid: (distance(node, targets[sid]), sid))
            qty = remaining.pop(sid)
            target = targets[sid]
            walk = distance(node, target)
            points.extend(
                graph.nodes[n]["point"]
                for n in nx.shortest_path(graph, node, target, weight="weight")[1:]
            )
            route_distance += walk
            yield env.timeout(walk / dataset.demand.behavior.speed_m_s)
            queued_at = env.now
            resource_id = sid.rsplit(":", 1)[0] if planogram is not None else sid
            with resources[resource_id].request() as request:
                yield request
                wait += env.now - queued_at
                yield env.timeout(dataset.demand.behavior.dwell_s * qty)
            visited.append(sid)
            node = target
        back = distance(node, start)
        points.extend(
            graph.nodes[n]["point"]
            for n in nx.shortest_path(graph, node, start, weight="weight")[1:]
        )
        points.append(dataset.floorplan.entrance)
        route_distance += back + connector
        yield env.timeout((back + connector) / dataset.demand.behavior.speed_m_s)
        journeys.append(
            {
                "kind": kind,
                "id": identifier,
                "arrival_s": arrival,
                "completion_s": env.now,
                "elapsed_s": env.now - begin,
                "distance_m": route_distance,
                "wait_s": wait,
                "late": env.now - begin > due_s,
                "picks": [{"sku": sku, "quantity": qty} for sku, qty in items],
            }
        )
        routes.append({"id": identifier, "kind": kind, "shelves": visited, "points_m": points})

    arrival = 0.0
    skus = [p.sku for p in dataset.products]
    weights = [p.demand for p in dataset.products]
    for i in range(dataset.demand.customers):
        arrival += rng.expovariate(dataset.demand.arrivals_per_hour / 3600)
        if arrival > dataset.demand.horizon_s:
            break
        basket = (
            list(rng.choice(dataset.demand.baskets))
            if dataset.demand.baskets
            else [rng.choices(skus, weights=weights if sum(weights) else None)[0]]
        )
        env.process(
            journey("customer", f"C{i + 1}", arrival, [(sku, 1) for sku in basket], math.inf)
        )
    epoch = min(
        (datetime.fromisoformat(o.placed_at).timestamp() for o in dataset.orders), default=0
    )
    for order in dataset.orders:
        arrival = datetime.fromisoformat(order.placed_at).timestamp() - epoch
        if arrival <= dataset.demand.horizon_s:
            env.process(
                journey(
                    "picker",
                    order.id,
                    arrival,
                    [
                        (line.sku, line.quantity)
                        for line in dataset.order_lines
                        if line.order_id == order.id
                    ],
                    order.due_s,
                )
            )
    env.run()
    count = len(journeys)
    return SimulationResult(
        metrics={
            "journeys": journeys,
            "routes": routes,
            "completed": count,
            "mean_distance_m": sum(float(x["distance_m"]) for x in journeys) / max(1, count),
            "mean_wait_s": sum(float(x["wait_s"]) for x in journeys) / max(1, count),
            "late_orders": sum(bool(x["late"]) for x in journeys if x["kind"] == "picker"),
            "walkable_cells": len(graph),
            "simulation_end_s": env.now,
        },
        assumptions=(
            "Synthetic baskets and Poisson customer arrivals; no observed trajectories",
            "Customers and pickers use nearest-next-shelf routes on a four-neighbor grid",
            "Congestion is a one-server shelf service queue, not corridor pedestrian dynamics",
            "Arrivals are truncated at horizon_s; admitted journeys drain to completion",
            "Order arrivals use seconds since earliest supplied order timestamp",
        ),
    )
