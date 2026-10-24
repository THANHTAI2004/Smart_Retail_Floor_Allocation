"""Run the direction-A paper campaigns sequentially, resumably, then pool reports per block.

Order follows docs/research/EXPERIMENT_DESIGN_DEEPMG.md section 8 (X3 last). Each campaign
is resumed when its directory exists and is not COMPLETED; reports are written once into
new directories. The journal records every attempt with UTC times and final status.
Do not edit Python source under backend/src while this runs: the drift guard stops it.
"""

import json
import traceback
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from smart_retail.application.experiments.campaign import run
from smart_retail.application.experiments.reports import report
from smart_retail.contracts.experiments import CampaignSpec

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
CONFIGS = ROOT / "experiments" / "configs" / "paper-v2"
RESULTS = ROOT / "experiments" / "results" / "20261023-paper-v2"
REPORTS = ROOT / "experiments" / "reports" / "20261023-paper-v2"
JOURNAL = RESULTS / "journal.json"
ORDER = ["X1", "X4", "X2", "X2b", "X5", "X6", "X3"]


def now():
    return datetime.now(UTC).isoformat()


def record(journal, entry):
    journal.append(entry)
    JOURNAL.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    journal = json.loads(JOURNAL.read_text(encoding="utf-8")) if JOURNAL.exists() else []
    index = json.loads((CONFIGS / "index.json").read_text(encoding="utf-8"))
    blocks = defaultdict(list)
    for row in index:
        blocks[row["block"]].append(row["config"])
    for block in ORDER:
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
    for block in ORDER:
        target = REPORTS / block
        if target.exists():
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
