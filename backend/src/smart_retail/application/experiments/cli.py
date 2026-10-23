"""python -m smart_retail.application.experiments.cli --help"""

import argparse
import math
from pathlib import Path

from smart_retail.application.experiments.campaign import run
from smart_retail.application.experiments.generators import generate
from smart_retail.application.experiments.partition import partition
from smart_retail.application.experiments.reports import report
from smart_retail.application.experiments.storage import read, verify_integrity, write
from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.experiments import CampaignSpec, DatasetSpec
from smart_retail.contracts.inputs import to_domain
from smart_retail.infrastructure.filesystem import normalize_fs_path


def equivalent(a, b, atol=1e-8, rtol=1e-9):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, abs_tol=atol, rel_tol=rtol)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k], atol, rtol) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(equivalent(x, y, atol, rtol) for x, y in zip(a, b))
    return a == b


def compare(left: Path, right: Path):
    left, right = normalize_fs_path(left), normalize_fs_path(right)
    verify_integrity(left)
    verify_integrity(right)
    a = {r["job_key"]: r for r in (read(p) for p in (left / "records").glob("*.json"))}
    b = {r["job_key"]: r for r in (read(p) for p in (right / "records").glob("*.json"))}
    rows = []
    for key in sorted(a.keys() | b.keys()):
        x, y = a.get(key), b.get(key)
        item = {"job_key": key, "present_in_both": x is not None and y is not None}
        if x and y:
            item["same_status"] = x["status"] == y["status"]
            item["same_input_hash"] = x["input_sha256"] == y["input_sha256"]
            item["byte_identical_result"] = (
                x["result_sha256"] is not None and x["result_sha256"] == y["result_sha256"]
            )
            if x["status"] == y["status"] == "SUCCEEDED":
                one = read(left / "artifacts" / x["run_id"] / "result.json")
                two = read(right / "artifacts" / y["run_id"] / "result.json")
                item["numerically_equivalent"] = equivalent(one, two)
            else:
                item["numerically_equivalent"] = None
                item["same_failure_code"] = (x.get("error") or {}).get("code") == (
                    y.get("error") or {}
                ).get("code")
        rows.append(item)
    return {
        "atol": 1e-8,
        "rtol": 1e-9,
        "rows": rows,
        "scope": "Scientific result JSON excludes wall/CPU/cache-hit telemetry, which remains in receipts/stage artifacts",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Synthetic experiment platform; all output paths are explicit"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "resume"):
        sub = commands.add_parser(name)
        sub.add_argument("--config", type=Path, required=True)
        sub.add_argument("--output", type=Path, required=True)
        sub.add_argument("--max-new-jobs", type=int)
    for name in ("status", "verify"):
        sub = commands.add_parser(name)
        sub.add_argument("campaign", type=Path)
    sub = commands.add_parser("analyze", help="Report one campaign or pool split parts")
    sub.add_argument("campaign", type=Path, nargs="+")
    sub.add_argument("--output", type=Path, required=True)
    sub = commands.add_parser("split-config", help="Split a >1,000-job design into parts")
    sub.add_argument("--config", type=Path, required=True)
    sub.add_argument("--output-dir", type=Path, required=True)
    sub.add_argument("--max-jobs", type=int, default=1000)
    sub = commands.add_parser("replay")
    sub.add_argument("campaign", type=Path)
    sub.add_argument("--output", type=Path, required=True)
    sub = commands.add_parser("compare")
    sub.add_argument("left", type=Path)
    sub.add_argument("right", type=Path)
    sub.add_argument("--output", type=Path, required=True)
    sub = commands.add_parser("generate")
    sub.add_argument("--scale", choices=["tiny", "small", "medium", "large"], default="tiny")
    sub.add_argument(
        "--scenario",
        choices=["feasible", "infeasible", "high_load", "volatile", "uneven"],
        default="feasible",
    )
    sub.add_argument("--seed", type=int, default=101)
    sub.add_argument("--output", type=Path, required=True)
    sub = commands.add_parser("validate-dataset")
    sub.add_argument("dataset", type=Path)
    args = parser.parse_args()
    if args.command in ("run", "resume"):
        spec = CampaignSpec.model_validate(read(args.config))
        result = run(
            spec,
            args.output.resolve(),
            resume=args.command == "resume",
            max_new_jobs=args.max_new_jobs,
        )
    elif args.command == "generate":
        args.output.mkdir(parents=True, exist_ok=False)
        data, manifest = generate(
            DatasetSpec(id=args.scale, scale=args.scale, seed=args.seed, scenario=args.scenario)
        )
        write(args.output / "input.json", data, immutable=True)
        write(args.output / "manifest.json", manifest, immutable=True)
        result = manifest
    elif args.command == "validate-dataset":
        data = read(args.dataset / "input.json")
        to_domain(data)
        if canonical_hash(data) != read(args.dataset / "manifest.json")["sha256"]:
            raise ValueError("Dataset fingerprint mismatch")
        result = {"status": "PASS"}
    elif args.command == "status":
        result = read(args.campaign / "checkpoint.json")
    elif args.command == "verify":
        result = verify_integrity(args.campaign)
    elif args.command == "analyze":
        result = report(args.campaign, args.output)
    elif args.command == "split-config":
        args.output_dir.mkdir(parents=True, exist_ok=False)
        parts = partition(read(args.config), args.max_jobs)
        for part in parts:
            write(
                args.output_dir / f"{part.name}.json", part.model_dump(mode="json"), immutable=True
            )
        result = {part.name: part.max_jobs for part in parts}
    elif args.command == "compare":
        result = compare(args.left, args.right)
        write(args.output, result, immutable=True)
    else:
        verify_integrity(args.campaign)
        spec = CampaignSpec.model_validate(read(args.campaign / "configuration.json"))
        result = run(spec, args.output.resolve())
    print(result)


if __name__ == "__main__":
    main()
