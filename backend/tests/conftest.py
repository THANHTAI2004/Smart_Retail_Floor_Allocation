import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from smart_retail.api.main import create_app
from smart_retail.infrastructure.database import Base, connect


@pytest.fixture
def sample():
    return json.loads(
        (Path(__file__).resolve().parents[2] / "datasets/samples/small_store.json").read_text(
            encoding="utf-8"
        )
    )


@pytest.fixture
def database(tmp_path):
    url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    engine, factory = connect(url)
    Base.metadata.create_all(engine)
    yield url, factory
    engine.dispose()


@pytest.fixture
def client(database):
    app = create_app(database[0])
    with TestClient(app) as client:
        yield client


@pytest.fixture
def saved_project(client, sample):
    response = client.post("/api/projects", json={"name": "Integration study"})
    assert response.status_code == 201
    project = response.json()
    for key, payload in sample.items():
        response = client.put(
            f"/api/projects/{project['id']}/inputs/{key}",
            params={"expected_revision": project["revision"]},
            json=payload,
        )
        assert response.status_code == 200, response.text
        project = response.json()
    return project
