"""deepmg-style results layout: one folder per arm with sum/eachfold/mean files.

Mirrors deepmg (pypi.org/project/deepmg) ``results/<prefix>/``: ``*_file_sum.txt``
(parameters, per-fold rows, final summary; renamed ``*_file_sum_ok.txt`` once every
planned job of the arm has an outcome), ``*_file_eachfold.txt`` (``--save_folds``),
``*_file_mean_*.txt`` per-repetition fold means with time (``--save_avg_run``) and
``*_config.json`` to repeat exactly that arm (``--save_para``). Classification
metrics (ACC/AUC/MCC) are replaced by the declared optimization metrics.
"""

import json
import statistics
from collections import defaultdict
from pathlib import Path

from smart_retail.application.experiments.storage import read, write

FOLD_COLUMNS = (
    "seed",
    "repetition",
    "cv_fold",
    "status",
    "evaluation_status",
    "train_orders",
    "test_orders",
    "train_objective",
    "test_objective",
    "generalization_gap",
    "test_mean_distance_m",
    "test_mean_wait_s",
    "mean_distance_m",
    "mean_wait_s",
    "wall_s",
    "run_id",
)
SUMMARY_METRICS = (
    "train_objective",
    "test_objective",
    "generalization_gap",
    "test_mean_distance_m",
    "test_mean_wait_s",
    "wall_s",
)
MEAN_FILES = {
    "test_objective": "file_mean_test_objective.txt",
    "test_mean_distance_m": "file_mean_test_distance.txt",
}


def cell(value) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def line(values) -> str:
    return "\t".join(cell(v) for v in values) + "\n"


def stats(values: list[float]) -> tuple:
    if not values:
        return (0, None, None)
    sd = statistics.stdev(values) if len(values) > 1 else None
    return (len(values), statistics.mean(values), sd)


def successful(records: list[dict], metric: str) -> list[float]:
    return [
        r[metric]
        for r in records
        if r["status"] == "SUCCEEDED" and isinstance(r.get(metric), (int, float))
    ]


def prefix(configuration: dict, experiment: str, dataset: str, treatment: str) -> str:
    spec = configuration.get("evaluation")
    if spec is None:
        protocol = "nocv"
    elif spec["split"] == "kfold":
        protocol = f"k{spec['n_folds']}"
    else:
        protocol = f"holdout{spec['test_size']}"
    runs = len(configuration["seeds"]) * configuration["repetitions"]
    budget = f"{configuration['job_time_limit_s']:g}"
    return f"{experiment}_{dataset}_{treatment}_{protocol}_r{runs}_t{budget}s"


def arm_config(configuration: dict, experiment: str, dataset: str, treatment: str, jobs: int):
    """A one-arm campaign whose jobs reproduce the same job keys and inputs."""
    source = next(e for e in configuration["experiments"] if e["id"] == experiment)
    return {
        **configuration,
        "name": f"{configuration['name']}-{experiment}-{dataset}-{treatment}"[:120],
        "datasets": [d for d in configuration["datasets"] if d["id"] == dataset],
        "experiments": [
            {
                **source,
                "datasets": [dataset],
                "treatments": [t for t in source["treatments"] if t["id"] == treatment],
            }
        ],
        "max_jobs": jobs,
    }


def export(roots: list[Path], output: Path, rows: list[dict], configurations: list[dict]):
    planned: dict[tuple, int] = defaultdict(int)
    origin: dict[tuple, dict] = {}
    for root, configuration in zip(roots, configurations):
        keys = set()
        for job in read(root / "plan.json")["jobs"]:
            key = (job["experiment"], job["dataset"], job["treatment"])
            planned[key] += 1
            keys.add(key)
        for key in keys:
            current = arm_config(configuration, *key, planned[key])
            if key not in origin:
                origin[key] = current
                continue
            previous = origin[key]
            variable = {"name", "seeds", "max_jobs", "max_wall_s"}
            if {k: v for k, v in previous.items() if k not in variable} != {
                k: v for k, v in current.items() if k not in variable
            }:
                raise ValueError("Pooled arm configurations differ beyond seed partitions")
            origin[key] = {
                **previous,
                "seeds": sorted(set(previous["seeds"]) | set(current["seeds"])),
                "max_wall_s": min(14400.0, previous["max_wall_s"] + current["max_wall_s"]),
            }
    arms: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        arms[row["experiment"], row["dataset"], row["treatment"]].append(row)
    written = []
    for key in sorted(planned):
        experiment, dataset, treatment = key
        configuration = origin[key]
        name = prefix(configuration, *key)
        folder = output / "results" / name
        folder.mkdir(parents=True)
        records = sorted(
            arms.get(key, []),
            key=lambda r: (r["seed"], r["repetition"], r.get("cv_fold", -1)),
        )
        complete = len(records) == planned[key]
        source = next(e for e in configuration["experiments"] if e["id"] == experiment)
        overrides = next(t for t in source["treatments"] if t["id"] == treatment)["overrides"]
        dataset_spec = next(d for d in configuration["datasets"] if d["id"] == dataset)
        write(
            folder / f"{name}_config.json",
            arm_config(configuration, *key, planned[key]),
            immutable=True,
        )
        with (folder / f"{name}_file_eachfold.txt").open("x", encoding="utf-8") as stream:
            stream.write(line(FOLD_COLUMNS))
            for record in records:
                stream.write(line(record.get(c) for c in FOLD_COLUMNS))
        by_run: dict[tuple, list[dict]] = defaultdict(list)
        for record in records:
            by_run[record["seed"], record["repetition"]].append(record)
        for metric, filename in MEAN_FILES.items():
            with (folder / f"{name}_{filename}").open("x", encoding="utf-8") as stream:
                stream.write(line(("seed", "repetition", "folds_ok", "mean", "sd", "time_s")))
                for (seed, repetition), group in sorted(by_run.items()):
                    time_s = sum(r.get("wall_s") or 0 for r in group)
                    stream.write(
                        line((seed, repetition, *stats(successful(group, metric)), time_s))
                    )
        header = [
            f"# deepmg-style summary\t{experiment}\t{dataset}\t{treatment}",
            f"# campaign\t{configuration['name']}",
            f"# question\t{source['question']}",
            f"# dataset\t{json.dumps(dataset_spec, sort_keys=True)}",
            f"# treatment\t{json.dumps(overrides, sort_keys=True)}",
            f"# evaluation\t{json.dumps(configuration.get('evaluation'), sort_keys=True)}",
            f"# seeds\t{configuration['seeds']}\trepetitions\t{configuration['repetitions']}",
            f"# job_time_limit_s\t{configuration['job_time_limit_s']}"
            f"\tmemory_limit_mb\t{configuration['memory_limit_mb']}",
            f"# planned\t{planned[key]}\tattempted\t{len(records)}",
        ]
        summary = f"{name}_file_sum{'_ok' if complete else ''}.txt"
        with (folder / summary).open("x", encoding="utf-8") as stream:
            stream.write("\n".join(header) + "\n")
            stream.write(line(FOLD_COLUMNS))
            for record in records:
                stream.write(line(record.get(c) for c in FOLD_COLUMNS))
            stream.write(line(("summary", "n", "mean", "sd")))
            for metric in SUMMARY_METRICS:
                stream.write(line((metric, *stats(successful(records, metric)))))
            succeeded = sum(r["status"] == "SUCCEEDED" for r in records)
            total = sum(r.get("wall_s") or 0 for r in records)
            stream.write(line(("succeeded", succeeded, None, None)))
            stream.write(line(("total_time_s", None, total, None)))
        written.append({"arm": name, "complete": complete, "jobs": len(records)})
    return written
