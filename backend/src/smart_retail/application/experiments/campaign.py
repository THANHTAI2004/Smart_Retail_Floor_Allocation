"""Resumable one-worker campaigns using the production durable run queue."""

import copy
import hashlib
import os
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path

from smart_retail.application import projects
from smart_retail.application.experiments.generators import generate, merge
from smart_retail.application.experiments.storage import fingerprint, read, verify_integrity, write
from smart_retail.application.experiments.validation import verify
from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.experiments import CampaignSpec
from smart_retail.contracts.inputs import SECTIONS, to_domain
from smart_retail.infrastructure.database import connect
from smart_retail.infrastructure.filesystem import logical_fs_path, normalize_fs_path
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.workers.resources import is_alive
from smart_retail.workers.runner import work_once


def utc():
    return datetime.now(UTC).isoformat()


def initialize(spec: CampaignSpec, root: Path):
    root = normalize_fs_path(root)
    began = time.monotonic()
    root.mkdir(parents=True, exist_ok=False)
    disk = shutil.disk_usage(root)
    if disk.free < 512 * 1024**2:
        raise ValueError("At least 512 MiB free disk space required")
    write(root / "configuration.json", spec.model_dump(mode="json"), immutable=True)
    datasets = {}
    for ds in spec.datasets:
        data, manifest = generate(ds)
        datasets[ds.id] = data
        write(root / "datasets" / ds.id / "input.json", data, immutable=True)
        write(root / "datasets" / ds.id / "manifest.json", manifest, immutable=True)
    jobs = []
    for experiment in spec.experiments:
        for dataset_id in experiment.datasets:
            for treatment in experiment.treatments:
                for seed in spec.seeds:
                    for repetition in range(spec.repetitions):
                        data = merge(copy.deepcopy(datasets[dataset_id]), treatment.overrides)
                        data["optimization"].update(
                            seed=seed,
                            time_limit_s=spec.job_time_limit_s,
                            memory_limit_mb=spec.memory_limit_mb,
                        )
                        to_domain(data)
                        job = {
                            "experiment": experiment.id,
                            "dataset": dataset_id,
                            "treatment": treatment.id,
                            "seed": seed,
                            "repetition": repetition,
                            "overrides": treatment.overrides,
                            "input_sha256": canonical_hash(data),
                        }
                        job["key"] = canonical_hash(job)
                        jobs.append(job)
    write(root / "plan.json", {"jobs": jobs}, immutable=True)
    write(
        root / "identity.json",
        {
            "runtime": runtime_identity(),
            "config_sha256": canonical_hash(spec.model_dump(mode="json")),
            "created_utc": utc(),
            "free_disk_bytes": disk.free,
            "worker_limit": 1,
        },
        immutable=True,
    )
    write(
        root / "checkpoint.json",
        {
            "status": "READY",
            "planned": len(jobs),
            "completed": 0,
            "spent_wall_s": time.monotonic() - began,
            "records": [],
        },
    )
    write(root / "integrity.json", fingerprint(root))


def run(spec: CampaignSpec, root: Path, *, resume: bool = False, max_new_jobs: int | None = None):
    root = normalize_fs_path(root)
    if not resume:
        initialize(spec, root)
    verify_integrity(root)
    identity = read(root / "identity.json")
    if identity["runtime"] != runtime_identity() or identity["config_sha256"] != canonical_hash(
        spec.model_dump(mode="json")
    ):
        raise ValueError("Source/dependency/configuration drift; create a new campaign")
    lock = root / ".supervisor.lock"
    if lock.exists():
        old = read(lock)
        if not is_alive(old["pid"]):
            lock.unlink()
        else:
            raise ValueError("Campaign already has a live supervisor")
    write(lock, {"pid": os.getpid(), "started_utc": utc()}, immutable=True)
    campaign_database = (
        "sr_campaign_" + hashlib.sha256(str(logical_fs_path(root.resolve())).encode()).hexdigest()[:24]
    )
    engine, factory = connect(database=campaign_database)
    engine.ready()
    checkpoint = read(root / "checkpoint.json")
    records = [read(path) for path in sorted((root / "records").glob("*.json"))]
    done = {record["job_key"] for record in records}
    jobs = read(root / "plan.json")["jobs"]
    started = time.monotonic()
    initial_spent = checkpoint["spent_wall_s"]
    new_jobs = 0
    status = "COMPLETED"

    def cancellation():
        return (root / "cancel.request").exists() or (
            root.parent / ".requests" / f"{root.name}.cancel"
        ).exists()

    try:
        for job in jobs:
            if runtime_identity() != identity["runtime"]:
                raise ValueError(
                    "Source/dependency drift during campaign; no mixed-source results accepted"
                )
            if job["key"] in done:
                continue
            if cancellation():
                status = "CANCELLED"
                break
            if (
                len(records) >= spec.max_jobs
                or initial_spent + time.monotonic() - started >= spec.max_wall_s
            ):
                status = "NOT_EXECUTED_RESOURCE_LIMIT"
                break
            if max_new_jobs is not None and new_jobs >= max_new_jobs:
                status = "PAUSED_PARTIAL"
                break
            key = job["key"]
            sections = merge(
                read(root / "datasets" / job["dataset"] / "input.json"), job["overrides"]
            )
            sections["optimization"].update(
                seed=job["seed"],
                time_limit_s=spec.job_time_limit_s,
                memory_limit_mb=spec.memory_limit_mb,
            )
            if canonical_hash(sections) != job["input_sha256"]:
                raise ValueError("Reconstructed job input fingerprint mismatch")
            attempt_file = root / "jobs" / f"{key}.json"
            if attempt_file.exists():
                attempts = read(attempt_file)["run_ids"]
            else:
                attempts = []
            final = None
            for attempt in range(spec.max_retries + 1):
                if attempts:
                    with factory() as db:
                        old = projects.get_run(db, attempts[-1])
                        if old.status in ("RUNNING", "CANCEL_REQUESTED"):
                            evidence = root / "artifacts" / old.id / "supervisor.json"
                            if evidence.exists() and is_alive(read(evidence)["child_pid"]):
                                raise ValueError(
                                    "Previous child is still alive; inspect the recorded supervisor before resume"
                                )
                            if not evidence.exists() and (
                                old.started_epoch is None or time.time() - old.started_epoch < 360
                            ):
                                raise ValueError(
                                    "Unresolved worker lease; wait for expiry and inspect before resume"
                                )
                            if old.lease_until is None or old.lease_until > time.time():
                                raise ValueError(
                                    "Worker lease is still live; do not steal it during resume"
                                )
                            db.mark_worker_lost(old)
                            old = projects.get_run(db, old.id)
                        if old.status == "QUEUED":
                            run_id = old.id
                        elif (
                            old.status == "SUCCEEDED"
                            or old.error is None
                            or old.error.get("code") not in ("WORKER_CRASH", "WORKER_LOST")
                        ):
                            final = projects.run_dict(old, include_snapshot=True)
                            break
                        else:
                            if len(attempts) >= spec.max_retries + 1:
                                final = projects.run_dict(old, include_snapshot=True)
                                break
                            run_id = None
                else:
                    run_id = None
                if run_id is None:
                    with factory() as db:
                        project = projects.create_project(db, f"{spec.name}/{key[:12]}")
                        for section in SECTIONS:
                            project = projects.save_section(
                                db,
                                project["id"],
                                section,
                                sections[section],
                                project["revision"],
                            )
                        queued = projects.enqueue(db, project["id"])
                        run_id = queued["id"]
                        attempts.append(run_id)
                        write(attempt_file, {"job_key": key, "run_ids": attempts})
                work_once(
                    factory,
                    root / "artifacts",
                    cancelled=cancellation,
                    cache_root=(root / "artifacts" / run_id / ".stage-cache")
                    if spec.cache_policy == "isolated"
                    else root / ".stage-cache",
                )
                with factory() as db:
                    saved = projects.get_run(db, run_id)
                    final = projects.run_dict(saved, include_snapshot=True)
                if (
                    final["status"] == "SUCCEEDED"
                    or final["error"] is None
                    or final["error"].get("code") not in ("WORKER_CRASH", "WORKER_LOST")
                ):
                    break
            if final is None:
                raise RuntimeError("No terminal job outcome")
            artifact = root / "artifacts" / final["id"]
            if final["snapshot"]["_runtime"] != identity["runtime"]:
                raise ValueError("Job runtime identity differs from campaign identity")
            receipt = read(artifact / "receipt.json")
            validation = (
                verify(final["snapshot"], final["result"])
                if final["result"]
                else {"status": "NO_SOLUTION", "reason": final["error"]}
            )
            record = {k: v for k, v in job.items() if k not in ("overrides", "key", "input_sha256")}
            record.update(
                job_key=key,
                run_id=final["id"],
                attempts=attempts,
                status=final["status"],
                failed_stage=final["stage"] if final["status"] != "SUCCEEDED" else None,
                error=final["error"],
                input_sha256=final["input_sha256"],
                result_sha256=final["result_sha256"],
                validation=validation,
                wall_s=receipt["wall_s"],
                peak_child_rss_bytes=receipt["peak_child_rss_bytes"],
                sampled_child_cpu_s=receipt["sampled_child_cpu_s"],
                started_utc=receipt["started_utc"],
                ended_utc=receipt["ended_utc"],
            )
            if final["result"]:
                stages = final["result"]["stages"]
                joint = final["result"].get("joint")
                if joint:
                    record["solution_feasible"] = joint.get("best") is not None
                    record.update(
                        joint_objective=(joint.get("best") or {}).get("score"),
                        joint_evaluations=joint["evaluations"],
                        joint_iterations_to_best=max(
                            (e.get("iteration", 0) for e in joint["trace"] if e.get("accepted")),
                            default=0,
                        ),
                        joint_status=joint["status"],
                        proof_status=joint["proof_status"],
                        certificate_verification=(joint.get("verification") or {}).get("status"),
                        holdout_objective=joint.get("holdout", {}).get("score"),
                        joint_gap=(joint.get("certificate") or {}).get("absolute_gap"),
                        joint_evaluated_states=(joint.get("certificate") or {}).get(
                            "evaluated_states"
                        ),
                        joint_pruned_states=(joint.get("certificate") or {}).get("pruned_states"),
                    )
                for stage, key_name in (
                    ("T1", "t1_objective"),
                    ("T2", "t2_objective"),
                    ("T3", "t3_objective"),
                ):
                    if stage in stages:
                        record[key_name] = stages[stage]["objective"]
                record["mip_gap"] = stages.get("T3", {}).get("mip_gap")
                if "T4" in stages:
                    record.update(
                        {
                            k: v
                            for k, v in stages["T4"]["metrics"].items()
                            if isinstance(v, (int, float, str))
                        }
                    )
                if joint and joint.get("best"):
                    record["first_scenario_mean_distance_m"] = record.get("mean_distance_m")
                    record["first_scenario_mean_wait_s"] = record.get("mean_wait_s")
                    components = joint["best"]["components"]
                    scales = joint["normalization"]["scales"]
                    record["mean_distance_m"] = components[0] * scales[0]
                    record["mean_wait_s"] = components[1] * scales[1]
                    record["training_scenario_seeds"] = joint["best"]["scenario_seeds"]
            write(root / "records" / f"{key}.json", record, immutable=True)
            records.append(record)
            new_jobs += 1
            done.add(key)
            write(
                root / "checkpoint.json",
                {
                    "status": "RUNNING",
                    "planned": len(jobs),
                    "completed": len(records),
                    "spent_wall_s": initial_spent + time.monotonic() - started,
                },
            )
            write(root / "integrity.json", fingerprint(root))
            print(
                f"{job['experiment']}/{job['dataset']}/{job['treatment']}/{job['seed']}: {final['status']}",
                flush=True,
            )
    except Exception:
        status = "FAILED"
        raise
    finally:
        write(
            root / "checkpoint.json",
            {
                "status": status if len(records) < len(jobs) else "COMPLETED",
                "planned": len(jobs),
                "completed": len(records),
                "spent_wall_s": initial_spent + time.monotonic() - started,
                "not_executed": len(jobs) - len(records),
                "ended_utc": utc(),
            },
        )
        write(root / "integrity.json", fingerprint(root))
        engine.dispose()
        lock.unlink()
    return read(root / "checkpoint.json")
