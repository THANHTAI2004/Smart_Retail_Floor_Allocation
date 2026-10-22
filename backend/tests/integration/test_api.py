import copy

from smart_retail.infrastructure.database import connect
from smart_retail.workers.runner import work_once


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


def test_orders_references_are_checked_atomically_in_project_aggregate(
    client, database, saved_project
):
    _, factory = database
    with factory() as db:
        stored = db.get_project(saved_project["id"])
        assert len(stored.sections["orders"]["orders"]) == 1
        assert len(stored.sections["orders"]["order_lines"]) == 2
        assert len(stored.sections["products"]["items"]) == 2
    bad = copy.deepcopy(saved_project["sections"]["orders"])
    bad["order_lines"][0]["order_id"] = "missing"
    response = client.put(
        f"/api/projects/{saved_project['id']}/inputs/orders?expected_revision=7", json=bad
    )
    assert response.status_code == 422
    assert client.get(f"/api/projects/{saved_project['id']}").json() == saved_project


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


def test_mongo_reconnect_preserves_project_and_indexes(database, saved_project):
    name, _ = database
    owner, _ = connect(database=name)
    owner.ready()
    assert owner.get_project(saved_project["id"]).revision == 7
    assert "queue_status_created" in owner.database.optimization_runs.index_information()
    owner.dispose()
    reopened, _ = connect(database=name)
    reopened.ready()
    assert reopened.get_project(saved_project["id"]).sections == saved_project["sections"]
    reopened.dispose()


def test_missing_project_and_blank_name(client):
    assert client.get("/api/projects/missing").status_code == 404
    assert client.post("/api/projects", json={"name": "  "}).status_code == 422
