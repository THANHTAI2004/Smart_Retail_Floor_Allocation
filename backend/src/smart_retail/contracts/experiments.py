"""Strict, versioned executable campaign manifests shared by CLI and HTTP."""

from typing import Literal, Self

from pydantic import Field, model_validator

from smart_retail.contracts.inputs import Contract, Identifier


class DatasetSpec(Contract):
    id: Identifier
    scale: Literal["tiny", "small", "medium", "large"] = "tiny"
    seed: int = Field(default=101, ge=0, le=2147483647)
    scenario: Literal["feasible", "infeasible", "high_load", "volatile", "uneven"] = "feasible"
    category_assignment: Literal["free", "fixed"] = "free"
    variable_facings: bool = False
    levels: int = Field(default=2, ge=1, le=5)
    height_scale: float = Field(default=1, ge=0.5, le=2)
    input_path: str | None = Field(default=None, max_length=500)
    input_file_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def imported_identity(self) -> Self:
        if (self.input_path is None) != (self.input_file_sha256 is None):
            raise ValueError("Imported dataset requires both input_path and input_file_sha256")
        return self


class Treatment(Contract):
    id: Identifier
    overrides: dict = Field(default_factory=dict)


class ExperimentSpec(Contract):
    id: Literal["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14", "E15"]
    question: str = Field(min_length=5)
    hypothesis: str = Field(min_length=5)
    datasets: list[Identifier] = Field(min_length=1, max_length=20)
    treatments: list[Treatment] = Field(min_length=1, max_length=10)
    metrics: list[
        Literal[
            "wall_s",
            "peak_child_rss_bytes",
            "mean_distance_m",
            "mean_wait_s",
            "t2_objective",
            "t3_objective",
            "t1_objective",
            "joint_objective", "joint_evaluations", "joint_iterations_to_best", "holdout_objective",
        ]
    ] = Field(default=["wall_s", "mean_distance_m", "mean_wait_s"], min_length=1)
    acceptance: str = Field(min_length=5)
    statistical_method: Literal["descriptive_paired_exploratory"] = "descriptive_paired_exploratory"


class CampaignSpec(Contract):
    schema_version: Literal["1.0"] = "1.0"
    name: str = Field(min_length=1, max_length=120)
    data_origin: Literal["SYNTHETIC"] = "SYNTHETIC"
    datasets: list[DatasetSpec] = Field(min_length=1, max_length=20)
    experiments: list[ExperimentSpec] = Field(min_length=1, max_length=10)
    seeds: list[int] = Field(default=[11, 23, 37], min_length=1, max_length=100)
    repetitions: int = Field(default=1, ge=1, le=10)
    job_time_limit_s: float = Field(default=15, gt=0, le=300)
    memory_limit_mb: int = Field(default=1024, ge=128, le=8192)
    max_wall_s: float = Field(default=600, gt=0, le=14400)
    max_jobs: int = Field(default=128, ge=1, le=1000)
    max_retries: int = Field(default=1, ge=0, le=2)
    workers: Literal[1] = 1
    cache_policy: Literal["isolated", "reuse"] = "isolated"

    @model_validator(mode="after")
    def references(self) -> Self:
        count = sum(
            len(e.datasets) * len(e.treatments) * len(self.seeds) * self.repetitions
            for e in self.experiments
        )
        if count > 1000:
            raise ValueError(
                "Campaign plan exceeds the hard limit of 1,000 jobs; split the design explicitly"
            )
        ids = {d.id for d in self.datasets}
        if len(ids) != len(self.datasets) or len({e.id for e in self.experiments}) != len(
            self.experiments
        ):
            raise ValueError("Dataset and experiment identifiers must be unique")
        if len(set(self.seeds)) != len(self.seeds) or any(
            not 0 <= s <= 2147483647 for s in self.seeds
        ):
            raise ValueError("Seeds must be distinct non-negative 32-bit integers")
        for experiment in self.experiments:
            if not set(experiment.datasets) <= ids:
                raise ValueError("Unknown dataset in experiment")
            if len({t.id for t in experiment.treatments}) != len(experiment.treatments):
                raise ValueError("Treatment IDs must be unique within an experiment")
        return self
