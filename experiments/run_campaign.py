"""Synthetic research smoke campaign through the production durable process queue.

Run from repository root. Existing output directories are never overwritten.
"""

import argparse
import copy
import hashlib
import json
import platform
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

from scipy.stats import t
from smart_retail.application.projects import (
    create_project,
    enqueue,
    get_run,
    save_section,
)
from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.inputs import SECTIONS
from smart_retail.infrastructure.database import connect
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.workers.runner import work_once

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())


def write(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def cases(sample: dict):
    """Paired treatments. These are small synthetic probes, not acceptance thresholds."""
    for experiment in range(1, 9):
        for treatment in ("baseline", "treatment"):
            data = copy.deepcopy(sample)
            data["optimization"].update(time_limit_s=15, max_iterations=50000)
            changed = treatment == "treatment"
            if experiment == 1 and changed:
                data["floorplan"]["boundary"] = [
                    [0, 0],
                    [12, 0],
                    [12, 8],
                    [8, 8],
                    [8, 9],
                    [0, 9],
                ]
            elif experiment == 2:
                data["optimization"]["algorithm"] = "milp" if changed else "greedy"
            elif experiment == 3:
                # Small stock/load witness with an independently known optimum of 14.
                data["shelves"]["items"] = [
                    {
                        "id": "S",
                        "width_m": 1,
                        "depth_m": 0.6,
                        "height_m": 1,
                        "levels": [
                            {
                                "id": "L",
                                "width_m": 1,
                                "depth_m": 0.6,
                                "height_m": 0.5,
                                "max_load_kg": 6,
                            }
                        ],
                    }
                ]
                data["categories"]["items"] = [
                    {"id": "C", "name": "Synthetic", "required_width_m": 0.6}
                ]
                data["products"]["items"] = [
                    {
                        "sku": sku,
                        "name": sku,
                        "category_id": "C",
                        "width_m": 0.3,
                        "depth_m": 0.2,
                        "height_m": 0.2,
                        "weight_kg": 1,
                        "demand": demand,
                        "stack_layers": 2,
                        "clearance_m": 0,
                    }
                    for sku, demand in (("A", 3), ("B", 1))
                ]
                data["demand"]["baskets"] = [["A", "B"]]
                data["orders"] = {"orders": [], "order_lines": []}
                data["optimization"]["slotting_algorithm"] = (
                    "milp" if changed else "first_fit"
                )
            elif experiment == 4:
                data["shelves"]["layout_mode"] = "fixed"
                for i, shelf in enumerate(data["shelves"]["items"]):
                    shelf.update(x=(7 if changed else 1), y=1 + i * 3)
            elif experiment == 5:
                data["optimization"]["candidate_count"] = 4 if changed else 1
            elif experiment == 6:
                for p in data["products"]["items"]:
                    p["demand"] *= 2 if changed else 1
                data["demand"]["arrivals_per_hour"] *= 2 if changed else 1
            elif experiment == 7:
                data["optimization"].update(
                    candidate_count=4, wait_weight=1 if changed else 0
                )
            elif experiment == 8 and changed:
                template_shelf = copy.deepcopy(data["shelves"]["items"][0])
                template_product = copy.deepcopy(data["products"]["items"][0])
                for i in range(2, 8):
                    sid, cid, sku = f"SYN{i}", f"CAT{i}", f"SKU{i}"
                    data["shelves"]["items"].append(
                        {**copy.deepcopy(template_shelf), "id": sid}
                    )
                    data["categories"]["items"].append(
                        {"id": cid, "name": cid, "required_width_m": 2}
                    )
                    data["products"]["items"].append(
                        {
                            **copy.deepcopy(template_product),
                            "sku": sku,
                            "category_id": cid,
                        }
                    )
            yield f"E{experiment:02}", treatment, data


def summarize(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        groups.setdefault((row["experiment"], row["treatment"]), []).append(row)
    summary = []
    for (experiment, treatment), group in groups.items():
        record = {
            "experiment": experiment,
            "treatment": treatment,
            "runs": len(group),
            "succeeded": sum(r["status"] == "SUCCEEDED" for r in group),
            "metrics": {},
        }
        for metric in (
            "wall_s",
            "mean_distance_m",
            "mean_wait_s",
            "t2_objective",
            "t3_objective",
        ):
            values = [r[metric] for r in group if r.get(metric) is not None]
            n = len(values)
            if not n:
                continue
            mean = statistics.mean(values)
            sd = statistics.stdev(values) if n > 1 else None
            half = float(t.ppf(0.975, n - 1)) * sd / n**0.5 if n > 1 else None
            record["metrics"][metric] = {
                "n": n,
                "mean": mean,
                "sample_sd": sd,
                "ci95": [mean - half, mean + half] if half is not None else None,
            }
        summary.append(record)
    return summary


def run_one(
    factory, output: Path, data: dict, experiment: str, treatment: str, seed: int
) -> dict:
    data = copy.deepcopy(data)
    data.pop("_runtime", None)
    data["optimization"]["seed"] = seed
    with factory() as db:
        project = create_project(db, f"{experiment}/{treatment}/{seed}")
        for section in SECTIONS:
            project = save_section(
                db, project["id"], section, data[section], project["revision"]
            )
        run = enqueue(db, project["id"])
    began = time.perf_counter()
    assert work_once(factory, output / "artifacts")
    wall_s = time.perf_counter() - began
    with factory() as db:
        saved = get_run(db, run["id"])
        row = {
            "experiment": experiment,
            "treatment": treatment,
            "seed": seed,
            "run_id": saved.id,
            "status": saved.status,
            "error": saved.error,
            "wall_s": wall_s,
            "input_sha256": saved.input_sha256,
            "result_sha256": saved.result_sha256,
            "peak_child_memory_bytes": None,
        }
        if saved.result is not None:
            result = saved.result
            assert canonical_hash(result) == saved.result_sha256
            for stage, source, target in (
                ("T2", "objective", "t2_objective"),
                ("T3", "objective", "t3_objective"),
            ):
                row[target] = result["stages"][stage][source]
            for key in ("mean_distance_m", "mean_wait_s"):
                row[key] = result["stages"]["T4"]["metrics"][key]
            row["selected_candidate"] = result["integrated"]["selected_candidate"]
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="11,23,37,53,71")
    parser.add_argument(
        "--replay",
        type=Path,
        help="Saved input.json; source/dependency identity must match",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    seeds = [int(v) for v in args.seeds.split(",")]
    if len(seeds) != len(set(seeds)):
        raise ValueError("Independent seed identifiers must be unique")
    sample = json.loads(
        (ROOT / "datasets/samples/small_store.json").read_text(encoding="utf-8")
    )
    identity = runtime_identity()
    configuration = {
        "started_utc": datetime.now(UTC).isoformat(),
        "runtime": identity,
        "campaign_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sample_sha256": canonical_hash(sample),
        "seeds": seeds,
        "platform": platform.platform(),
        "data_kind": "SYNTHETIC",
        "model_version": "strip-packing-and-grid-multistart-v1",
        "rights": "Local synthetic fixtures; no real-store data or external usage rights asserted",
        "memory_measurement": "Not instrumented; null rather than parent-process memory proxy",
        "scope": "Small synthetic smoke campaign; insufficient for general scalability or field validity",
    }
    write(output / "configuration.json", configuration)
    engine, factory = connect(database="sr_legacy_campaign_" + hashlib.sha256(str(output.resolve()).encode()).hexdigest()[:24])
    engine.ready()
    rows = []
    scenarios = list(cases(sample))
    if args.replay:
        data = json.loads(args.replay.read_text(encoding="utf-8"))
        if data.get("_runtime") != identity:
            raise ValueError("Replay source/dependencies differ from the saved input")
        scenarios = [("REPLAY", "saved", data)]
        seeds = [data["optimization"]["seed"]]
    try:
        for experiment, treatment, data in scenarios:
            for seed in seeds:
                row = run_one(factory, output, data, experiment, treatment, seed)
                rows.append(row)
                write(output / "runs.json", rows)
                print(experiment, treatment, seed, row["status"], flush=True)
        write(output / "summary.json", summarize(rows))
        write(
            output / "completed.json",
            {
                "ended_utc": datetime.now(UTC).isoformat(),
                "runs": len(rows),
                "succeeded": sum(r["status"] == "SUCCEEDED" for r in rows),
            },
        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
