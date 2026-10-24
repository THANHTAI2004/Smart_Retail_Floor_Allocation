"""Export unique-job descriptive results with explicit historical/follow-up accounting."""

import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from paper_recovery import supplemental_rows
from smart_retail.application.experiments.storage import read
from smart_retail.application.workflow import canonical_hash

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())
BASE = ROOT / "experiments/results/20261023-paper-v2"
METRICS = [
    "joint_objective",
    "test_objective",
    "test_mean_distance_m",
    "test_mean_wait_s",
    "wall_s",
]


def csv_file(path, rows):
    columns = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "experiments/reports/20261023-paper-v2" / f"user-statistics-{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    original, plans, blocks = {}, {}, {}
    identities = set()
    for row in read(ROOT / "experiments/configs/paper-v2/index.json"):
        config = read(ROOT / "experiments/configs/paper-v2" / row["config"])
        name = config["name"]
        blocks[name] = row["block"]
        identities.add(canonical_hash(read(BASE / name / "identity.json")["runtime"]))
        for job in read(BASE / name / "plan.json")["jobs"]:
            plans[(name, job["key"])] = job
        for path in (BASE / name / "records").glob("*.json"):
            record = read(path)
            original[(name, record["job_key"])] = record
    followups, all_retry = {}, []
    for row in supplemental_rows():
        name = read(Path(row["config"]))["name"]
        identities.add(canonical_hash(read(BASE / name / "identity.json")["runtime"]))
        retry_plan = {j["key"]: j for j in read(BASE / name / "plan.json")["jobs"]}
        for path in (BASE / name / "records").glob("*.json"):
            record = read(path)
            key = (row["source_campaign"], record["job_key"])
            assert (
                key in plans
                and retry_plan[key[1]]["input_sha256"] == plans[key]["input_sha256"]
            )
            assert (
                canonical_hash(
                    read(BASE / name / "artifacts" / record["run_id"] / "input.json")
                )
                == record["input_sha256"]
            )
            if key in original:
                assert record["input_sha256"] == original[key]["input_sha256"]
            all_retry.append(record)
            if record["job_key"] in row["target_job_keys"]:
                assert key not in followups
                followups[key] = record
    assert len(identities) == 1
    selected, history = [], []
    for key in plans:
        previous = original.get(key)
        current = followups.get(key, previous)
        if previous and previous["status"] != "SUCCEEDED":
            history.append(
                {
                    "source_campaign": key[0],
                    "job_key": key[1],
                    "original_status": previous["status"],
                    "original_code": (previous.get("error") or {}).get("code"),
                    "followup_status": followups.get(key, {}).get("status"),
                    "followup_code": (followups.get(key, {}).get("error") or {}).get(
                        "code"
                    ),
                }
            )
        if current:
            if current["status"] == "SUCCEEDED":
                assert current["validation"]["status"] == "PASS"
            selected.append(
                {
                    **current,
                    "block": blocks[key[0]],
                    "source_campaign": key[0],
                    "record_origin": "followup" if key in followups else "original",
                    "original_status": previous["status"] if previous else "UNEXECUTED",
                }
            )
    block_rows = []
    for block in ["X1", "X4", "X2", "X2b", "X5", "X6", "X3"]:
        records = [r for r in selected if r["block"] == block]
        planned = sum(blocks[name] == block for name, _ in plans)
        counts = Counter(r["status"] for r in records)
        block_rows.append(
            {
                "block": block,
                "planned": planned,
                "executed": len(records),
                "succeeded": counts["SUCCEEDED"],
                "failed": len(records) - counts["SUCCEEDED"],
                "unexecuted": planned - len(records),
                "evaluation_status": dict(
                    Counter(
                        r.get("evaluation_status", "NOT_APPLICABLE") for r in records
                    )
                ),
            }
        )
    grouped = defaultdict(list)
    for record in selected:
        grouped[(record["block"], record["treatment"])].append(record)
    arms = []
    for (block, arm), records in sorted(grouped.items()):
        entry = {
            "block": block,
            "treatment": arm,
            "executed": len(records),
            "succeeded": sum(r["status"] == "SUCCEEDED" for r in records),
        }
        entry["failed"] = len(records) - entry["succeeded"]
        for metric in METRICS:
            values = [
                r[metric]
                for r in records
                if r["status"] == "SUCCEEDED"
                and isinstance(r.get(metric), (int, float))
            ]
            entry[metric + "_n"] = len(values)
            entry[metric + "_mean"] = statistics.mean(values) if values else None
        arms.append(entry)
    pair_key = lambda r: (
        r["experiment"],
        r["dataset"],
        r["seed"],
        r.get("cv_fold"),
        r.get("repetition"),
    )
    comparisons = []
    for (block, arm), records in sorted(grouped.items()):
        if arm == "baseline" or (block, "baseline") not in grouped:
            continue
        baseline = {
            pair_key(r): r
            for r in grouped[(block, "baseline")]
            if r["status"] == "SUCCEEDED"
        }
        metric = "joint_objective" if block == "X1" else "test_objective"
        pairs = [
            (baseline[pair_key(r)], r)
            for r in records
            if r["status"] == "SUCCEEDED"
            and pair_key(r) in baseline
            and isinstance(r.get(metric), (int, float))
            and isinstance(baseline[pair_key(r)].get(metric), (int, float))
        ]
        if not pairs:
            continue
        before = statistics.mean(a[metric] for a, _ in pairs)
        after = statistics.mean(b[metric] for _, b in pairs)
        comparisons.append(
            {
                "block": block,
                "treatment": arm,
                "reference": "baseline",
                "metric": metric,
                "matched_pairs": len(pairs),
                "instances": len({a["dataset"] for a, _ in pairs}),
                "reference_mean": before,
                "treatment_mean": after,
                "reduction_percent": 100 * (before - after) / before
                if before
                else None,
                "wins": sum(b[metric] < a[metric] - 1e-10 for a, b in pairs),
                "ties": sum(abs(b[metric] - a[metric]) <= 1e-10 for a, b in pairs),
                "losses": sum(b[metric] > a[metric] + 1e-10 for a, b in pairs),
            }
        )
    summary = {
        "checked_utc": datetime.now(UTC).isoformat(),
        "selection_rule": "One row per original job; explicit requested follow-up when present, otherwise original. All original outcomes retained separately. Paired-fold extras excluded.",
        "planned": len(plans),
        "executed_unique": len(selected),
        "succeeded_latest_attempt": sum(r["status"] == "SUCCEEDED" for r in selected),
        "failed_latest_attempt": sum(r["status"] != "SUCCEEDED" for r in selected),
        "original_attempts": len(original),
        "original_failures": sum(r["status"] != "SUCCEEDED" for r in original.values()),
        "supplemental_attempts_including_paired_extras": len(all_retry),
        "supplemental_target_attempts": len(followups),
        "all_attempt_failure_codes": dict(
            Counter(
                (r.get("error") or {}).get("code", r["status"])
                for r in list(original.values()) + all_retry
                if r["status"] != "SUCCEEDED"
            )
        ),
        "latest_failure_codes": dict(
            Counter(
                (r.get("error") or {}).get("code", r["status"])
                for r in selected
                if r["status"] != "SUCCEEDED"
            )
        ),
        "certificate_verification": dict(
            Counter(
                r.get("certificate_verification", "NOT_APPLICABLE")
                for r in selected
                if r["block"] == "X1"
            )
        ),
        "blocks": block_rows,
        "arms": arms,
        "paired_descriptive_comparisons": comparisons,
        "watcher": {
            k: read(ROOT / "var/paper-unattended/status.json").get(k)
            for k in ["status", "updated_utc", "error", "backup"]
        },
        "limits": [
            "Descriptive comparisons only; no new significance tests performed.",
            "Matched successful pairs exclude failed baseline pairs; report success rates alongside scores.",
            "Folds sharing training data are not independent.",
            "Wall times are worker times, not whole-campaign elapsed times; scheduling and extra campaign budgets varied.",
            "Synthetic datasets; no field validation or production capacity claim.",
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "selected-records.json").write_text(
        json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    csv_file(
        out / "block-summary.csv",
        [{k: v for k, v in r.items() if k != "evaluation_status"} for r in block_rows],
    )
    csv_file(out / "method-summary.csv", arms)
    csv_file(out / "paired-comparisons.csv", comparisons)
    csv_file(out / "original-failure-followups.csv", history)
    csv_file(
        out / "latest-failures.csv",
        [
            {
                "block": r["block"],
                "dataset": r["dataset"],
                "treatment": r["treatment"],
                "seed": r["seed"],
                "fold": r.get("cv_fold"),
                "code": (r.get("error") or {}).get("code"),
                "message": (r.get("error") or {}).get("message"),
                "job_key": r["job_key"],
                "origin": r["record_origin"],
            }
            for r in selected
            if r["status"] != "SUCCEEDED"
        ],
    )
    manifest = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in out.iterdir()
        if p.is_file()
    }
    (out / "checksums.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(str(out), flush=True)
    print(
        json.dumps(
            {
                k: v
                for k, v in summary.items()
                if k not in {"arms", "paired_descriptive_comparisons", "limits"}
            },
            ensure_ascii=True,
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
