"""Deterministic feasible-or-rejected decision edits, ranked by observed T4 evidence."""

import copy
import math
from dataclasses import replace
from itertools import zip_longest

from smart_retail.contracts.inputs import to_domain
from smart_retail.engines.t1_layout.geometry import violations


def resize(row, product, shelf, *, face=None, level=None, orientation=None, facings=None, x=None):
    row = dict(row)
    row.update(
        face=row["face"] if face is None else face,
        level_id=row["level_id"] if level is None else level["id"],
        orientation=row["orientation"] if orientation is None else orientation,
        facings=row["facings"] if facings is None else facings,
        x_m=row["x_m"] if x is None else x,
    )
    level = next(v for v in shelf["levels"] if v["id"] == row["level_id"])
    width, depth = (product["width_m"], product["depth_m"])
    if row["orientation"] == 90:
        width, depth = depth, width
    clearance = product.get("clearance_m", 0.01)
    row["width_m"] = row["facings"] * (width + clearance)
    # Layers/depth are explicit decisions too: retain them when changing face/level.
    row["capacity_units"] = row["facings"] * row["layers"] * row["depth_units"]
    row["load_kg"] = row["capacity_units"] * product.get("weight_kg", 0)
    return row


def interleave(queues, weights=None):
    """Fair round-robin over layer queues, or smooth weighted round-robin by `weights`."""
    if weights is None:
        return [action for group in zip_longest(*queues.values()) for action in group if action]
    declared = list(queues)
    pending = {layer: list(q) for layer, q in queues.items() if q}
    credit = dict.fromkeys(pending, 0.0)
    order = []
    while pending:
        total = sum(weights[layer] for layer in pending)
        for layer in pending:
            credit[layer] += weights[layer]
        # Deterministic tie-break by declared layer order.
        layer = max(pending, key=lambda k: (credit[k], -declared.index(k)))
        credit[layer] -= total
        order.append(pending[layer].pop(0))
        if not pending[layer]:
            del pending[layer], credit[layer]
    return order


def actions(state, feedback, sections, config, weights=None):
    original = state["decisions"]
    shelves = sections["shelves"]["items"]
    products = {p["sku"]: p for p in sections["products"]["items"]}
    queues: dict[str, list[dict]] = {layer: [] for layer in config.layers}
    steps = config.t1_steps or [1]
    objective_t3 = config.t3_scope == "objective"
    domain = to_domain(sections) if config.geometry_prefilter and "T1" in queues else None

    def geometry_valid(poses):
        if domain is None:
            return True
        layout = tuple(
            replace(s, x=poses[s.id][0], y=poses[s.id][1], rotation=poses[s.id][2])
            for s in sorted(domain.shelves, key=lambda v: v.id)
        )
        return not violations(domain.floorplan, layout)

    def add(layer, kind, decision, changed):
        if layer == "T1" and not geometry_valid(decision["poses"]):
            return
        if layer in queues:
            queues[layer].append(
                {
                    "layer": layer,
                    "type": kind,
                    "decisions": decision,
                    "changed": changed,
                    "evidence": feedback["diagnostic_evidence"],
                }
            )

    hot = dict(feedback["hot_shelves"])
    step = sections["floorplan"].get("grid_m", 0.25)
    for s in sorted(shelves, key=lambda v: (-hot.get(v["id"], 0), v["id"])):
        if s.get("locked"):
            continue
        sid = s["id"]
        x, y, angle = original["poses"][sid]
        moves = [
            pose
            for k in steps
            for pose in (
                [x - k * step, y, angle],
                [x, y - k * step, angle],
                [x + k * step, y, angle],
                [x, y + k * step, angle],
            )
        ]
        for pose in [*moves, [x, y, 90 - angle]]:
            d = copy.deepcopy(original)
            d["poses"][sid] = pose
            # T1 changes invalidate optimized allocation/packing; preserve only explicit pose.
            d.pop("assignment")
            d.pop("placements")
            add("T1", "T1_ROTATE" if pose[2] != angle else "T1_MOVE", d, [sid])
    movable = [s["id"] for s in shelves if not s.get("locked")]
    for i, a in enumerate(movable):
        for b in movable[i + 1 :]:
            d = copy.deepcopy(original)
            d["poses"][a], d["poses"][b] = d["poses"][b], d["poses"][a]
            d.pop("assignment")
            d.pop("placements")
            add("T1", "T1_SWAP", d, [a, b])
    picked = feedback["sku_pick_counts"]
    category_heat = {
        c["id"]: sum(
            picked.get(p["sku"], 0) for p in products.values() if p["category_id"] == c["id"]
        )
        for c in sections["categories"]["items"]
    }
    cats = sorted(sections["categories"]["items"], key=lambda c: (-category_heat[c["id"]], c["id"]))
    for c in cats:
        if c.get("fixed_shelf_id"):
            continue
        cid = c["id"]
        for s in shelves:
            if s["id"] == original["assignment"][cid]:
                continue
            d = copy.deepcopy(original)
            d["assignment"][cid] = s["id"]
            d.pop("placements")
            add("T2", "T2_REASSIGN", d, [cid])
        for other in cats:
            if other["id"] <= cid or other.get("fixed_shelf_id"):
                continue
            d = copy.deepcopy(original)
            a = d["assignment"]
            a[cid], a[other["id"]] = a[other["id"]], a[cid]
            d.pop("placements")
            add("T2", "T2_SWAP", d, [cid, other["id"]])
    by_shelf = {s["id"]: s for s in shelves}
    order = sorted(
        enumerate(original["placements"]),
        key=lambda ir: (-picked.get(ir[1]["sku"], 0), ir[1]["sku"]),
    )
    for i, row in order:
        p = products[row["sku"]]
        s = by_shelf[row["shelf_id"]]
        changes = [("T3_FACE", {"face": f}) for f in range(s.get("faces", 1)) if f != row["face"]]
        if objective_t3:
            # T4 routes to the shelf face only; level/orientation/position never change
            # the score, and facings matter only through the capacity shortfall term.
            short = row["capacity_units"] < p.get("demand", 1)
            if short and row["facings"] + 1 <= (p.get("max_facings") or p.get("facings", 1)):
                changes.append(("T3_FACINGS", {"facings": row["facings"] + 1}))
            for kind, kwargs in changes:
                d = copy.deepcopy(original)
                d["placements"][i] = resize(row, p, s, **kwargs)
                add("T3", kind, d, [row["sku"]])
            continue
        changes += [
            ("T3_LEVEL", {"level": lv}) for lv in s["levels"] if lv["id"] != row["level_id"]
        ]
        changes += [
            ("T3_ORIENTATION", {"orientation": a})
            for a in p.get("orientations", [0])
            if a != row["orientation"]
        ]
        changes += [
            ("T3_FACINGS", {"facings": f})
            for f in (row["facings"] + 1, row["facings"] - 1)
            if (p.get("min_facings") or p.get("facings", 1))
            <= f
            <= (p.get("max_facings") or p.get("facings", 1))
        ]
        level = next(lv for lv in s["levels"] if lv["id"] == row["level_id"])
        changes += [
            ("T3_POSITION", {"x": x})
            for x in (0, level["width_m"] - row["width_m"])
            if x >= 0 and not math.isclose(x, row["x_m"])
        ]
        for kind, kwargs in changes:
            d = copy.deepcopy(original)
            d["placements"][i] = resize(row, p, s, **kwargs)
            add("T3", kind, d, [row["sku"]])
    for a, row in enumerate(original["placements"]):
        for b in range(a + 1, len(original["placements"])):
            other = original["placements"][b]
            if other["shelf_id"] != row["shelf_id"]:
                continue
            if objective_t3 and other["face"] == row["face"]:
                continue
            d = copy.deepcopy(original)
            for dest, src in ((a, other), (b, row)):
                d["placements"][dest] = resize(
                    d["placements"][dest],
                    products[d["placements"][dest]["sku"]],
                    by_shelf[row["shelf_id"]],
                    face=src["face"],
                    level=next(
                        v for v in by_shelf[row["shelf_id"]]["levels"] if v["id"] == src["level_id"]
                    ),
                    x=src["x_m"],
                )
            add("T3", "T3_SWAP", d, [row["sku"], other["sku"]])
    for policy in ("nearest", "return", "exact"):
        if policy != original["routing_policy"]:
            d = copy.deepcopy(original)
            d["routing_policy"] = policy
            add("T4", "T4_POLICY", d, [policy])
    # Fair (or success-weighted) round-robin across layers; max_actions is a declared
    # truncated neighborhood.
    return interleave(queues, weights)[: config.max_actions]
