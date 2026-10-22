"""Bounded feasibility repair when the sequential packing cannot initialize a loop."""

import copy
import itertools
import time

from smart_retail.application.stage_workflow import _candidate
from smart_retail.domain.models import EngineError


def initialize(
    sections, config, assess, event, deadline, cancelled, progress, cache, observer, evaluations
):
    try:
        return assess(None)
    except EngineError as exc:
        if exc.code not in ("SLOTTING_FAILED", "INFEASIBLE"):
            raise
        event(
            {
                "status": "FAILED",
                "phase": "INITIALIZATION",
                "reason": exc.code,
                "scope": "Sequential failure; joint infeasibility is not inferred",
            }
        )
    partial = copy.deepcopy(sections)
    partial["optimization"].update(joint=None, stop_after_stage="T2")
    upstream = _candidate(
        partial, cancelled, progress, deadline=deadline, cache=cache, observer=observer
    )
    poses = {s["id"]: [s["x"], s["y"], s["rotation"]] for s in upstream["stages"]["T1"]["shelves"]}
    categories = sections["categories"]["items"]
    shelf_ids = [s["id"] for s in sections["shelves"]["items"]]
    choices = [[c["fixed_shelf_id"]] if c.get("fixed_shelf_id") else shelf_ids for c in categories]
    for assignment in itertools.product(*choices):
        if evaluations() >= config.max_evaluations or time.monotonic() >= deadline:
            raise EngineError(
                "SEARCH_EXHAUSTED",
                "Bounded initialization repair exhausted; joint infeasibility not proven",
            )
        decision = {
            "poses": poses,
            "assignment": dict(zip([c["id"] for c in categories], assignment)),
            "routing_policy": sections["demand"].get("routing_policy", "nearest"),
        }
        try:
            state = assess(decision)
        except EngineError as exc:
            if exc.code in ("CANCELLED", "TIMEOUT", "CACHE_CORRUPT"):
                raise
            event(
                {
                    "status": "FAILED",
                    "action": "REPAIR_T2",
                    "layer": "T2",
                    "reason": exc.code,
                    "accepted": False,
                }
            )
            continue
        event(
            {
                "status": "INITIALIZED",
                "action": "REPAIR_T2",
                "layer": "T2",
                "reason": "VALID_INITIAL_WITNESS",
                "accepted": True,
                "candidate_id": state["id"],
                "decisions": state["decisions"],
            }
        )
        return state
    raise EngineError(
        "SEARCH_EXHAUSTED",
        "No initializer within declared assignment neighborhood; infeasibility not proven",
    )
