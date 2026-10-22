"""HTTP adapters only; numerical work belongs to the external worker."""

import logging
import time
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from smart_retail.application import projects
from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.inputs import SECTIONS
from smart_retail.contracts.outputs import ProjectOutput, RunOutput, ValidationOutput
from smart_retail.infrastructure.database import ProjectRecord, RunRecord, WorkerHeartbeat, connect
from smart_retail.infrastructure.provenance import runtime_identity
from smart_retail.reporting.export import planogram_csv, report_json

logger = logging.getLogger("smart_retail.api")


class NewProject(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=200)


def create_app(url: str | None = None) -> FastAPI:
    engine, factory = connect(url)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        engine.dispose()

    app = FastAPI(title="Smart Retail Floor Allocation", version="0.1.0", lifespan=lifespan)
    app.state.session_factory = factory
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type"],
    )

    def session():
        with factory() as value:
            yield value

    DB = Annotated[Session, Depends(session)]

    @app.exception_handler(projects.ServiceError)
    async def service_error(_: Request, exc: projects.ServiceError):
        return JSONResponse(status_code=exc.status, content={"detail": str(exc)})

    @app.exception_handler(ValidationError)
    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc):
        errors = [{"path": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": errors})

    @app.middleware("http")
    async def timing(request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        logger.info(
            "%s %s status=%d elapsed_ms=%.1f",
            request.method,
            request.url.path,
            response.status_code,
            (time.monotonic() - start) * 1000,
        )
        return response

    @app.get("/api/health")
    def health(db: DB):
        db.execute(text("SELECT 1"))
        heartbeats = db.scalars(select(WorkerHeartbeat)).all()
        return {
            "status": "ok",
            "database": engine.dialect.name,
            "worker_online": any(time.time() - w.epoch < 10 for w in heartbeats),
            "runtime": runtime_identity(),
        }

    @app.get("/api/schemas")
    def schemas():
        return {key: value.model_json_schema() for key, value in SECTIONS.items()}

    @app.get("/api/projects", response_model=list[ProjectOutput])
    def list_projects(db: DB):
        return [
            projects.project_dict(p)
            for p in db.scalars(select(ProjectRecord).order_by(ProjectRecord.created_at.desc()))
        ]

    @app.post("/api/projects", status_code=201, response_model=ProjectOutput)
    def create(payload: NewProject, db: DB):
        return projects.create_project(db, payload.name)

    @app.get("/api/projects/{identifier}", response_model=ProjectOutput)
    def get(identifier: str, db: DB):
        return projects.project_dict(projects.get_project(db, identifier))

    @app.put("/api/projects/{identifier}/inputs/{section}", response_model=ProjectOutput)
    def save(
        identifier: str, section: str, payload: dict, db: DB, expected_revision: int = Query(ge=0)
    ):
        return projects.save_section(db, identifier, section, payload, expected_revision)

    @app.post("/api/projects/{identifier}/validate", response_model=ValidationOutput)
    def validate(identifier: str, db: DB):
        return projects.validation_report(projects.get_project(db, identifier).sections)

    @app.post("/api/projects/{identifier}/runs", status_code=202, response_model=RunOutput)
    def enqueue(identifier: str, db: DB):
        return projects.enqueue(db, identifier)

    @app.get("/api/projects/{identifier}/runs", response_model=list[RunOutput])
    def runs(identifier: str, db: DB):
        return projects.list_runs(db, identifier)

    @app.get("/api/runs/{identifier}", response_model=RunOutput)
    def run(identifier: str, db: DB):
        return projects.run_dict(projects.get_run(db, identifier), include_snapshot=True)

    @app.post("/api/runs/{identifier}/cancel", response_model=RunOutput)
    def cancel(identifier: str, db: DB):
        return projects.cancel(db, identifier)

    @app.post("/api/runs/{identifier}/replay", status_code=202, response_model=RunOutput)
    def replay(identifier: str, db: DB):
        old = projects.get_run(db, identifier)
        if old.snapshot.get("_runtime") != runtime_identity():
            raise projects.ServiceError(
                409, "Runtime/source identity changed; replay would not use the original engine"
            )
        new = RunRecord(
            id=projects.uuid4().__str__(),
            project_id=old.project_id,
            project_revision=old.project_revision,
            input_sha256=old.input_sha256,
            snapshot=old.snapshot,
            status="QUEUED",
            stage="PENDING",
            created_at=projects.now(),
        )
        db.add(new)
        db.commit()
        return projects.run_dict(new)

    @app.get("/api/runs/{identifier}/report")
    def report(identifier: str, db: DB, format: str = "json"):
        run = projects.run_dict(projects.get_run(db, identifier), include_snapshot=True)
        if canonical_hash(run["snapshot"]) != run["input_sha256"]:
            raise projects.ServiceError(409, "Stored input checksum mismatch")
        if run["result"] and canonical_hash(run["result"]) != run["result_sha256"]:
            raise projects.ServiceError(409, "Stored result checksum mismatch")
        if format not in ("json", "csv"):
            raise projects.ServiceError(422, "Report format must be json or csv")
        content = report_json(run) if format == "json" else planogram_csv(run)
        return Response(
            content,
            media_type="application/json" if format == "json" else "text/csv",
            headers={"Content-Disposition": f'attachment; filename="retail-{identifier}.{format}"'},
        )

    return app


app = create_app()
