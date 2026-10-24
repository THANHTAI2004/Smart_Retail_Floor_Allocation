"""Adaptive two/three isolated campaigns; X3 last; unchanged scientific source."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from paper_recovery import prepare_recovery, supplemental_rows
from paper_resource_guard import Guard, Sampler, resource_failure
from smart_retail.application.experiments.storage import read, write
from smart_retail.contracts.experiments import CampaignSpec
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.workers.resources import is_alive

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
CONFIGS = ROOT / "experiments/configs/paper-v2"
RESULTS = ROOT / "experiments/results/20261023-paper-v2"
STATE = ROOT / "var/paper-parallel"
ORDER = ["X1", "X4", "X2", "X2b", "X5", "X6", "X3"]
GROUPS = [["X1"], ["X4"], ["X2", "X2b"], ["X5"], ["X6", "RECOVERY"], ["X3"]]
CONTROL = STATE / "concurrency.json"


def now():
    return datetime.now(UTC).isoformat()


def available_slots(active, limit=2):
    if limit not in (2, 3):
        raise ValueError("Only two or three campaign slots are authorized")
    return max(0, limit - len(active))


def concurrency():
    value = read(CONTROL)["slots"] if CONTROL.exists() else 2
    available_slots([], value)
    return value


def record_files():
    return list(RESULTS.glob("*/records/*.json"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--adopt-existing", action="store_true")
    args = parser.parse_args()
    baseline = read(ROOT / "var/continue-20261023-01/preflight.json")["runtime"]
    if runtime_identity() != baseline:
        raise RuntimeError("Source/dependency drift; refuse mixed-source execution")
    if not args.check_only:
        prepare_recovery()
    rows = read(CONFIGS / "index.json") + supplemental_rows()
    if args.check_only:
        print(
            json.dumps(
                {
                    "slots": concurrency(),
                    "groups": GROUPS,
                    "campaigns": len(rows),
                    "jobs": sum(r["jobs"] for r in rows),
                }
            )
        )
        return
    STATE.mkdir(parents=True, exist_ok=True)
    lock = STATE / "runner.lock.json"
    if lock.exists():
        if is_alive(read(lock)["pid"]):
            raise RuntimeError("Parallel coordinator already running")
        lock.unlink()
    write(lock, {"pid": os.getpid(), "started_utc": now()}, immutable=True)
    journal_file = STATE / "journal.json"
    journal = read(journal_file) if journal_file.exists() else []
    active = {}
    sampler, guard = Sampler(), Guard()
    seen_records = {str(path) for path in record_files()}
    last_sample = 0.0
    measurement = {}
    try:
        if args.adopt_existing:
            for path in RESULTS.glob("*/.supervisor.lock"):
                owner = read(path)["pid"]
                if not is_alive(owner):
                    continue
                root = path.parent
                entry = next(
                    (
                        e
                        for e in reversed(journal)
                        if e["campaign"] == root.name and e["status"] == "RUNNING"
                    ),
                    None,
                )
                if entry is None:
                    raise RuntimeError("Live campaign missing from schedule journal")
                pid = entry["pid"] if is_alive(entry["pid"]) else owner
                for name, expected in entry["existing_record_sha256"].items():
                    if (
                        hashlib.sha256(
                            (root / "records" / name).read_bytes()
                        ).hexdigest()
                        != expected
                    ):
                        raise RuntimeError("Historical record changed before adoption")
                entry["existing_record_sha256"] = {
                    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (root / "records").glob("*.json")
                }
                entry["adopted_utc"] = now()
                active[pid] = (None, root, entry)
            write(journal_file, journal)
        elif any(is_alive(read(p)["pid"]) for p in RESULTS.glob("*/.supervisor.lock")):
            raise RuntimeError("Live supervisors require explicit adoption")
        for group in GROUPS:
            block = "+".join(group)
            pending = []
            for row in rows:
                if row["block"] not in group:
                    continue
                spec = CampaignSpec.model_validate(read(CONFIGS / row["config"]))
                checkpoint = RESULTS / spec.name / "checkpoint.json"
                if checkpoint.exists() and read(checkpoint)["status"] == "COMPLETED":
                    continue
                if (
                    checkpoint.exists()
                    and read(checkpoint)["status"] == "NOT_EXECUTED_RESOURCE_LIMIT"
                ):
                    # Original budgets are immutable; supplemental shards own omitted keys.
                    continue
                if any(v[1].name == spec.name for v in active.values()):
                    continue
                pending.append((row, spec))
            # Earlier groups may be complete while live adopted owners belong to X2.
            if not pending and not any(v[2]["block"] in group for v in active.values()):
                continue
            while pending or any(v[2]["block"] in group for v in active.values()):
                if runtime_identity() != baseline:
                    raise RuntimeError(
                        "Source/dependency changed during parallel schedule"
                    )
                limit = concurrency()
                if time.monotonic() - last_sample >= 5:
                    measurement = sampler.sample()
                    failure = False
                    for path in record_files():
                        if str(path) not in seen_records:
                            failure |= resource_failure(
                                read(path), measurement["cpu_percent"]
                            )
                            seen_records.add(str(path))
                    reason = guard.reason(measurement, failure)
                    if limit == 3 and reason:
                        limit = 2
                        write(
                            CONTROL,
                            {
                                "slots": 2,
                                "latched": True,
                                "reason": reason,
                                "updated_utc": now(),
                                "measurement": measurement,
                                "drain": "Optional third campaign finishes its current one-job slice; no running job is cancelled.",
                            },
                        )
                        print(now(), "FALLBACK_TO_TWO", reason, flush=True)
                    last_sample = time.monotonic()
                while pending and available_slots(active, limit):
                    row, spec = pending.pop(0)
                    root = RESULTS / spec.name
                    if (
                        shutil.disk_usage(
                            root.resolve() if root.exists() else RESULTS
                        ).free
                        < 2 * 1024**3
                    ):
                        raise RuntimeError(
                            "Less than 2 GiB free on campaign storage; refusing another campaign"
                        )
                    if (root / "cancel.request").exists() or (
                        RESULTS / ".requests" / f"{spec.name}.cancel"
                    ).exists():
                        raise RuntimeError(
                            "Cancellation request still present; inspect handover"
                        )
                    if (root / ".supervisor.lock").exists() and is_alive(
                        read(root / ".supervisor.lock")["pid"]
                    ):
                        raise RuntimeError("Campaign still owned by another supervisor")
                    attempt = sum(e.get("campaign") == spec.name for e in journal) + 1
                    log = STATE / f"{spec.name}-attempt{attempt}.log"
                    while (
                        log.exists()
                    ):  # A disk-full exit may precede journal publication.
                        attempt += 1
                        log = STATE / f"{spec.name}-attempt{attempt}.log"
                    before = {
                        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (root / "records").glob("*.json")
                    }
                    command = [
                        sys.executable,
                        "-u",
                        "-m",
                        "smart_retail.application.experiments.cli",
                        "resume" if root.exists() else "run",
                        "--config",
                        str(CONFIGS / row["config"]),
                        "--output",
                        str(root),
                    ]
                    optional_slot = len(active) >= 2
                    if optional_slot:
                        command += ["--max-new-jobs", "1"]
                    with log.open("xb") as stream:
                        process = subprocess.Popen(
                            command,
                            cwd=ROOT,
                            stdin=subprocess.DEVNULL,
                            stdout=stream,
                            stderr=stream,
                            creationflags=subprocess.CREATE_NO_WINDOW
                            if os.name == "nt"
                            else 0,
                        )
                    entry = {
                        "campaign": spec.name,
                        "block": row["block"],
                        "pid": process.pid,
                        "started_utc": now(),
                        "status": "RUNNING",
                        "execution_mode": f"parallel_campaigns_{limit}",
                        "optional_one_job_slice": optional_slot,
                        "existing_record_sha256": before,
                        "command": command,
                        "log": str(log),
                    }
                    journal.append(entry)
                    write(journal_file, journal)
                    active[process.pid] = (process, root, entry)
                    print(now(), "START", spec.name, process.pid, flush=True)
                for pid, (process, root, entry) in list(active.items()):
                    code = (
                        process.poll()
                        if process is not None
                        else (None if is_alive(pid) else 0)
                    )
                    if code is None or (
                        (root / ".supervisor.lock").exists()
                        and is_alive(read(root / ".supervisor.lock")["pid"])
                    ):
                        continue
                    for name, expected in entry["existing_record_sha256"].items():
                        if (
                            hashlib.sha256(
                                (root / "records" / name).read_bytes()
                            ).hexdigest()
                            != expected
                        ):
                            raise RuntimeError(
                                "A completed historical record was modified"
                            )
                    checkpoint = (
                        read(root / "checkpoint.json")
                        if (root / "checkpoint.json").exists()
                        else {}
                    )
                    sliced = (
                        code == 0
                        and checkpoint.get("status") == "PAUSED_PARTIAL"
                        and entry.get("optional_one_job_slice")
                    )
                    entry.update(
                        ended_utc=now(),
                        exit_code=code if process is not None else None,
                        checkpoint=checkpoint,
                        status="SLICE_COMPLETED"
                        if sliced
                        else "COMPLETED"
                        if code == 0 and checkpoint.get("status") == "COMPLETED"
                        else "INCOMPLETE",
                        existing_records_unchanged=True,
                    )
                    write(journal_file, journal)
                    del active[pid]
                    if checkpoint.get("status") in {
                        "COMPLETED",
                        "NOT_EXECUTED_RESOURCE_LIMIT",
                    }:
                        added = prepare_recovery()
                        rows.extend(added)
                        for extra in added:
                            pending.append(
                                (
                                    extra,
                                    CampaignSpec.model_validate(
                                        read(Path(extra["config"]))
                                    ),
                                )
                            )
                    if sliced:
                        row = next(
                            r
                            for r in rows
                            if read(CONFIGS / r["config"])["name"] == root.name
                        )
                        pending.insert(
                            0,
                            (
                                row,
                                CampaignSpec.model_validate(
                                    read(CONFIGS / row["config"])
                                ),
                            ),
                        )
                    print(now(), entry["status"], entry["campaign"], flush=True)
                write(
                    STATE / "status.json",
                    {
                        "status": "RUNNING",
                        "updated_utc": now(),
                        "block": block,
                        "slots": limit,
                        "resources": measurement,
                        "active": [
                            {"pid": p, "campaign": v[2]["campaign"]}
                            for p, v in active.items()
                        ],
                        "pending_in_block": [s.name for _, s in pending],
                    },
                )
                if active:
                    time.sleep(1)
        write(
            STATE / "finished.json",
            {
                "status": "SCHEDULE_FINISHED",
                "ended_utc": now(),
                "campaign_processes": len(journal),
            },
        )
    finally:
        # Existing durable supervisors retain ownership if coordinator itself fails;
        # the unattended watcher waits for them before any bounded retry.
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
