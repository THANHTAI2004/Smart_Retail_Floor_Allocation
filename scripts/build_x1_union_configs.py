"""X1 phase 2: exact search over the union of phase-1 heuristic solutions (paper-v3).

Phase 1 (paper-x1-tiny*) runs seq_milp, random_search, annealing and feedback. This
script verifies those completed campaigns, collects every successful best decision per
instance (all arms, all seeds) and declares one bundled finite space per instance:
distinct layouts x distinct allocations x routing policies. The exact arm uses the same
experiment ids, seeds and objective as phase 1, so a pooled report pairs heuristic and
exact jobs on identical (instance, seed) units. Configs are appended to index.json as
block X1b; existing files are never replaced.

Usage: python scripts/build_x1_union_configs.py  (the paper runner calls build_union itself)
"""

import copy
import json
import sys
from collections import defaultdict
from pathlib import Path

from build_paper_configs import JOINT_METRICS, OUT, arm, campaign, experiment, finalize

from smart_retail.application.experiments.finite_spaces import union_space
from smart_retail.application.experiments.storage import verify_integrity
from smart_retail.contracts.experiments import planned_jobs

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results" / "paper-v3"
PHASE1 = "paper-x1-tiny"
NAME = "paper-x1-tiny-exact"
# Exact enumerates every state and the verifier re-evaluates every leaf.
STATE_CAP = 400


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def phase1_roots(results=RESULTS):
    return sorted(
        p for p in results.glob(f"{PHASE1}*") if p.is_dir() and not p.name.startswith(NAME)
    )


def build_union(roots, out=OUT):
    index_path = out / "index.json"
    index = read(index_path)
    if any(row["block"] == "X1b" for row in index):
        raise SystemExit("X1b configs already exist; refusing to replace them")
    if not roots:
        raise SystemExit("No phase-1 X1 campaigns found")
    datasets: dict[str, dict] = {}
    experiments: dict[str, str] = {}
    seeds: set[int] = set()
    decisions: dict[str, list[dict]] = defaultdict(list)
    for root in roots:
        if read(root / "checkpoint.json")["status"] != "COMPLETED":
            raise SystemExit(f"{root.name} is not COMPLETED; phase 2 needs every phase-1 job")
        verify_integrity(root)
        configuration = read(root / "configuration.json")
        seeds.update(configuration["seeds"])
        for item in configuration["datasets"]:
            datasets[item["id"]] = item
        for e in configuration["experiments"]:
            for dataset_id in e["datasets"]:
                experiments[dataset_id] = e["id"]
        for path in sorted((root / "records").glob("*.json")):
            record = read(path)
            if record["status"] != "SUCCEEDED":
                continue
            best = (read(root / "artifacts" / record["run_id"] / "result.json").get("joint") or {}).get("best")
            if best:
                decisions[record["dataset"]].append(best["decisions"])
    # One campaign per instance: the space is instance-specific, while the experiment id
    # must equal phase 1 so the pooled report pairs exact with every heuristic.
    evidence, specs = {}, []
    for dataset_id in sorted(decisions):
        space, info = union_space(decisions[dataset_id])
        if info["states"] > STATE_CAP:
            raise SystemExit(f"{dataset_id}: union space has {info['states']} states (cap {STATE_CAP})")
        evidence[dataset_id] = info
        treatment = arm("exact", info["states"], mode="exact", finite_space=space)
        item = datasets[dataset_id]
        specs.append(campaign(
            f"{NAME}-{dataset_id}", [item],
            [experiment(experiments[dataset_id], "Gap between heuristics and the certified optimum of the union of their own solutions", [item], [treatment], JOINT_METRICS)],
            sorted(seeds), 900))
        print(dataset_id, info, flush=True)
    rows = []
    for spec in specs:
        for part in finalize(spec):
            path = out / f"{part.name}.json"
            if path.exists():
                raise SystemExit(f"{path} exists; refusing to replace it")
            path.write_text(json.dumps(part.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8")
            rows.append({"block": "X1b", "config": path.name, "jobs": planned_jobs(part), "job_time_limit_s": part.job_time_limit_s})
    (out / "x1-union-spaces.json").write_text(
        json.dumps({"phase1": [r.name for r in roots], "spaces": evidence}, indent=2) + "\n", encoding="utf-8"
    )
    index_path.write_text(json.dumps(index + rows, indent=2) + "\n", encoding="utf-8")
    return copy.deepcopy(rows)


def main():
    rows = build_union(phase1_roots())
    for row in rows:
        print(row)


if __name__ == "__main__":
    sys.exit(main())
