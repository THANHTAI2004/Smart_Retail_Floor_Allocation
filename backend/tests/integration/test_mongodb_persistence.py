"""Real MongoDB concurrency, fencing, overflow and persistence tests; no fake driver."""

import copy
import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from bson import Binary

from smart_retail.application import projects
from smart_retail.infrastructure.mongodb.serializers import sha


def test_concurrent_project_updates_exactly_one_revision_wins(database, saved_project, sample):
    store = database[1]()
    pid = saved_project["id"]

    def save(i):
        try:
            return projects.save_section(
                store, pid, "demand", {**sample["demand"], "customers": i}, 7
            )["revision"]
        except projects.ServiceError as exc:
            return exc.status

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(save, range(8)))
    assert results.count(8) == 1 and results.count(409) == 7
    assert store.get_project(pid).revision == 8
    with pytest.raises(projects.ServiceError) as error:
        projects.save_section(store, "missing", "demand", sample["demand"], 0)
    assert error.value.status == 404


def test_concurrent_atomic_claim_unique_and_expired_owner_fenced(database, saved_project):
    store = database[1]()
    queued = [projects.enqueue(store, saved_project["id"]) for _ in range(16)]
    with ThreadPoolExecutor(max_workers=12) as executor:
        claims = list(executor.map(lambda i: store.claim(f"worker-{i}", time.time()), range(24)))
    claimed = [r for r in claims if r]
    assert len({r.id for r in claimed}) == len(claimed) == 16
    assert {r.id for r in claimed} == {r["id"] for r in queued}
    old = claimed[0]
    store.database.optimization_runs.update_one(
        {"_id": old.id}, {"$set": {"lease_until": time.time() - 1}}
    )
    assert store.recover_expired(time.time()) == 1
    assert store.get_run(old.id).status == "TIMED_OUT"
    assert not store.renew(old)
    old.status = "SUCCEEDED"
    assert store.publish(old) is None
    # Simulate an explicit operator retry of that document; old token cannot
    # overwrite a new owner's state even if it reads the new record afterward.
    store.database.optimization_runs.update_one({"_id": old.id}, {"$set": {"status": "QUEUED"}})
    new = store.claim("new-owner", time.time())
    assert new.id == old.id
    fresh = store.get_run(old.id)
    fresh.status = "SUCCEEDED"
    assert store.publish(fresh, owner=old) is None
    assert store.get_run(old.id).worker_id == "new-owner"
    assert store.get_run(old.id).status == "RUNNING"


def test_cancel_wins_final_publish_race_and_snapshot_immutable(database, saved_project):
    store = database[1]()
    queued = projects.enqueue(store, saved_project["id"])
    record = store.claim("race-worker", time.time())
    original = copy.deepcopy(record.snapshot)
    record.snapshot["optimization"]["seed"] = 999
    record.status = "SUCCEEDED"
    store.cancel_run(record.id)
    saved = store.publish(record)
    assert saved.status == "CANCELLED"
    assert saved.snapshot == original
    assert saved.input_sha256 == queued["input_sha256"]


def test_gridfs_large_result_and_arbitrary_precision_numbers_roundtrip(database, saved_project):
    store = database[1]()
    queued = projects.enqueue(store, saved_project["id"])
    record = store.get_run(queued["id"])
    record.id = str(uuid4())
    record.status = "SUCCEEDED"
    record.result = {"large": "x" * (17 * 1024**2), "proof_fraction": [10**120 + 7, 10**100 + 3]}
    record.result_sha256 = sha(record.result)
    store.insert_run(record)
    raw = store.database.optimization_runs.find_one({"_id": record.id})
    assert raw["result"] is None and raw["result_ref"]["bytes"] > 16 * 1024**2
    reopened = store.get_run(record.id)
    assert reopened.result == record.result and sha(reopened.result) == record.result_sha256
    blob = raw["result_ref"]["id"]
    chunk = store.database.research_payloads.chunks.find_one({"files_id": blob, "n": 0})
    store.database.research_payloads.chunks.update_one(
        {"_id": chunk["_id"]}, {"$set": {"data": Binary(b"!" + bytes(chunk["data"])[1:])}}
    )
    with pytest.raises(ValueError, match="checksum"):
        store.get_run(record.id)


def test_worker_restart_recovery_and_non_ttl_indexes(database, saved_project):
    store = database[1]()
    projects.enqueue(store, saved_project["id"])
    record = store.claim("dead-worker", time.time())
    store.cancel_run(record.id)
    store.database.optimization_runs.update_one(
        {"_id": record.id}, {"$set": {"lease_until": time.time() - 1}}
    )
    assert store.recover_expired(time.time()) == 1
    assert store.get_run(record.id).status == "CANCELLED"
    assert store.claim("restarted-worker", time.time()) is None
    store.heartbeat("restarted-worker")
    assert store.worker_online()
    for name in ["projects", "optimization_runs", "worker_heartbeats"]:
        assert all(
            "expireAfterSeconds" not in v for v in store.database[name].index_information().values()
        )


def test_corrupt_result_cannot_be_published(database, saved_project):
    store = database[1]()
    projects.enqueue(store, saved_project["id"])
    record = store.claim("checksum-worker", time.time())
    record.status = "SUCCEEDED"
    record.result = {"proof": "altered"}
    record.result_sha256 = sha({"proof": "original"})
    with pytest.raises(ValueError, match="checksum"):
        store.publish(record)
    assert store.get_run(record.id).status == "RUNNING"
