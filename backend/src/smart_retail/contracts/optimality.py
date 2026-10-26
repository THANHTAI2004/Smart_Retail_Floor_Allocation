"""A finite model declares every decision domain; no continuous-space claim."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator


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
    poses: dict[str, list[tuple[float, float, Literal[0, 90]]]] = Field(default_factory=dict)
    assignments: dict[str, list[str]] = Field(default_factory=dict)
    placements: dict[str, list[dict]] = Field(default_factory=dict)
    # Bundled domains: a whole layout (every shelf pose) or a whole allocation (category
    # assignment plus all SKU rows) is one option. They replace the per-key domains.
    layouts: list[dict[str, tuple[float, float, Literal[0, 90]]]] | None = Field(
        default=None, min_length=1
    )
    allocations: list[dict] | None = Field(default=None, min_length=1)
    routing_policies: list[Literal["nearest", "return", "exact"]] = Field(
        default=["nearest"], min_length=1, max_length=3
    )
    max_states: int = Field(default=20000, ge=1, le=20000)

    @model_serializer(mode="wrap")
    def omit_absent_bundles(self, handler):
        # Spaces without bundles keep their pre-existing canonical form and digest.
        data = handler(self)
        for key in ("layouts", "allocations"):
            if data.get(key) is None:
                data.pop(key, None)
        return data

    @model_validator(mode="after")
    def validate_rows(self):
        for sku, rows in self.placements.items():
            for row in rows:
                value = Placement.model_validate(row)
                if value.sku != sku:
                    raise ValueError("Placement domain contains another SKU")
        if self.layouts is not None:
            if self.poses:
                raise ValueError("Use either per-shelf poses or layout bundles")
            if len({frozenset(layout) for layout in self.layouts}) != 1:
                raise ValueError("Every layout bundle must cover the same shelves")
        if self.allocations is not None:
            if self.assignments or self.placements:
                raise ValueError("Use either per-key assignments/placements or allocation bundles")
            for allocation in self.allocations:
                if set(allocation) != {"assignment", "placements"}:
                    raise ValueError("An allocation bundle has assignment and placements only")
                skus = [Placement.model_validate(r).sku for r in allocation["placements"]]
                if len(set(skus)) != len(skus):
                    raise ValueError("An allocation bundle places each SKU once")
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
