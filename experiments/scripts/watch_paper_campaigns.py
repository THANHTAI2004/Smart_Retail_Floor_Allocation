"""Keep the machine awake and finalize the existing unattended paper batch.

Does not edit backend source, experiment configs or historical outcomes. Restarts
an interrupted batch at most twice using the existing drift/lease-aware runner.
"""

import argparse
import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from paper_recovery import coverage, supplemental_rows
from smart_retail.application.experiments.reports import report
from smart_retail.application.experiments.storage import read, verify_integrity, write
from smart_retail.contracts.experiments import CampaignSpec, planned_jobs
from smart_retail.infrastructure.mongodb.client import connect
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.workers.resources import is_alive

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
CONFIGS = ROOT / "experiments/configs/paper-v2"
RESULTS = ROOT / "experiments/results/20261023-paper-v2"
REPORTS = ROOT / "experiments/reports/20261023-paper-v2"
STATE = ROOT / "var/paper-unattended"
BASELINE = ROOT / "var/continue-20261023-01/preflight.json"


def now():
    return datetime.now(UTC).isoformat()


def designs():
    return [
        (row["block"], CampaignSpec.model_validate(read(CONFIGS / row["config"])))
        for row in read(CONFIGS / "index.json") + supplemental_rows()
    ]


def inventory():
    rows = []
    for block, spec in designs():
        root = RESULTS / spec.name
        checkpoint = (
            read(root / "checkpoint.json")
            if (root / "checkpoint.json").exists()
            else {}
        )
        rows.append(
            {
                "block": block,
                "campaign": spec.name,
                "planned": planned_jobs(spec),
                "completed": checkpoint.get("completed", 0),
                "status": checkpoint.get("status", "NOT_STARTED"),
            }
        )
    return rows


def active_supervisors():
    active = []
    for path in RESULTS.glob("*/.supervisor.lock"):
        try:
            pid = read(path)["pid"]
        except FileNotFoundError:
            continue  # Supervisor finished between directory listing and read.
        if is_alive(pid):
            active.append(pid)
    return active


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_report(root):
    manifest = read(root / "manifest.json")
    for name, expected in manifest["files"].items():
        path = (root / name).resolve()
        if (
            not path.is_relative_to(root.resolve())
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected
        ):
            raise ValueError(f"Report checksum mismatch: {name}")
    return len(manifest["files"])


def verify_campaign(root, expected):
    integrity = verify_integrity(root)
    plan = read(root / "plan.json")["jobs"]
    records = [read(path) for path in (root / "records").glob("*.json")]
    keys = {job["key"] for job in plan}
    if len(keys) != expected or len({r["job_key"] for r in records}) != len(records):
        raise ValueError("Unexpected or duplicate campaign job keys")
    if any(r["job_key"] not in keys for r in records):
        raise ValueError("Record is outside the planned campaign")
    if read(root / "identity.json")["runtime"] != read(BASELINE)["runtime"]:
        raise ValueError("Campaign identity differs from the verified source")
    for row in records:
        receipt = read(root / "artifacts" / row["run_id"] / "receipt.json")
        if (
            receipt["status"] != row["status"]
            or receipt["input_sha256"] != row["input_sha256"]
        ):
            raise ValueError("Record and worker receipt differ")
        if row["status"] == "SUCCEEDED" and row["validation"]["status"] != "PASS":
            raise ValueError("Successful job lacks independent validation")
    return {
        "integrity": integrity,
        "recorded": len(records),
        "unexecuted": expected - len(records),
        "outcomes": dict(Counter(r["status"] for r in records)),
        "evaluations": dict(
            Counter(r.get("evaluation_status", "NOT_APPLICABLE") for r in records)
        ),
    }


def failure_kind(record):
    code = (record.get("error") or {}).get("code", record.get("status"))
    message = (record.get("error") or {}).get("message", "").lower()
    if (
        "no space left on device" in message
        or "not enough space on the disk" in message
    ):
        return "STORAGE_EXHAUSTED"
    if code in {"WORKER_CRASH", "WORKER_LOST", "DATABASE_UNAVAILABLE"}:
        return "INFRASTRUCTURE_RETRIES_EXHAUSTED"
    if code in {"TIMEOUT", "TIMED_OUT", "RESOURCE_LIMIT", "PROBLEM_LIMIT"}:
        return "DECLARED_RESOURCE_LIMIT"
    if code in {"INFEASIBLE", "SEARCH_EXHAUSTED", "SLOTTING_FAILED"}:
        return "MODEL_OR_SEARCH_OUTCOME"
    if record.get("evaluation_status") == "NOT_EXECUTED_BUDGET":
        return "HELD_OUT_BUDGET_LIMIT"
    return "NEEDS_CODE_DIAGNOSIS"


def collect_failures():
    """Incremental live triage; never rewrite outcomes or scientific source."""
    directory = STATE / "job-errors"
    directory.mkdir(exist_ok=True)
    counts = Counter()
    for root in RESULTS.iterdir():
        if not root.is_dir():
            continue
        for path in (root / "records").glob("*.json"):
            record = read(path)
            if record["status"] == "SUCCEEDED" and record.get("evaluation_status") in (
                None,
                "COMPLETED",
            ):
                continue
            kind = failure_kind(record)
            counts[kind] += 1
            target = directory / f"{root.name}-{path.stem}.json"
            if target.exists():
                continue
            artifact = (root / "artifacts" / record["run_id"]).resolve()
            if not artifact.is_relative_to((root / "artifacts").resolve()):
                raise ValueError("Invalid error artifact path")
            evidence = directory / f"{root.name}-{path.stem}"
            evidence.mkdir(exist_ok=False)
            hashes = {}
            for name in (
                "input.json",
                "error.json",
                "receipt.json",
                "supervisor.json",
                "progress.json",
            ):
                source = artifact / name
                if source.exists():
                    raw = source.read_bytes()
                    with (evidence / name).open("xb") as stream:
                        stream.write(raw)
                    hashes[name] = hashlib.sha256(raw).hexdigest()
            write(
                target,
                {
                    "detected_utc": now(),
                    "campaign": root.name,
                    "job_key": record["job_key"],
                    "classification": kind,
                    "record": record,
                    "evidence_sha256": hashes,
                    "automatic_action": "Campaign already applies bounded WORKER_CRASH/WORKER_LOST retries; retain terminal outcome and continue other jobs. Unknown code defects require a tested new source identity and a separate output namespace.",
                },
                immutable=True,
            )
            print(now(), "JOB_ALERT", root.name, record["job_key"], kind, flush=True)
    return dict(counts)


def backup(destination, paths):
    destination.mkdir(parents=True, exist_ok=False)
    archive_path = destination / "paper-results.zip"
    sources = {}
    last_space_check = 0.0
    with zipfile.ZipFile(
        archive_path, "x", compression=zipfile.ZIP_DEFLATED, allowZip64=True
    ) as archive:
        for base in paths:
            base = base.absolute()

            def walk_files(directory):
                for folder, dirs, names in os.walk(directory, followlinks=False):
                    dirs[:] = sorted(
                        d
                        for d in dirs
                        if not (Path(folder) / d).is_junction()
                        and not (Path(folder) / d).is_symlink()
                    )
                    for filename in sorted(names):
                        yield Path(folder) / filename

            files = walk_files(base) if base.is_dir() else [base]
            for path in files:
                if not path.is_file() or path.suffix == ".tmp":
                    continue
                name = path.relative_to(ROOT).as_posix()
                if name in sources:
                    continue
                if time.monotonic() - last_space_check > 10:
                    if shutil.disk_usage(destination).free < 2 * 1024**3:
                        raise RuntimeError(
                            "Backup storage below 2 GiB free; originals preserved"
                        )
                    last_space_check = time.monotonic()
                digest = hashlib.sha256()
                info = zipfile.ZipInfo.from_file(path, name)
                info.compress_type = zipfile.ZIP_DEFLATED
                with (
                    path.open("rb") as src,
                    archive.open(info, "w", force_zip64=True) as dst,
                ):
                    while chunk := src.read(1024 * 1024):
                        digest.update(chunk)
                        dst.write(chunk)
                sources[name] = digest.hexdigest()
    with zipfile.ZipFile(archive_path) as archive:
        for name, expected in sources.items():
            digest = hashlib.sha256()
            with archive.open(name) as stream:
                while chunk := stream.read(1024 * 1024):
                    digest.update(chunk)
            if digest.hexdigest() != expected:
                raise ValueError(f"Backup readback mismatch: {name}")
    receipt = {
        "archive": str(archive_path),
        "entries": len(sources),
        "readback": "PASS",
        "files": sources,
    }
    write(destination / "manifest.json", receipt, immutable=True)
    return {k: v for k, v in receipt.items() if k != "files"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner-pid", type=int)
    parser.add_argument(
        "--backup-root", type=Path, default=Path.home() / "Documents/SmartRetailBackups"
    )
    parser.add_argument(
        "--runner-script",
        default="scripts/run_paper_campaigns.py",
        choices=["scripts/run_paper_campaigns.py", "scripts/run_paper_parallel.py"],
    )
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--verify-campaign", type=Path)
    args = parser.parse_args()
    if args.verify_campaign:
        spec = CampaignSpec.model_validate(
            read(args.verify_campaign / "configuration.json")
        )
        print(
            json.dumps(
                verify_campaign(args.verify_campaign, planned_jobs(spec)), indent=2
            )
        )
        return
    if args.check_only:
        assert runtime_identity() == read(BASELINE)["runtime"]
        print(
            json.dumps(
                {"campaigns": inventory(), "active_supervisors": active_supervisors()},
                indent=2,
            )
        )
        return
    if args.runner_pid is None:
        parser.error("--runner-pid is required")
    STATE.mkdir(parents=True, exist_ok=True)
    lock = STATE / "watcher.lock.json"
    if lock.exists():
        if is_alive(read(lock)["pid"]):
            raise RuntimeError("Unattended watcher is already running")
        lock.unlink()
    write(lock, {"pid": os.getpid(), "started_utc": now()}, immutable=True)
    keep_awake = False
    result = {
        "started_utc": now(),
        "status": "MONITORING",
        "restarts": 0,
        "runner_script": args.runner_script,
    }
    try:
        if os.name == "nt":
            keep_awake = bool(
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
            )
            if not keep_awake:
                raise RuntimeError("Windows rejected keep-awake request")
        result["keep_awake"] = keep_awake
        runner_pid = args.runner_pid
        while True:
            current = inventory()
            result.update(
                updated_utc=now(),
                campaigns=current,
                runner_pid=runner_pid,
                job_alerts=collect_failures(),
                error_scan_interval_s=30,
            )
            write(STATE / "status.json", result)
            if is_alive(runner_pid) or active_supervisors():
                time.sleep(30)
                continue
            incomplete = [r for r in current if r["completed"] != r["planned"]]
            resume_states = {
                "NOT_STARTED",
                "FAILED",
                "RUNNING",
                "READY",
                "PAUSED_PARTIAL",
            }
            if args.runner_script.endswith("run_paper_parallel.py"):
                # The controlled handover paused future campaigns as CANCELLED.
                resume_states.add("CANCELLED")
            retryable = [
                r
                for r in incomplete
                if r["status"] in resume_states
                and not (RESULTS / r["campaign"] / "cancel.request").exists()
                and not (RESULTS / ".requests" / f"{r['campaign']}.cancel").exists()
            ]
            if retryable and result["restarts"] < 2:
                if runtime_identity() != read(BASELINE)["runtime"]:
                    raise RuntimeError(
                        "Source/dependency drift; unattended restart refused"
                    )
                # Respect expired leases after an interrupted supervisor.
                result["status"] = "WAITING_FOR_LEASE_EXPIRY"
                write(STATE / "status.json", result)
                for _ in range(13):
                    time.sleep(30)
                for health_attempt in range(3):
                    owner, _ = connect(database="sr_paper_unattended_health")
                    try:
                        owner.ready()
                        break
                    except RuntimeError:
                        if health_attempt == 2:
                            raise
                        time.sleep(10)
                    finally:
                        owner.dispose()
                attempt = result["restarts"] + 1
                with (STATE / f"restart-{attempt}.log").open("xb") as stream:
                    process = subprocess.Popen(
                        [sys.executable, "-u", args.runner_script],
                        cwd=ROOT,
                        stdout=stream,
                        stderr=stream,
                        stdin=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                        if os.name == "nt"
                        else 0,
                    )
                runner_pid = process.pid
                result.update(status="MONITORING", restarts=attempt)
                continue
            break
        result["status"] = "VERIFYING"
        write(STATE / "status.json", result)
        checks, blocks = [], defaultdict(list)
        for block, spec in designs():
            root = RESULTS / spec.name
            if (root / "integrity.json").exists():
                check = verify_campaign(root, planned_jobs(spec))
                checks.append({"campaign": spec.name, **check})
                if check["recorded"]:
                    blocks[spec.name if block == "RECOVERY" else block].append(root)
            else:
                checks.append(
                    {
                        "campaign": spec.name,
                        "unexecuted": planned_jobs(spec),
                        "recorded": 0,
                    }
                )
        report_checks = []
        for block, roots in blocks.items():
            target = REPORTS / block
            try:
                count = verify_report(target)
                expected = sum(len(list((r / "records").glob("*.json"))) for r in roots)
                if len(read(target / "results.json")) != expected:
                    raise ValueError("Existing report is incomplete")
            except (OSError, ValueError, KeyError):
                target = REPORTS / f"{block}-verified-{datetime.now(UTC):%Y%m%dT%H%M%S}"
                report(roots, target)
                count = verify_report(target)
            report_checks.append(
                {"block": block, "path": str(target), "verified_files": count}
            )
        result.update(campaign_verification=checks, reports=report_checks)
        supplemental = coverage()
        write(ROOT / "var/paper-parallel/recovery/coverage.json", supplemental)
        result["supplemental_coverage"] = {
            k: v for k, v in supplemental.items() if k != "entries"
        }
        parallel_journal = ROOT / "var/paper-parallel/journal.json"
        if args.runner_script.endswith("run_paper_parallel.py"):
            mode_file = (
                REPORTS / f"execution-mode-{datetime.now(UTC):%Y%m%dT%H%M%S}.json"
            )
            write(
                mode_file,
                {
                    "execution_mode": "sequential_then_adaptive_parallel_campaigns_2_or_3",
                    "transition": read(ROOT / "var/paper-parallel/handover.json"),
                    "schedule": read(parallel_journal),
                    "concurrency_control": read(
                        ROOT / "var/paper-parallel/concurrency.json"
                    )
                    if (ROOT / "var/paper-parallel/concurrency.json").exists()
                    else None,
                    "three_slot_transition": read(
                        ROOT / "var/paper-parallel/three-slot-handover.json"
                    )
                    if (ROOT / "var/paper-parallel/three-slot-handover.json").exists()
                    else None,
                    "storage_recovery": read(ROOT / "var/paper-storage-recovery.json")
                    if (ROOT / "var/paper-storage-recovery.json").exists()
                    else None,
                    "limitation": "Wall time and budget-limited search outcomes can be affected by concurrent campaigns. Do not treat sequential and parallel wall measurements as a controlled speed comparison.",
                    "reports": report_checks,
                },
                immutable=True,
            )
            result["execution_mode_receipt"] = str(mode_file)
        unexecuted = sum(c["unexecuted"] for c in checks)
        failures = sum(
            n
            for c in checks
            for s, n in c.get("outcomes", {}).items()
            if s != "SUCCEEDED"
        )
        evaluation_limits = sum(
            n
            for c in checks
            for s, n in c.get("evaluations", {}).items()
            if s not in ("COMPLETED", "NOT_APPLICABLE")
        )
        result.update(
            unexecuted=unexecuted,
            job_failures=failures,
            evaluation_limits=evaluation_limits,
        )
        destination = (
            args.backup_root / f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}-paper-complete"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(destination.parent).free < 5 * 1024**3:
            raise RuntimeError(
                "Backup needs at least 5 GiB free initially; streaming guard preserves 2 GiB and scientific originals"
            )
        result["status"] = "BACKING_UP"
        write(STATE / "status.json", result)
        result["backup"] = backup(
            destination,
            [
                ROOT / "experiments/results",
                ROOT / "experiments/reports",
                ROOT / "experiments/configs",
                ROOT / "experiments/docs",
                ROOT / "experiments/runtime",
                ROOT / "experiments/databases",
                ROOT / "experiments/scripts",
                ROOT / "experiments/visualization",
                ROOT / "experiments/migration",
                ROOT / "experiments/README.md",
                ROOT / "experiments/VI_TRI_DU_LIEU.md",
                ROOT / "HANDOFF.md",
                ROOT / "docs/research/CONTINUATION_20261023.md",
                ROOT / args.runner_script,
                ROOT / "scripts/paper_resource_guard.py",
                ROOT / "scripts/paper_recovery.py",
                Path(__file__).resolve(),
            ],
        )
        result.update(
            status="VERIFIED_ALL_JOBS_SUCCEEDED"
            if not (unexecuted or failures or evaluation_limits)
            else "FINISHED_WITH_LIMITATIONS",
            ended_utc=now(),
        )
        write(STATE / "completion.json", result, immutable=True)
        print(result["status"], flush=True)
    except Exception:
        result.update(
            status="NEEDS_ATTENTION", error=traceback.format_exc(), ended_utc=now()
        )
        write(STATE / "failure.json", result)
        raise
    finally:
        result["keep_awake_released"] = True
        if keep_awake:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        write(STATE / "status.json", result)
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
