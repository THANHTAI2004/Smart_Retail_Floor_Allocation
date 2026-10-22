"""Offline SQLite is a read-only migration source, never the primary runtime."""

import hashlib
import json
import sqlite3
from dataclasses import asdict

import pytest

from smart_retail.application import projects
from smart_retail.infrastructure.mongodb.migration import migrate


def legacy_file(path, store, project):
    queued = projects.enqueue(store, project["id"])
    run = store.get_run(queued["id"])
    c = sqlite3.connect(path)
    c.execute(
        "create table projects (id text,name text,created_at text,sections text,revision int)"
    )
    c.execute("create table product_keys (project_id text,sku text)")
    c.execute("create table orders (project_id text,id text,placed_at text,kind text,due_s real)")
    c.execute("create table order_lines (project_id text,order_id text,sku text,quantity int)")
    c.execute("create table worker_heartbeats (id text,epoch real)")
    c.execute(
        "create table optimization_runs (id text,project_id text,project_revision int,input_sha256 text,snapshot text,status text,stage text,created_at text,started_epoch real,result text,error text,result_sha256 text)"
    )
    c.execute(
        "insert into projects values (?,?,?,?,?)",
        (
            project["id"],
            project["name"],
            project["created_at"],
            json.dumps(project["sections"]),
            project["revision"],
        ),
    )
    for p in project["sections"]["products"]["items"]:
        c.execute("insert into product_keys values (?,?)", (project["id"], p["sku"]))
    for o in project["sections"]["orders"]["orders"]:
        c.execute(
            "insert into orders values (?,?,?,?,?)",
            (project["id"], o["id"], o["placed_at"], o["kind"], o["due_s"]),
        )
    for line in project["sections"]["orders"]["order_lines"]:
        c.execute(
            "insert into order_lines values (?,?,?,?)",
            (project["id"], line["order_id"], line["sku"], line["quantity"]),
        )
    c.execute("insert into worker_heartbeats values (?,?)", ("old-online-worker", 9999999999))
    value = asdict(run)
    fields = [
        "id",
        "project_id",
        "project_revision",
        "input_sha256",
        "snapshot",
        "status",
        "stage",
        "created_at",
        "started_epoch",
        "result",
        "error",
        "result_sha256",
    ]
    c.execute(
        "insert into optimization_runs values (?,?,?,?,?,?,?,?,?,?,?,?)",
        tuple(
            json.dumps(value[k])
            if k in ["snapshot", "result", "error"] and value[k] is not None
            else value[k]
            for k in fields
        ),
    )
    c.commit()
    c.close()
    return run


def test_migration_dry_run_idempotent_conflict_checksums_and_offline_workers(
    database, saved_project, tmp_path
):
    from smart_retail.infrastructure.mongodb.client import connect

    source = tmp_path / "source.db"
    run = legacy_file(source, database[1](), saved_project)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    name = database[0] + "_migrated"
    dry = migrate(
        source,
        tmp_path / "dry-backup",
        tmp_path / "dry.json",
        dry_run=True,
        check_target=True,
        database=name,
    )
    target, _ = connect(database=name)
    assert (
        target.database.projects.count_documents({}) == 0 and dry["status"] == "DRY_RUN_VALIDATED"
    )
    applied = migrate(source, tmp_path / "backup", tmp_path / "apply.json", database=name)
    assert applied["status"] == "MONGODB_MIGRATION_VERIFIED"
    assert target.get_run(run.id).input_sha256 == run.input_sha256
    assert not target.worker_online()
    repeated = migrate(source, tmp_path / "again-backup", tmp_path / "again.json", database=name)
    assert repeated["inserted"]["projects"] == 0 and repeated["existing_equal"]["projects"] == 1
    target.database.projects.update_one(
        {"_id": saved_project["id"]}, {"$set": {"name": "Target edit must survive"}}
    )
    with pytest.raises(ValueError, match="conflicting"):
        migrate(source, tmp_path / "conflict-backup", tmp_path / "conflict.json", database=name)
    assert target.get_project(saved_project["id"]).name == "Target edit must survive"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    target.dispose()


def test_migration_rejects_corrupt_scientific_hash_before_writing(
    database, saved_project, tmp_path
):
    source = tmp_path / "source.db"
    legacy_file(source, database[1](), saved_project)
    c = sqlite3.connect(source)
    c.execute("update optimization_runs set input_sha256='corrupt'")
    c.commit()
    c.close()
    with pytest.raises(ValueError, match="checksum"):
        migrate(
            source, tmp_path / "backup", tmp_path / "report.json", database=database[0] + "_target"
        )
    assert not json.loads((tmp_path / "report.json").read_text())["scientific_hashes_valid"]


def test_migration_orphan_rows_and_active_run_policy(database, saved_project, tmp_path):
    from smart_retail.infrastructure.mongodb.migration import read_sqlite, source_documents

    source = tmp_path / "source.db"
    legacy_file(source, database[1](), saved_project)
    rows = read_sqlite(source)
    rows["product_keys"].append({"project_id": "missing", "sku": "orphan"})
    with pytest.raises(ValueError, match="orphan"):
        source_documents(rows)
    rows["product_keys"].pop()
    for status in ("RUNNING", "CANCEL_REQUESTED"):
        rows["optimization_runs"][0]["status"] = status
        with pytest.raises(ValueError, match="Active source run"):
            source_documents(rows)
        _, runs, workers, recovery = source_documents(rows, active_policy="mark-lost")
        assert runs[0].status == "FAILED"
        assert runs[0].error["code"] == "MIGRATION_RECOVERY_REQUIRED"
        assert recovery[0]["source_status"] == status
        assert rows["optimization_runs"][0]["status"] == status
        assert all(w["epoch"] == 0 and w["status"] == "MIGRATED_OFFLINE" for w in workers)
