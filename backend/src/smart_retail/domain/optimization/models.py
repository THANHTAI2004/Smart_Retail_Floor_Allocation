"""Business models for optimization. No HTTP or ORM dependencies."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class OptimizationConfig:
    joint: str | None = None
    seed: int = 42
    time_limit_s: float = 30
    max_iterations: int = 10000
    algorithm: Literal["milp", "greedy"] = "milp"
    distance_weight: float = 1
    affinity_weight: float = 1
    capacity_weight: float = 0
    slotting_algorithm: Literal["first_fit", "milp"] = "first_fit"
    candidate_count: int = 1
    travel_weight: float = 1
    wait_weight: float = 0
    stock_weight: float = 0
    layout_algorithm: str = "grid"
    stop_after_stage: str = "T4"
    memory_limit_mb: int = 2048


@dataclass(frozen=True)
class OptimizationRun:
    id: str
    project_id: str
    input_sha256: str
    status: str
