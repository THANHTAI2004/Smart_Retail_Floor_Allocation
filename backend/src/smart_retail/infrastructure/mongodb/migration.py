"""Read-only SQLite extraction, recoverable backup and conflict-safe MongoDB import."""

import argparse
import hashlib
import json
import sqlite3
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pymongo.errors import DuplicateKeyError

from smart_retail.contracts.inputs import validate_references
from smart_retail.infrastructure.mongodb.client import connect
from smart_retail.infrastructure.mongodb.serializers import record_document, sha
from smart_retail.infrastructure.repositories.contracts import ProjectRecord, RunRecord


def read_sqlite(path):
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    rows = {
        name: [dict(row) for row in connection.execute("SELECT * FROM " + name)]
        for name in (
            "projects",
            "product_keys",
            "orders",
            "order_lines",
            "optimization_runs",
            "worker_heartbeats",
        )
    }
    connection.close()
    for row in rows["projects"]:
        row["sections"] = json.loads(row["sections"])
    for row in rows["optimization_runs"]:
        for field in ("snapshot", "result", "error"):
            if isinstance(row[field], str):
                row[field] = json.loads(row[field])
    return rows


def backup_sqlite(source, directory):
    directory.mkdir(parents=True, exist_ok=False)
    backup = directory / "sqlite-backup.db"
    original = sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)
    destination = sqlite3.connect(backup)
    original.backup(destination)
    destination.close()
    original.close()
    check = sqlite3.connect(backup.resolve().as_uri() + "?mode=ro", uri=True)
    assert check.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    check.close()
    digest = hashlib.sha256(backup.read_bytes()).hexdigest()
    (directory / "VERIFIED.json").write_text(
        json.dumps({"backup": str(backup), "sha256": digest, "integrity_check": "ok"}, indent=2),
        encoding="utf-8",
    )
    return backup, digest


def source_documents(rows, active_policy="reject"):
    projects = [ProjectRecord(**row) for row in rows["projects"]]
    by_project = {p.id: p for p in projects}
    for table in ("product_keys", "orders", "order_lines", "optimization_runs"):
        if any(row["project_id"] not in by_project for row in rows[table]):
            raise ValueError("Source orphan project reference in " + table)
    for project in projects:
        errors = validate_references(project.sections)
        if errors:
            raise ValueError("Source project reference violation: " + project.id)
        order_data = project.sections.get("orders", {})
        keys = {r["sku"] for r in rows["product_keys"] if r["project_id"] == project.id}
        if keys != {p["sku"] for p in project.sections.get("products", {}).get("items", [])}:
            raise ValueError("Source relational product keys differ from embedded aggregate")
        orders = [
            {k: v for k, v in r.items() if k != "project_id"}
            for r in rows["orders"]
            if r["project_id"] == project.id
        ]
        lines = [
            {k: v for k, v in r.items() if k != "project_id"}
            for r in rows["order_lines"]
            if r["project_id"] == project.id
        ]
        if sorted(orders, key=lambda r: r["id"]) != sorted(
            order_data.get("orders", []), key=lambda r: r["id"]
        ):
            raise ValueError("Source relational orders differ from embedded aggregate")
        if sorted(lines, key=lambda r: (r["order_id"], r["sku"])) != sorted(
            order_data.get("order_lines", []), key=lambda r: (r["order_id"], r["sku"])
        ):
            raise ValueError("Source relational order lines differ from embedded aggregate")
    recovery = []
    runs = []
    for row in rows["optimization_runs"]:
        if row["project_id"] not in by_project:
            raise ValueError("Orphan run")
        if sha(row["snapshot"]) != row["input_sha256"]:
            raise ValueError("Source snapshot checksum mismatch")
        if row["result"] is not None and sha(row["result"]) != row["result_sha256"]:
            raise ValueError("Source result checksum mismatch")
        record = RunRecord(**row)
        if record.status in ("RUNNING", "CANCEL_REQUESTED"):
            if active_policy == "reject":
                raise ValueError(
                    "Active source run: freeze services or specify --active-policy mark-lost"
                )
            recovery.append(
                {"id": record.id, "source_status": record.status, "target_status": "FAILED"}
            )
            record.status = "FAILED"
            record.error = {
                "code": "MIGRATION_RECOVERY_REQUIRED",
                "message": "Imported active source run; original status retained in migration manifest",
            }
        runs.append(record)
    # Historic observations can never make a worker look online after migration.
    workers = [
        {"_id": r["id"], "epoch": 0, "status": "MIGRATED_OFFLINE", "source_epoch": r["epoch"]}
        for r in rows["worker_heartbeats"]
    ]
    return projects, runs, workers, recovery


def migrate(
    source,
    backup_dir,
    output,
    *,
    dry_run=False,
    check_target=False,
    active_policy="reject",
    database=None,
    cutover=False,
):
    if output.exists():
        raise FileExistsError(output)
    backup, digest = backup_sqlite(source, backup_dir)
    rows = read_sqlite(backup)
    report = {
        "status": "DRY_RUN_VALIDATED",
        "started_utc": datetime.now(UTC).isoformat(),
        "source_backup": str(backup),
        "source_sha256": digest,
        "source_counts": {k: len(v) for k, v in rows.items()},
        "scientific_hashes_valid": False,
        "recovery": [],
        "dry_run": dry_run,
        "inserted": {},
        "existing_equal": {},
        "conflicts": [],
    }
    store = None
    try:
        projects, runs, workers, recovery = source_documents(rows, active_policy)
        report["scientific_hashes_valid"] = True
        report["recovery"] = recovery
        if not dry_run or check_target:
            store, _ = connect(database=database)
            store.database.command("ping")
            report["target_database"] = store.settings.database
            report["target_counts_before"] = {
                name: store.database[name].count_documents({})
                for name in ("projects", "optimization_runs", "worker_heartbeats")
            }
            operations = [
                ("projects", projects, store.get_project, store.create_project),
                ("optimization_runs", runs, store.get_run, store.insert_run),
            ]
            # Complete preflight before the first insert; reject conflicting IDs.
            for name, records, getter, _ in operations:
                report["inserted"][name] = 0
                report["existing_equal"][name] = 0
                for record in records:
                    current = getter(record.id)
                    if current is not None and sha(asdict(current)) != sha(asdict(record)):
                        report["conflicts"].append({"collection": name, "id": record.id})
            for worker in workers:
                old = store.database.worker_heartbeats.find_one({"_id": worker["_id"]})
                if old is not None and old != worker:
                    report["conflicts"].append(
                        {"collection": "worker_heartbeats", "id": worker["_id"]}
                    )
            if report["conflicts"]:
                raise ValueError("Target has conflicting document IDs; nothing overwritten")
            if not dry_run:
                store.ready()
                for name, records, getter, insert in operations:
                    for record in records:
                        old = getter(record.id)
                        if old is None:
                            try:
                                insert(record)
                                report["inserted"][name] += 1
                            except DuplicateKeyError:
                                pass
                        else:
                            report["existing_equal"][name] += 1
                        if sha(asdict(getter(record.id))) != sha(asdict(record)):
                            raise ValueError("Target readback mismatch or concurrent target edit")
                for worker in workers:
                    store.database.worker_heartbeats.update_one(
                        {"_id": worker["_id"]}, {"$setOnInsert": worker}, upsert=True
                    )
                    if store.database.worker_heartbeats.find_one({"_id": worker["_id"]}) != worker:
                        raise ValueError("Worker metadata mismatch")
                report["target_matched"] = {
                    "projects": len(projects),
                    "optimization_runs": len(runs),
                    "worker_heartbeats": len(workers),
                    "product_keys": sum(
                        len(p.sections.get("products", {}).get("items", [])) for p in projects
                    ),
                    "orders": sum(
                        len(p.sections.get("orders", {}).get("orders", [])) for p in projects
                    ),
                    "order_lines": sum(
                        len(p.sections.get("orders", {}).get("order_lines", [])) for p in projects
                    ),
                }
                report["status"] = "MONGODB_MIGRATION_VERIFIED"
                receipt_id = str(uuid4())
                report["receipt_id"] = receipt_id
                store.database.migration_receipts.insert_one(
                    {
                        "_id": receipt_id,
                        "source_sha256": digest,
                        "status": report["status"],
                        "matched": report["target_matched"],
                        "source_documents_sha256": sha(
                            [record_document(r) for r in projects + runs]
                        ),
                    }
                )
                if cutover:
                    if recovery:
                        raise ValueError("Cutover requires resolved active source jobs")
                    target = Path("var/mongodb/cutover.json")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists():
                        raise FileExistsError(
                            "Existing cutover receipt must be reviewed, not overwritten"
                        )
                    target.write_text(
                        json.dumps(
                            {
                                "database": store.settings.database,
                                "receipt_id": receipt_id,
                                "source_sha256": digest,
                                "backup": str(backup),
                            },
                            indent=2,
                        ),
                        encoding="utf-8",
                    )
    except Exception as exc:
        report["status"] = "MIGRATION_FAILED"
        report["error_type"] = type(exc).__name__
        raise
    finally:
        report["ended_utc"] = datetime.now(UTC).isoformat()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        if store:
            store.dispose()
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Read-only SQLite -> MongoDB migration with verified external backup"
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--backup-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--database")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-target", action="store_true")
    parser.add_argument("--cutover", action="store_true")
    parser.add_argument("--active-policy", choices=["reject", "mark-lost"], default="reject")
    args = parser.parse_args()
    if args.cutover and args.dry_run:
        parser.error("cutover cannot be a dry run")
    try:
        report = migrate(
            args.source,
            args.backup_dir,
            args.output,
            dry_run=args.dry_run,
            check_target=args.check_target,
            active_policy=args.active_policy,
            database=args.database,
            cutover=args.cutover,
        )
    except Exception as exc:
        print(
            "Migration rejected:",
            type(exc).__name__,
            "; inspect sanitized manifest and source/target privately",
        )
        raise SystemExit(1) from None
    print(report["status"], report.get("target_matched", report["source_counts"]))


if __name__ == "__main__":
    main()
