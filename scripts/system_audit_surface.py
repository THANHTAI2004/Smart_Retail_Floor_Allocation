"""Read/write API surface probes in one isolated audit database; no numerical jobs."""

import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from smart_retail.api.main import create_app
from smart_retail.contracts.inputs import SECTIONS
from smart_retail.contracts.tabular import TABLES
from smart_retail.infrastructure.database import connect


def main():
    root = Path(__file__).resolve().parents[1]
    audit = json.loads((root / "var/system-audit-current.json").read_text(encoding="utf-8"))
    output = Path(audit["root"]) / "api-surface.json"
    if output.exists():
        raise FileExistsError(output)
    database = audit["database_prefix"] + uuid4().hex[:12] + "_surface"
    owner, factory = connect(database=database)
    owner.ready()
    assert factory().list_projects() == []
    collection = owner.database.audit_crud
    collection.insert_one({"_id": "owned-crud-probe", "value": 1})
    assert collection.find_one({"_id": "owned-crud-probe"})["value"] == 1
    assert (
        collection.update_one(
            {"_id": "owned-crud-probe", "value": 1}, {"$set": {"value": 2}}
        ).modified_count
        == 1
    )
    assert collection.find_one({"_id": "owned-crud-probe"})["value"] == 2
    assert collection.delete_one({"_id": "owned-crud-probe"}).deleted_count == 1
    assert collection.find_one({"_id": "owned-crud-probe"}) is None
    sample = json.loads((root / "datasets/samples/small_store.json").read_text(encoding="utf-8"))
    checks = []
    with TestClient(create_app(database=database)) as client:
        schemas = client.get("/api/schemas")
        assert schemas.status_code == 200 and set(schemas.json()) == set(SECTIONS)
        project = client.post("/api/projects", json={"name": "API export audit"}).json()
        for section, payload in sample.items():
            response = client.put(
                f"/api/projects/{project['id']}/inputs/{section}",
                params={"expected_revision": project["revision"]},
                json=payload,
            )
            assert response.status_code == 200, response.text
            project = response.json()
        for section in SECTIONS:
            url = f"/api/projects/{project['id']}/inputs/{section}/export"
            response = client.get(url)
            assert response.status_code == 200
            assert response.json() == project["sections"][section]
            csv = client.get(url, params={"format": "csv"})
            assert csv.status_code == (200 if section in TABLES else 422)
            if section in TABLES:
                response = client.post(
                    f"/api/projects/{project['id']}/inputs/{section}/import-csv",
                    json={"text": csv.text, "expected_revision": project["revision"]},
                )
                assert response.status_code == 200, response.text
                updated = response.json()
                assert updated["sections"] == project["sections"]
                assert updated["revision"] == project["revision"] + 1
                project = updated
            checks.append(
                {
                    "section": section,
                    "json_status": 200,
                    "csv_status": csv.status_code,
                    "csv_roundtrip": section in TABLES,
                }
            )
        assert client.get("/api/projects/not-found").status_code == 404
        assert client.get(f"/api/projects/{project['id']}/inputs/unknown/export").status_code == 404
        assert (
            client.get(
                f"/api/projects/{project['id']}/inputs/products/export?format=bad"
            ).status_code
            == 422
        )
        schema = client.get("/openapi.json").json()
        assert factory().get_project(project["id"]).sections == project["sections"]
        output.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "native_crud": "PASS: only the owned audit_crud marker was deleted",
                    "database": database,
                    "checks": checks,
                    "schemas": sorted(schemas.json()),
                    "routes": schema["paths"],
                    "missing_project_status": 404,
                    "unknown_section_status": 404,
                    "bad_export_format_status": 422,
                    "revision": project["revision"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    owner.dispose()
    print("API surface PASS: seven JSON exports, four lossless CSV roundtrips, real MongoDB")


if __name__ == "__main__":
    main()
