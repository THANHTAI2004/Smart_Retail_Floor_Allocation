"""Durable database queue, atomic claims, killable child processes, hard wall budgets."""

import argparse
import json
import logging
import multiprocessing as mp
import os
import socket
import time
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from smart_retail.application.workflow import canonical_hash, execute
from smart_retail.domain.models import EngineError
from smart_retail.infrastructure.database import ROOT, connect
from smart_retail.infrastructure.filesystem import normalize_fs_path
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.infrastructure.stage_cache import StageCache
from smart_retail.workers.resources import sample as sample_resources

logger = logging.getLogger("smart_retail.worker")


def memory_exceeded(rss_bytes: int | None, limit_mb: int | None) -> bool:
    """A null limit explicitly disables only the per-job RSS cutoff."""
    return limit_mb is not None and rss_bytes is not None and rss_bytes > limit_mb * 1024**2


def read_progress(path: Path) -> str | None:
    """A missed progress sample must not interrupt process supervision on Windows."""
    try:
        return json.loads(normalize_fs_path(path).read_text(encoding="utf-8"))["stage"]
    except (PermissionError, FileNotFoundError):
        return None


def atomic_json(path: Path, value: dict) -> None:
    path = normalize_fs_path(path)
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


def child(snapshot: dict, directory: str, cache_directory: str | None = None) -> None:
    root = normalize_fs_path(directory)
    try:
        if snapshot.get("_runtime") != runtime_identity():
            raise EngineError(
                "SOURCE_DRIFT", "Source or numerical dependency identity changed since enqueue"
            )
        stages = root / "stages"
        stages.mkdir()
        events: list[str] = []

        def observe(stage, key, inputs, value, hit, elapsed):
            payload = (
                asdict(value) if is_dataclass(value) and not isinstance(value, type) else value
            )
            event = {
                "stage": stage,
                "cache_key": key,
                "inputs": inputs,
                "output": payload,
                "output_sha256": canonical_hash(payload),
                "cache_hit": hit,
                "elapsed_s": elapsed,
                "recorded_utc": datetime.now(UTC).isoformat(),
            }
            path = stages / f"{len(events):04}-{stage}.json"
            atomic_json(path, event)
            events.append(path.name)

        result = execute(
            snapshot,
            progress=lambda stage: atomic_json(root / "progress.json", {"stage": stage}),
            stage_cache=StageCache(
                Path(cache_directory) if cache_directory else root.parent / ".stage-cache"
            ),
            observer=observe,
        )

        # Cache-hit and elapsed telemetry live in stage artifacts, outside scientific result bytes.
        def scientific(value):
            if isinstance(value, dict):
                return {k: scientific(v) for k, v in value.items() if k not in ("hit", "telemetry")}
            if isinstance(value, (tuple, list)):
                return [scientific(v) for v in value]
            return value

        result = scientific(result)
        result["runtime"] = snapshot["_runtime"]
        atomic_json(root / "result.json", result)
    except Exception as exc:
        atomic_json(
            root / "error.json",
            {
                "code": getattr(exc, "code", "EXECUTION_ERROR"),
                "message": str(exc),
                "stage": getattr(exc, "stage", None),
            },
        )


def wall_budget(limit_s: float) -> float:
    """Supervisor wall limit: solver budget plus child startup and finalization grace.

    Budget-exhausting searches still verify and write their result after the solver
    deadline; a fixed 2 s grace killed completed medium-scale feedback jobs.
    """
    return limit_s + max(15.0, 0.1 * limit_s)


def work_once(
    factory,
    artifact_root: Path,
    heartbeat_id: str = "test",
    cancelled=lambda: False,
    cache_root: Path | None = None,
) -> bool:
    artifact_root = normalize_fs_path(artifact_root)
    cache_root = normalize_fs_path(cache_root) if cache_root else None
    with factory() as db:
        db.recover_expired(time.time())
        candidate = db.claim(heartbeat_id, time.time())
        if candidate is None:
            return False
        identifier = candidate.id
        snapshot = candidate.snapshot
        if canonical_hash(snapshot) != candidate.input_sha256:
            candidate.status = "FAILED"
            candidate.error = {"code": "INPUT_CORRUPT", "message": "Snapshot checksum mismatch"}
            db.publish(candidate)
            return True
    directory = artifact_root / identifier
    directory.mkdir(parents=True, exist_ok=False)
    atomic_json(directory / "input.json", snapshot)
    context = mp.get_context("spawn")
    process = context.Process(
        target=child,
        args=(snapshot, str(directory), str(cache_root) if cache_root else None),
        daemon=True,
    )
    began = time.monotonic()
    started_utc = datetime.now(UTC).isoformat()
    try:
        process.start()
    except Exception as exc:
        error = {
            "code": "WORKER_CRASH",
            "message": f"Process creation failed: {type(exc).__name__}: {exc}",
        }
        with factory() as db:
            failed = candidate
            failed.status = "FAILED"
            failed.error = error
            db.publish(failed)
        atomic_json(directory / "error.json", error)
        atomic_json(
            directory / "receipt.json",
            {
                "run_id": identifier,
                "status": "FAILED",
                "stage": "PENDING",
                "input_sha256": canonical_hash(snapshot),
                "result_sha256": None,
                "error": error,
                "child_exit": None,
                "started_utc": started_utc,
                "ended_utc": datetime.now(UTC).isoformat(),
                "wall_s": time.monotonic() - began,
                "peak_child_rss_bytes": None,
                "sampled_child_cpu_s": None,
                "resource_samples": 0,
                "memory_limit_mb": snapshot["optimization"].get("memory_limit_mb", 2048),
            },
        )
        return True
    atomic_json(
        directory / "supervisor.json",
        {
            "child_pid": process.pid,
            "supervisor_pid": os.getpid(),
            "started_utc": datetime.now(UTC).isoformat(),
            "input_sha256": canonical_hash(snapshot),
        },
    )
    peak_rss = cpu_s = 0.0
    resource_samples = 0
    budget = wall_budget(snapshot["optimization"]["time_limit_s"])
    terminal = None
    try:
        while process.is_alive():
            if cancelled():
                terminal = "CANCELLED"
            usage = sample_resources(process.pid or 0)
            if usage["peak_rss_bytes"] is not None:
                peak_rss = max(peak_rss, usage["peak_rss_bytes"])
                resource_samples += 1
            if usage["cpu_s"] is not None:
                cpu_s = max(cpu_s, usage["cpu_s"])
            memory_limit_mb = snapshot["optimization"].get("memory_limit_mb", 2048)
            if memory_exceeded(usage["rss_bytes"], memory_limit_mb):
                terminal = "RESOURCE_LIMIT"
            with factory() as db:
                db.heartbeat(heartbeat_id)
                state = db.get_run(identifier)
                if not db.renew(candidate):
                    terminal = "LEASE_LOST"
                if state.status == "CANCEL_REQUESTED":
                    terminal = "CANCELLED"
                if time.monotonic() - began > budget and terminal is None:
                    terminal = "TIMED_OUT"
                progress = directory / "progress.json"
                stage = read_progress(progress)
                if stage is not None:
                    state.stage = stage
                db.renew(candidate, state.stage)
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
        run = db.get_run(identifier)
        if run.status == "CANCEL_REQUESTED":
            terminal = "CANCELLED"
        if terminal:
            run.status = "FAILED" if terminal == "RESOURCE_LIMIT" else terminal
            run.error = {"code": terminal, "message": "Supervisor stopped the child process"}
        elif (directory / "result.json").exists() and process.exitcode == 0:
            result = json.loads((directory / "result.json").read_text(encoding="utf-8"))
            if result["input_sha256"] != canonical_hash(snapshot):
                raise RuntimeError("Worker input identity mismatch")
            run.result = result
            run.result_sha256 = canonical_hash(result)
            run.status = "SUCCEEDED"
            run.stage = "COMPLETE"
            if result.get("joint") and result["joint"].get("best") is None:
                joint = result["joint"]
                code = (
                    "INFEASIBLE"
                    if joint.get("proof_status") == "INFEASIBLE_PROVEN"
                    else (
                        "TIMEOUT"
                        if joint.get("status") == "TIMEOUT"
                        else "CANCELLED"
                        if joint.get("status") == "CANCELLED"
                        else "SEARCH_EXHAUSTED"
                    )
                )
                run.status = {
                    "INFEASIBLE": "INFEASIBLE",
                    "TIMEOUT": "TIMED_OUT",
                    "CANCELLED": "CANCELLED",
                }.get(code, "FAILED")
                run.error = {
                    "code": code,
                    "message": "Joint search has no feasible incumbent; proof artifacts retained",
                    "stage": "JOINT",
                }
                run.stage = "JOINT"
        else:
            error_path = directory / "error.json"
            error = (
                json.loads(error_path.read_text(encoding="utf-8"))
                if error_path.exists()
                else {"code": "WORKER_CRASH", "message": f"Child exited {process.exitcode}"}
            )
            run.error = error
            run.stage = error.get("stage") or run.stage
            run.status = {
                "TIMEOUT": "TIMED_OUT",
                "INFEASIBLE": "INFEASIBLE",
                "CANCELLED": "CANCELLED",
            }.get(error["code"], "FAILED")
        published = db.publish(run, owner=candidate)
        if published is None:
            logger.warning("run=%s stale owner rejected", identifier)
            run = db.get_run(identifier)
        else:
            run = published
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
                "started_utc": started_utc,
                "ended_utc": datetime.now(UTC).isoformat(),
                "wall_s": time.monotonic() - began,
                "peak_child_rss_bytes": int(peak_rss) if resource_samples else None,
                "sampled_child_cpu_s": cpu_s if resource_samples else None,
                "resource_samples": resource_samples,
                "memory_limit_mb": snapshot["optimization"].get("memory_limit_mb", 2048),
            },
        )
        logger.info("run=%s status=%s", identifier, run.status)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    owner, factory = connect()
    owner.ready()
    artifact_root = Path(os.getenv("SMART_RETAIL_ARTIFACTS", str(ROOT / "var" / "artifacts")))
    worker_id = f"{socket.gethostname()}-{uuid4()}"
    while True:
        with factory() as db:
            db.heartbeat(worker_id)
        worked = work_once(factory, artifact_root, worker_id)
        if args.once:
            break
        if not worked:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
