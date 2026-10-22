"""Transactional project edits, referential integrity and reproducible run snapshots."""

import copy
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.inputs import SECTIONS, to_domain, validate_references
from smart_retail.infrastructure.database import (
    OrderLineRecord,
    OrderRecord,
    ProductKey,
    ProjectRecord,
    RunRecord,
)
from smart_retail.infrastructure.provenance import runtime_identity


class ServiceError(ValueError):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status


def now() -> str:
    return datetime.now(UTC).isoformat()


def project_dict(record: ProjectRecord) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "revision": record.revision,
        "created_at": record.created_at,
        "sections": record.sections,
        "completion": {k: k in record.sections for k in SECTIONS},
    }


def get_project(session: Session, identifier: str) -> ProjectRecord:
    project = session.get(ProjectRecord, identifier)
    if project is None:
        raise ServiceError(404, "Project not found")
    return project


def create_project(session: Session, name: str) -> dict:
    project = ProjectRecord(id=str(uuid4()), name=name.strip(), created_at=now(), sections={})
    session.add(project)
    session.commit()
    return project_dict(project)


def sync_orders(session: Session, project_id: str, sections: dict) -> None:
    session.execute(delete(OrderLineRecord).where(OrderLineRecord.project_id == project_id))
    session.execute(delete(OrderRecord).where(OrderRecord.project_id == project_id))
    session.execute(delete(ProductKey).where(ProductKey.project_id == project_id))
    session.add_all(
        ProductKey(project_id=project_id, sku=p["sku"])
        for p in sections.get("products", {}).get("items", [])
    )
    session.flush()
    session.add_all(
        OrderRecord(project_id=project_id, **o)
        for o in sections.get("orders", {}).get("orders", [])
    )
    session.flush()
    session.add_all(
        OrderLineRecord(project_id=project_id, **o)
        for o in sections.get("orders", {}).get("order_lines", [])
    )


def save_section(
    session: Session, identifier: str, section: str, payload: dict, expected_revision: int
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
    changed = session.execute(
        update(ProjectRecord)
        .where(ProjectRecord.id == identifier, ProjectRecord.revision == expected_revision)
        .values(sections=sections, revision=expected_revision + 1)
        .returning(ProjectRecord.id)
    ).scalar_one_or_none()
    if changed is None:
        session.rollback()
        raise ServiceError(409, "Project changed in another session. Reload before saving.")
    if section in ("products", "orders"):
        sync_orders(session, identifier, sections)
    session.commit()
    session.expire_all()
    return project_dict(get_project(session, identifier))


def validation_report(sections: dict) -> dict:
    errors = validate_references(sections)
    missing = sorted(set(SECTIONS) - sections.keys())
    try:
        to_domain(sections)
    except ValueError as exc:
        errors.append(str(exc))
    return {"valid": not errors and not missing, "missing": missing, "errors": errors}


def enqueue(session: Session, identifier: str) -> dict:
    project = get_project(session, identifier)
    report = validation_report(project.sections)
    if not report["valid"]:
        raise ServiceError(422, "; ".join(report["errors"]))
    snapshot = copy.deepcopy(project.sections)
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
    session.add(run)
    session.commit()
    return run_dict(run)


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


def get_run(session: Session, identifier: str) -> RunRecord:
    run = session.get(RunRecord, identifier)
    if run is None:
        raise ServiceError(404, "Run not found")
    return run


def cancel(session: Session, identifier: str) -> dict:
    get_run(session, identifier)
    session.execute(
        update(RunRecord)
        .where(RunRecord.id == identifier, RunRecord.status == "QUEUED")
        .values(status="CANCELLED")
    )
    session.execute(
        update(RunRecord)
        .where(RunRecord.id == identifier, RunRecord.status == "RUNNING")
        .values(status="CANCEL_REQUESTED")
    )
    session.commit()
    session.expire_all()
    return run_dict(get_run(session, identifier))


def list_runs(session: Session, identifier: str) -> list[dict]:
    get_project(session, identifier)
    return [
        run_dict(r)
        for r in session.scalars(
            select(RunRecord)
            .where(RunRecord.project_id == identifier)
            .order_by(RunRecord.created_at.desc())
            .limit(100)
        )
    ]
