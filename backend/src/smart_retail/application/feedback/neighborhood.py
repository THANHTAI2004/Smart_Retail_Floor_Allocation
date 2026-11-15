# Vai trò: Sinh các thay đổi quyết định T1–T4 và sắp thứ tự theo chẩn đoán.
# Đề xuất vẫn cần được đánh giá và kiểm tra tính khả thi.
"""Deterministic feasible-or-rejected decision edits, ranked by observed T4 evidence."""

import copy
import math
import random
from dataclasses import replace
from itertools import zip_longest

from smart_retail.application.feedback import surrogate
from smart_retail.application.feedback.restarts import DEFAULT_RESTART_STEP, restart
from smart_retail.application.stage_workflow import canonical_hash
from smart_retail.contracts.inputs import to_domain
from smart_retail.engines.t1_layout.geometry import violations

DEFAULT_POOL = 96
# Shelf fields that identify or place a shelf; every other field is physical.
POSE_FIELDS = ("id", "x", "y", "rotation", "locked")


# Trích quyết định vật lý để so sánh hoặc sửa ứng viên mà không trộn telemetry.
def physical(shelf):
    """Hash of a shelf's physical attributes: equal for shelves that differ only in id/pose."""
    return canonical_hash({k: v for k, v in shelf.items() if k not in POSE_FIELDS})


# Xác định quyết định bị khóa để sinh lân cận đúng giới hạn đầu vào.
def pinned(sections):
    """Shelves that a category is fixed to; moving their pose is never a mere relabel."""
    return {c["fixed_shelf_id"] for c in sections["categories"]["items"] if c.get("fixed_shelf_id")}


# Nhận diện hoán vị kệ tương đương để kiểm soát các bước đổi nhãn trung tính.
def relabel(sections, before, after):
    """True when the poses `after` only permute physically identical shelves of `before`."""
    kinds = {s["id"]: physical(s) for s in sections["shelves"]["items"]}
    if any(after[sid] != before[sid] for sid in pinned(sections)):
        return False

    # Hàm signature: xử lý bước signature trong phạm vi module hiện tại.
    def signature(poses):
        return sorted((tuple(round(v, 8) for v in poses[sid]), kinds[sid]) for sid in poses)

    return signature(before) == signature(after)


# Hàm resize: xử lý bước resize trong phạm vi module hiện tại.
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


# Hàm interleave: xử lý bước interleave trong phạm vi module hiện tại.
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


# Hàm geometry_valid: xử lý bước geometry valid trong phạm vi module hiện tại.
def geometry_valid(domain, poses):
    layout = tuple(
        replace(s, x=poses[s.id][0], y=poses[s.id][1], rotation=poses[s.id][2])
        for s in sorted(domain.shelves, key=lambda v: v.id)
    )
    return not violations(domain.floorplan, layout)


# Hàm make_action: tạo action theo quy tắc trong thân hàm.
def make_action(layer, kind, decision, changed, feedback):
    return {
        "layer": layer,
        "type": kind,
        "decisions": decision,
        "changed": changed,
        "evidence": feedback["diagnostic_evidence"],
    }


# Hàm t1_edits: xử lý bước t1 edits trong phạm vi module hiện tại.
def t1_edits(state, feedback, sections, config):
    """Single T1 edits as (type, decision, changed): shelf by shelf, hottest first, then swaps."""
    original = state["decisions"]
    shelves = sections["shelves"]["items"]
    hot = dict(feedback["hot_shelves"])
    step = sections["floorplan"].get("grid_m", 0.25)
    steps = config.t1_steps or [1]
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
            yield "T1_ROTATE" if pose[2] != angle else "T1_MOVE", d, [sid]
    movable = [s["id"] for s in shelves if not s.get("locked")]
    kinds = {s["id"]: physical(s) for s in shelves} if config.drop_identical_swaps else {}
    fixed = pinned(sections) if config.drop_identical_swaps else set()
    for i, a in enumerate(movable):
        for b in movable[i + 1 :]:
            if kinds and kinds[a] == kinds[b] and not {a, b} & fixed:
                # Swapping identical shelves only relabels them: same score, one evaluation.
                continue
            d = copy.deepcopy(original)
            d["poses"][a], d["poses"][b] = d["poses"][b], d["poses"][a]
            d.pop("assignment")
            d.pop("placements")
            yield "T1_SWAP", d, [a, b]


# Tạo tập ứng viên vị trí kệ có seed để sàng lọc trước khi đánh giá mô phỏng đầy đủ.
def t1_pool(state, feedback, sections, config, pool_seed, deadline=math.inf):
    """Seeded sample of the geometry-valid single T1 edits plus compound random walks.

    Compound walks move 2..N shelves at once. The pool is ranked by the surrogate, which
    drops layouts without a valid topology, or shuffled when no surrogate is configured.
    """
    original = state["decisions"]
    domain = to_domain(sections)
    singles = [
        make_action("T1", kind, d, changed, feedback)
        for kind, d, changed in t1_edits(state, feedback, sections, config)
        if geometry_valid(domain, d["poses"])
    ]
    rng = random.Random(pool_seed)
    pool = rng.sample(singles, min(len(singles), config.surrogate_pool or DEFAULT_POOL))
    movable = sum(1 for s in sections["shelves"]["items"] if not s.get("locked"))
    for variant in range(1, (config.compound_moves or 0) + 1):
        decision, changed = restart(
            state,
            sections,
            pool_seed,
            variant,
            max_step=config.restart_max_step or DEFAULT_RESTART_STEP,
            edits=rng.randint(2, max(2, movable)),
        )
        if decision is None or (
            config.drop_identical_swaps
            and relabel(sections, original["poses"], decision["poses"])
        ):
            continue
        d = copy.deepcopy(original)
        d["poses"] = decision["poses"]
        d.pop("assignment")
        d.pop("placements")
        pool.append(make_action("T1", "T1_COMPOUND", d, changed, feedback))
    unique: dict[str, dict] = {}
    for action in pool:
        if action["decisions"]["poses"] != original["poses"]:
            unique.setdefault(canonical_hash(action["decisions"]), action)
    pool = list(unique.values())
    if config.surrogate:
        heat = surrogate.heat(feedback, sections, config.surrogate == "walk_heat")
        return surrogate.rank(pool, sections, heat, deadline)
    rng.shuffle(pool)
    return pool


# Sinh lân cận theo các layer được bật; thứ tự đề xuất không bảo đảm mọi ứng viên đều khả thi.
def actions(state, feedback, sections, config, weights=None, pool_seed=None, deadline=math.inf):
    original = state["decisions"]
    shelves = sections["shelves"]["items"]
    products = {p["sku"]: p for p in sections["products"]["items"]}
    queues: dict[str, list[dict]] = {layer: [] for layer in config.layers}
    objective_t3 = config.t3_scope == "objective"
    pooled = pool_seed is not None and (
        config.surrogate_pool is not None or config.surrogate is not None
    )
    prefilter = config.geometry_prefilter and "T1" in queues and not pooled
    domain = to_domain(sections) if prefilter else None

    # Hàm add: xử lý bước add trong phạm vi module hiện tại.
    def add(layer, kind, decision, changed):
        if layer == "T1" and domain is not None and not geometry_valid(domain, decision["poses"]):
            return
        if layer in queues:
            queues[layer].append(make_action(layer, kind, decision, changed, feedback))

    if pooled:
        if "T1" in queues:
            queues["T1"] = t1_pool(state, feedback, sections, config, pool_seed, deadline)
    else:
        for kind, d, changed in t1_edits(state, feedback, sections, config):
            add("T1", kind, d, changed)
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
