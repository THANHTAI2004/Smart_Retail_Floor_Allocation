from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from smart_retail.infrastructure.database import (
    OrderLineRecord,
    OrderRecord,
    ProductKey,
    connect,
)
from smart_retail.workers.runner import work_once
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError


def test_crud_revision_and_partial_updates(client, saved_project, sample):
    pid = saved_project["id"]
    assert client.post(f"/api/projects/{pid}/validate").json()["valid"]
    stale = client.put(
        f"/api/projects/{pid}/inputs/demand?expected_revision=0", json=sample["demand"]
    )
    assert stale.status_code == 409
    updated = {**sample["demand"], "customers": 3}
    response = client.put(f"/api/projects/{pid}/inputs/demand?expected_revision=7", json=updated)
    assert response.status_code == 200
    assert response.json()["sections"]["products"] == saved_project["sections"]["products"]
    assert client.get(f"/api/projects/{pid}").json()["revision"] == 8


def test_bad_input_leaves_database_unchanged(client, saved_project, sample):
    pid = saved_project["id"]
    sample["products"]["items"][0]["category_id"] = "missing"
    response = client.put(
        f"/api/projects/{pid}/inputs/products?expected_revision=7", json=sample["products"]
    )
    assert response.status_code == 422
    assert client.get(f"/api/projects/{pid}").json() == saved_project
    response = client.put(
        f"/api/projects/{pid}/inputs/floorplan?expected_revision=7", json={"boundary": []}
    )
    assert response.status_code == 422


def test_orders_have_relational_foreign_keys(database, saved_project):
    _, factory = database
    with factory() as db:
        assert len(list(db.scalars(select(OrderRecord)))) == 1
        assert len(list(db.scalars(select(OrderLineRecord)))) == 2
        assert len(list(db.scalars(select(ProductKey)))) == 2
        db.add(
            OrderLineRecord(
                project_id=saved_project["id"], order_id="missing", sku="WATER", quantity=1
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()


def test_queue_snapshot_worker_replay_and_report(client, saved_project, database, tmp_path):
    run = client.post(f"/api/projects/{saved_project['id']}/runs").json()
    assert run["status"] == "QUEUED"
    assert work_once(database[1], tmp_path / "artifacts")
    finished = client.get(f"/api/runs/{run['id']}").json()
    assert finished["status"] == "SUCCEEDED", finished
    assert finished["result"]["input_sha256"] == run["input_sha256"]
    assert (tmp_path / "artifacts" / run["id"] / "receipt.json").exists()
    assert (
        client.get(f"/api/runs/{run['id']}/report").json()["run"]["snapshot"]
        == finished["snapshot"]
    )
    csv = client.get(f"/api/runs/{run['id']}/report?format=csv")
    assert "WATER" in csv.text and "RICE" in csv.text
    replay = client.post(f"/api/runs/{run['id']}/replay")
    assert replay.status_code == 202
    assert work_once(database[1], tmp_path / "artifacts")
    replayed = client.get(f"/api/runs/{replay.json()['id']}").json()
    assert replayed["result_sha256"] == finished["result_sha256"]


def test_cancel_queued_is_terminal(client, saved_project, database, tmp_path):
    run = client.post(f"/api/projects/{saved_project['id']}/runs").json()
    cancel = client.post(f"/api/runs/{run['id']}/cancel").json()
    assert cancel["status"] == "CANCELLED"
    assert not work_once(database[1], tmp_path / "artifacts")


def test_worker_time_budget(client, saved_project, sample, database, tmp_path):
    pid = saved_project["id"]
    payload = {**sample["optimization"], "time_limit_s": 0.000001}
    assert (
        client.put(
            f"/api/projects/{pid}/inputs/optimization?expected_revision=7", json=payload
        ).status_code
        == 200
    )
    run = client.post(f"/api/projects/{pid}/runs").json()
    assert work_once(database[1], tmp_path / "artifacts")
    assert client.get(f"/api/runs/{run['id']}").json()["status"] == "TIMED_OUT"


def test_migration_roundtrip(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'migrated.db').as_posix()}"
    monkeypatch.setenv("SMART_RETAIL_DATABASE_URL", url)
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    command.upgrade(config, "head")
    engine, _ = connect(url)
    assert set(inspect(engine).get_table_names()) >= {
        "projects",
        "orders",
        "order_lines",
        "optimization_runs",
    }
    engine.dispose()
    command.downgrade(config, "base")
    engine, _ = connect(url)
    assert inspect(engine).get_table_names() == ["alembic_version"]
    engine.dispose()


def test_missing_project_and_blank_name(client):
    assert client.get("/api/projects/missing").status_code == 404
    assert client.post("/api/projects", json={"name": "  "}).status_code == 422
