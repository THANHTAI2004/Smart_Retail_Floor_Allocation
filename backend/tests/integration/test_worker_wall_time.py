# Vai trò: Kiểm thử ngân sách wall time bao gồm cả độ trễ tạo tiến trình.
# Các assertion mô tả hành vi mong đợi; kết quả chỉ được xác nhận sau khi chạy test.
import time
from types import SimpleNamespace

from smart_retail.application.experiments.storage import read
from smart_retail.workers import runner


# Hàm test_wall_measurement_includes_process_creation_latency: kiểm tra kịch bản wall measurement includes process creation latency bằng các assertion trong thân hàm.
def test_wall_measurement_includes_process_creation_latency(
    client, saved_project, database, tmp_path, monkeypatch
):
    context = runner.mp.get_context("spawn")

    # Hàm process: xử lý bước process trong phạm vi module hiện tại.
    def process(*args, **kwargs):
        child = context.Process(*args, **kwargs)

        class DelayedProcess:
            # Hàm __getattr__: xử lý bước getattr trong phạm vi module hiện tại.
            def __getattr__(self, name):
                return getattr(child, name)

            # Hàm start: xử lý bước start trong phạm vi module hiện tại.
            def start(self):
                time.sleep(0.7)
                child.start()

        return DelayedProcess()

    monkeypatch.setattr(runner.mp, "get_context", lambda _: SimpleNamespace(Process=process))
    queued = client.post(f"/api/projects/{saved_project['id']}/runs").json()
    began = time.monotonic()
    runner.work_once(database[1], tmp_path / "artifacts")
    outer = time.monotonic() - began
    receipt = read(tmp_path / "artifacts" / queued["id"] / "receipt.json")
    assert receipt["status"] == "SUCCEEDED"
    assert receipt["wall_s"] >= outer - 0.4
