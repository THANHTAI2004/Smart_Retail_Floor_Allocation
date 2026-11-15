# Vai trò: Kiểm thử hủy tiến trình con thật và từ chối snapshot bị sửa.
# Các assertion mô tả hành vi mong đợi; kết quả chỉ được xác nhận sau khi chạy test.
import json
import time
from concurrent.futures import ThreadPoolExecutor

from smart_retail.workers.runner import read_progress, work_once


# Hàm test_cancellation_kills_a_real_running_t4_child: kiểm tra kịch bản cancellation kills a real running t4 child bằng các assertion trong thân hàm.
def test_cancellation_kills_a_real_running_t4_child(
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
    run = client.post(f"/api/projects/{pid}/runs").json()
    root = tmp_path / "running-artifacts"
    progress = root / run["id"] / "progress.json"
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(work_once, database[1], root)
        end = time.monotonic() + 15
        while time.monotonic() < end:
            if read_progress(progress) == "T4":
                break
            assert not future.done(), "Worker finished before the cancellation checkpoint"
            time.sleep(0.02)
        else:
            raise AssertionError("Real T4 did not start within 15 seconds")
        response = client.post(f"/api/runs/{run['id']}/cancel")
        assert response.json()["status"] == "CANCEL_REQUESTED"
        assert future.result(timeout=10)
    final = client.get(f"/api/runs/{run['id']}").json()
    assert final["status"] == "CANCELLED"
    assert final["result"] is None
    receipt = json.loads((root / run["id"] / "receipt.json").read_text())
    assert receipt["child_exit"] != 0


# Hàm test_snapshot_corruption_fails_before_execution: kiểm tra kịch bản snapshot corruption fails before execution bằng các assertion trong thân hàm.
def test_snapshot_corruption_fails_before_execution(client, saved_project, database, tmp_path):
    run = client.post(f"/api/projects/{saved_project['id']}/runs").json()
    with database[1]() as db:
        stored = db.get_run(run["id"])
        snapshot = dict(stored.snapshot)
        snapshot["optimization"] = {**snapshot["optimization"], "seed": 999}
        db.database.optimization_runs.update_one({"_id":run["id"]},{"$set":{"snapshot":snapshot}})
    assert work_once(database[1], tmp_path / "artifacts")
    final = client.get(f"/api/runs/{run['id']}").json()
    assert final["error"]["code"] == "INPUT_CORRUPT"
    assert client.get(f"/api/runs/{run['id']}/report").status_code == 409
