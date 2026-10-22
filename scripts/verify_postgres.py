"""Run only against a disposable verification database configured by the caller."""

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient
from smart_retail.api.main import create_app
from smart_retail.infrastructure.database import connect
from smart_retail.workers.runner import work_once


def main():
    url = os.environ["SMART_RETAIL_DATABASE_URL"]
    if not url.startswith("postgresql"):
        raise RuntimeError("This verification requires PostgreSQL")
    sample = json.loads(
        Path("datasets/samples/small_store.json").read_text(encoding="utf-8")
    )
    app = create_app(url)
    _, factory = connect(url)
    with TestClient(app) as client:
        project = client.post(
            "/api/projects", json={"name": "PostgreSQL integration verification"}
        ).json()
        for section, value in sample.items():
            response = client.put(
                f"/api/projects/{project['id']}/inputs/{section}?expected_revision={project['revision']}",
                json=value,
            )
            assert response.status_code == 200, response.text
            project = response.json()
        run = client.post(f"/api/projects/{project['id']}/runs").json()
        assert work_once(factory, Path("var/postgres-verification-artifacts"))
        final = client.get(f"/api/runs/{run['id']}").json()
        assert final["status"] == "SUCCEEDED", final
        assert client.get(f"/api/runs/{run['id']}/report").status_code == 200
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "project_id": project["id"],
                    "run_id": run["id"],
                    "result_sha256": final["result_sha256"],
                }
            )
        )


if __name__ == "__main__":
    main()
