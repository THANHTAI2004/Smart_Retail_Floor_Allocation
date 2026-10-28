"""Declared finite scenario objective and bounded closed-loop controls."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator


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
    mode: Literal[
        "sequential", "multistart", "random_search", "annealing", "feedback", "exact", "hybrid"
    ] = "feedback"
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
    # Annealing: T0 relative to the initial score; geometric cooling to T0 * final_ratio.
    annealing_initial_temperature: float = Field(default=0.01, gt=0, le=1)
    annealing_final_ratio: float = Field(default=0.01, gt=0, le=1)
    finite_space: dict | None = None
    verify_certificate: bool = True
    # paper-v4 search controls. None keeps the paper-v3 behavior and canonical form.
    # T1 move lengths in grid steps (None: [1]); geometry_prefilter drops T1 edits that
    # violate boundary/clearance before they spend an evaluation (None: False).
    t1_steps: list[int] | None = Field(default=None, min_length=1, max_length=10)
    geometry_prefilter: bool | None = None
    # "objective": only T3 edits that can change the joint score (face, cross-face swap,
    # facings while capacity is short); T4 routes to shelf faces only (None: "all").
    t3_scope: Literal["all", "objective"] | None = None
    # "adaptive": layers share the action list by smoothed observed success rate
    # instead of a fair round-robin (None: "round_robin").
    layer_allocation: Literal["round_robin", "adaptive"] | None = None
    # Iterated local search: on local convergence, restart feedback from a random-walk
    # perturbation of the best plan with kick_edits geometry-valid T1 edits (None: 0 / 3).
    kicks: int | None = Field(default=None, ge=0, le=100)
    kick_edits: int | None = Field(default=None, ge=1, le=50)
    # Largest grid displacement of a random-walk T1 edit (random_search, multistart,
    # kicks). None: 3.
    restart_max_step: int | None = Field(default=None, ge=1, le=10)
    # Equal-wall-time comparison: no new evaluation starts after search_time_s seconds of
    # search; the rest of time_limit_s is left for verification and held-out scoring.
    search_time_s: float | None = Field(default=None, gt=0, le=3600)
    # Two-fidelity screening: a candidate is first simulated on the first screen_seeds
    # scenario seeds and fully evaluated only when its screened score is at most
    # (1 + screen_margin) x the reference plan's score on the same seeds. max_evaluations
    # then counts full-evaluation equivalents (seed simulations / len(scenario_seeds)).
    screen_seeds: int | None = Field(default=None, ge=1, le=9)
    screen_margin: float | None = Field(default=None, ge=0, le=1)

    @model_serializer(mode="wrap")
    def omit_absent_search_controls(self, handler):
        data = handler(self)
        for key in V4_CONTROLS:
            if data.get(key) is None:
                data.pop(key, None)
        return data

    @model_validator(mode="after")
    def scenarios(self):
        all_seeds = self.scenario_seeds + self.holdout_seeds
        if len(set(all_seeds)) != len(all_seeds) or any(s < 0 or s > 2147483647 for s in all_seeds):
            raise ValueError("Training/holdout seeds must be distinct, disjoint 32-bit seeds")
        if self.mode in ("exact", "hybrid") and self.finite_space is None:
            raise ValueError("Exact/hybrid requires an explicit finite decision space")
        if self.t1_steps is not None and (
            len(set(self.t1_steps)) != len(self.t1_steps) or not all(1 <= s <= 10 for s in self.t1_steps)
        ):
            raise ValueError("t1_steps must be distinct grid multiples in 1..10")
        if self.screen_seeds is not None and (
            self.screen_seeds >= len(self.scenario_seeds) or self.mode in ("exact", "hybrid")
        ):
            raise ValueError(
                "screen_seeds must be fewer than scenario_seeds and is not used by exact/hybrid"
            )
        if self.screen_margin is not None and self.screen_seeds is None:
            raise ValueError("screen_margin requires screen_seeds")
        return self


V4_CONTROLS = (
    "t1_steps",
    "geometry_prefilter",
    "t3_scope",
    "layer_allocation",
    "kicks",
    "kick_edits",
    "restart_max_step",
    "search_time_s",
    "screen_seeds",
    "screen_margin",
)
