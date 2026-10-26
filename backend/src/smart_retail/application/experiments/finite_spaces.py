"""Declared finite decision spaces built from heuristic solutions, for exact reference runs (X1).

The union space bundles whole layers: every distinct layout (all shelf poses) found by
the sequential pipeline or a heuristic is one option, every distinct allocation
(category assignment plus all SKU rows) is one option, and so is every routing policy.
Exact search over layouts x allocations x policies therefore contains every supplied
solution, so heuristic minus exact is a non-negative gap, and a strictly better exact
state shows that recombining layers of different solutions pays off. Optimality is
claimed only inside this declared space, never globally.
"""

from smart_retail.contracts.optimality import Placement

ROW_KEYS = tuple(Placement.model_fields)


def union_space(decisions: list[dict]) -> tuple[dict, dict]:
    layouts: list[dict] = []
    allocations: list[dict] = []
    policies: list[str] = []
    for decision in decisions:
        layout = {k: list(v) for k, v in sorted(decision["poses"].items())}
        rows = sorted(
            ({k: row[k] for k in ROW_KEYS} for row in decision["placements"]),
            key=lambda row: row["sku"],
        )
        allocation = {"assignment": dict(sorted(decision["assignment"].items())), "placements": rows}
        if layout not in layouts:
            layouts.append(layout)
        if allocation not in allocations:
            allocations.append(allocation)
        if decision["routing_policy"] not in policies:
            policies.append(decision["routing_policy"])
    space = {
        "layouts": layouts,
        "allocations": allocations,
        "routing_policies": policies,
    }
    states = len(layouts) * len(allocations) * len(policies)
    return space, {
        "states": states,
        "layouts": len(layouts),
        "allocations": len(allocations),
        "routing_policies": policies,
        "source_decisions": len(decisions),
    }
