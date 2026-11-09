"""Generate the paper-v5 campaign configs (W1-W2) into experiments/configs/paper-v5/.

Design: docs/research/EXPERIMENT_DESIGN_DEEPMG.md, section 12. Changes after the
paper-v4 results (HANDOFF.md, 2026-11-03):
- feedback_v5: feedback_v4 plus a T4-calibrated surrogate (walk_heat) that ranks a large
  pool of T1 candidates, compound multi-shelf moves and a surrogate-ranked warm start;
- genetic: a steady-state genetic algorithm at the same evaluation budget as a further
  baseline next to random_search and annealing;
- feedback_v5, its ablations and annealing skip swaps of physically identical shelves
  (drop_identical_swaps); annealing also uses t3_scope "objective" (stronger than paper-v4);
- every stochastic arm derives its search seed from the instance content and the job seed
  (search_seed_scope "instance"), so instances of one scale no longer share a random stream;
- four floor-plan families (grid, corner_entrance, wide, columns) per scale on fresh
  instance seeds (8001+) and 3-5 search seeds, so conclusions do not rest on one geometry
  or one random draw;
- W1: main held-out comparison (E61, temporal holdout); W2: leave-one-component-out
  ablation of feedback_v5 on small instances (E62).
Budgets and job caps are those of paper-v4 (V4_SCALES). Load calibration (order interval,
picker count) is reused per scale from experiments/configs/paper-v3/calibration.json, where it
was measured on the grid family only; the picker utilization of the other families is not
calibrated and is recorded in each job's picker_utilization. W1 parts are indexed medium,
small, tiny. Building runs no simulation. Existing output directories are never
replaced.
"""

import json
import sys
from pathlib import Path

from build_paper_configs import CV_METRICS, HOLDOUT, arm, campaign, experiment
from build_paper_v4_configs import CALIBRATION, V4, V4_SCALES, v4
from build_paper_v4_configs import PART_JOBS as V4_PART_JOBS

from smart_retail.application.experiments.partition import partition
from smart_retail.contracts.experiments import planned_jobs

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
OUT = ROOT / "experiments" / "configs" / "paper-v5"
# Jobs per part by job cap (paper-v4 table). Medium now has six arms per instance x seed
# (paper-v4: five), so one unit needs six jobs; a part of six medium jobs stays near 2.5 h.
PART_JOBS = {**V4_PART_JOBS, 3600: 6}
FAMILIES = ("grid", "corner_entrance", "wide", "columns")
# Per-job search seeds are derived from the instance content: equal seeds on different
# instances do not share a random stream.
INSTANCE = {"search_seed_scope": "instance"}
GENETIC = {"mode": "genetic", "population": 8, "mutation_edits": 2}
# All generated shelves are physically identical, so a swap only relabels two shelves: same
# score, one evaluation. Annealing (uniform moves) also gets the objective T3 scope, so it no
# longer spends budget on score-neutral level/position edits (declared: stronger than the
# paper-v4 annealing arm).
NO_RELABEL = {"drop_identical_swaps": True}
ANNEALING = {"mode": "annealing", **NO_RELABEL, "t3_scope": "objective"}
# All paper-v5 controls on (contracts/feedback.py) except restart_evaluations, which is
# 25% of the budget per scale; V5_OFF removes or weakens one component at a time.
V5 = {
    **V4,
    "surrogate": "walk_heat",
    "surrogate_pool": 96,
    "compound_moves": 32,
    "restart_samples": 128,
    "search_seed_scope": "instance",
    **NO_RELABEL,
}
RESTART_EVALUATIONS = {"tiny": 10, "small": 8, "medium": 10}
V5_OFF = {
    "surrogate": {"surrogate": None},
    "compound": {"compound_moves": None},
    "restart": {"restart_samples": None, "restart_evaluations": None},
    "heat": {"surrogate": "walk"},
}
# Scale -> (first instance seed, instances per family, search seeds). Medium comes first in
# the index: its job times are the least known (no paper-v5 pilot), so they surface early.
W1_SCALES = {
    "medium": (8201, 2, [1, 2, 3]),
    "small": (8101, 3, [1, 2, 3, 4, 5]),
    "tiny": (8001, 3, [1, 2, 3, 4, 5]),
}
W2_FIRST, W2_PER_FAMILY, W2_SEEDS = 8301, 2, [1, 2, 3]


def v5(scale, **changes):
    settings = {**V5, "restart_evaluations": RESTART_EVALUATIONS[scale], **changes}
    return v4(**settings)


def arms(scale):
    budget = V4_SCALES[scale][2]
    return [
        arm("seq_milp", budget, mode="sequential"),
        arm("random_search", budget, mode="random_search", **INSTANCE),
        arm("annealing", budget, **ANNEALING, **INSTANCE),
        arm("genetic", budget, **GENETIC, **INSTANCE),
        arm("feedback_v4", budget, **v4(**INSTANCE)),
        arm("feedback_v5", budget, **v5(scale)),
    ]


def ablation_arms(scale):
    budget = V4_SCALES[scale][2]
    return [arm("seq_milp", budget, mode="sequential"), arm("feedback_v5", budget, **v5(scale))] + [
        arm(f"v5_no_{name}", budget, **v5(scale, **off)) for name, off in V5_OFF.items()
    ]


def finalize(spec):
    """Split over-limit designs; give every part a job ceiling and a wall budget."""
    parts = partition(spec, PART_JOBS.get(int(spec["job_time_limit_s"]), 1000))
    if len(parts) == 1:
        parts = [parts[0].model_copy(update={"name": spec["name"]})]
    result = []
    for part in parts:
        jobs = planned_jobs(part)
        wall = min(14400.0, max(600.0, jobs * (part.job_time_limit_s + 5)))
        result.append(part.model_copy(update={"max_jobs": jobs, "max_wall_s": wall}))
    return result


def build():
    load = json.loads(CALIBRATION.read_text(encoding="utf-8"))["scales"]

    def datasets(scale, first, per_family):
        facings, orders, *_ = V4_SCALES[scale]
        items = []
        for seed in range(first, first + per_family * len(FAMILIES)):
            family = FAMILIES[(seed - first) // per_family]
            items.append({
                "id": f"{scale}_f{facings}_{family}_s{seed}",
                "scale": scale,
                "seed": seed,
                "facings": facings,
                "orders": orders,
                "order_interval_s": load[scale]["order_interval_s"],
                "picker_count": load[scale]["picker_count"],
                "layout_family": family,
            })
        return items

    designs = []
    # W1: main held-out comparison, four floor-plan families per scale.
    for scale, (first, per_family, seeds) in W1_SCALES.items():
        items = datasets(scale, first, per_family)
        designs.append(("W1", campaign(
            f"paper-v5-w1-{scale}", items,
            [experiment("E61", "Does feedback_v5 beat sequential pipelines and equal-budget random search, annealing and a genetic algorithm across floor-plan families and search seeds?", items, arms(scale), CV_METRICS)],
            seeds, V4_SCALES[scale][3], HOLDOUT)))

    # W2: leave-one-component-out ablation of feedback_v5 on small instances.
    small = datasets("small", W2_FIRST, W2_PER_FAMILY)
    designs.append(("W2", campaign(
        "paper-v5-w2-ablation", small,
        [experiment("E62", "Which feedback_v5 component (surrogate, heat weighting, compound moves, warm start) carries the held-out improvement at equal budget?", small, ablation_arms("small"), CV_METRICS)],
        W2_SEEDS, V4_SCALES["small"][3], HOLDOUT)))
    return designs


def main():
    if OUT.exists():
        sys.exit(f"{OUT} exists; choose a new directory instead of replacing configs")
    designs = build()
    parts = [(block, part) for block, spec in designs for part in finalize(spec)]
    OUT.mkdir(parents=True)
    index = []
    for block, part in parts:
        path = OUT / f"{part.name}.json"
        path.write_text(json.dumps(part.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8")
        index.append({"block": block, "config": path.name, "jobs": planned_jobs(part), "job_time_limit_s": part.job_time_limit_s})
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    for row in index:
        print(row)
    print("total jobs", sum(r["jobs"] for r in index))


if __name__ == "__main__":
    main()
