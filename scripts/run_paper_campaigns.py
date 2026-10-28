"""Run the direction-A paper campaigns sequentially, resumably, then pool reports per block.

Order follows docs/research/EXPERIMENT_DESIGN_DEEPMG.md section 8 (X3 last). Each campaign
is resumed when its directory exists and is not COMPLETED; reports are written once into
new directories. The journal records every attempt with UTC times and final status.
Do not edit Python source under backend/src while this runs: the drift guard stops it.
"""

import argparse
import json
import traceback
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from build_x1_union_configs import build_union, phase1_roots

from smart_retail.application.experiments.campaign import run
from smart_retail.application.experiments.reports import report
from smart_retail.contracts.experiments import CampaignSpec

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
# Block order per config set. paper-v4 runs the diagnostic designs (step/guidance,
# ablation, budget) before the confirmatory main comparison V1.
SETS = {
    "paper-v3": ["X1", "X1b", "X4", "X2", "X5", "X6", "X3"],
    "paper-v4": ["V2", "V4", "V3", "V1", "VL", "V5"],
}
CONFIGS = ROOT / "experiments" / "configs" / "paper-v3"
RESULTS = ROOT / "experiments" / "results" / "paper-v3"
REPORTS = ROOT / "experiments" / "reports" / "paper-v3"
JOURNAL = RESULTS / "journal.json"
ORDER = SETS["paper-v3"]


def select(name):
    """Point configs, results, reports, journal and block order at one config set."""
    global CONFIGS, RESULTS, REPORTS, JOURNAL, ORDER
    CONFIGS = ROOT / "experiments" / "configs" / name
    RESULTS = ROOT / "experiments" / "results" / name
    REPORTS = ROOT / "experiments" / "reports" / name
    JOURNAL = RESULTS / "journal.json"
    ORDER = SETS[name]


def now():
    return datetime.now(UTC).isoformat()


def record(journal, entry):
    journal.append(entry)
    JOURNAL.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")


def load_blocks():
    blocks = defaultdict(list)
    for row in json.loads((CONFIGS / "index.json").read_text(encoding="utf-8")):
        blocks[row["block"]].append(row["config"])
    return blocks


def prepare_union(journal):
    """Build X1b once every phase-1 X1 campaign is COMPLETED (journaled either way)."""
    entry = {"block": "X1b", "action": "build_union", "started_utc": now()}
    try:
        entry["configs"] = build_union(phase1_roots(RESULTS), CONFIGS)
        entry["status"] = "BUILT"
    except SystemExit as exc:
        entry.update(status="NOT_BUILT", reason=str(exc))
    except Exception as exc:  # noqa: BLE001 - journal every failure, continue with next block
        entry.update(status="BUILD_ERROR", error=f"{type(exc).__name__}: {exc}", trace=traceback.format_exc())
    entry["ended_utc"] = now()
    record(journal, entry)
    print(f"[{now()}] X1b union configs: {entry['status']}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", choices=sorted(SETS), default="paper-v3", help="config set to run")
    select(parser.parse_args().set)
    RESULTS.mkdir(parents=True, exist_ok=True)
    journal = json.loads(JOURNAL.read_text(encoding="utf-8")) if JOURNAL.exists() else []
    for block in ORDER:
        blocks = load_blocks()
        if block == "X1b" and not blocks["X1b"]:
            prepare_union(journal)
            blocks = load_blocks()
        for name in blocks[block]:
            spec = CampaignSpec.model_validate(
                json.loads((CONFIGS / name).read_text(encoding="utf-8"))
            )
            output = RESULTS / spec.name
            checkpoint = output / "checkpoint.json"
            if checkpoint.exists():
                state = json.loads(checkpoint.read_text(encoding="utf-8"))
                if state["status"] == "COMPLETED":
                    continue
            entry = {"block": block, "config": name, "output": str(output), "started_utc": now()}
            print(f"[{now()}] {block} {name}", flush=True)
            try:
                state = run(spec, output, resume=output.exists())
                entry.update(status=state["status"], completed=state["completed"], planned=state["planned"])
            except Exception as exc:  # noqa: BLE001 - journal every failure, continue with next campaign
                entry.update(status="SUPERVISOR_ERROR", error=f"{type(exc).__name__}: {exc}", trace=traceback.format_exc())
            entry["ended_utc"] = now()
            record(journal, entry)
            print(f"[{now()}] {name}: {entry['status']}", flush=True)
    blocks = load_blocks()
    # Heuristic (X1) and exact-on-union (X1b) jobs share experiment ids and seeds: pool them.
    blocks["X1"] = blocks["X1"] + blocks.pop("X1b", [])
    for block in ORDER:
        target = REPORTS / block
        if block == "X1b" or target.exists():
            continue
        roots = [
            RESULTS / json.loads((CONFIGS / name).read_text(encoding="utf-8"))["name"]
            for name in blocks[block]
        ]
        roots = [r for r in roots if (r / "records").exists()]
        entry = {"block": block, "report": str(target), "campaigns": [r.name for r in roots], "started_utc": now()}
        try:
            entry["result"] = report(roots, target)
            entry["status"] = "REPORTED"
        except Exception as exc:  # noqa: BLE001 - journal every failure, continue with next block
            entry.update(status="REPORT_ERROR", error=f"{type(exc).__name__}: {exc}", trace=traceback.format_exc())
        entry["ended_utc"] = now()
        record(journal, entry)
        print(f"[{now()}] report {block}: {entry['status']}", flush=True)


if __name__ == "__main__":
    main()
