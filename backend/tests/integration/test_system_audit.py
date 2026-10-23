"""Cross-boundary audit receipts from real isolated MongoDB and injected outages."""

import copy
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest
from pymongo import MongoClient

from smart_retail.contracts.inputs import SECTIONS
from smart_retail.infrastructure.mongodb.serializers import Payloads, sha
from smart_retail.workers.resources import sample as resource_sample
from smart_retail.workers.runner import read_progress, work_once


def receipt(name, value):
    destination = os.getenv("SMART_RETAIL_AUDIT_OUTPUT")
    if destination:
        path = Path(destination) / "checks" / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def test_each_input_save_matches_direct_mongo_readback(client, database, sample):
    project = client.post("/api/projects", json={"name": "Seven input readback audit"}).json()
    store = database[1]()
    checks = []
    for section, payload in sample.items():
        before = project["revision"]
        response = client.put(
            f"/api/projects/{project['id']}/inputs/{section}",
            params={"expected_revision": before},
            json=payload,
        )
        assert response.status_code == 200, response.text
        project = response.json()
        direct = store.get_project(project["id"])
        assert direct.sections == project["sections"]
        assert direct.revision == before + 1
        assert client.get(f"/api/projects/{project['id']}").json()["sections"] == direct.sections
        checks.append(
            {
                "section": section,
                "revision": direct.revision,
                "direct_mongodb_sha256": sha(direct.sections),
                "http_status": 200,
            }
        )
    assert len(checks) == 7
    receipt("seven-input-readback", {"status": "PASS", "database": database[0], "checks": checks})


def test_invalid_input_matrix_is_atomic(client, database, saved_project, sample):
    store = database[1]()
    pid = saved_project["id"]
    before = store.get_project(pid)
    cases = []
    for section in sample:
        if any(field.is_required() for field in SECTIONS[section].model_fields.values()):
            cases.append((section, {"schema_version": "1.1"}, "missing-fields"))
        cases.append(
            (section, {**sample[section], "unknown_field": "must-not-disappear"}, "extra-field")
        )
    products = copy.deepcopy(sample["products"])
    products["items"][0]["category_id"] = "UNKNOWN"
    cases.append(("products", products, "unknown-category"))
    products = copy.deepcopy(sample["products"])
    products["items"][0]["width_m"] = -1
    cases.append(("products", products, "negative-size"))
    products = copy.deepcopy(sample["products"])
    products["items"].append(copy.deepcopy(products["items"][0]))
    cases.append(("products", products, "duplicate-sku"))
    outcomes = []
    for section, payload, reason in cases:
        response = client.put(
            f"/api/projects/{pid}/inputs/{section}",
            params={"expected_revision": before.revision},
            json=payload,
        )
        assert response.status_code == 422, (section, reason, response.text)
        assert store.get_project(pid) == before
        outcomes.append({"section": section, "case": reason, "status": 422, "db_unchanged": True})
    response = client.put(
        f"/api/projects/{pid}/inputs/demand", params={"expected_revision": 0}, json=sample["demand"]
    )
    assert response.status_code == 409
    receipt("invalid-input-matrix", {"status": "PASS", "cases": outcomes, "revision_conflict": 409})


def test_project_oversize_refused_before_mutation(database, saved_project):
    store = database[1]()
    before = store.get_project(saved_project["id"])
    with pytest.raises(ValueError, match="8 MiB"):
        store.save_project(before.id, before.revision, {"oversize": "x" * (9 * 1024**2)})
    assert store.get_project(before.id) == before


def test_actual_database_disconnect_is_sanitized_503(client, database):
    # Replace only this isolated API store's real driver connection after startup.
    # A real refused TCP connection triggers PyMongo, not a fake database/error.
    store = client.app.state.session_factory()
    store.client.close()
    store.client = MongoClient(
        "mongodb://127.0.0.1:1",
        serverSelectionTimeoutMS=250,
        connectTimeoutMS=250,
        socketTimeoutMS=250,
    )
    store.database = store.client[database[0]]
    store.payloads = Payloads(store.database)
    began = time.monotonic()
    response = client.get("/api/projects")
    assert response.status_code == 503
    assert response.json()["code"] == "DATABASE_UNAVAILABLE"
    assert "mongodb://" not in response.text
    assert time.monotonic() - began < 5
    receipt(
        "database-disconnect",
        {
            "status": "PASS",
            "http_status": 503,
            "elapsed_s": time.monotonic() - began,
            "credentials_exposed": False,
        },
    )


def test_bounded_api_latency_and_resource_observation(client, saved_project):
    durations = []
    before = resource_sample(os.getpid())
    for _ in range(30):
        start = time.perf_counter()
        response = client.get(f"/api/projects/{saved_project['id']}")
        durations.append(time.perf_counter() - start)
        assert response.status_code == 200
        assert response.json()["revision"] == saved_project["revision"]
    ordered = sorted(durations)
    receipt(
        "api-latency",
        {
            "status": "PASS",
            "requests": 30,
            "mean_s": sum(durations) / 30,
            "p50_s": ordered[14],
            "p95_s": ordered[28],
            "max_s": max(durations),
            "before_resources": before,
            "after_resources": resource_sample(os.getpid()),
            "scope": "Sequential ASGI/real MongoDB latency, not network load or long-duration leak proof",
        },
    )


def test_real_worker_process_crash_and_expired_lease_recovery(
    client, saved_project, sample, database, tmp_path
):
    pid = saved_project["id"]
    floor = {**sample["floorplan"], "boundary": [[0, 0], [60, 0], [60, 60], [0, 60]]}
    assert (
        client.put(
            f"/api/projects/{pid}/inputs/floorplan?expected_revision=7", json=floor
        ).status_code
        == 200
    )
    job = client.post(f"/api/projects/{pid}/runs").json()
    artifacts = tmp_path / "crashed-worker"
    env = dict(os.environ)
    env["MONGODB_DATABASE"] = database[0]
    env["SMART_RETAIL_ARTIFACTS"] = str(artifacts)
    with (tmp_path / "worker.log").open("wb") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "smart_retail.workers.runner", "--once"],
            env=env,
            stdout=log,
            stderr=log,
            start_new_session=os.name != "nt",
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if read_progress(artifacts / job["id"] / "progress.json") == "T4":
                    break
                assert process.poll() is None, "Worker exited before crash checkpoint"
                time.sleep(0.02)
            else:
                raise AssertionError("T4 did not start")
        finally:
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        check=True,
                        capture_output=True,
                    )
                else:
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=10)
    store = database[1]()
    old = store.get_run(job["id"])
    assert old.status == "RUNNING"
    store.database.optimization_runs.update_one(
        {"_id": old.id}, {"$set": {"lease_until": time.time() - 1}}
    )
    assert not work_once(database[1], artifacts, heartbeat_id="restart-audit")
    saved = store.get_run(old.id)
    assert saved.status == "TIMED_OUT" and saved.error["code"] == "WORKER_LOST"
    assert saved.result is None
    old.status = "SUCCEEDED"
    assert store.publish(old) is None
    receipt(
        "real-worker-crash",
        {
            "status": "PASS",
            "process_exit": process.returncode,
            "before_recovery": "RUNNING",
            "after_recovery": saved.status,
            "old_owner_fenced": True,
        },
    )
