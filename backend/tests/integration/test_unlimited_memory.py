import json

import pytest

from smart_retail.workers import runner


@pytest.mark.parametrize("limit,expected", [(None, "SUCCEEDED"), (2048, "FAILED")])
def test_worker_honors_unlimited_and_finite_rss(
    limit, expected, client, saved_project, sample, database, tmp_path, monkeypatch
):
    optimization = {**sample["optimization"], "memory_limit_mb": limit}
    response = client.put(
        f"/api/projects/{saved_project['id']}/inputs/optimization?expected_revision=7",
        json=optimization,
    )
    assert response.status_code == 200
    queued = client.post(f"/api/projects/{saved_project['id']}/runs").json()
    # Report 16 GiB without allocating it: finite limits must stop the child;
    # explicit null must let the same real child produce its result.
    monkeypatch.setattr(runner, "sample_resources", lambda _: {
        "rss_bytes": 16 * 1024**3, "peak_rss_bytes": 16 * 1024**3, "cpu_s": 0.1
    })
    root = tmp_path / "artifacts"
    assert runner.work_once(database[1], root)
    final = client.get(f"/api/runs/{queued['id']}").json()
    assert final["status"] == expected
    receipt = json.loads((root / queued["id"] / "receipt.json").read_text())
    assert receipt["memory_limit_mb"] == limit
    if limit is None:
        assert final["result"] is not None
    else:
        assert final["error"]["code"] == "RESOURCE_LIMIT"
