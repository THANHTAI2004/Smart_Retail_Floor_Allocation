# Vai trò: Hợp đồng phản hồi HTTP cho dự án, lần chạy và lỗi.
# Giữ định dạng API tách khỏi cấu trúc lưu trữ nội bộ.
"""Public HTTP output contracts, separate from the ORM and domain models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ProjectOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    revision: int
    created_at: str
    sections: dict
    completion: dict[str, bool]


class RunError(BaseModel):
    code: str
    message: str


class RunOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    project_id: str
    project_revision: int
    input_sha256: str
    status: Literal[
        "QUEUED",
        "RUNNING",
        "CANCEL_REQUESTED",
        "CANCELLED",
        "SUCCEEDED",
        "FAILED",
        "TIMED_OUT",
        "INFEASIBLE",
    ]
    stage: str
    created_at: str
    result: dict | None
    error: RunError | None
    result_sha256: str | None
    snapshot: dict | None = None


class ValidationOutput(BaseModel):
    valid: bool
    missing: list[str]
    errors: list[str]
