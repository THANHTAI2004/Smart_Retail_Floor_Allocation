"""Application orchestration and mode dispatch."""

import math
import time
from collections.abc import Callable

from smart_retail.application.evaluation import integrated_score, with_held_out
from smart_retail.application.stage_workflow import _candidate
from smart_retail.application.stage_workflow import canonical_hash as canonical_hash
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError


def execute(
    sections: dict,
    cancelled: Callable[[], bool] = lambda: False,
    progress: Callable[[str], None] = lambda _: None,
    *,
    stage_cache: dict | None = None,
    observer: Callable = lambda *args: None,
) -> dict:
    """Bounded full-stage candidate evaluation; no global optimality assertion.

    Candidate 0 is always the baseline, all candidates share one wall budget.
    A failed layout/allocation is evidence about that candidate only.
    """
    dataset = to_domain(sections)
    if sections["optimization"].get("evaluation") is not None:
        return with_held_out(
            sections,
            execute,
            cancelled=cancelled,
            progress=progress,
            stage_cache=stage_cache,
            observer=observer,
        )
    if dataset.config.joint is not None:
        from smart_retail.application.feedback.coordinator import optimize

        return optimize(sections, cancelled, progress, stage_cache=stage_cache, observer=observer)
    deadline = time.monotonic() + dataset.config.time_limit_s
    records: list[dict] = []
    solutions: list[tuple[float, int, dict]] = []
    cache: dict = stage_cache if stage_cache is not None else {}
    for index in range(dataset.config.candidate_count):
        if cancelled():
            raise EngineError("CANCELLED", "Run was cancelled")
        if time.monotonic() >= deadline:
            if solutions:
                break
            raise EngineError("TIMEOUT", "Integrated budget exhausted")
        try:
            candidate = _candidate(
                sections,
                cancelled,
                progress,
                deadline=deadline,
                variant=index,
                cache=cache,
                observer=observer,
            )
        except EngineError as exc:
            if exc.code in ("CANCELLED", "INVALID_SOLUTION", "INVALID_INPUT"):
                raise
            records.append(
                {
                    "candidate": index,
                    "status": exc.code,
                    "message": str(exc),
                    "failed_stage": exc.stage,
                }
            )
            if dataset.config.candidate_count == 1:
                raise
            if exc.code == "TIMEOUT":
                break
            continue
        if dataset.config.stop_after_stage != "T4":
            stage = dataset.config.stop_after_stage
            if stage == "T1":
                from smart_retail.domain.models import Shelf, ShelfLevel
                from smart_retail.engines.t1_layout.geometry import footprint

                shelves = [
                    Shelf(**{**s, "levels": tuple(ShelfLevel(**level) for level in s["levels"])})
                    for s in candidate["stages"]["T1"]["shelves"]
                ]
                score = sum(
                    math.dist(
                        dataset.floorplan.entrance,
                        (footprint(s).centroid.x, footprint(s).centroid.y),
                    )
                    for s in shelves
                )
            elif stage == "T2":
                score = candidate["stages"]["T2"]["objective"]
            else:
                score = -candidate["stages"]["T3"]["objective"]
            records.append(
                {
                    "candidate": index,
                    "status": "FEASIBLE",
                    "score": score,
                    "components": [score],
                    "stages": candidate["stages"],
                    "stage_cache": candidate["stage_cache"],
                }
            )
            solutions.append((score, index, candidate))
            continue
        score, components = integrated_score(sections, candidate["stages"])
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
        "stop_after_stage": dataset.config.stop_after_stage,
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
