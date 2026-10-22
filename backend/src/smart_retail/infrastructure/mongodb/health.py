"""Connection/index verification CLI. Credentials never appear in reports."""

import argparse
import json
from pathlib import Path

from smart_retail.infrastructure.mongodb.client import connect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cutover-check", action="store_true")
    args = parser.parse_args()
    owner, _ = connect()
    try:
        owner.ready()
        receipt_path = Path("var/mongodb/cutover.json")
        if args.cutover_check and receipt_path.exists():
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if receipt[
                "database"
            ] != owner.settings.database or not owner.database.migration_receipts.find_one(
                {
                    "_id": receipt["receipt_id"],
                    "status": "MONGODB_MIGRATION_VERIFIED",
                    "source_sha256": receipt["source_sha256"],
                }
            ):
                raise RuntimeError("Cutover receipt does not match this MongoDB target")
        result = {
            "status": "ok",
            "database": "mongodb",
            "database_name": owner.settings.database,
            "version": owner.database.command("buildInfo")["version"],
            "indexes": {
                n: list(owner.database[n].index_information())
                for n in ["projects", "optimization_runs", "worker_heartbeats"]
            },
        }
        if args.output:
            if args.output.exists():
                raise FileExistsError(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print("MongoDB connection and indexes verified")
    finally:
        owner.dispose()


if __name__ == "__main__":
    main()
