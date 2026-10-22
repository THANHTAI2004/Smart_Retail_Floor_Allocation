"""A finite model declares every decision domain; no continuous-space claim."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Placement(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    sku: str
    shelf_id: str
    level_id: str
    face: int = Field(ge=0, le=1, strict=True)
    x_m: float = Field(ge=0)
    width_m: float = Field(gt=0)
    orientation: Literal[0, 90]
    facings: int = Field(ge=1, strict=True)
    layers: int = Field(ge=1, strict=True)
    depth_units: int = Field(ge=1, strict=True)
    capacity_units: int = Field(ge=1, strict=True)
    load_kg: float = Field(ge=0)


class FiniteSpace(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    model_version: Literal["joint-finite-1"] = "joint-finite-1"
    poses: dict[str, list[tuple[float, float, Literal[0, 90]]]]
    assignments: dict[str, list[str]]
    placements: dict[str, list[dict]]
    routing_policies: list[Literal["nearest", "return", "exact"]] = Field(
        default=["nearest"], min_length=1, max_length=3
    )
    max_states: int = Field(default=20000, ge=1, le=20000)

    @model_validator(mode="after")
    def validate_rows(self):
        for sku, rows in self.placements.items():
            for row in rows:
                value = Placement.model_validate(row)
                if value.sku != sku:
                    raise ValueError("Placement domain contains another SKU")
        return self


PROOF_STATUSES = (
    "GLOBAL_OPTIMAL_CERTIFIED",
    "BOUNDED_GAP",
    "FEASIBLE_NOT_PROVEN",
    "INFEASIBLE_PROVEN",
    "SEARCH_EXHAUSTED",
    "TIMEOUT",
    "INVALID_MODEL",
    "INVALID_SOLUTION",
    "PROOF_VERIFICATION_FAILED",
)
