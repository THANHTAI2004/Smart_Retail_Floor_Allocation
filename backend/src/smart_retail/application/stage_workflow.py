"""Application orchestration. Engines never choose the whole-system workflow."""

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import asdict

from smart_retail.application.decisions import (
    decided_assignment as _decided_assignment,
)
from smart_retail.application.decisions import (
    decided_layout as _decided_layout,
)
from smart_retail.application.decisions import (
    decided_planogram as _decided_planogram,
)
from smart_retail.application.decisions import (
    decided_simulation as _decided_simulation,
)
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError
from smart_retail.engines.t1_layout.engine import solve as layout
from smart_retail.engines.t2_allocation.engine import solve as allocate
from smart_retail.engines.t3_slotting.engine import solve as slot


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
    observer: Callable = lambda *args: None,
    decisions: dict | None = None,
) -> dict:
    dataset = to_domain(sections)
    decisions = decisions or {}
    result: dict = {
        "input_sha256": canonical_hash(sections),
        "seed": dataset.config.seed,
        "floorplan": sections["floorplan"],
        "stages": {},
        "stage_cache": {},
    }

    def cached(stage: str, inputs: dict, compute: Callable):
        def cache_key(values):
            return canonical_hash(
                {
                    "stage": stage,
                    "version": "research-v1",
                    "runtime": sections.get("_runtime"),
                    "joint_context": sections.get("_joint_context"),
                    "budget_s": dataset.config.time_limit_s,
                    "inputs": values,
                }
            )

        key = cache_key(inputs)
        # A supplied physical decision identical to a cached official solve reuses
        # that verified artifact. An upstream decision edit never forces unrelated
        # recomputation merely by changing auto-vs-explicit representation.
        requested = inputs.get("decision")
        if requested is not None and cache is not None:
            automatic = {**inputs, "decision": None}
            automatic_key = cache_key(automatic)
            if automatic_key in cache:
                previous = cache[automatic_key]
                physical = (
                    {s.id: [s.x, s.y, s.rotation] for s in previous.shelves}
                    if stage == "T1"
                    else previous["assignment"]
                    if stage == "T2"
                    else list(previous.placements)
                    if stage == "T3"
                    else None
                )
                if canonical_hash({"value": physical}) == canonical_hash({"value": requested}):
                    key = automatic_key
        began = time.monotonic()
        hit = cache is not None and key in cache
        try:
            value = cache[key] if cache is not None and key in cache else compute()
        except EngineError as exc:
            exc.stage = stage
            raise
        status = value.get("status") if isinstance(value, dict) else getattr(value, "status", None)
        if cache is not None and status != "FEASIBLE_TIME_LIMIT":
            cache[key] = value
        observer(stage, key, inputs, value, hit, time.monotonic() - began)
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
            "algorithm": dataset.config.layout_algorithm,
            "decision": decisions.get("poses"),
        },
        lambda: (
            _decided_layout(dataset, decisions, deadline)
            if "poses" in decisions
            else layout(
                dataset.floorplan,
                dataset.shelves,
                dataset.layout_mode,
                deadline=deadline,
                max_iterations=dataset.config.max_iterations,
                cancelled=cancelled,
                variant=variant,
                algorithm=dataset.config.layout_algorithm,
            )
        ),
    )
    result["stages"]["T1"] = asdict(t1)
    if dataset.config.stop_after_stage == "T1":
        result["status"] = "SUCCEEDED"
        return result
    check("T2")
    t2 = cached(
        "T2",
        {
            "shelves": asdict(t1),
            "categories": sections["categories"],
            "floor": sections["floorplan"],
            "algorithm": dataset.config.algorithm,
            "distance_weight": dataset.config.distance_weight,
            "affinity_weight": dataset.config.affinity_weight,
            "decision": decisions.get("assignment"),
        },
        lambda: (
            _decided_assignment(dataset, t1, decisions)
            if "assignment" in decisions
            else allocate(
                dataset.floorplan,
                t1.shelves,
                dataset.categories,
                algorithm=dataset.config.algorithm,
                distance_weight=dataset.config.distance_weight,
                affinity_weight=dataset.config.affinity_weight,
                time_limit_s=max(0.001, deadline - time.monotonic()),
            )
        ),
    )
    result["stages"]["T2"] = t2
    if dataset.config.stop_after_stage == "T2":
        result["status"] = "SUCCEEDED"
        return result
    check("T3")
    t3 = cached(
        "T3",
        {
            "shelves": asdict(t1),
            "products": sections["products"],
            "assignment": t2["assignment"],
            "algorithm": dataset.config.slotting_algorithm,
            "decision": decisions.get("placements"),
        },
        lambda: (
            _decided_planogram(dataset, t1, t2, decisions)
            if "placements" in decisions
            else slot(
                t1.shelves,
                dataset.products,
                t2["assignment"],
                algorithm=dataset.config.slotting_algorithm,
                deadline=deadline,
                cancelled=cancelled,
            )
        ),
    )
    result["stages"]["T3"] = asdict(t3)
    if dataset.config.stop_after_stage == "T3":
        result["status"] = "SUCCEEDED"
        return result
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
            "routing_policy": decisions.get("routing_policy"),
        },
        lambda: _decided_simulation(dataset, t1, t2, t3, decisions, deadline),
    )
    result["stages"]["T4"] = asdict(t4)
    check("COMPLETE")
    result["status"] = "SUCCEEDED"
    return result
