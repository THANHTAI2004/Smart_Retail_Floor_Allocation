# Vai trò: Fixture dùng chung cho pytest: dữ liệu mẫu, kết nối database test, HTTP client và dự án đã lưu.
# Vòng đời tài nguyên theo scope fixture.
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from smart_retail.api.main import create_app
from smart_retail.infrastructure.database import connect


@pytest.fixture
# Hàm sample: lấy mẫu dữ liệu hoặc tài nguyên cho phạm vi kiểm tra hiện tại.
def sample():
    return json.loads(
        (Path(__file__).resolve().parents[2] / "datasets/samples/small_store.json").read_text(
            encoding="utf-8"
        )
    )


@pytest.fixture
# Hàm database: xử lý bước database trong phạm vi module hiện tại.
def database(tmp_path):
    name = os.getenv("SMART_RETAIL_TEST_DB_PREFIX", "sr_test_") + uuid4().hex[:20]
    engine, factory = connect(database=name)
    try:
        engine.ready()
    except RuntimeError:
        pytest.skip("BLOCKED_MONGODB_RUNTIME: real MongoDB required for integration tests")
    yield name, factory
    engine.dispose()


@pytest.fixture
# Hàm client: xử lý bước client trong phạm vi module hiện tại.
def client(database):
    app = create_app(database=database[0])
    with TestClient(app) as client:
        yield client


@pytest.fixture
# Hàm saved_project: xử lý bước saved project trong phạm vi module hiện tại.
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
