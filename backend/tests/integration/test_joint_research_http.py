import copy
import time


def test_joint_http_worker_certificate_report_and_safe_artifact(client, tmp_path, monkeypatch):
    monkeypatch.setenv("SMART_RETAIL_RESEARCH_HOME", str(tmp_path / "research"))
    configs = client.get("/api/research/configurations").json()
    spec = copy.deepcopy(
        next(c["configuration"] for c in configs if c["id"] == "joint_certification")
    )
    spec["seeds"] = [11]
    spec["experiments"][0]["treatments"] = [
        t for t in spec["experiments"][0]["treatments"] if t["id"] in ("exact", "feedback")
    ]
    response = client.post("/api/research/campaigns", json=spec)
    assert response.status_code == 202, response.text
    identifier = response.json()["id"]
    base = f"/api/research/campaigns/{identifier}"
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        value = client.get(base).json()
        assert value["status"] != "FAILED", value
        if value.get("supervisor", {}).get("report"):
            break
        time.sleep(0.1)
    else:
        raise AssertionError("Real joint supervisor/report did not complete")
    assert len(value["records"]) == 2
    records = {r["treatment"]: r for r in value["records"]}
    assert all(
        r["status"] == "SUCCEEDED" and r["validation"]["status"] == "PASS" for r in records.values()
    )
    exact = client.get(base + f"/jobs/{records['exact']['job_key']}/joint")
    assert exact.status_code == 200
    proof = exact.json()["joint"]
    assert proof["proof_status"] == "GLOBAL_OPTIMAL_CERTIFIED"
    assert proof["verification"]["status"] == "PASS"
    assert records["feedback"]["joint_objective"] > records["exact"]["joint_objective"]
    assert client.get(base + "/jobs/not-a-key/joint").status_code == 404
    manifest = client.get(base + "/report/manifest.json").json()
    assert manifest["files"]["joint-trace.csv"]
    assert manifest["files"]["figures/joint-convergence.png"]
    assert client.get(base + "/report/joint-comparison.csv").status_code == 200
    assert client.get(base + f"/report/certificates/{records['exact']['job_key']}.json").json()[
        "complete"
    ]
