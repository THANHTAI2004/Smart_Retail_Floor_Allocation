"""Declared finite scenario objective and bounded closed-loop controls."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Objective(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, frozen=True)
    weights: tuple[float, float, float, float] = (1, 0, 0, 0)
    scales: tuple[float, float, float, float] = (100, 100, 1, 1)

    @model_validator(mode="after")
    def valid(self):
        if min(self.weights) < 0 or sum(self.weights) <= 0 or min(self.scales) <= 0:
            raise ValueError("Nonnegative positive-sum weights and fixed positive scales required")
        return self


class JointConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    mode: Literal["sequential", "multistart", "feedback", "exact", "hybrid"] = "feedback"
    scenario_seeds: list[int] = Field(default=[11], min_length=1, max_length=10)
    scenario_seed_policy: Literal["fixed", "job_seed_offsets"] = "fixed"
    holdout_seeds: list[int] = Field(default_factory=list, max_length=10)
    objective: Objective = Field(default_factory=Objective)
    layers: list[Literal["T1", "T2", "T3", "T4"]] = Field(default=["T1", "T2", "T3"])
    max_iterations: int = Field(default=5, ge=0, le=100)
    max_evaluations: int = Field(default=100, ge=1, le=20000)
    max_actions: int = Field(default=30, ge=1, le=1000)
    patience: int = Field(default=1, ge=1, le=20)
    tolerance: float = Field(default=1e-9, ge=0, le=0.1)
    target: float | None = Field(default=None, ge=0)
    policy: Literal["first_improvement", "best_improvement"] = "best_improvement"
    finite_space: dict | None = None
    verify_certificate: bool = True

    @model_validator(mode="after")
    def scenarios(self):
        all_seeds = self.scenario_seeds + self.holdout_seeds
        if len(set(all_seeds)) != len(all_seeds) or any(s < 0 or s > 2147483647 for s in all_seeds):
            raise ValueError("Training/holdout seeds must be distinct, disjoint 32-bit seeds")
        if self.mode in ("exact", "hybrid") and self.finite_space is None:
            raise ValueError("Exact/hybrid requires an explicit finite decision space")
        return self
