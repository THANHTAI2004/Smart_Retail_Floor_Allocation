import time

from smart_retail.application.experiments.storage import read


def test_research_http_runs_real_child_and_exports_audited_report(client, tmp_path, monkeypatch):
    home = tmp_path / "research"
    monkeypatch.setenv("SMART_RETAIL_RESEARCH_HOME", str(home))
    configurations = client.get("/api/research/configurations").json()
    spec = next(c["configuration"] for c in configurations if c["id"] == "pilot")
    spec["experiments"] = [spec["experiments"][1]]
    spec["seeds"] = [11]
    spec["datasets"] = [d for d in spec["datasets"] if d["id"] == "tiny"]
    assert len(client.get("/api/research/datasets").json()) == 4
    response = client.post("/api/research/campaigns", json=spec)
    assert response.status_code == 202
    identifier = response.json()["id"]
    end = time.monotonic() + 45
    while time.monotonic() < end:
        value = client.get(f"/api/research/campaigns/{identifier}").json()
        assert value["status"] != "FAILED", value
        if value.get("supervisor", {}).get("report"):
            break
        time.sleep(0.1)
    else:
        raise AssertionError("Real campaign supervisor did not publish a report")
    assert value["completed"] == 2
    assert all(
        r["status"] == "SUCCEEDED" and r["validation"]["status"] == "PASS" for r in value["records"]
    )
    manifest = client.get(f"/api/research/campaigns/{identifier}/report/manifest.json")
    assert manifest.status_code == 200
    assert manifest.json()["datasets"][0]["sha256"]
    assert client.get(f"/api/research/campaigns/{identifier}/report/missing.csv").status_code == 404
    assert client.get("/api/research/campaigns/not-an-id").status_code == 404
    assert read(home / identifier / "checkpoint.json")["status"] == "COMPLETED"
