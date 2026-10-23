"""Bounded numerical, dependency and resource probes; only isolated audit databases."""

import argparse
import copy
import json
import math
import time
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from smart_retail.application import projects
from smart_retail.application.experiments.generators import generate
from smart_retail.application.experiments.storage import write
from smart_retail.application.feedback.diagnostics import analyze
from smart_retail.application.feedback.evaluator import evaluate
from smart_retail.application.feedback.neighborhood import actions
from smart_retail.application.workflow import execute
from smart_retail.contracts.experiments import DatasetSpec
from smart_retail.contracts.feedback import JointConfig
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError
from smart_retail.engines.t1_layout.engine import solve as layout
from smart_retail.engines.t1_layout.engine import violations
from smart_retail.infrastructure.mongodb.client import connect
from smart_retail.infrastructure.mongodb.serializers import sha
from smart_retail.workers.runner import work_once

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def feedback(output):
    sections = load(ROOT / "datasets/joint/two-shelves.json")
    config = JointConfig(
        mode="feedback",
        max_actions=100,
        max_evaluations=60,
        finite_space=load(ROOT / "datasets/joint/two-shelves-space.json"),
    )
    sections["optimization"]["joint"] = config.model_dump(mode="json")
    cache = {}

    def assess(decision):
        return evaluate(
            sections,
            config,
            decision,
            time.monotonic() + 30,
            lambda: False,
            lambda _: None,
            cache,
            lambda *args: None,
        )

    initial = assess(None)
    write(output / "feedback-initial.json", initial, immutable=True)
    proposals = actions(initial, analyze(initial, sections), sections, config)
    results = []
    for layer, field in [("T1", "poses"), ("T2", "assignment"), ("T3", "placements")]:
        for action in proposals:
            if action["layer"] != layer:
                continue
            try:
                candidate = assess(action["decisions"])
            except EngineError:
                continue
            if candidate["decisions"][field] == initial["decisions"][field]:
                continue
            invalidated = []
            for stage in ["T1", "T2", "T3", "T4"]:
                if (
                    candidate["result"]["stage_cache"][stage]["key"]
                    != initial["result"]["stage_cache"][stage]["key"]
                ):
                    invalidated.append(stage)
            assert (
                invalidated
                == {
                    "T1": ["T1", "T2", "T3", "T4"],
                    "T2": ["T2", "T3", "T4"],
                    "T3": ["T3", "T4"],
                }[layer]
            )
            assert candidate["validation"] == "PASS"
            write(
                output / f"feedback-action-{layer}.json",
                {"action": action, "candidate": candidate},
                immutable=True,
            )
            results.append(
                {
                    "layer": layer,
                    "type": action["type"],
                    "actual_decision_changed": True,
                    "invalidated": invalidated,
                    "before_score": initial["score"],
                    "after_score": candidate["score"],
                    "validation": "PASS",
                    "before_sha": sha(initial["decisions"]),
                    "after_sha": sha(candidate["decisions"]),
                }
            )
            break
        else:
            raise AssertionError("No feasible actual action for " + layer)
    same = assess(initial["decisions"])
    assert same["id"] == initial["id"]
    policy = copy.deepcopy(initial["decisions"])
    policy["routing_policy"] = "return"
    changed = assess(policy)
    assert (
        changed["result"]["stage_cache"]["T4"]["key"]
        != initial["result"]["stage_cache"]["T4"]["key"]
    )
    loop = execute(sections)
    joint = loop["joint"]
    iterations = sorted({e["iteration"] for e in joint["trace"] if e.get("iteration", 0) > 0})
    assert len(iterations) >= 2
    accepted = [e for e in joint["trace"] if e.get("accepted")]
    assert accepted and all(e["after"] < e["before"] - config.tolerance for e in accepted)
    assert joint["evaluations"] <= config.max_evaluations
    write(output / "feedback-multiloop.json", loop, immutable=True)
    plateau = load(ROOT / "datasets/joint/local-trap.json")
    plateau["optimization"]["joint"] = JointConfig(layers=["T3"], max_iterations=4).model_dump(
        mode="json"
    )
    no_improve = execute(plateau)["joint"]
    assert no_improve["status"] == "CONVERGED_LOCAL"
    write(
        output / "feedback-summary.json",
        {
            "status": "PASS",
            "actions": results,
            "iterations": iterations,
            "evaluations": joint["evaluations"],
            "accepted": len(accepted),
            "initial_score": joint["initial_score"],
            "final_score": joint["best"]["score"],
            "termination": joint["status"],
            "no_improvement_stop": no_improve["status"],
            "global_optimality_claimed": False,
        },
        immutable=True,
    )


def engine_checks(output):
    sections = load(ROOT / "datasets/samples/small_store.json")
    d = to_domain(sections)
    cases = []
    baseline = layout(d.floorplan, d.shelves, "optimizable", deadline=time.monotonic() + 10)
    assert not violations(d.floorplan, baseline.shelves)
    for name, floor, shelves, mode in [
        ("tiny", d.floorplan, d.shelves, "optimizable"),
        (
            "obstacle",
            replace(
                d.floorplan,
                obstacles=(((0.1, 0.1), (0.4, 0.1), (0.4, 0.4), (0.1, 0.4)),),
            ),
            d.shelves,
            "optimizable",
        ),
        (
            "fixed",
            d.floorplan,
            tuple(replace(s, locked=True) for s in baseline.shelves),
            "fixed",
        ),
        ("multiple", d.floorplan, d.shelves, "optimizable"),
    ]:
        began = time.monotonic()
        value = layout(floor, shelves, mode, deadline=time.monotonic() + 10)
        assert not violations(floor, value.shelves)
        if name == "fixed":
            assert value.shelves == shelves
        cases.append(
            {
                "case": name,
                "wall_s": time.monotonic() - began,
                "result": asdict(value),
                "violations": [],
            }
        )
    impossible = tuple(replace(s, width_m=10000, depth_m=10000) for s in d.shelves)
    try:
        layout(
            d.floorplan,
            impossible,
            "optimizable",
            deadline=time.monotonic() + 2,
            max_iterations=100,
        )
    except EngineError as exc:
        cases.append(
            {
                "case": "oversize-no-layout",
                "engine_status": exc.code,
                "independent_reason": "Both footprint dimensions exceed all store spans; no 0/90 pose can fit",
                "heuristic_failure_not_labeled_proof": True,
            }
        )
    else:
        raise AssertionError("Oversized shelves accepted")
    sample = copy.deepcopy(sections)
    sample["demand"]["customers"] = 0
    result = execute(sample)
    metric = result["stages"]["T4"]["metrics"]
    journey = metric["journeys"][0]
    points = metric["routes"][0]["points_m"]
    distance = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
    assert math.isclose(distance, journey["distance_m"])
    assert {p["sku"]: p["quantity"] for p in journey["picks"]} == {
        "WATER": 3,
        "RICE": 2,
    }
    expected = distance / 1.2 + 5 * 4
    assert math.isclose(journey["elapsed_s"], expected)
    write(
        output / "manual-route.json",
        {
            "status": "PASS",
            "points": points,
            "independent_distance_m": distance,
            "independent_elapsed_s": expected,
            "journey": journey,
            "assumptions": "No customers; one picker order, speed 1.2 m/s, 5 units x 4 s/unit",
        },
        immutable=True,
    )
    write(output / "t1-fixtures.json", {"status": "PASS", "cases": cases}, immutable=True)


def performance(output, prefix):
    store, factory = connect(database=prefix + uuid4().hex[:12] + "_performance")
    store.ready()
    records = []
    for scale in ["tiny", "small", "medium"]:
        sections, manifest = generate(DatasetSpec(id=scale, scale=scale, seed=101))
        sections["optimization"]["time_limit_s"] = 20
        p = projects.create_project(store, "Bounded audit " + scale)
        for section, value in sections.items():
            p = projects.save_section(store, p["id"], section, value, p["revision"])
        latency = []
        for _ in range(20):
            t = time.perf_counter()
            store.get_project(p["id"])
            latency.append(time.perf_counter() - t)
        t = time.monotonic()
        job = projects.enqueue(store, p["id"])
        queued = time.monotonic()
        assert work_once(
            factory, output / "performance-artifacts", heartbeat_id="audit-performance"
        )
        final = store.get_run(job["id"])
        directory = output / "performance-artifacts" / job["id"]
        r = load(directory / "receipt.json")
        assert final.status == "SUCCEEDED" and final.started_epoch is not None
        stages = [load(p) for p in sorted((directory / "stages").glob("*.json"))]
        record = {
            "scale": scale,
            "database": store.settings.database,
            "run_id": job["id"],
            "status": final.status,
            "error": final.error,
            "wall_s": time.monotonic() - t,
            "enqueue_s": queued - t,
            "queue_delay_s": final.started_epoch
            - datetime.fromisoformat(final.created_at).timestamp(),
            "query_target": "projects by id",
            "query_mean_s": sum(latency) / len(latency),
            "query_max_s": max(latency),
            "receipt": r,
            "stages": [
                {
                    "stage": s["stage"],
                    "elapsed_s": s["elapsed_s"],
                    "cache_hit": s["cache_hit"],
                }
                for s in stages
            ],
            "artifact_bytes": sum(p.stat().st_size for p in directory.rglob("*") if p.is_file()),
            "dataset": manifest["counts"],
        }
        records.append(record)
        print("bounded performance", scale, final.status, flush=True)
    write(
        output / "performance.json",
        {
            "status": "PASS",
            "scope": "Three bounded queued jobs; not a long-duration leak/load study",
            "records": records,
            "large": "NOT_APPLICABLE: bounded audit avoids uncontrolled load",
        },
        immutable=True,
    )
    store.dispose()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    engine_checks(args.output)
    print("engine/manual route PASS", flush=True)
    feedback(args.output)
    print("actual feedback/recomputation PASS", flush=True)
    performance(args.output, args.prefix)


if __name__ == "__main__":
    main()
