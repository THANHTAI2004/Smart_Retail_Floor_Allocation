"""Durable database queue, atomic claims, killable child processes, hard wall budgets."""

import argparse
import json
import logging
import multiprocessing as mp
import os
import socket
import time
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select, update

from smart_retail.application.workflow import canonical_hash, execute
from smart_retail.domain.models import EngineError
from smart_retail.infrastructure.database import ROOT, RunRecord, WorkerHeartbeat, connect
from smart_retail.infrastructure.provenance import runtime_identity

logger = logging.getLogger("smart_retail.worker")


def read_progress(path: Path) -> str | None:
    """A missed progress sample must not interrupt process supervision on Windows."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))["stage"]
    except (PermissionError, FileNotFoundError):
        return None


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=True, allow_nan=False, indent=2), encoding="utf-8"
    )
    # Windows readers briefly hold a handle that prevents replacement. Retry
    # only that transient sharing violation; publish the complete JSON atomically.
    for attempt in range(50):
        try:
            temporary.replace(path)
            break
        except PermissionError:
            if attempt == 49:
                raise
            time.sleep(0.01)


def child(snapshot: dict, directory: str) -> None:
    root = Path(directory)
    try:
        if snapshot.get("_runtime") != runtime_identity():
            raise EngineError(
                "SOURCE_DRIFT", "Source or numerical dependency identity changed since enqueue"
            )
        result = execute(
            snapshot, progress=lambda stage: atomic_json(root / "progress.json", {"stage": stage})
        )
        result["runtime"] = snapshot["_runtime"]
        atomic_json(root / "result.json", result)
    except Exception as exc:
        atomic_json(
            root / "error.json",
            {"code": getattr(exc, "code", "EXECUTION_ERROR"), "message": str(exc)},
        )


def work_once(factory, artifact_root: Path, heartbeat_id: str = "test") -> bool:
    with factory() as db:
        # A dead supervisor cannot retain a job indefinitely. The hard job limit is <=300s.
        stale = list(
            db.scalars(
                select(RunRecord).where(
                    RunRecord.status.in_(["RUNNING", "CANCEL_REQUESTED"]),
                    RunRecord.started_epoch < time.time() - 360,
                )
            )
        )
        for run in stale:
            run.status = "TIMED_OUT"
            run.error = {"code": "WORKER_LOST", "message": "Worker lease expired"}
        db.commit()
        candidate = db.scalar(
            select(RunRecord)
            .where(RunRecord.status == "QUEUED")
            .order_by(RunRecord.created_at)
            .limit(1)
        )
        if candidate is None:
            return False
        identifier = candidate.id
        changed = db.execute(
            update(RunRecord)
            .where(RunRecord.id == identifier, RunRecord.status == "QUEUED")
            .values(status="RUNNING", started_epoch=time.time())
        )
        db.commit()
        if changed.rowcount != 1:
            return False
        db.refresh(candidate)
        snapshot = candidate.snapshot
        if canonical_hash(snapshot) != candidate.input_sha256:
            candidate.status = "FAILED"
            candidate.error = {"code": "INPUT_CORRUPT", "message": "Snapshot checksum mismatch"}
            db.commit()
            return True
    directory = artifact_root / identifier
    directory.mkdir(parents=True, exist_ok=False)
    atomic_json(directory / "input.json", snapshot)
    context = mp.get_context("spawn")
    process = context.Process(target=child, args=(snapshot, str(directory)), daemon=True)
    process.start()
    began = time.monotonic()
    budget = snapshot["optimization"]["time_limit_s"] + 2  # child startup grace
    terminal = None
    try:
        while process.is_alive():
            with factory() as db:
                db.merge(WorkerHeartbeat(id=heartbeat_id, epoch=time.time()))
                state = db.get(RunRecord, identifier)
                if state.status == "CANCEL_REQUESTED":
                    terminal = "CANCELLED"
                if time.monotonic() - began > budget and terminal is None:
                    terminal = "TIMED_OUT"
                progress = directory / "progress.json"
                stage = read_progress(progress)
                if stage is not None:
                    state.stage = stage
                db.commit()
            if terminal:
                process.terminate()
                break
            process.join(0.1)
    finally:
        process.join(5)
        if process.is_alive():
            process.kill()
            process.join()
    with factory() as db:
        run = db.get(RunRecord, identifier)
        if run.status == "CANCEL_REQUESTED":
            terminal = "CANCELLED"
        if terminal:
            run.status = terminal
            run.error = {"code": terminal, "message": "Supervisor stopped the child process"}
        elif (directory / "result.json").exists() and process.exitcode == 0:
            result = json.loads((directory / "result.json").read_text(encoding="utf-8"))
            if result["input_sha256"] != canonical_hash(snapshot):
                raise RuntimeError("Worker input identity mismatch")
            run.result = result
            run.result_sha256 = canonical_hash(result)
            run.status = "SUCCEEDED"
            run.stage = "COMPLETE"
        else:
            error_path = directory / "error.json"
            error = (
                json.loads(error_path.read_text(encoding="utf-8"))
                if error_path.exists()
                else {"code": "WORKER_CRASH", "message": f"Child exited {process.exitcode}"}
            )
            run.error = error
            run.status = {
                "TIMEOUT": "TIMED_OUT",
                "INFEASIBLE": "INFEASIBLE",
                "CANCELLED": "CANCELLED",
            }.get(error["code"], "FAILED")
        db.commit()
        atomic_json(
            directory / "receipt.json",
            {
                "run_id": identifier,
                "status": run.status,
                "stage": run.stage,
                "input_sha256": run.input_sha256,
                "result_sha256": run.result_sha256,
                "error": run.error,
                "child_exit": process.exitcode,
            },
        )
        logger.info("run=%s status=%s", identifier, run.status)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    _, factory = connect()
    artifact_root = Path(os.getenv("SMART_RETAIL_ARTIFACTS", str(ROOT / "var" / "artifacts")))
    worker_id = f"{socket.gethostname()}-{uuid4()}"
    while True:
        with factory() as db:
            db.merge(WorkerHeartbeat(id=worker_id, epoch=time.time()))
            db.commit()
        worked = work_once(factory, artifact_root, worker_id)
        if args.once:
            break
        if not worked:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
