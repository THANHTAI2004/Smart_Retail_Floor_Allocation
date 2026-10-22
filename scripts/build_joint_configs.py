"""Publish executable E11-E15 designs; no outcomes or optimal values are fabricated."""

import hashlib
import json
from pathlib import Path

from smart_retail.contracts.experiments import CampaignSpec

ROOT = Path(__file__).resolve().parents[1]


def main():
    datasets = []
    for name in ["local-trap", "two-shelves"]:
        path = ROOT / f"datasets/joint/{name}.json"
        datasets.append(
            {
                "id": name.replace("-", "_"),
                "scale": "tiny",
                "input_path": f"datasets/joint/{name}.json",
                "input_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    space = json.loads((ROOT / "datasets/joint/local-trap-space.json").read_text())
    common = {
        "objective": {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]},
        "scenario_seeds": [0, 101],
        "scenario_seed_policy": "job_seed_offsets",
        "max_iterations": 3,
        "max_evaluations": 80,
        "max_actions": 24,
    }

    def treatment(name, mode, layers=None, finite=False, holdout=False):
        joint = {**common, "mode": mode}
        if layers is not None:
            joint["layers"] = layers
        if finite:
            joint["finite_space"] = space
        if holdout:
            joint["holdout_seeds"] = [10001, 20003]
        return {
            "id": name,
            "overrides": {
                "optimization": {
                    "candidate_count": 3 if mode == "multistart" else 1,
                    "joint": joint,
                }
            },
        }

    modes = [
        treatment("baseline", "sequential"),
        treatment("multistart", "multistart"),
        treatment("feedback", "feedback"),
    ]
    designs = [
        (
            "joint_effectiveness",
            "E11",
            ["two_shelves"],
            modes,
            "Does operational feedback improve the fixed common objective over sequential and multistart?",
        ),
        (
            "joint_ablation",
            "E12",
            ["two_shelves"],
            [treatment("baseline", "sequential")]
            + [
                treatment(layer.lower(), "feedback", [layer])
                for layer in ["T1", "T2", "T3"]
            ]
            + [treatment("combined", "feedback")],
            "Which declared layer neighborhood contributes a valid objective improvement?",
        ),
        (
            "joint_certification",
            "E13",
            ["local_trap"],
            modes
            + [
                treatment("exact", "exact", finite=True),
                treatment("hybrid", "hybrid", finite=True),
            ],
            "Can complete finite search certify and independently verify a better solution than a strict local plateau?",
        ),
        (
            "joint_scalability",
            "E14",
            ["local_trap", "two_shelves", "small"],
            [treatment("baseline", "sequential"), treatment("feedback", "feedback")],
            "How do decision counts and measured resources grow under fixed safe evaluation budgets?",
        ),
        (
            "joint_holdout",
            "E15",
            ["two_shelves"],
            [
                treatment("baseline", "sequential", holdout=True),
                treatment("feedback", "feedback", holdout=True),
            ],
            "Does the selected fixed-training-scenario solution retain its objective on disjoint synthetic holdout seeds?",
        ),
    ]
    for name, eid, ids, arms, question in designs:
        config = {
            "name": name,
            "datasets": datasets + [{"id": "small", "scale": "small"}],
            "experiments": [
                {
                    "id": eid,
                    "question": question,
                    "hypothesis": "Feedback may improve objective; certification requires complete verified finite enumeration.",
                    "datasets": ids,
                    "treatments": arms,
                    "metrics": [
                        "joint_objective",
                        "joint_evaluations",
                        "joint_iterations_to_best",
                        "holdout_objective",
                        "wall_s",
                        "mean_distance_m",
                        "mean_wait_s",
                    ],
                    "acceptance": "Zero independent constraint violations; preserve nonimprovements, bounds, failed and unverified outcomes.",
                }
            ],
            "seeds": [11, 23, 37],
            "job_time_limit_s": 60,
            "memory_limit_mb": 1024,
            "max_wall_s": 1200,
            "max_jobs": 128,
            "workers": 1,
            "cache_policy": "isolated",
        }
        # Vary the common training/holdout sets by campaign job seed in campaign.py.
        spec = CampaignSpec.model_validate(config)
        path = ROOT / f"experiments/configs/{name}.json"
        with path.open("x", encoding="utf-8") as f:
            json.dump(spec.model_dump(mode="json"), f, indent=2)


if __name__ == "__main__":
    main()
