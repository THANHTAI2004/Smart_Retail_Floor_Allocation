"""Independently audit stored witnesses and compute exploratory paired statistics."""

import argparse
import hashlib
import itertools
import json
import math
import statistics
from pathlib import Path

from scipy.stats import t, ttest_rel
from shapely.geometry import LineString, Polygon
from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import Shelf, ShelfLevel
from smart_retail.engines.t1_layout.engine import footprint
from smart_retail.engines.t1_layout.engine import violations as geometry_errors
from smart_retail.engines.t2_allocation.validation import replay as allocation_replay
from smart_retail.engines.t3_slotting.validation import violations as packing_errors


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit(campaign: Path) -> dict:
    rows = read(campaign / "runs.json")
    successes = 0
    for row in rows:
        folder = campaign / "artifacts" / row["run_id"]
        sections = read(folder / "input.json")
        assert canonical_hash(sections) == row["input_sha256"]
        receipt = read(folder / "receipt.json")
        assert receipt["status"] == row["status"]
        if row["status"] != "SUCCEEDED":
            assert read(folder / "error.json") == row["error"]
            continue
        result = read(folder / "result.json")
        assert (
            canonical_hash(result) == row["result_sha256"] == receipt["result_sha256"]
        )
        assert result["input_sha256"] == row["input_sha256"]
        dataset = to_domain(sections)
        for candidate in result["integrated"]["candidates"]:
            if candidate["status"] != "FEASIBLE":
                continue
            stages = candidate["stages"]
            shelves = tuple(
                Shelf(
                    **{
                        **s,
                        "levels": tuple(ShelfLevel(**level) for level in s["levels"]),
                    }
                )
                for s in stages["T1"]["shelves"]
            )
            assert not geometry_errors(dataset.floorplan, shelves)
            assignment = stages["T2"]["assignment"]
            errors, cost = allocation_replay(
                dataset.floorplan,
                shelves,
                dataset.categories,
                assignment,
                dataset.config.distance_weight,
            )
            assert not errors and math.isclose(
                cost, stages["T2"]["objective"], abs_tol=1e-8
            )
            assert not packing_errors(
                shelves, dataset.products, assignment, tuple(stages["T3"]["placements"])
            )
            metrics = stages["T4"]["metrics"]
            routes = {(r["kind"], r["id"]): r for r in metrics["routes"]}
            for journey in metrics["journeys"]:
                points = routes[journey["kind"], journey["id"]]["points_m"]
                assert (
                    tuple(points[0]) == tuple(points[-1]) == dataset.floorplan.entrance
                )
                distance = 0.0
                for a, b in itertools.pairwise(points):
                    distance += math.dist(a, b)
                    if a == b:
                        continue
                    segment = LineString([a, b])
                    assert Polygon(dataset.floorplan.boundary).covers(segment)
                    assert all(not segment.intersects(footprint(s)) for s in shelves)
                    assert all(
                        not segment.intersects(Polygon(o))
                        for o in dataset.floorplan.obstacles
                    )
                assert math.isclose(distance, journey["distance_m"], abs_tol=1e-7)
                quantity = sum(p["quantity"] for p in journey["picks"])
                elapsed = (
                    distance / dataset.demand.behavior.speed_m_s
                    + quantity * dataset.demand.behavior.dwell_s
                    + journey["wait_s"]
                )
                assert math.isclose(elapsed, journey["elapsed_s"], abs_tol=1e-7)
                if journey["kind"] == "picker":
                    expected = {
                        line.sku: line.quantity
                        for line in dataset.order_lines
                        if line.order_id == journey["id"]
                    }
                    assert expected == {
                        p["sku"]: p["quantity"] for p in journey["picks"]
                    }
        successes += 1
    return {
        "runs_audited": len(rows),
        "successful_runs_audited": successes,
        "checks": [
            "input/result/receipt checksums",
            "all feasible candidate geometry",
            "independent T2 constraints/objective",
            "independent T3 physical replay",
            "all T4 route segments, distance, elapsed time and order quantities",
        ],
    }


def paired(rows: list[dict]) -> list[dict]:
    comparisons = []
    for experiment in sorted({r["experiment"] for r in rows}):
        arms = {
            arm: {
                r["seed"]: r
                for r in rows
                if r["experiment"] == experiment
                and r["treatment"] == arm
                and r["status"] == "SUCCEEDED"
            }
            for arm in ("baseline", "treatment")
        }
        seeds = sorted(arms["baseline"].keys() & arms["treatment"].keys())
        for metric in ("mean_distance_m", "mean_wait_s", "wall_s"):
            record = {
                "experiment": experiment,
                "metric": metric,
                "paired_seeds": seeds,
                "n": len(seeds),
                "mean_treatment_minus_baseline": None,
                "ci95": None,
                "exploratory_p": None,
                "holm_p": None,
            }
            if len(seeds) >= 2:
                a, b = [
                    [arms[arm][seed][metric] for seed in seeds]
                    for arm in ("baseline", "treatment")
                ]
                differences = [y - x for x, y in zip(a, b)]
                mean, sd = statistics.mean(differences), statistics.stdev(differences)
                half = float(t.ppf(0.975, len(seeds) - 1)) * sd / len(seeds) ** 0.5
                record.update(
                    mean_treatment_minus_baseline=mean, ci95=[mean - half, mean + half]
                )
                if sd > 1e-10:
                    record["exploratory_p"] = float(ttest_rel(b, a).pvalue)
                else:
                    record["test_limitation"] = (
                        "Constant paired differences; no t-test inference reported"
                    )
            comparisons.append(record)
    tested = sorted(
        (r for r in comparisons if r["exploratory_p"] is not None),
        key=lambda r: r["exploratory_p"],
    )
    previous = 0.0
    for rank, record in enumerate(tested):
        previous = max(previous, min(1, (len(tested) - rank) * record["exploratory_p"]))
        record["holm_p"] = previous
    return comparisons


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    target = args.campaign / "analysis.json"
    if target.exists():
        raise FileExistsError(
            "Analysis already exists; preserve it and use a new campaign/version"
        )
    result = {
        "audit": audit(args.campaign),
        "paired": paired(read(args.campaign / "runs.json")),
        "interpretation": "Exploratory five-seed synthetic probes; no generalization or field validity claim",
    }
    if args.replay:
        replay = read(args.replay / "runs.json")[0]
        originals = read(args.campaign / "runs.json")
        original = next(
            row
            for row in originals
            if row["input_sha256"] == replay["input_sha256"]
            and row["result_sha256"] == replay["result_sha256"]
        )
        result["replay"] = {
            "original_run": original["run_id"],
            "new_run": replay["run_id"],
            "identical_input_and_result_checksums": True,
        }
        result["replay_audit"] = audit(args.replay)
    result["artifact_sha256"] = {
        p.relative_to(args.campaign).as_posix(): hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
        for p in sorted(args.campaign.rglob("*.json"))
    }
    target.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps({"audit": result["audit"], "replay": result.get("replay")}, indent=2)
    )


if __name__ == "__main__":
    main()
