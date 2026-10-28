"""Generate the direction-A paper campaign configs (X1-X6) into experiments/configs/paper/.

Design: docs/research/EXPERIMENT_DESIGN_DEEPMG.md. Every campaign is validated by
CampaignSpec; designs above 1,000 jobs are split with the platform partitioner so
that paired units never cross campaigns. Existing output files are never replaced.
"""

import copy
import json
import sys
from pathlib import Path

from smart_retail.application.experiments.partition import partition
from smart_retail.contracts.experiments import planned_jobs

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
OUT = ROOT / "experiments" / "configs" / "paper-v2"
LONG_LIMIT_S = 900
# Worst case per 900 s job ~990 s with grace; keep every part below the 4 h campaign ceiling.
LONG_PART_JOBS = 24
CONFIGS = ROOT / "experiments" / "configs"
OBJECTIVE = {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]}


def load(name):
    return json.loads((CONFIGS / f"{name}.json").read_text(encoding="utf-8"))


PILOT_ARMS = {t["id"]: t["overrides"] for t in load("pilot_cv")["experiments"][0]["treatments"]}
ARMS = [{"id": arm, "overrides": PILOT_ARMS[arm]} for arm in ("baseline", "seq_milp", "multistart", "feedback")]
JOINT_METRICS = ["joint_objective", "joint_evaluations", "joint_iterations_to_best", "mean_distance_m", "mean_wait_s", "wall_s", "peak_child_rss_bytes"]
CV_METRICS = ["test_objective", "train_objective", "generalization_gap", "test_mean_distance_m", "test_mean_wait_s", "wall_s", "peak_child_rss_bytes"]
ACCEPT = "Zero independent violations on training and held-out replays; all failures, budget-limited and unexecuted outcomes retained."


def dataset(identifier, scale, seed, facings):
    return {"id": identifier, "scale": scale, "seed": seed, "facings": facings}


def experiment(identifier, question, datasets, treatments, metrics):
    return {
        "id": identifier,
        "question": question,
        "hypothesis": "Treatment effects are estimated, not assumed; zero and adverse effects are valid outcomes.",
        "datasets": [d["id"] for d in datasets],
        "treatments": treatments,
        "metrics": metrics,
        "acceptance": ACCEPT,
        "statistical_method": "descriptive_paired_exploratory",
    }


def campaign(name, datasets, experiments, seeds, time_limit, evaluation=None):
    spec = {
        "schema_version": "1.1",
        "name": name,
        "data_origin": "SYNTHETIC",
        "datasets": datasets,
        "experiments": experiments,
        "seeds": seeds,
        "repetitions": 1,
        "job_time_limit_s": float(time_limit),
        "memory_limit_mb": 2048,
        "max_wall_s": 14400.0,
        "max_jobs": 1000,
        "max_retries": 1,
        "workers": 1,
        "cache_policy": "isolated",
    }
    if evaluation:
        spec["evaluation"] = evaluation
    return spec


def finalize(spec):
    """Split over-limit designs; give every part a job ceiling and a wall budget."""
    parts = partition(spec, LONG_PART_JOBS if spec["job_time_limit_s"] > 60 else 1000)
    if len(parts) == 1:
        parts = [parts[0].model_copy(update={"name": spec["name"]})]
    result = []
    for part in parts:
        jobs = planned_jobs(part)
        wall = min(14400.0, max(600.0, jobs * (part.job_time_limit_s + 5)))
        result.append(part.model_copy(update={"max_jobs": jobs, "max_wall_s": wall}))
    return result


def build():
    kfold10 = {"split": "kfold", "n_folds": 10, "budget_fraction": 0.25}
    kfold2 = {"split": "kfold", "n_folds": 2, "budget_fraction": 0.25}
    holdout = {"split": "temporal_holdout", "test_size": 0.2, "budget_fraction": 0.25}
    designs = []

    # X1: correctness and finite exact reference (E13 arms) on the declared local-trap space.
    certification = load("joint_certification")
    trap = [d for d in certification["datasets"] if d["id"] == "local_trap"]
    e13 = certification["experiments"][0]
    designs.append(("X1", campaign(
        "paper-x1-exact", trap,
        [experiment("E17", "Do accepted plans pass independent replay and how far are heuristics from the finite exact optimum?", trap, copy.deepcopy(e13["treatments"]), JOINT_METRICS)],
        list(range(1, 31)), 60)))

    # X2: main held-out comparison, deepmg-style repeated stratified k-fold.
    tiny = [dataset(f"tiny_f6_s{s}", "tiny", s, 6) for s in (101, 202, 303)]
    small = [dataset(f"small_f4_s{s}", "small", s, 4) for s in (101, 202, 303)]
    designs.append(("X2", campaign(
        "paper-x2-tiny", tiny,
        [experiment("E18", "Do integrated feedback plans beat sequential pipelines on held-out orders?", tiny, ARMS, CV_METRICS)],
        list(range(1, 11)), 60, kfold10)))
    designs.append(("X2", campaign(
        "paper-x2-small", small,
        [experiment("E18", "Do integrated feedback plans beat sequential pipelines on held-out orders?", small, ARMS, CV_METRICS)],
        list(range(1, 6)), 60, kfold10)))

    # X2b: instance generalization with 5x2cv.
    for name, scale, facings, seeds, limit in (
        ("paper-x2b-tiny", "tiny", 6, range(1001, 1011), 60),
        ("paper-x2b-small", "small", 4, range(2001, 2011), 60),
        ("paper-x2b-medium", "medium", 3, range(3001, 3004), LONG_LIMIT_S),
    ):
        items = [dataset(f"{scale}_f{facings}_s{s}", scale, s, facings) for s in seeds]
        repeats = list(range(1, 4)) if scale == "medium" else list(range(1, 6))
        designs.append(("X2b", campaign(
            name, items,
            [experiment("E19", "Does the method ranking hold across independently generated instances?", items, ARMS, CV_METRICS)],
            repeats, limit, kfold2)))

    # X3: locked external instances, temporal holdout (run once, last).
    for name, scale, facings, seeds in (("paper-x3-tiny", "tiny", 6, range(9001, 9006)), ("paper-x3-small", "small", 4, range(9101, 9106))):
        items = [dataset(f"{scale}_f{facings}_s{s}", scale, s, facings) for s in seeds]
        designs.append(("X3", campaign(
            name, items,
            [experiment("E20", "Do conclusions hold on locked instances evaluated on the latest 20% of orders?", items, ARMS, CV_METRICS)],
            list(range(1, 11)), 60, holdout)))

    # X4: scalability without held-out split.
    for name, scale, facings, seeds, repeats, limit, arms in (
        ("paper-x4-tiny", "tiny", 6, (101, 202, 303), range(1, 6), 60, ARMS),
        ("paper-x4-small", "small", 4, (101, 202, 303), range(1, 6), 60, ARMS),
        ("paper-x4-medium", "medium", 3, (3001, 3002, 3003), range(1, 6), LONG_LIMIT_S, ARMS),
        ("paper-x4-large", "large", 2, (4001,), range(1, 3), LONG_LIMIT_S, ARMS[:2]),
    ):
        items = [dataset(f"{scale}_f{facings}_s{s}", scale, s, facings) for s in seeds]
        designs.append(("X4", campaign(
            name, items,
            [experiment("E21", "How do wall time, memory and objective scale with instance size under fixed budgets?", items, arms, JOINT_METRICS)],
            list(repeats), limit)))

    # X5: ablation of feedback layers (E12 arms) on capacity-bound small instances.
    ablation = load("joint_ablation")["experiments"][0]["treatments"]
    layered = []
    for treatment in copy.deepcopy(ablation):
        optimization = treatment["overrides"].setdefault("optimization", {})
        optimization.update(algorithm="milp", slotting_algorithm="milp")
        optimization["joint"].update(objective=OBJECTIVE, scenario_seeds=[0, 101], scenario_seed_policy="job_seed_offsets")
        layered.append(treatment)
    designs.append(("X5", campaign(
        "paper-x5-ablation", small,
        [experiment("E22", "Which feedback layers (T1/T2/T3) carry the held-out improvement?", small, layered, CV_METRICS)],
        list(range(1, 6)), 60, kfold2)))

    # X6: one-factor-at-a-time sensitivity; one experiment per factor level.
    factors = [
        ("arrivals", [("demand", "arrivals_per_hour", v) for v in (15, 30, 60)]),
        ("pickers", [("demand", "picker_count", v) for v in (1, 2, 4)]),
        ("customers", [("demand", "customers", v) for v in (5, 10, 20)]),
        ("wait_weight", [("objective", 1, v) for v in (0.0, 0.2, 1.0)]),
    ]
    experiments = []
    number = 23
    for factor, levels in factors:
        for section, key, value in levels:
            arms = []
            for label, source in (("baseline", "seq_milp"), ("feedback", "feedback")):
                overrides = copy.deepcopy(PILOT_ARMS[source])
                if section == "demand":
                    overrides["demand"] = {key: value}
                else:
                    weights = list(overrides["optimization"]["joint"]["objective"]["weights"])
                    weights[key] = value
                    overrides["optimization"]["joint"]["objective"]["weights"] = weights
                arms.append({"id": label, "overrides": overrides})
            experiments.append(experiment(f"E{number}", f"Sensitivity: {factor} = {value}; does feedback keep its held-out effect?", tiny, arms, CV_METRICS))
            number += 1
    for index in range(0, len(experiments), 6):
        designs.append(("X6", campaign(f"paper-x6-sensitivity-{index // 6 + 1}", tiny, experiments[index:index + 6], list(range(1, 6)), 60, kfold2)))
    return designs


def main():
    if OUT.exists():
        sys.exit(f"{OUT} exists; choose a new directory instead of replacing configs")
    OUT.mkdir(parents=True)
    index = []
    for block, spec in build():
        for part in finalize(spec):
            path = OUT / f"{part.name}.json"
            path.write_text(json.dumps(part.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8")
            index.append({"block": block, "config": path.name, "jobs": planned_jobs(part), "job_time_limit_s": part.job_time_limit_s})
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    for row in index:
        print(row)
    print("total jobs", sum(r["jobs"] for r in index))


if __name__ == "__main__":
    main()
