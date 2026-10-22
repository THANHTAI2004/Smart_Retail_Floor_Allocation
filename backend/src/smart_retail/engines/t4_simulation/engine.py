"""T4 grid routes + SimPy shelf-service contention. All customer behavior is synthetic."""

import math
import random
import time
from datetime import datetime
from typing import Any

import networkx as nx
import simpy
from shapely.geometry import LineString, Polygon

from smart_retail.domain.models import (
    EngineError,
    Planogram,
    RetailDataset,
    Shelf,
    SimulationResult,
)
from smart_retail.engines.navigation import navigation as walkability
from smart_retail.engines.t1_layout.geometry import footprint
from smart_retail.engines.t4_simulation.routing import order as route_order


def navigation(
    dataset: RetailDataset,
    shelves: tuple[Shelf, ...],
    deadline: float = math.inf,
    required_faces: dict[str, set[int]] | None = None,
):
    return walkability(dataset.floorplan, shelves, deadline, required_faces)


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
    pickers = simpy.Resource(env, capacity=dataset.demand.picker_count)
    picker_busy = [0.0]
    max_queue = {s.id: 0 for s in shelves}
    distances: dict[tuple, float] = {}

    def distance(a: tuple, b: tuple) -> float:
        if (a, b) not in distances:
            distances[(a, b)] = nx.shortest_path_length(graph, a, b, weight="weight")
        return distances[(a, b)]

    journeys: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    connector = math.dist(dataset.floorplan.entrance, graph.nodes[start]["point"])
    exits = []
    if dataset.floorplan.exits:
        boundary = Polygon(dataset.floorplan.boundary)
        solids = [footprint(s) for s in shelves] + [Polygon(o) for o in dataset.floorplan.obstacles]
        connected = nx.node_connected_component(graph, start)
        for point in dataset.floorplan.exits:
            eligible = [
                n
                for n in connected
                if boundary.covers(LineString([point, graph.nodes[n]["point"]]))
                and not any(
                    s.intersects(LineString([point, graph.nodes[n]["point"]])) for s in solids
                )
            ]
            node = min(eligible, key=lambda n: (math.dist(point, graph.nodes[n]["point"]), n))
            exits.append((node, point, math.dist(point, graph.nodes[node]["point"])))

    def travel_journey(
        kind: str, identifier: str, arrival: float, items: list[tuple[str, int]], due_s: float
    ):
        begin = arrival
        picker_wait = env.now - arrival
        service_start = env.now
        node = start
        route_distance, wait = connector, picker_wait
        points = [dataset.floorplan.entrance, graph.nodes[start]["point"]]
        yield env.timeout(connector / dataset.demand.behavior.speed_m_s)
        remaining: dict[str, int] = {}
        for sku, qty in items:
            sid = sku_shelf[sku]
            remaining[sid] = remaining.get(sid, 0) + qty
        visited = []
        sequence = route_order(
            dataset.demand.routing_policy, {sid: targets[sid] for sid in remaining}, start, distance
        )
        while remaining:
            if time.monotonic() >= deadline:
                raise EngineError("TIMEOUT", "T4 simulation time limit")
            sid = sequence.pop(0)
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
                max_queue[resource_id] = max(
                    max_queue[resource_id], len(resources[resource_id].queue)
                )
                yield request
                wait += env.now - queued_at
                yield env.timeout(dataset.demand.behavior.dwell_s * qty)
            visited.append(sid)
            node = target
            if dataset.demand.routing_policy == "return":
                back_step = distance(node, start)
                points.extend(
                    graph.nodes[n]["point"]
                    for n in nx.shortest_path(graph, node, start, weight="weight")[1:]
                )
                route_distance += back_step
                yield env.timeout(back_step / dataset.demand.behavior.speed_m_s)
                node = start
        end_node, end_point, end_connector = start, dataset.floorplan.entrance, connector
        if kind == "customer" and exits:
            end_node, end_point, end_connector = min(
                exits, key=lambda item: (distance(node, item[0]) + item[2], item[1])
            )
        back = distance(node, end_node)
        points.extend(
            graph.nodes[n]["point"]
            for n in nx.shortest_path(graph, node, end_node, weight="weight")[1:]
        )
        points.append(end_point)
        route_distance += back + end_connector
        yield env.timeout((back + end_connector) / dataset.demand.behavior.speed_m_s)
        journeys.append(
            {
                "kind": kind,
                "id": identifier,
                "arrival_s": arrival,
                "completion_s": env.now,
                "elapsed_s": env.now - begin,
                "distance_m": route_distance,
                "wait_s": wait,
                "picker_wait_s": picker_wait,
                "shelf_wait_s": wait - picker_wait,
                "travel_s": route_distance / dataset.demand.behavior.speed_m_s,
                "picking_s": sum(qty for _, qty in items) * dataset.demand.behavior.dwell_s,
                "late": env.now - begin > due_s,
                "picks": [{"sku": sku, "quantity": qty} for sku, qty in items],
            }
        )
        routes.append({"id": identifier, "kind": kind, "shelves": visited, "points_m": points})
        if kind == "picker":
            picker_busy[0] += env.now - service_start

    def journey(kind, identifier, arrival, items, due_s):
        yield env.timeout(arrival)
        if kind == "picker":
            with pickers.request() as request:
                yield request
                yield from travel_journey(kind, identifier, arrival, items, due_s)
        else:
            yield from travel_journey(kind, identifier, arrival, items, due_s)

    arrival = 0.0
    skus = [p.sku for p in dataset.products]
    weights = [p.demand for p in dataset.products]
    arrivals: list[float] = []
    if dataset.demand.periods:
        for period in dataset.demand.periods:
            arrival = period.start_s
            if period.arrivals_per_hour == 0:
                continue
            while len(arrivals) < dataset.demand.customers:
                arrival += rng.expovariate(period.arrivals_per_hour / 3600)
                if arrival >= period.end_s:
                    break
                arrivals.append(arrival)
    else:
        for _ in range(dataset.demand.customers):
            arrival += rng.expovariate(dataset.demand.arrivals_per_hour / 3600)
            if arrival > dataset.demand.horizon_s:
                break
            arrivals.append(arrival)
    for i, arrival in enumerate(arrivals):
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
            "total_distance_m": sum(float(x["distance_m"]) for x in journeys),
            "total_travel_s": sum(float(x["travel_s"]) for x in journeys),
            "total_picking_s": sum(float(x["picking_s"]) for x in journeys),
            "mean_completion_s": sum(float(x["elapsed_s"]) for x in journeys) / max(1, count),
            "max_shelf_queue": max(max_queue.values(), default=0),
            "picker_utilization": picker_busy[0] / max(1e-9, env.now * dataset.demand.picker_count),
            "throughput_per_hour": count * 3600 / max(1e-9, env.now),
            "routing_policy": dataset.demand.routing_policy,
        },
        assumptions=(
            "Synthetic baskets and Poisson customer arrivals; no observed trajectories",
            f"Routing policy {dataset.demand.routing_policy} uses four-neighbor shortest paths; exact policy proves only a closed tour over <=10 service locations",
            f"Finite picker pool: {dataset.demand.picker_count}; order elapsed includes pool wait",
            "Piecewise demand periods override the global customer arrival rate; gaps have zero arrivals",
            "Customers finish at the least-cost declared exit connector; pickers return to entrance. Exact tour policy optimizes a closed start tour before exit evaluation, not a multi-exit open TSP",
            "Congestion is a one-server shelf service queue, not corridor pedestrian dynamics",
            "Arrivals are truncated at horizon_s; admitted journeys drain to completion",
            "Order arrivals use seconds since earliest supplied order timestamp",
        ),
    )
