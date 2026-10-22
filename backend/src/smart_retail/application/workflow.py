"""Application orchestration. Engines never choose the whole-system workflow."""

import hashlib
import json
import math
import time
from collections.abc import Callable
from dataclasses import asdict

from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError
from smart_retail.engines.t1_layout.engine import solve as layout
from smart_retail.engines.t2_allocation.engine import solve as allocate
from smart_retail.engines.t3_slotting.engine import solve as slot
from smart_retail.engines.t4_simulation.engine import solve as simulate


def canonical_hash(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
        ).encode()
    ).hexdigest()


def _candidate(
    sections: dict,
    cancelled: Callable[[], bool] = lambda: False,
    progress: Callable[[str], None] = lambda _: None,
    *,
    deadline: float,
    variant: int = 0,
    cache: dict | None = None,
) -> dict:
    dataset = to_domain(sections)
    result: dict = {
        "input_sha256": canonical_hash(sections),
        "seed": dataset.config.seed,
        "floorplan": sections["floorplan"],
        "stages": {},
        "stage_cache": {},
    }

    def cached(stage: str, inputs: dict, compute: Callable):
        key = canonical_hash(
            {
                "stage": stage,
                "version": "research-v1",
                "runtime": sections.get("_runtime"),
                "inputs": inputs,
            }
        )
        hit = cache is not None and key in cache
        value = cache[key] if cache is not None and key in cache else compute()
        if cache is not None:
            cache[key] = value
        result["stage_cache"][stage] = {"key": key, "hit": hit}
        return value

    def check(stage: str) -> None:
        progress(stage)
        if cancelled():
            raise EngineError("CANCELLED", "Run was cancelled")
        if time.monotonic() >= deadline:
            raise EngineError("TIMEOUT", f"Budget exhausted before {stage}")

    check("T1")
    t1 = cached(
        "T1",
        {
            "floor": sections["floorplan"],
            "shelves": sections["shelves"],
            "variant": variant if dataset.layout_mode != "fixed" else 0,
            "max_iterations": dataset.config.max_iterations,
        },
        lambda: layout(
            dataset.floorplan,
            dataset.shelves,
            dataset.layout_mode,
            deadline=deadline,
            max_iterations=dataset.config.max_iterations,
            cancelled=cancelled,
            variant=variant,
        ),
    )
    result["stages"]["T1"] = asdict(t1)
    check("T2")
    t2 = cached(
        "T2",
        {
            "shelves": asdict(t1),
            "categories": sections["categories"],
            "floor": sections["floorplan"],
            "algorithm": dataset.config.algorithm,
            "distance_weight": dataset.config.distance_weight,
        },
        lambda: allocate(
            dataset.floorplan,
            t1.shelves,
            dataset.categories,
            algorithm=dataset.config.algorithm,
            distance_weight=dataset.config.distance_weight,
            time_limit_s=max(0.001, deadline - time.monotonic()),
        ),
    )
    result["stages"]["T2"] = t2
    check("T3")
    t3 = cached(
        "T3",
        {
            "shelves": asdict(t1),
            "products": sections["products"],
            "assignment": t2["assignment"],
            "algorithm": dataset.config.slotting_algorithm,
        },
        lambda: slot(
            t1.shelves,
            dataset.products,
            t2["assignment"],
            algorithm=dataset.config.slotting_algorithm,
            deadline=deadline,
            cancelled=cancelled,
        ),
    )
    result["stages"]["T3"] = asdict(t3)
    check("T4")
    t4 = cached(
        "T4",
        {
            "shelves": asdict(t1),
            "planogram": asdict(t3),
            "assignment": t2["assignment"],
            "floor": sections["floorplan"],
            "demand": sections["demand"],
            "orders": sections["orders"],
            "products": sections["products"],
            "seed": dataset.config.seed,
        },
        lambda: simulate(dataset, t1.shelves, t2["assignment"], deadline, t3),
    )
    result["stages"]["T4"] = asdict(t4)
    check("COMPLETE")
    result["status"] = "SUCCEEDED"
    return result


def execute(
    sections: dict,
    cancelled: Callable[[], bool] = lambda: False,
    progress: Callable[[str], None] = lambda _: None,
) -> dict:
    """Bounded full-stage candidate evaluation; no global optimality assertion.

    Candidate 0 is always the baseline, all candidates share one wall budget.
    A failed layout/allocation is evidence about that candidate only.
    """
    dataset = to_domain(sections)
    deadline = time.monotonic() + dataset.config.time_limit_s
    records: list[dict] = []
    solutions: list[tuple[float, int, dict]] = []
    diagonal = max(
        math.dist(a, b) for a in dataset.floorplan.boundary for b in dataset.floorplan.boundary
    )
    demand = {p.sku: p.demand for p in dataset.products}
    cache: dict = {}
    for index in range(dataset.config.candidate_count):
        if cancelled():
            raise EngineError("CANCELLED", "Run was cancelled")
        if time.monotonic() >= deadline:
            if solutions:
                break
            raise EngineError("TIMEOUT", "Integrated budget exhausted")
        try:
            candidate = _candidate(
                sections, cancelled, progress, deadline=deadline, variant=index, cache=cache
            )
        except EngineError as exc:
            if exc.code in ("CANCELLED", "INVALID_SOLUTION", "INVALID_INPUT"):
                raise
            records.append({"candidate": index, "status": exc.code, "message": str(exc)})
            if dataset.config.candidate_count == 1:
                raise
            if exc.code == "TIMEOUT":
                break
            continue
        metrics = candidate["stages"]["T4"]["metrics"]
        capacity = {p["sku"]: p["capacity_units"] for p in candidate["stages"]["T3"]["placements"]}
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
        score = sum(a * b for a, b in zip(components, weights)) / sum(weights)
        records.append(
            {
                "candidate": index,
                "status": "FEASIBLE",
                "score": score,
                "components": components,
                "stages": candidate["stages"],
                "stage_cache": candidate["stage_cache"],
            }
        )
        solutions.append((score, index, candidate))
    if not solutions:
        if records and records[-1]["status"] == "TIMEOUT":
            raise EngineError("TIMEOUT", "Integrated budget exhausted without a complete candidate")
        raise EngineError(
            "SEARCH_EXHAUSTED", "No complete candidate found; joint infeasibility is not proven"
        )
    _, selected, result = min(solutions, key=lambda item: (item[0], item[1]))
    feasible = [r for r in records if r["status"] == "FEASIBLE"]
    pareto = [
        r["candidate"]
        for r in feasible
        if not any(
            all(a <= b for a, b in zip(other["components"], r["components"]))
            and any(a < b for a, b in zip(other["components"], r["components"]))
            for other in feasible
        )
    ]
    result["integrated"] = {
        "algorithm": "bounded_grid_multistart_v1",
        "selected_candidate": selected,
        "requested_candidates": dataset.config.candidate_count,
        "evaluated_candidates": len(records),
        "candidates": records,
        "pareto_candidates": pareto,
        "global_optimality_proven": False,
        "termination": "CANDIDATE_LIMIT"
        if len(records) == dataset.config.candidate_count and records[-1]["status"] != "TIMEOUT"
        else "TIME_BUDGET",
        "normalization": [
            "mean route m / floor diagonal m",
            "mean wait s / arrival horizon s",
            "sum positive (demand - capacity units) / max(1, total demand)",
        ],
        "assumptions": [
            "Product demand is treated as horizon unit demand for stock shortfall scoring",
            "T1 variants change sweep direction, orientation order and shelf order",
            "One shared wall budget; deterministic candidate ordering can favor early candidates",
            "Content-addressed stage reuse is limited to this run; no historical artifacts are reused",
        ],
    }
    return result
