"""Replay only historical failed job keys under the current source, without overwriting evidence."""

import argparse
import copy
import hashlib
import json
from pathlib import Path

from smart_retail.application.experiments.campaign import initialize, run
from smart_retail.application.experiments.storage import fingerprint, read, verify_integrity, write
from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.experiments import CampaignSpec
from smart_retail.infrastructure.provenance import runtime_identity


def physical_input(snapshot):
    value = copy.deepcopy(snapshot)
    value.pop("_runtime", None)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    ledger = {"status": "RUNNING", "source": str(source), "runtime": runtime_identity(),
              "campaigns": [], "jobs": []}
    ledger_path = output / "replay-ledger.json"
    write(ledger_path, ledger)
    originals = {}
    try:
        for root in sorted(source.iterdir()):
            if not (root / "configuration.json").exists():
                continue
            failed = [read(p) for p in sorted((root / "records").glob("*.json"))
                      if read(p)["status"] != "SUCCEEDED"]
            if not failed:
                continue
            verify_integrity(root)
            originals[root.name] = hashlib.sha256((root / "integrity.json").read_bytes()).hexdigest()
            spec = CampaignSpec.model_validate(read(root / "configuration.json"))
            target = output / root.name
            initialize(spec, target)
            generated = {job["key"]: job for job in read(target / "plan.json")["jobs"]}
            previous = {job["key"]: job for job in read(root / "plan.json")["jobs"]}
            selected = []
            for record in failed:
                key = record["job_key"]
                if generated[key] != previous[key]:
                    raise ValueError("Reconstructed job inputs/budgets differ from original")
                selected.append(generated[key])
            write(target / "full-plan-receipt.json", read(target / "plan.json"), immutable=True)
            write(target / "plan.json", {"jobs": selected})
            write(target / "replay-selection.json", {
                "original": str(root), "keys": [r["job_key"] for r in failed],
                "original_runtime": read(root / "identity.json")["runtime"],
                "policy": "Same physical inputs and job budgets, current source; separate repair evidence"
            }, immutable=True)
            checkpoint = read(target / "checkpoint.json")
            checkpoint["planned"] = len(selected)
            write(target / "checkpoint.json", checkpoint)
            write(target / "integrity.json", fingerprint(target))
            final = run(spec, target, resume=True)
            verification = verify_integrity(target)
            ledger["campaigns"].append({"name": root.name, "checkpoint": final,
                                        "integrity": verification})
            for old in failed:
                record = read(target / "records" / f"{old['job_key']}.json")
                before = read(root / "artifacts" / old["run_id"] / "input.json")
                after = read(target / "artifacts" / record["run_id"] / "input.json")
                if physical_input(before) != physical_input(after):
                    raise ValueError("Physical input changed during replay")
                row = {"campaign": root.name, "job_key": old["job_key"],
                       "dataset": old["dataset"], "fold": old.get("cv_fold"),
                       "original_run_id": old["run_id"], "run_id": record["run_id"],
                       "old_status": old["status"], "new_status": record["status"],
                       "validation": record["validation"], "error": record.get("error"),
                       "physical_input_sha256": canonical_hash(physical_input(after))}
                result = target / "artifacts" / record["run_id"] / "result.json"
                if result.exists():
                    value = read(result)
                    row["planogram_status"] = value["stages"]["T3"]["status"]
                    row["evaluation_status"] = (value.get("evaluation") or {}).get("status")
                ledger["jobs"].append(row)
            write(ledger_path, ledger)
        for name, digest in originals.items():
            if hashlib.sha256((source / name / "integrity.json").read_bytes()).hexdigest() != digest:
                raise ValueError("Historical integrity manifest changed")
        ledger["status"] = "COMPLETED"
        ledger["summary"] = {"attempted": len(ledger["jobs"]),
                             "succeeded": sum(r["new_status"] == "SUCCEEDED" for r in ledger["jobs"]),
                             "historical_manifests_unchanged": True}
        write(ledger_path, ledger)
        print(json.dumps(ledger["summary"]), flush=True)
    except BaseException as exc:
        ledger.update(status="ERROR", error=f"{type(exc).__name__}: {exc}")
        write(ledger_path, ledger)
        raise


if __name__ == "__main__":
    main()
