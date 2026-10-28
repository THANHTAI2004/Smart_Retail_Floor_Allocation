"""Generate the paper-v4 campaign configs (V1-V4) into experiments/configs/paper-v4/.

Design: docs/research/EXPERIMENT_DESIGN_DEEPMG.md, section 11. Changes after the
paper-v3 results (Ket_qua_thuc_nghiem_lan_2.docx):
- feedback_v4: multi-step T1 moves with a geometry prefilter, objective-relevant T3
  edits, adaptive layer allocation and iterated-local-search kicks;
- V2 separates step size from T4 guidance (2 x 2: random walk step 1 / 3 versus
  guided feedback step 1 / 1-3);
- V3 budget grid {16, 30, 40, 80} on one scale, so scale and budget are not confounded;
- V4 leave-one-out ablation of the feedback_v4 components;
- fresh instance seeds (7001-7710) never used for paper-v3 tuning; at least 10
  instances per design except large;
- medium gets the tiny budget 40 (job cap 3,600 s), so V1 has one budget at every scale;
- VL: large instances compared at equal wall time (search_time_s), not equal evaluations;
- V5: two-fidelity screening (screen_seeds) on medium, budget in full-evaluation
  equivalents.
Load calibration is reused from experiments/configs/paper-v3/calibration.json (same
generator and target utilization), so building runs no simulation. Existing output
directories are never replaced.
"""

import json
import sys
from pathlib import Path

from build_paper_configs import CV_METRICS, HOLDOUT, KFOLD5, SCALES, arm, campaign, experiment

from smart_retail.application.experiments.partition import partition
from smart_retail.contracts.experiments import planned_jobs

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
OUT = ROOT / "experiments" / "configs" / "paper-v4"
CALIBRATION = ROOT / "experiments" / "configs" / "paper-v3" / "calibration.json"
# paper-v3 scales with medium raised to the tiny budget (40 x ~39 s/evaluation ~ 26 min).
V4_SCALES = {**SCALES, "medium": (3, 500, 40, 3600, 3001)}
# Jobs per part by job cap; one instance x seed x all arms/folds must fit a part and a
# realistic part stays under the 4 h campaign ceiling (medium: 5 arms ~ 1.8 h).
PART_JOBS = {300: 45, 600: 25, 900: 14, 3600: 5}
# Large: equal wall time. 3,000 s of search, the rest of the 3,600 s cap is left for
# verification and held-out scoring; max_evaluations is only a safety bound.
LARGE_SEARCH_S = 3000
LARGE = {"max_evaluations": 20000, "search_time_s": LARGE_SEARCH_S}
# V5 screening: 1 of 2 scenario seeds, promote within 2% of the reference plan (declared).
SCREEN = {"screen_seeds": 1, "screen_margin": 0.02}
FEEDBACK = {"mode": "feedback", "max_iterations": 100, "max_actions": 24, "policy": "first_improvement"}
# All paper-v4 controls on (contracts/feedback.py); V4 removes one at a time.
V4 = {
    "t1_steps": [1, 2, 3],
    "geometry_prefilter": True,
    "t3_scope": "objective",
    "layer_allocation": "adaptive",
    "kicks": 10,
    "kick_edits": 3,
    "patience": 2,
}
V4_OFF = {
    "steps": {"t1_steps": None},
    "prefilter": {"geometry_prefilter": None},
    "t3_scope": {"t3_scope": None},
    "adaptive": {"layer_allocation": None},
    "kicks": {"kicks": None, "kick_edits": None, "patience": None},
}


def v4(**changes):
    settings = {**FEEDBACK, **V4, **changes}
    return {k: v for k, v in settings.items() if v is not None}


def arms(budget):
    return [
        arm("seq_milp", budget, mode="sequential"),
        arm("random_search", budget, mode="random_search"),
        arm("annealing", budget, mode="annealing"),
        arm("feedback", budget, **FEEDBACK),
        arm("feedback_v4", budget, **v4()),
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

    def dataset(scale, seed):
        facings, orders, *_ = V4_SCALES[scale]
        return {
            "id": f"{scale}_f{facings}_s{seed}",
            "scale": scale,
            "seed": seed,
            "facings": facings,
            "orders": orders,
            "order_interval_s": load[scale]["order_interval_s"],
            "picker_count": load[scale]["picker_count"],
        }

    def budget(scale):
        return V4_SCALES[scale][2]

    def limit(scale):
        return V4_SCALES[scale][3]

    designs = []
    # V1: main held-out comparison on fresh instances, 10 per scale.
    for scale, first, repeats, evaluation in (
        ("tiny", 7001, [1, 2], KFOLD5),
        ("small", 7101, [1], KFOLD5),
        ("medium", 7201, [1], HOLDOUT),
    ):
        items = [dataset(scale, s) for s in range(first, first + 10)]
        designs.append(("V1", campaign(
            f"paper-v4-v1-{scale}", items,
            [experiment("E51", "Does feedback_v4 beat sequential pipelines and equal-budget random search / annealing on held-out orders of fresh instances?", items, arms(budget(scale)), CV_METRICS)],
            repeats, limit(scale), evaluation)))

    # V2: step size versus guidance at equal budget (2 x 2 plus the reference).
    small2 = [dataset("small", s) for s in range(7301, 7311)]
    b = budget("small")
    factorial = [
        arm("seq_milp", b, mode="sequential"),
        arm("random_step1", b, mode="random_search", restart_max_step=1),
        arm("random_step3", b, mode="random_search"),
        arm("guided_step1", b, **FEEDBACK),
        arm("guided_step3", b, **FEEDBACK, t1_steps=[1, 2, 3], geometry_prefilter=True),
    ]
    designs.append(("V2", campaign(
        "paper-v4-v2-step-guidance", small2,
        [experiment("E52", "Is the random-search advantage due to step size and prefiltering rather than the absence of T4 guidance?", small2, factorial, CV_METRICS)],
        [1], limit("small"), KFOLD5)))

    # V3: evaluation-budget grid on one scale (temporal holdout keeps the cost bounded).
    small3 = [dataset("small", s) for s in range(7401, 7411)]
    grid = [arm("seq_milp", 80, mode="sequential")]
    for n in (16, 30, 40, 80):
        grid += [
            arm(f"random_search_b{n}", n, mode="random_search"),
            arm(f"feedback_v4_b{n}", n, **v4()),
        ]
    designs.append(("V3", campaign(
        "paper-v4-v3-budget", small3,
        [experiment("E53", "How do feedback_v4 and random search improve with the evaluation budget on one scale?", small3, grid, CV_METRICS)],
        [1], 900, HOLDOUT)))

    # V4: leave-one-component-out ablation of feedback_v4.
    small4 = [dataset("small", s) for s in range(7501, 7511)]
    ablation = [arm("seq_milp", b, mode="sequential"), arm("feedback_v4", b, **v4())] + [
        arm(f"v4_no_{name}", b, **v4(**off)) for name, off in V4_OFF.items()
    ]
    designs.append(("V4", campaign(
        "paper-v4-v4-ablation", small4,
        [experiment("E54", "Which feedback_v4 component carries the held-out improvement at equal budget?", small4, ablation, CV_METRICS)],
        [1], limit("small"), HOLDOUT)))

    # VL: large instances at equal wall time (uncalibrated generator load, as paper-v3 X4).
    large = [{"id": f"large_f2_s{s}", "scale": "large", "seed": s, "facings": 2} for s in range(7601, 7604)]
    timed = [
        arm("seq_milp", 1, mode="sequential"),
        arm("random_search", 1, mode="random_search", **LARGE),
        arm("feedback_v4", 1, **v4(**LARGE)),
    ]
    designs.append(("VL", campaign(
        "paper-v4-vl-large", large,
        [experiment("E55", "At equal wall time, does feedback_v4 keep its advantage on large instances?", large, timed, CV_METRICS)],
        [1], 3600, HOLDOUT)))

    # V5: two-fidelity screening at equal full-evaluation-equivalent budget (medium).
    medium5 = [dataset("medium", s) for s in range(7701, 7711)]
    m = budget("medium")
    screened = [
        arm("seq_milp", m, mode="sequential"),
        arm("random_search", m, mode="random_search"),
        arm("random_search_screen", m, mode="random_search", **SCREEN),
        arm("feedback_v4", m, **v4()),
        arm("feedback_v4_screen", m, **v4(**SCREEN)),
    ]
    designs.append(("V5", campaign(
        "paper-v4-v5-screening", medium5,
        [experiment("E56", "Does two-fidelity screening improve held-out objective at the same full-evaluation-equivalent budget?", medium5, screened, CV_METRICS)],
        [1], limit("medium"), HOLDOUT)))
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
