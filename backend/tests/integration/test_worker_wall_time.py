import time
from types import SimpleNamespace

from smart_retail.application.experiments.storage import read
from smart_retail.workers import runner


def test_wall_measurement_includes_process_creation_latency(
    client, saved_project, database, tmp_path, monkeypatch
):
    context = runner.mp.get_context("spawn")

    def process(*args, **kwargs):
        child = context.Process(*args, **kwargs)

        class DelayedProcess:
            def __getattr__(self, name):
                return getattr(child, name)

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
