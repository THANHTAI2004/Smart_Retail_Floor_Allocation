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
    def get_project(self, identifier: str) -> ProjectRecord | None: ...
    def create_project(self, record: ProjectRecord) -> None: ...
    def list_projects(self) -> list[ProjectRecord]: ...
    def save_project(
        self, identifier: str, revision: int, sections: dict
    ) -> ProjectRecord | None: ...


class RunRepository(Protocol):
    def get_run(self, identifier: str) -> RunRecord | None: ...
    def insert_run(self, record: RunRecord) -> None: ...
    def list_runs(self, project_id: str) -> list[RunRecord]: ...
    def cancel_run(self, identifier: str) -> RunRecord | None: ...


class WorkerRepository(Protocol):
    def claim(self, worker_id: str, now: float) -> RunRecord | None: ...
    def recover_expired(self, now: float) -> int: ...
    def heartbeat(self, worker_id: str) -> None: ...


class Repositories(ProjectRepository, RunRepository, WorkerRepository, Protocol):
    """Application dependency; concrete MongoDB implementation stays in infrastructure."""
