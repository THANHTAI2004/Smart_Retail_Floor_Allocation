"""Paper-v3 campaigns: three slots, drain third above 90% RAM, restore below 80%."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from build_x1_union_configs import build_union, phase1_roots
from paper_resource_guard import Sampler

from smart_retail.application.experiments.reports import report
from smart_retail.application.experiments.storage import read, verify_integrity, write
from smart_retail.contracts.experiments import CampaignSpec
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.workers.resources import is_alive

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["X1", "X1b", "X4", "X2", "X5", "X6", "X3"]


def now():
    return datetime.now(UTC).isoformat()


def desired_slots(current, ram):
    if ram > 90:
        return 2
    if ram < 80:
        return 3
    return current


def load_spec(path):
    spec = CampaignSpec.model_validate(read(path))
    if spec.memory_limit_mb is not None:
        raise ValueError(f"Expected unlimited RSS: {path}")
    return spec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configs", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--generated-time-multiplier", type=int, choices=(1, 2), default=1,
                        help="Time multiplier for newly built X1b configs; input configs are already scaled")
    args = parser.parse_args()
    configs, results, reports, state = (
        p.resolve() for p in (args.configs, args.results, args.reports, args.state)
    )
    rows = read(configs / "index.json")
    for row in rows:
        load_spec(configs / row["config"])
    if args.check_only:
        print(json.dumps({"campaigns": len(rows), "jobs": sum(r["jobs"] for r in rows),
                          "memory_limit_mb": None, "slots": 3, "down_above": 90,
                          "up_below": 80}))
        return
    state.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)
    lock = state / "runner.lock.json"
    if lock.exists() and is_alive(read(lock)["pid"]):
        raise RuntimeError("Adaptive coordinator already running")
    if any(is_alive(read(p)["pid"]) for p in results.glob("*/.supervisor.lock")):
        raise RuntimeError("Existing campaign supervisors must finish before restart")
    lock.unlink(missing_ok=True)
    write(lock, {"pid": os.getpid(), "started_utc": now()}, immutable=True)
    baseline = runtime_identity()
    identity_file = state / "runtime.json"
    if identity_file.exists() and read(identity_file) != baseline:
        raise RuntimeError("Runtime changed; use a new results directory")
    if not identity_file.exists():
        write(identity_file, baseline, immutable=True)
    journal_path = state / "journal.json"
    journal = read(journal_path) if journal_path.exists() else []
    sampler, slots, active = Sampler(), 3, {}
    last_sample, resources = 0.0, {}

    def event(**entry):
        journal.append({"utc": now(), **entry})
        write(journal_path, journal)
        print(now(), json.dumps(entry), flush=True)

    try:
        for block in ORDER:
            rows = read(configs / "index.json")
            if block == "X1b" and not any(r["block"] == block for r in rows):
                # No generation until every heuristic phase-1 campaign is complete.
                built = build_union(phase1_roots(results), configs)
                for row in built:
                    path = configs / row["config"]
                    data = read(path)
                    data["memory_limit_mb"] = None
                    data["job_time_limit_s"] *= args.generated_time_multiplier
                    data["max_wall_s"] *= args.generated_time_multiplier
                    CampaignSpec.model_validate(data)
                    write(path, data)
                # Keep the generated index metadata synchronized with the effective configs.
                index = read(configs / "index.json")
                for row in index:
                    row["job_time_limit_s"] = read(configs / row["config"])["job_time_limit_s"]
                write(configs / "index.json", index)
                rows = read(configs / "index.json")
                event(action="BUILD_X1B", campaigns=len(built))
            pending = []
            for row in rows:
                if row["block"] != block:
                    continue
                spec = load_spec(configs / row["config"])
                checkpoint = results / spec.name / "checkpoint.json"
                if checkpoint.exists() and read(checkpoint)["status"] in (
                    "COMPLETED", "NOT_EXECUTED_RESOURCE_LIMIT"
                ):
                    continue
                pending.append(row)
            while pending or active:
                if (state / "stop.request").exists():
                    # Drain every active slice/campaign; never cancel a running job.
                    pending.clear()
                if time.monotonic() - last_sample >= 5:
                    if runtime_identity() != baseline:
                        raise RuntimeError("Source/dependency drift; admission stopped")
                    resources = sampler.sample()
                    new_slots = desired_slots(slots, resources["ram_percent"])
                    if new_slots != slots:
                        event(action="SLOTS_CHANGED", previous=slots, slots=new_slots,
                              resources=resources)
                    slots, last_sample = new_slots, time.monotonic()
                for pid, item in list(active.items()):
                    code = item["process"].poll()
                    if code is None:
                        continue
                    item["stream"].close()
                    checkpoint = read(item["root"] / "checkpoint.json") if (
                        item["root"] / "checkpoint.json"
                    ).exists() else {}
                    for name, digest in item["before"].items():
                        if hashlib.sha256((item["root"] / "records" / name).read_bytes()).hexdigest() != digest:
                            raise RuntimeError("Previously completed record was changed")
                    status = checkpoint.get("status")
                    event(action="EXIT", campaign=item["root"].name, pid=pid,
                          exit_code=code, checkpoint=checkpoint)
                    del active[pid]
                    if code != 0 or status not in (
                        "COMPLETED", "PAUSED_PARTIAL", "NOT_EXECUTED_RESOURCE_LIMIT"
                    ):
                        raise RuntimeError(f"Campaign failed; inspect {item['log']}")
                    if status == "PAUSED_PARTIAL" and not (state / "stop.request").exists():
                        pending.insert(0, item["row"])
                while pending and len(active) < slots:
                    row = pending.pop(0)
                    spec = load_spec(configs / row["config"])
                    root = results / spec.name
                    # Two continuous campaigns; optional third yields at each job boundary.
                    sliced = len(active) >= 2
                    command = [sys.executable, "-u", "-m",
                               "smart_retail.application.experiments.cli",
                               "resume" if root.exists() else "run", "--config",
                               str(configs / row["config"]), "--output", str(root)]
                    if sliced:
                        command += ["--max-new-jobs", "1"]
                    log = state / f"{spec.name}-{time.time_ns()}.log"
                    stream = log.open("xb")
                    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (root / "records").glob("*.json")}
                    try:
                        process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                                   stdout=stream, stderr=stream,
                                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
                    except Exception:
                        stream.close()
                        raise
                    active[process.pid] = {"process": process, "stream": stream,
                                           "root": root, "row": row, "before": before,
                                           "sliced": sliced, "log": str(log)}
                    event(action="START", campaign=spec.name, pid=process.pid,
                          optional_one_job_slice=sliced, log=str(log))
                write(state / "status.json", {"status": "RUNNING", "updated_utc": now(),
                      "block": block, "slots": slots, "resources": resources,
                      "memory_limit_mb": None, "active": [
                          {"pid": pid, "campaign": v["root"].name,
                           "optional_one_job_slice": v["sliced"]} for pid, v in active.items()],
                      "pending": len(pending)})
                if active:
                    time.sleep(1)
            if (state / "stop.request").exists():
                event(action="DRAINED_STOP")
                return
        # Verify all evidence, then pool X1 heuristics and exact-on-union together.
        rows = read(configs / "index.json")
        for block in (b for b in ORDER if b != "X1b"):
            selected = [r for r in rows if r["block"] in ({"X1", "X1b"} if block == "X1" else {block})]
            roots = [results / load_spec(configs / r["config"]).name for r in selected]
            for root in roots:
                verify_integrity(root)
            if not (reports / block).exists():
                report(roots, reports / block)
            event(action="VERIFIED_REPORTED", block=block)
        write(state / "finished.json", {"status": "COMPLETED", "ended_utc": now()})
    except BaseException as exc:
        write(state / "error.json", {"error": f"{type(exc).__name__}: {exc}", "utc": now(),
                                    "active_pids": list(active)})
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
