"""Generate the direction-A paper campaign configs (X1-X6) into experiments/configs/paper-v3/.

Design: docs/research/EXPERIMENT_DESIGN_DEEPMG.md, section "paper-v3". Changes after the
paper-v2 review (Ket_qua_thuc_nghiem_lan_1.docx):
- equal evaluation budgets per scale for every search arm (random_search, annealing,
  feedback); wall-time limits are generous safety caps, not the budget;
- order load calibrated per scale to picker utilization 0.75 (sequential plan), more
  orders per instance, 5-fold CV with population order rate in every fold;
- X1 on 10 generated tiny instances in two phases: heuristics here, then exact search
  over the union of their solutions (block X1b, scripts/build_x1_union_configs.py);
- X5 ablation with equal budgets; X6 on small instances; seq_milp is the reference id.
Every campaign is validated by CampaignSpec; designs above the part size are split with
the platform partitioner so paired units never cross campaigns. Existing output
directories are never replaced. Calibration runs the sequential pipeline a few times
per scale while building.
"""

import copy
import json
import sys
from pathlib import Path

from smart_retail.application.experiments.calibration import calibrate
from smart_retail.application.experiments.partition import partition
from smart_retail.contracts.experiments import DatasetSpec, planned_jobs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "configs" / "paper-v3"
CONFIGS = ROOT / "experiments" / "configs"
OBJECTIVE = {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]}
TARGET_UTILIZATION = 0.75
# Scale -> (facings, orders, evaluation budget, job wall cap s, calibration reference seed).
SCALES = {
    "tiny": (6, 150, 40, 300, 101),
    "small": (4, 300, 30, 600, 101),
    "medium": (3, 500, 16, 900, 3001),
}
# Parts stay below the 4 h campaign ceiling at realistic cost (sequential arms take seconds,
# search arms well under the cap); one instance x seed x all arms/folds must fit a part.
PART_JOBS = {300: 45, 600: 25, 900: 14}
MILP = {"algorithm": "milp", "slotting_algorithm": "milp", "candidate_count": 1}
JOINT = {"objective": OBJECTIVE, "scenario_seeds": [0, 101], "scenario_seed_policy": "job_seed_offsets"}
JOINT_METRICS = ["joint_objective", "joint_evaluations", "joint_evaluations_to_best", "mean_distance_m", "mean_wait_s", "wall_s", "peak_child_rss_bytes"]
CV_METRICS = ["test_objective", "train_objective", "generalization_gap", "test_mean_distance_m", "test_mean_wait_s", "joint_evaluations", "joint_evaluations_to_best", "wall_s"]
ACCEPT = "Zero independent violations on training and held-out replays; all failures, budget-limited and unexecuted outcomes retained."
KFOLD5 = {"split": "kfold", "n_folds": 5, "budget_fraction": 0.25, "order_rate": "population"}
HOLDOUT = {"split": "temporal_holdout", "test_size": 0.2, "budget_fraction": 0.25}


def arm(identifier, budget, **joint):
    optimization = copy.deepcopy(MILP)
    if identifier == "baseline":
        optimization.update(algorithm="greedy", slotting_algorithm="first_fit")
    settings = {**copy.deepcopy(JOINT), "max_evaluations": budget, **joint}
    optimization["joint"] = settings
    return {"id": identifier, "overrides": {"optimization": optimization}}


def arms(budget, *, baseline=True):
    """Sequential references plus three search arms sharing one evaluation budget."""
    chosen = [arm("baseline", budget, mode="sequential")] if baseline else []
    return chosen + [
        arm("seq_milp", budget, mode="sequential"),
        arm("random_search", budget, mode="random_search"),
        arm("annealing", budget, mode="annealing"),
        # first_improvement: a 24-action best-improvement sweep would spend most of a
        # 16-40 evaluation budget on one iteration.
        arm("feedback", budget, mode="feedback", max_iterations=100, max_actions=24, policy="first_improvement"),
    ]


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
    parts = partition(spec, PART_JOBS.get(int(spec["job_time_limit_s"]), 1000))
    if len(parts) == 1:
        parts = [parts[0].model_copy(update={"name": spec["name"]})]
    result = []
    for part in parts:
        jobs = planned_jobs(part)
        wall = min(14400.0, max(600.0, jobs * (part.job_time_limit_s + 5)))
        result.append(part.model_copy(update={"max_jobs": jobs, "max_wall_s": wall}))
    return result


def calibrations():
    """One calibrated order interval per scale (reference instance, sequential seq_milp plan)."""
    chosen, evidence = {}, {}
    overrides = {"optimization": {**MILP, "time_limit_s": 900}}
    for scale, (facings, orders, _, _, seed) in SCALES.items():
        spec = DatasetSpec(id=f"{scale}_reference", scale=scale, seed=seed, facings=facings, orders=orders)
        tuned, record = calibrate(spec, overrides, target=TARGET_UTILIZATION)
        chosen[scale] = {"order_interval_s": tuned.order_interval_s, "picker_count": tuned.picker_count}
        evidence[scale] = record
        print(scale, "interval", tuned.order_interval_s, "utilization", round(record["achieved_utilization"], 3), flush=True)
    return chosen, evidence


def build():
    load, evidence = calibrations()

    def dataset(scale, seed, *, interval_factor=1.0):
        facings, orders, *_ = SCALES[scale]
        suffix = "" if interval_factor == 1.0 else f"_load{round(TARGET_UTILIZATION / interval_factor * 100)}"
        return {
            "id": f"{scale}_f{facings}{suffix}_s{seed}",
            "scale": scale,
            "seed": seed,
            "facings": facings,
            "orders": orders,
            "order_interval_s": round(load[scale]["order_interval_s"] * interval_factor, 2),
            "picker_count": load[scale]["picker_count"],
        }

    def budget(scale):
        return SCALES[scale][2]

    def limit(scale):
        return SCALES[scale][3]

    designs = []

    # X1: finite exact reference. local_trap keeps the paper-v2 arms; generated tiny
    # instances get a declared neighborhood space around their sequential plan.
    certification = load_config("joint_certification")
    trap = [d for d in certification["datasets"] if d["id"] == "local_trap"]
    e13 = certification["experiments"][0]
    designs.append(("X1", campaign(
        "paper-x1-trap", trap,
        [experiment("E17", "Do accepted plans pass independent replay and how far are heuristics from the finite exact optimum?", trap, copy.deepcopy(e13["treatments"]), JOINT_METRICS)],
        list(range(1, 31)), 60)))
    # Phase 1 of the generated-instance reference: heuristics only. Phase 2 (block X1b,
    # scripts/build_x1_union_configs.py, called by the runner) certifies the optimum of
    # the union of these solutions under the same experiment ids and seeds.
    tiny_x1 = [dataset("tiny", s) for s in range(5001, 5011)]
    heuristics = experiment("E41", "Gap between heuristics and the certified optimum of the union of their own solutions", tiny_x1, arms(budget("tiny"), baseline=False), JOINT_METRICS)
    designs.append(("X1", campaign("paper-x1-tiny", tiny_x1, [heuristics], [1, 2], limit("tiny"))))

    # X2: main held-out comparison, 10 instances per scale, 5-fold CV at population order rate.
    for scale, seeds, repeats in (("tiny", range(101, 111), [1, 2]), ("small", range(101, 111), [1])):
        items = [dataset(scale, s) for s in seeds]
        designs.append(("X2", campaign(
            f"paper-x2-{scale}", items,
            [experiment("E18", "Does T4 feedback beat sequential pipelines and equal-budget random search / annealing on held-out orders?", items, arms(budget(scale)), CV_METRICS)],
            repeats, limit(scale), KFOLD5)))
    medium = [dataset("medium", s) for s in range(3001, 3005)]
    designs.append(("X2", campaign(
        "paper-x2-medium", medium,
        [experiment("E19", "Does the comparison hold on medium instances (temporal holdout)?", medium, arms(budget("medium")), CV_METRICS)],
        [1], limit("medium"), HOLDOUT)))

    # X3: locked instances, temporal holdout (run once, last).
    for scale, seeds, repeats in (("tiny", range(9001, 9011), [1, 2]), ("small", range(9101, 9111), [1])):
        items = [dataset(scale, s) for s in seeds]
        designs.append(("X3", campaign(
            f"paper-x3-{scale}", items,
            [experiment("E20", "Do conclusions hold on locked instances evaluated on the latest 20% of orders?", items, arms(budget(scale)), CV_METRICS)],
            repeats, limit(scale), HOLDOUT)))

    # X4: scalability without held-out split. Large keeps the uncalibrated generator load
    # and sequential arms only: it documents the limit, not a feedback result.
    for scale in ("tiny", "small", "medium"):
        items = [dataset(scale, s) for s in (101, 202, 303)]
        designs.append(("X4", campaign(
            f"paper-x4-{scale}", items,
            [experiment("E21", "How do wall time, memory and objective scale with instance size under fixed evaluation budgets?", items, [a for a in arms(budget(scale)) if a["id"] in ("seq_milp", "annealing", "feedback")], JOINT_METRICS)],
            [1], limit(scale))))
    large = [{"id": "large_f2_s4001", "scale": "large", "seed": 4001, "facings": 2}]
    designs.append(("X4", campaign(
        "paper-x4-large", large,
        [experiment("E21", "How do wall time, memory and objective scale with instance size under fixed evaluation budgets?", large, arms(budget("medium"))[:2], JOINT_METRICS)],
        [1, 2], 900)))

    # X5: layer ablation, equal evaluation budget for every feedback variant.
    small5 = [dataset("small", s) for s in range(101, 106)]
    layered = [arm("seq_milp", budget("small"), mode="sequential")] + [
        arm(name, budget("small"), mode="feedback", layers=layers, max_iterations=100, max_actions=24, policy="first_improvement")
        for name, layers in (("t1", ["T1"]), ("t2", ["T2"]), ("t3", ["T3"]), ("combined", ["T1", "T2", "T3"]))
    ]
    designs.append(("X5", campaign(
        "paper-x5-ablation", small5,
        [experiment("E22", "Which feedback layers carry the held-out improvement at equal evaluation budget?", small5, layered, CV_METRICS)],
        [1], limit("small"), KFOLD5)))

    # X6: one-factor-at-a-time sensitivity on small instances, temporal holdout.
    small6 = [dataset("small", s) for s in range(201, 206)]
    pair = [a for a in arms(budget("small")) if a["id"] in ("seq_milp", "feedback")]

    def with_override(section, key, value):
        result = copy.deepcopy(pair)
        for treatment in result:
            if section == "objective":
                weights = list(treatment["overrides"]["optimization"]["joint"]["objective"]["weights"])
                weights[key] = value
                treatment["overrides"]["optimization"]["joint"]["objective"] = {**OBJECTIVE, "weights": weights}
            else:
                treatment["overrides"][section] = {key: value}
        return result

    factor_campaigns = []
    number = 23
    experiments = []
    for factor, value, treatments in (
        [("pickers", v, with_override("demand", "picker_count", v)) for v in (1, 2, 4)]
        + [("customers", v, with_override("demand", "customers", v)) for v in (15, 30, 60)]
        + [("wait_weight", v, with_override("objective", 1, v)) for v in (0.0, 0.2, 1.0)]
    ):
        experiments.append(experiment(f"E{number:02d}", f"Sensitivity: {factor} = {value}; does feedback keep its held-out effect?", small6, treatments, CV_METRICS))
        number += 1
    factor_campaigns.append(("paper-x6-demand", small6, experiments))
    loads = []
    load_items = []
    for utilization in (0.5, 0.9):
        items = [dataset("small", s, interval_factor=TARGET_UTILIZATION / utilization) for s in range(201, 206)]
        load_items += items
        loads.append(experiment(f"E{number:02d}", f"Sensitivity: picker utilization ~{utilization}; does feedback keep its held-out effect?", items, copy.deepcopy(pair), CV_METRICS))
        number += 1
    factor_campaigns.append(("paper-x6-load", load_items, loads))
    for name, items, chosen in factor_campaigns:
        designs.append(("X6", campaign(name, items, chosen, [1], limit("small"), HOLDOUT)))
    return designs, {"target_utilization": TARGET_UTILIZATION, "scales": evidence}


def load_config(name):
    return json.loads((CONFIGS / f"{name}.json").read_text(encoding="utf-8"))


def main():
    if OUT.exists():
        sys.exit(f"{OUT} exists; choose a new directory instead of replacing configs")
    designs, calibration = build()
    OUT.mkdir(parents=True)
    (OUT / "calibration.json").write_text(json.dumps(calibration, indent=2) + "\n", encoding="utf-8")
    index = []
    for block, spec in designs:
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
