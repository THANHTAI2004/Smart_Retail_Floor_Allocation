"""Demand estimation from orders and out-of-sample scoring of a selected plan.

Training and held-out sections are derived by the same estimation rule. Held-out
orders reach only this module; optimization runs on a copy without them.
"""

import copy
import math
import time
from collections import defaultdict
from collections.abc import Callable

from smart_retail.application.stage_workflow import _candidate, canonical_hash
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError

ASSUMPTIONS = [
    "Product demand = ordered units in the subset x population orders / subset orders",
    "Category demand = sum of its estimated product demand",
    "Held-out orders replay with the fixed selected layout, assignment, planogram and route policy",
    "Training and held-out loads differ when subsets differ in size; compare methods on identical folds",
]


def estimate_demand(sections: dict, orders: dict, population_orders: int) -> dict:
    """Return a copy whose orders and demand parameters come from ``orders`` only."""
    data = copy.deepcopy(sections)
    data["orders"] = copy.deepcopy(orders)
    units: dict[str, int] = defaultdict(int)
    for line in orders["order_lines"]:
        units[line["sku"]] += line["quantity"]
    factor = population_orders / max(1, len(orders["orders"]))
    by_category: dict[str, float] = defaultdict(float)
    for product in data["products"]["items"]:
        product["demand"] = round(units.get(product["sku"], 0) * factor, 6)
        by_category[product["category_id"]] += product["demand"]
    for category in data["categories"]["items"]:
        category["demand"] = round(by_category.get(category["id"], 0.0), 6)
    return data


def integrated_score(sections: dict, stages: dict) -> tuple[float, list[float]]:
    """Weighted integrated objective used by bounded candidate selection."""
    dataset = to_domain(sections)
    diagonal = max(
        math.dist(a, b) for a in dataset.floorplan.boundary for b in dataset.floorplan.boundary
    )
    metrics = stages["T4"]["metrics"]
    capacity = {p["sku"]: p["capacity_units"] for p in stages["T3"]["placements"]}
    demand = {p.sku: p.demand for p in dataset.products}
    components = [
        metrics["mean_distance_m"] / diagonal,
        metrics["mean_wait_s"] / dataset.demand.horizon_s,
        sum(max(0, value - capacity[sku]) for sku, value in demand.items())
        / max(1, sum(demand.values())),
    ]
    weights = (
        dataset.config.travel_weight,
        dataset.config.wait_weight,
        dataset.config.stock_weight,
    )
    return sum(a * b for a, b in zip(components, weights)) / sum(weights), components


def _metrics(results: list[dict]) -> dict:
    keys = ("mean_distance_m", "mean_wait_s", "late_orders", "completed")
    return {
        key: sum(r["stages"]["T4"]["metrics"][key] for r in results) / len(results) for key in keys
    }


def evaluate_held_out(
    sections: dict,
    result: dict,
    deadline: float,
    cancelled: Callable[[], bool],
    progress: Callable[[str], None],
    cache: dict,
    observer: Callable,
) -> dict:
    from smart_retail.application.experiments.validation import verify
    from smart_retail.application.feedback.coordinator import resolved_config
    from smart_retail.application.feedback.evaluator import decisions_of
    from smart_retail.application.feedback.evaluator import evaluate as joint_evaluate

    spec = sections["optimization"]["evaluation"]
    base = copy.deepcopy(sections)
    base["optimization"].pop("evaluation")
    test = estimate_demand(base, spec["orders"], spec["population_orders"])
    summary: dict = {
        "split": spec["split"],
        "fold": spec["fold"],
        "train_orders": len(sections["orders"]["orders"]),
        "test_orders": len(spec["orders"]["orders"]),
        "population_orders": spec["population_orders"],
        "input_sha256": canonical_hash(test),
        "assumptions": ASSUMPTIONS,
    }
    joint = result.get("joint")
    # Objective values are comparable only between arms sharing one definition.
    summary["objective_definition"] = (
        "joint:" + canonical_hash(joint["normalization"])[:16] if joint else "integrated-v1"
    )
    if joint is not None:
        best = joint.get("best")
        if best is None:
            return {**summary, "status": "NO_SOLUTION"}
        decisions, train_objective = best["decisions"], best["score"]
    elif base["optimization"].get("stop_after_stage", "T4") != "T4":
        return {**summary, "status": "NOT_APPLICABLE_PARTIAL_PIPELINE"}
    else:
        selected = result["integrated"]["selected_candidate"]
        record = next(c for c in result["integrated"]["candidates"] if c["candidate"] == selected)
        decisions, train_objective = decisions_of(result), record["score"]
    summary["train_objective"] = train_objective
    progress("EVALUATION")
    try:
        if joint is not None:
            held = joint_evaluate(
                test,
                resolved_config(test),
                decisions,
                deadline,
                cancelled,
                progress,
                cache,
                observer,
                seeds=best["scenario_seeds"],
            )
            objective, components, scored = held["score"], held["components"], held["scenarios"]
        else:
            replayed = _candidate(
                test,
                cancelled,
                progress,
                deadline=deadline,
                cache=cache,
                observer=observer,
                decisions=decisions,
            )
            replayed["integrated"] = {
                "candidates": [{"status": "FEASIBLE", "stages": replayed["stages"]}]
            }
            verify(test, replayed)
            objective, components = integrated_score(test, replayed["stages"])
            scored = [replayed]
    except EngineError as exc:
        if exc.code != "TIMEOUT":
            raise
        return {**summary, "status": "NOT_EXECUTED_BUDGET"}
    return {
        **summary,
        "status": "COMPLETED",
        "validation": "PASS",
        "objective": objective,
        "components": components,
        "generalization_gap": objective - train_objective,
        "metrics": _metrics(scored),
    }


def with_held_out(sections: dict, execute: Callable, **kwargs) -> dict:
    """Optimize on training orders within a reduced budget, then score held-out orders."""
    began = time.monotonic()
    spec = sections["optimization"]["evaluation"]
    total = sections["optimization"].get("time_limit_s", 30)
    training = copy.deepcopy(sections)
    training["optimization"].pop("evaluation")
    training["optimization"]["time_limit_s"] = total * (1 - spec["budget_fraction"])
    result = execute(training, **kwargs)
    result["input_sha256"] = canonical_hash(sections)
    cache = kwargs.get("stage_cache")
    result["evaluation"] = evaluate_held_out(
        sections,
        result,
        began + total,
        kwargs.get("cancelled", lambda: False),
        kwargs.get("progress", lambda _: None),
        cache if cache is not None else {},
        kwargs.get("observer", lambda *args: None),
    )
    return result
