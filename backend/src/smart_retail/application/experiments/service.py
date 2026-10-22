"""Local research dashboard services; numerical work stays in worker processes."""

import os
import re
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from smart_retail.application.experiments.generators import SIZES
from smart_retail.application.experiments.storage import read, write
from smart_retail.application.projects import ServiceError
from smart_retail.application.stage_workflow import canonical_hash
from smart_retail.contracts.experiments import CampaignSpec
from smart_retail.infrastructure.database import ROOT
from smart_retail.infrastructure.filesystem import normalize_fs_path
from smart_retail.workers.resources import is_alive


def home() -> Path:
    path = normalize_fs_path(os.getenv("SMART_RETAIL_RESEARCH_HOME", str(ROOT / "var/research"))).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def location(identifier: str) -> Path:
    if not re.fullmatch(r"[a-f0-9-]{36}", identifier):
        raise ServiceError(404, "Unknown campaign")
    return home() / identifier


def catalog():
    return [
        {
            "id": name,
            "version": "1.0",
            "data_origin": "SYNTHETIC",
            "counts": dict(zip(("shelves", "categories", "products", "orders"), values)),
            "source": "structured_store_v1; generated snapshots and SHA-256 stored in campaigns",
        }
        for name, values in SIZES.items()
    ]


def configurations():
    return [
        {"id": p.stem, "configuration": read(p)}
        for p in sorted((ROOT / "experiments/configs").glob("*.json"))
    ]


def launch(spec: CampaignSpec, *, identifier: str | None = None, resume: bool = False):
    for item in listing():
        supervisor = item.get("supervisor", {})
        if (
            supervisor.get("pid")
            and is_alive(supervisor["pid"])
            and supervisor.get("status") in ("QUEUED", "RUNNING")
        ):
            raise ServiceError(409, "One local campaign supervisor is already running")
    identifier = identifier or str(uuid4())
    root = location(identifier)
    requests = home() / ".requests"
    requests.mkdir(exist_ok=True)
    config = requests / f"{identifier}.json"
    if not resume:
        write(config, spec.model_dump(mode="json"), immutable=True)
    elif read(root / "checkpoint.json")["status"] not in ("PAUSED_PARTIAL", "FAILED"):
        raise ServiceError(409, "Only a paused or failed campaign can resume after audit")
    status = requests / f"{identifier}.status.json"
    write(status, {"status": "QUEUED"})
    report_root = home() / ".reports" / f"{identifier}-{uuid4().hex[:8]}"
    command = [
        sys.executable,
        "-m",
        "smart_retail.application.experiments.process",
        "--config",
        str(config),
        "--output",
        str(root),
        "--reports",
        str(report_root),
        "--status",
        str(status),
    ]
    if resume:
        command.append("--resume")
    log = (requests / f"{identifier}.log").open("ab")
    try:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    finally:
        log.close()
    write(status, {"status": "QUEUED", "pid": process.pid})
    return {"id": identifier, "status": "QUEUED", "supervisor_pid": process.pid}


def detail(identifier: str):
    root = location(identifier)
    request = home() / ".requests" / f"{identifier}.json"
    if not request.exists():
        raise ServiceError(404, "Unknown campaign")
    state_file = request.with_name(f"{identifier}.status.json")
    supervisor = read(state_file) if state_file.exists() else {"status": "QUEUED"}
    checkpoint = (
        read(root / "checkpoint.json") if (root / "checkpoint.json").exists() else supervisor
    )
    if supervisor["status"] == "FAILED":
        checkpoint = {**checkpoint, **supervisor}
    return {
        "id": identifier,
        "configuration": read(request),
        **checkpoint,
        "supervisor": supervisor,
        "records": [read(p) for p in sorted((root / "records").glob("*.json"))],
        "datasets": [read(p) for p in sorted((root / "datasets").glob("*/manifest.json"))],
    }


def listing():
    return [
        {k: v for k, v in detail(p.stem).items() if k != "records"}
        for p in sorted(
            (home() / ".requests").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        if re.fullmatch(r"[a-f0-9-]{36}", p.stem)
    ]


def cancel(identifier: str):
    detail(identifier)
    (home() / ".requests" / f"{identifier}.cancel").touch(exist_ok=True)
    return {"id": identifier, "status": "CANCEL_REQUESTED"}


def joint_result(identifier: str, job_key: str):
    detail(identifier)
    if not re.fullmatch(r"[a-f0-9]{64}", job_key):
        raise ServiceError(404, "Unknown job")
    record_path = location(identifier) / "records" / f"{job_key}.json"
    if not record_path.is_file():
        raise ServiceError(404, "Job is not complete")
    record = read(record_path)
    if not re.fullmatch(r"[a-f0-9-]{36}", record["run_id"]):
        raise ServiceError(409, "Invalid stored run identity")
    result = read(location(identifier) / "artifacts" / record["run_id"] / "result.json")
    if canonical_hash(result) != record["result_sha256"]:
        raise ServiceError(409, "Result checksum differs")
    if "joint" not in result:
        raise ServiceError(404, "This job did not use joint optimization")
    initial = result["integrated"]["candidates"]
    stages = initial[0]["stages"] if initial else result["stages"]
    return {
        "joint": result["joint"],
        "initial_decisions": {
            "poses": {s["id"]: [s["x"], s["y"], s["rotation"]] for s in stages["T1"]["shelves"]},
            "assignment": stages["T2"]["assignment"],
            "placements": stages["T3"]["placements"],
        }
        if stages
        else None,
        "shelves": stages["T1"]["shelves"] if stages else [],
        "floorplan": result.get("floorplan", {}),
    }


def report_file(identifier: str, relative: str) -> Path:
    data = detail(identifier)
    report = data["supervisor"].get("report")
    if not report:
        raise ServiceError(409, "Report is not ready")
    root = normalize_fs_path(report).resolve()
    path = (root / relative).resolve()
    if (
        not path.is_relative_to(root)
        or not path.is_file()
        or path.suffix not in (".json", ".csv", ".png", ".svg", ".md")
    ):
        raise ServiceError(404, "Unknown report file")
    return path
