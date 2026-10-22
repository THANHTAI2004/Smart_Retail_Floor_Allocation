"""Independent replay of persisted candidate witnesses without solver matrices."""

import math

from shapely.geometry import LineString, Polygon

from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import Shelf, ShelfLevel
from smart_retail.engines.navigation import validate_topology
from smart_retail.engines.t1_layout.geometry import footprint, violations
from smart_retail.engines.t2_allocation.validation import replay
from smart_retail.engines.t3_slotting.validation import violations as packing


def verify(sections: dict, result: dict) -> dict:
    data = to_domain(sections)
    checked = routes_checked = 0
    for candidate in result["integrated"]["candidates"]:
        if candidate["status"] != "FEASIBLE":
            continue
        stages = candidate["stages"]
        shelves = tuple(
            Shelf(**{**s, "levels": tuple(ShelfLevel(**level) for level in s["levels"])})
            for s in stages["T1"]["shelves"]
        )
        errors = violations(data.floorplan, shelves)
        if errors:
            raise ValueError("Independent geometry replay: " + "; ".join(errors))
        validate_topology(data.floorplan, shelves)
        if "T2" in stages:
            errors, objective = replay(
                data.floorplan,
                shelves,
                data.categories,
                stages["T2"]["assignment"],
                data.config.distance_weight,
                data.config.affinity_weight,
            )
            if errors or not math.isclose(objective, stages["T2"]["objective"], abs_tol=1e-7):
                raise ValueError("Independent allocation replay failed")
        if "T3" in stages:
            errors = packing(
                shelves,
                data.products,
                stages["T2"]["assignment"],
                tuple(stages["T3"]["placements"]),
            )
            if errors:
                raise ValueError("Independent packing replay: " + "; ".join(errors))
        if "T4" in stages:
            metrics = stages["T4"]["metrics"]
            route_map = {(r["kind"], r["id"]): r for r in metrics["routes"]}
            for journey in metrics["journeys"]:
                points = route_map[journey["kind"], journey["id"]]["points_m"]
                allowed = (
                    data.floorplan.exits
                    if journey["kind"] == "customer" and data.floorplan.exits
                    else (data.floorplan.entrance,)
                )
                if tuple(points[0]) != data.floorplan.entrance or tuple(points[-1]) not in allowed:
                    raise ValueError("Route entrance/exit replay mismatch")
                length = 0.0
                for a, b in zip(points, points[1:]):
                    length += math.dist(a, b)
                    if a == b:
                        continue
                    segment = LineString([a, b])
                    if (
                        not Polygon(data.floorplan.boundary).covers(segment)
                        or any(segment.intersects(footprint(s)) for s in shelves)
                        or any(segment.intersects(Polygon(o)) for o in data.floorplan.obstacles)
                    ):
                        raise ValueError("Route crosses a solid or boundary")
                if not math.isclose(length, journey["distance_m"], abs_tol=1e-7):
                    raise ValueError("Route distance replay mismatch")
                quantities = sum(p["quantity"] for p in journey["picks"])
                elapsed = (
                    length / data.demand.behavior.speed_m_s
                    + quantities * data.demand.behavior.dwell_s
                    + journey["wait_s"]
                )
                if not math.isclose(elapsed, journey["elapsed_s"], abs_tol=1e-7):
                    raise ValueError("Journey time replay mismatch")
                if journey["kind"] == "picker":
                    expected = {
                        line.sku: line.quantity
                        for line in data.order_lines
                        if line.order_id == journey["id"]
                    }
                    if expected != {p["sku"]: p["quantity"] for p in journey["picks"]}:
                        raise ValueError("Order quantity replay mismatch")
                routes_checked += 1
        checked += 1
    if checked == 0:
        joint = result.get("joint", {})
        certificate = joint.get("certificate") or {}
        if joint.get("proof_status") == "INFEASIBLE_PROVEN":
            from smart_retail.application.stage_workflow import canonical_hash

            payload = {k: v for k, v in certificate.items() if k != "artifact_sha256"}
            if (
                canonical_hash(payload) == certificate.get("artifact_sha256")
                and certificate.get("complete")
                and joint.get("verification", {}).get("status") == "PASS"
                and joint["verification"].get("checked") == certificate.get("total_states")
            ):
                return {
                    "status": "PASS",
                    "candidates": 0,
                    "routes": 0,
                    "scope": "Child independently verified exhaustive infeasibility of the declared finite model",
                }
        if joint and joint.get("best") is None and joint.get("proof_status") != "INFEASIBLE_PROVEN":
            return {
                "status": "NO_SOLUTION",
                "candidates": 0,
                "routes": 0,
                "reason": joint.get("status"),
                "scope": "No incumbent; no infeasibility proof inferred",
            }
        raise ValueError("No complete candidate witness")
    return {
        "status": "PASS",
        "candidates": checked,
        "routes": routes_checked,
        "scope": "Independent geometry/topology, assignment/objective, physical packing, route/time/order replay",
    }
