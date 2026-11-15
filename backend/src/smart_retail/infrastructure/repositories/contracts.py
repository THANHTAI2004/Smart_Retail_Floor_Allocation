# Vai trò: Record thuần và giao diện repository cho dự án, lần chạy và worker; tầng application phụ thuộc hợp đồng này.
"""Plain repository records and structural interfaces shared by application adapters."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ProjectRecord:
    id: str
    name: str
    created_at: str
    sections: dict = field(default_factory=dict)
    revision: int = 0
    schema_version: str = "1.1"


@dataclass
class RunRecord:
    id: str
    project_id: str
    project_revision: int
    input_sha256: str
    snapshot: dict
    status: str
    stage: str
    created_at: str
    started_epoch: float | None = None
    result: dict | None = None
    error: dict | None = None
    result_sha256: str | None = None
    worker_id: str | None = None
    lease_token: str | None = None
    lease_until: float | None = None


class ProjectRepository(Protocol):
    # Hàm get_project: đọc project theo quy tắc trong thân hàm.
    def get_project(self, identifier: str) -> ProjectRecord | None: ...
    # Hàm create_project: tạo mới project theo quy tắc trong thân hàm.
    def create_project(self, record: ProjectRecord) -> None: ...
    # Hàm list_projects: liệt kê projects theo quy tắc trong thân hàm.
    def list_projects(self) -> list[ProjectRecord]: ...
    # Hàm save_project: kiểm tra và lưu project theo quy tắc trong thân hàm.
    def save_project(
        self, identifier: str, revision: int, sections: dict
    ) -> ProjectRecord | None: ...


class RunRepository(Protocol):
    # Hàm get_run: đọc run theo quy tắc trong thân hàm.
    def get_run(self, identifier: str) -> RunRecord | None: ...
    # Hàm insert_run: xử lý bước insert run trong phạm vi module hiện tại.
    def insert_run(self, record: RunRecord) -> None: ...
    # Hàm list_runs: liệt kê runs theo quy tắc trong thân hàm.
    def list_runs(self, project_id: str) -> list[RunRecord]: ...
    # Hàm cancel_run: xử lý bước cancel run trong phạm vi module hiện tại.
    def cancel_run(self, identifier: str) -> RunRecord | None: ...


class WorkerRepository(Protocol):
    # Hàm claim: xử lý bước claim trong phạm vi module hiện tại.
    def claim(self, worker_id: str, now: float) -> RunRecord | None: ...
    # Hàm recover_expired: xử lý bước recover expired trong phạm vi module hiện tại.
    def recover_expired(self, now: float) -> int: ...
    # Hàm heartbeat: xử lý bước heartbeat trong phạm vi module hiện tại.
    def heartbeat(self, worker_id: str) -> None: ...


class Repositories(ProjectRepository, RunRepository, WorkerRepository, Protocol):
    """Application dependency; concrete MongoDB implementation stays in infrastructure."""
