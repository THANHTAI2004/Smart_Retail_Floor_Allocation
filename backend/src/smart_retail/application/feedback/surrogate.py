"""Walking-distance surrogate that ranks candidate layouts before they are simulated."""

import math
from dataclasses import replace

import networkx as nx

from smart_retail.application.stage_workflow import canonical_hash
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError, RetailDataset
from smart_retail.engines.navigation import navigation


def heat(feedback: dict, sections: dict, weighted: bool) -> dict[str, float]:
    """Category heat: units picked in the latest simulation + 1; flat 1.0 when not weighted."""
    values = dict.fromkeys((c["id"] for c in sections["categories"]["items"]), 1.0)
    if weighted:
        category = {p["sku"]: p["category_id"] for p in sections["products"]["items"]}
        for sku, quantity in feedback["sku_pick_counts"].items():
            values[category[sku]] += quantity
    return values


def distances(
    sections: dict,
    poses: dict[str, list],
    deadline: float = math.inf,
    *,
    domain: RetailDataset | None = None,
) -> dict[str, float] | None:
    """Shortest walk (m) from the entrance to each shelf's nearest pickup point on any face.

    None when the layout has no valid topology. TIMEOUT and CANCELLED are re-raised.
    """
    domain = to_domain(sections) if domain is None else domain
    layout = tuple(
        replace(s, x=poses[s.id][0], y=poses[s.id][1], rotation=poses[s.id][2])
        for s in sorted(domain.shelves, key=lambda v: v.id)
    )
    try:
        graph, start, targets = navigation(
            domain.floorplan, layout, deadline, {s.id: set(range(s.faces)) for s in layout}
        )
    except EngineError as exc:
        if exc.code in ("TIMEOUT", "CANCELLED"):
            raise
        return None
    reach = nx.single_source_dijkstra_path_length(graph, start, weight="weight")
    return {s.id: min(reach[targets[f"{s.id}:{face}"]] for face in range(s.faces)) for s in layout}


def value(sections: dict, distance: dict[str, float], heat: dict[str, float]) -> float:
    """Sum of heat x distance with fixed categories on their shelf, the rest paired greedily.

    By the rearrangement inequality the hottest free category takes the nearest shelf;
    the shelf list (fixed shelves included) repeats when categories outnumber shelves.
    """
    shelves = sorted(distance, key=lambda s: (distance[s], s))
    free = []
    total = 0.0
    for c in sections["categories"]["items"]:
        if c.get("fixed_shelf_id"):
            total += heat[c["id"]] * distance[c["fixed_shelf_id"]]
        else:
            free.append(c["id"])
    free.sort(key=lambda cid: (-heat[cid], cid))
    for i, cid in enumerate(free):
        total += heat[cid] * distance[shelves[i % len(shelves)]]
    return total


def rank(
    candidates: list[dict], sections: dict, heat: dict[str, float], deadline: float = math.inf
) -> list[dict]:
    """Copies of the candidates with their surrogate, best first; invalid layouts are dropped."""
    domain = to_domain(sections)
    scored = []
    for action in candidates:
        d = distances(sections, action["decisions"]["poses"], deadline, domain=domain)
        if d is not None:
            scored.append({**action, "surrogate": value(sections, d, heat)})
    return sorted(scored, key=lambda a: (a["surrogate"], canonical_hash(a["decisions"])))
