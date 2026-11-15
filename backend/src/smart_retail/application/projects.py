# Vai trò: Dịch vụ chỉnh sửa dự án, kiểm tra tham chiếu và tạo snapshot cho lần chạy.
# Revision được dùng để phát hiện cập nhật đồng thời.
"""Transactional project edits, referential integrity and reproducible run snapshots."""

import copy
from datetime import UTC, datetime
from uuid import uuid4

from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.inputs import SECTIONS, to_domain, validate_references
from smart_retail.contracts.migration import normalize
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.infrastructure.repositories.contracts import (
    ProjectRecord,
    Repositories,
    RunRecord,
)


class ServiceError(ValueError):
    # Hàm __init__: khởi tạo đối tượng và các phụ thuộc ban đầu.
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status


# Hàm now: lấy thời điểm hiện tại theo cách chuẩn hóa trong hàm.
def now() -> str:
    return datetime.now(UTC).isoformat()


# Hàm project_dict: xử lý bước project dict trong phạm vi module hiện tại.
def project_dict(record: ProjectRecord) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "revision": record.revision,
        "created_at": record.created_at,
        "sections": record.sections,
        "completion": {k: k in record.sections for k in SECTIONS},
    }


# Hàm get_project: đọc project theo quy tắc trong thân hàm.
def get_project(session: Repositories, identifier: str) -> ProjectRecord:
    project = session.get_project(identifier)
    if project is None:
        raise ServiceError(404, "Project not found")
    return project


# Hàm create_project: tạo mới project theo quy tắc trong thân hàm.
def create_project(session: Repositories, name: str) -> dict:
    project = ProjectRecord(id=str(uuid4()), name=name.strip(), created_at=now(), sections={})
    session.create_project(project)
    return project_dict(project)


# Kiểm tra revision và tham chiếu trên aggregate dự án trước khi công bố bản cập nhật.
def save_section(
    session: Repositories, identifier: str, section: str, payload: dict, expected_revision: int
) -> dict:
    if section not in SECTIONS:
        raise ServiceError(404, "Unknown input group")
    validated = SECTIONS[section].model_validate(payload).model_dump(mode="json")
    project = get_project(session, identifier)
    sections = copy.deepcopy(project.sections)
    sections[section] = validated
    errors = validate_references(sections)
    if errors:
        raise ServiceError(422, "; ".join(errors))
    try:
        changed = session.save_project(identifier, expected_revision, sections)
    except ValueError as exc:
        raise ServiceError(413, str(exc)) from exc
    if changed is None:
        get_project(session, identifier)
        raise ServiceError(409, "Project changed in another session. Reload before saving.")
    return project_dict(changed)


# Hàm validation_report: xử lý bước validation report trong phạm vi module hiện tại.
def validation_report(sections: dict) -> dict:
    errors = validate_references(sections)
    missing = sorted(set(SECTIONS) - sections.keys())
    try:
        to_domain(sections)
    except ValueError as exc:
        errors.append(str(exc))
    return {"valid": not errors and not missing, "missing": missing, "errors": errors}


# Chốt đầu vào của lần chạy để thay đổi dự án về sau không sửa snapshot của job đã xếp hàng.
def enqueue(session: Repositories, identifier: str) -> dict:
    project = get_project(session, identifier)
    report = validation_report(project.sections)
    if not report["valid"]:
        raise ServiceError(422, "; ".join(report["errors"]))
    snapshot, migrations = normalize(project.sections)
    snapshot["_contract_migrations"] = migrations
    snapshot["_runtime"] = runtime_identity()
    run = RunRecord(
        id=str(uuid4()),
        project_id=identifier,
        project_revision=project.revision,
        input_sha256=canonical_hash(snapshot),
        snapshot=snapshot,
        status="QUEUED",
        stage="PENDING",
        created_at=now(),
    )
    session.insert_run(run)
    return run_dict(run)


# Hàm run_dict: xử lý bước run dict trong phạm vi module hiện tại.
def run_dict(run: RunRecord, include_snapshot: bool = False) -> dict:
    result = {
        k: getattr(run, k)
        for k in (
            "id",
            "project_id",
            "project_revision",
            "input_sha256",
            "status",
            "stage",
            "created_at",
            "result",
            "error",
            "result_sha256",
        )
    }
    if include_snapshot:
        result["snapshot"] = run.snapshot
    return result


# Hàm get_run: đọc run theo quy tắc trong thân hàm.
def get_run(session: Repositories, identifier: str) -> RunRecord:
    run = session.get_run(identifier)
    if run is None:
        raise ServiceError(404, "Run not found")
    return run


# Hàm cancel: gửi hoặc ghi nhận yêu cầu hủy theo trạng thái hiện tại.
def cancel(session: Repositories, identifier: str) -> dict:
    get_run(session, identifier)
    record = session.cancel_run(identifier)
    if record is None:
        raise ServiceError(404, "Run not found")
    return run_dict(record)


# Hàm list_runs: liệt kê runs theo quy tắc trong thân hàm.
def list_runs(session: Repositories, identifier: str) -> list[dict]:
    get_project(session, identifier)
    return [run_dict(r) for r in session.list_runs(identifier)]
