# Vai trò: Phát lại các quyết định bố trí, phân bổ và xếp hàng đã chọn qua bộ kiểm tra chính thức trước khi dùng trong pipeline.
"""Replay explicit upstream decisions through the official engine validators."""

from dataclasses import replace

from smart_retail.domain.models import EngineError, Planogram
from smart_retail.engines.t1_layout.engine import solve as layout
from smart_retail.engines.t2_allocation.validation import replay
from smart_retail.engines.t3_slotting.validation import violations
from smart_retail.engines.t4_simulation.engine import solve as simulate


# Hàm decided_layout: xử lý bước decided layout trong phạm vi module hiện tại.
def decided_layout(dataset, decisions, deadline):
    poses = decisions["poses"]
    if set(poses) != {s.id for s in dataset.shelves}:
        raise EngineError("INVALID_DECISION", "Pose keys differ from shelf identities")
    shelves = []
    for s in dataset.shelves:
        x, y, angle = poses[s.id]
        if angle not in (0, 90) or (s.locked and (x, y, angle) != (s.x, s.y, s.rotation)):
            raise EngineError("INVALID_DECISION", "Locked pose or orientation violation")
        shelves.append(replace(s, x=x, y=y, rotation=angle))
    return layout(dataset.floorplan, tuple(shelves), "fixed", deadline=deadline)


# Hàm decided_assignment: xử lý bước decided assignment trong phạm vi module hiện tại.
def decided_assignment(dataset, t1, decisions):
    assignment = dict(decisions["assignment"])
    errors, objective = replay(
        dataset.floorplan,
        t1.shelves,
        dataset.categories,
        assignment,
        dataset.config.distance_weight,
        dataset.config.affinity_weight,
    )
    if errors:
        raise EngineError("INVALID_DECISION", "; ".join(errors))
    return {
        "assignment": assignment,
        "objective": objective,
        "status": "FEASIBLE_DECISION",
        "algorithm": "explicit_decision",
        "mip_gap": None,
    }


# Hàm decided_planogram: xử lý bước decided planogram trong phạm vi module hiện tại.
def decided_planogram(dataset, t1, t2, decisions):
    rows = tuple(dict(p) for p in decisions["placements"])
    errors = violations(t1.shelves, dataset.products, t2["assignment"], rows)
    if errors:
        raise EngineError("INVALID_DECISION", "; ".join(errors))
    demand = {p.sku: p.demand for p in dataset.products}
    return Planogram(
        rows,
        "FEASIBLE_DECISION",
        "explicit_decision",
        sum(demand[p["sku"]] * p["capacity_units"] for p in rows),
    )


# Hàm decided_simulation: xử lý bước decided simulation trong phạm vi module hiện tại.
def decided_simulation(dataset, t1, t2, t3, decisions, deadline):
    policy = decisions.get("routing_policy", dataset.demand.routing_policy)
    if policy not in ("nearest", "return", "exact"):
        raise EngineError("INVALID_DECISION", "Unsupported route policy")
    data = replace(dataset, demand=replace(dataset.demand, routing_policy=policy))
    return simulate(data, t1.shelves, t2["assignment"], deadline, t3)
