# Vai trò: Chạy đánh giá trên các seed kịch bản dùng chung và tính mục tiêu so sánh nhất quán.
# Các quyết định được kiểm tra trước khi được chọn.
"""Common-random-number evaluation and fixed, rational selection objective."""

import copy
from fractions import Fraction

from smart_retail.application.experiments.validation import verify
from smart_retail.application.stage_workflow import _candidate, canonical_hash


# Hàm decisions_of: xử lý bước decisions of trong phạm vi module hiện tại.
def decisions_of(result):
    stages = result["stages"]
    return {
        "poses": {s["id"]: [s["x"], s["y"], s["rotation"]] for s in stages["T1"]["shelves"]},
        "assignment": copy.deepcopy(stages["T2"]["assignment"]),
        "placements": [dict(p) for p in stages["T3"]["placements"]],
        "routing_policy": stages["T4"]["metrics"]["routing_policy"],
    }


# Chuyển giá trị sang phân số theo quy tắc của mục tiêu để so sánh nhất quán.
def fraction(value):
    return Fraction(str(value))


# Tính giá trị mục tiêu của quyết định theo định nghĩa và các thành phần đã khai báo.
def score(stages, sections, objective):
    metrics = stages["T4"]["metrics"]
    capacities = {p["sku"]: p["capacity_units"] for p in stages["T3"]["placements"]}
    demand = {p["sku"]: p.get("demand", 1) for p in sections["products"]["items"]}
    shortfall = sum(max(Fraction(0), fraction(d) - capacities[k]) for k, d in demand.items())
    shortfall /= max(Fraction(1), sum(map(fraction, demand.values())))
    values = [
        fraction(metrics["mean_distance_m"]),
        fraction(metrics["mean_wait_s"]),
        shortfall,
        Fraction(metrics["late_orders"], max(1, len(sections["orders"]["orders"]))),
    ]
    normalized = [v / fraction(s) for v, s in zip(values, objective.scales)]
    total = sum(v * fraction(w) for v, w in zip(normalized, objective.weights))
    return total / sum(map(fraction, objective.weights)), normalized


# Đánh giá cùng quyết định trên bộ seed chung giúp giảm sai khác do ngẫu nhiên giữa các phương pháp.
def evaluate(
    sections,
    config,
    decisions,
    deadline,
    cancelled,
    progress,
    cache,
    observer,
    seeds=None,
    variant=0,
    context_seeds=None,
):
    """Score `decisions` on `seeds`; `context_seeds` is the declared scenario set of the
    stage cache identity (screening evaluates a prefix of the set and reuses its stages)."""
    seeds = seeds or config.scenario_seeds
    scenarios, scores, vectors = [], [], []
    for seed in seeds:
        data = copy.deepcopy(sections)
        data["optimization"].update(joint=None, seed=seed, stop_after_stage="T4")
        data["_joint_context"] = {
            "objective": config.objective.model_dump(mode="json"),
            "scenario_set": list(context_seeds or seeds),
            "model": "joint-finite-1",
        }
        result = _candidate(
            data,
            cancelled,
            progress,
            deadline=deadline,
            variant=variant,
            cache=cache,
            observer=observer,
            decisions=decisions,
        )
        result["integrated"] = {"candidates": [{"status": "FEASIBLE", "stages": result["stages"]}]}
        verify(data, result)
        value, vector = score(result["stages"], sections, config.objective)
        scenarios.append(result)
        scores.append(value)
        vectors.append(vector)
    value = sum(scores) / len(scores)
    vector = [sum(v[i] for v in vectors) / len(vectors) for i in range(4)]
    return {
        "id": canonical_hash(decisions_of(scenarios[0])),
        "decisions": decisions_of(scenarios[0]),
        "result": scenarios[0],
        "scenarios": scenarios,
        "score": float(value),
        "score_fraction": [value.numerator, value.denominator],
        "components": list(map(float, vector)),
        "scenario_seeds": seeds,
        "validation": "PASS",
    }


# Tính điểm theo biểu diễn chính xác cho phép kiểm tra chứng nhận trong miền hữu hạn.
def exact_score(state):
    return Fraction(*state["score_fraction"])


# Hàm prefix_score: xử lý bước prefix score trong phạm vi module hiện tại.
def prefix_score(state, sections, objective, count):
    """Exact mean score of an evaluated state over its first `count` scenario seeds."""
    values = [score(s["stages"], sections, objective)[0] for s in state["scenarios"][:count]]
    return sum(values) / len(values)
