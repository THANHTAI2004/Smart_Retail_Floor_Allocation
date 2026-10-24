"""Explicit additional-budget campaigns; immutable originals and exact job inputs."""

import hashlib
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from smart_retail.application.experiments.campaign import initialize
from smart_retail.application.experiments.storage import read, write
from smart_retail.contracts.experiments import CampaignSpec, planned_jobs

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
RESULTS = ROOT / "experiments/results/20261023-paper-v2"
STATE = ROOT / "var/paper-parallel/recovery"
INDEX = STATE / "index.json"


def supplemental_rows():
    return read(INDEX) if INDEX.exists() else []


def shard_specs(config, targets):
    """Close requested keys over existing folds; record any additional paired jobs."""
    groups = defaultdict(list)
    for job in targets:
        groups[(job["experiment"], job["dataset"], job["treatment"])].append(job)
    result = []
    for (experiment, dataset, treatment), jobs in sorted(groups.items()):
        seeds = sorted({j["seed"] for j in jobs})
        chunk_size = 1 if config["job_time_limit_s"] > 60 else 5
        for offset in range(0, len(seeds), chunk_size):
            selected = seeds[offset : offset + chunk_size]
            requested = [j for j in jobs if j["seed"] in selected]
            digest = hashlib.sha256(
                "".join(sorted(j["key"] for j in requested)).encode()
            ).hexdigest()[:12]
            name = f"retry-20261024-{digest}"
            experiment_spec = next(
                e for e in config["experiments"] if e["id"] == experiment
            )
            experiment_spec = {
                **experiment_spec,
                "datasets": [dataset],
                "treatments": [
                    t for t in experiment_spec["treatments"] if t["id"] == treatment
                ],
            }
            spec = CampaignSpec.model_validate(
                {
                    **config,
                    "name": name,
                    "datasets": [d for d in config["datasets"] if d["id"] == dataset],
                    "experiments": [experiment_spec],
                    "seeds": selected,
                    "max_wall_s": 14400.0,
                    "max_jobs": 1000,
                }
            )
            result.append((spec, requested))
    return result


def prepare_recovery():
    """Discover original failures/budget omissions once; publish verified shard mappings."""
    STATE.mkdir(parents=True, exist_ok=True)
    existing = supplemental_rows()
    covered = {
        (r["source_campaign"], key) for r in existing for key in r["target_job_keys"]
    }
    new = []
    for row in read(ROOT / "experiments/configs/paper-v2/index.json"):
        config = read(ROOT / "experiments/configs/paper-v2" / row["config"])
        root = RESULTS / config["name"]
        if not (root / "plan.json").exists():
            continue
        records = {
            r["job_key"]: r
            for p in (root / "records").glob("*.json")
            for r in [read(p)]
        }
        checkpoint = read(root / "checkpoint.json")
        plan = read(root / "plan.json")["jobs"]
        requested = [
            j
            for j in plan
            if (config["name"], j["key"]) not in covered
            and (
                (j["key"] in records and records[j["key"]]["status"] != "SUCCEEDED")
                or (
                    j["key"] not in records
                    and checkpoint["status"] == "NOT_EXECUTED_RESOURCE_LIMIT"
                )
            )
        ]
        for spec, targets in shard_specs(config, requested):
            target = RESULTS / spec.name
            cfg = STATE / "configs" / f"{spec.name}.json"
            if not cfg.exists():
                write(cfg, spec.model_dump(mode="json"), immutable=True)
            elif read(cfg) != spec.model_dump(mode="json"):
                raise RuntimeError("Supplemental configuration collision")
            if not target.exists():
                initialize(spec, target)
            actual = read(target / "plan.json")["jobs"]
            original = {j["key"]: j for j in plan}
            for job in actual:
                if (
                    job["key"] not in original
                    or job["input_sha256"] != original[job["key"]]["input_sha256"]
                ):
                    raise RuntimeError(
                        "Supplemental job differs from frozen original input"
                    )
            keys = {j["key"] for j in targets}
            if not keys <= {j["key"] for j in actual}:
                raise RuntimeError("Supplemental plan misses requested jobs")
            new.append(
                {
                    "block": "RECOVERY",
                    "config": str(cfg),
                    "jobs": planned_jobs(spec),
                    "job_time_limit_s": spec.job_time_limit_s,
                    "source_campaign": config["name"],
                    "source_block": row["block"],
                    "target_job_keys": sorted(keys),
                    "original_outcomes": {
                        k: records[k]["status"]
                        if k in records
                        else "NOT_EXECUTED_RESOURCE_LIMIT"
                        for k in sorted(keys)
                    },
                    "paired_extra_job_keys": sorted(
                        j["key"] for j in actual if j["key"] not in keys
                    ),
                    "created_utc": datetime.now(UTC).isoformat(),
                    "additional_campaign_budget_s": spec.max_wall_s,
                    "input_checks": "All generated job keys and input SHA256 equal frozen originals",
                }
            )
    if new:
        write(INDEX, existing + new)
    return new


def coverage():
    entries = []
    for row in supplemental_rows():
        name = read(Path(row["config"]))["name"]
        records = {
            r["job_key"]: r
            for p in (RESULTS / name / "records").glob("*.json")
            for r in [read(p)]
        }
        for key in row["target_job_keys"]:
            record = records.get(key)
            entries.append(
                {
                    "source_campaign": row["source_campaign"],
                    "job_key": key,
                    "original_status": row["original_outcomes"][key],
                    "recovery_campaign": name,
                    "status": record["status"] if record else "PENDING",
                    "record_path": str(RESULTS / name / "records" / f"{key}.json")
                    if record
                    else None,
                }
            )
    by_original = {(e["source_campaign"], e["job_key"]): e for e in entries}
    planned = executed = succeeded = failed = 0
    for row in read(ROOT / "experiments/configs/paper-v2/index.json"):
        name = read(ROOT / "experiments/configs/paper-v2" / row["config"])["name"]
        primary = RESULTS / name
        originals = {
            r["job_key"]: r
            for p in (primary / "records").glob("*.json")
            for r in [read(p)]
        }
        for job in read(primary / "plan.json")["jobs"]:
            planned += 1
            followup = by_original.get((name, job["key"]))
            status = (
                followup["status"]
                if followup and followup["status"] != "PENDING"
                else originals.get(job["key"], {}).get("status")
            )
            executed += status is not None
            succeeded += status == "SUCCEEDED"
            failed += status == "FAILED"
    return {
        "targets": len(entries),
        "executed": sum(e["status"] != "PENDING" for e in entries),
        "succeeded": sum(e["status"] == "SUCCEEDED" for e in entries),
        "failed": sum(e["status"] == "FAILED" for e in entries),
        "entries": entries,
        "primary_job_coverage": {
            "planned": planned,
            "executed_unique": executed,
            "succeeded_latest_attempt": succeeded,
            "failed_latest_attempt": failed,
            "unexecuted": planned - executed,
            "historical_outcomes_preserved": True,
        },
    }


if __name__ == "__main__":
    added = prepare_recovery()
    print(
        {
            "new_shards": len(added),
            "target_jobs": sum(len(r["target_job_keys"]) for r in added),
            "execution_jobs": sum(r["jobs"] for r in added),
        }
    )
