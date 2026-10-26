"""Strict, versioned executable campaign manifests shared by CLI and HTTP."""

from typing import Literal, Self

from pydantic import Field, model_serializer, model_validator

from smart_retail.contracts.inputs import Contract, Identifier


class DatasetSpec(Contract):
    id: Identifier
    scale: Literal["tiny", "small", "medium", "large"] = "tiny"
    seed: int = Field(default=101, ge=0, le=2147483647)
    scenario: Literal["feasible", "infeasible", "high_load", "volatile", "uneven"] = "feasible"
    category_assignment: Literal["free", "fixed"] = "free"
    variable_facings: bool = False
    facings: int = Field(default=1, ge=1, le=20)
    levels: int = Field(default=2, ge=1, le=5)
    height_scale: float = Field(default=1, ge=0.5, le=2)
    input_path: str | None = Field(default=None, max_length=500)
    input_file_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    # Load calibration (paper-v3). None keeps the original generator and canonical form.
    orders: int | None = Field(default=None, ge=2, le=20000)
    order_interval_s: float | None = Field(default=None, gt=0, le=86400)
    picker_count: int | None = Field(default=None, ge=1, le=100)

    @model_serializer(mode="wrap")
    def omit_absent_calibration(self, handler):
        data = handler(self)
        for key in ("orders", "order_interval_s", "picker_count"):
            if data.get(key) is None:
                data.pop(key, None)
        return data

    @model_validator(mode="after")
    def imported_identity(self) -> Self:
        if (self.input_path is None) != (self.input_file_sha256 is None):
            raise ValueError("Imported dataset requires both input_path and input_file_sha256")
        return self


class Treatment(Contract):
    id: Identifier
    overrides: dict = Field(default_factory=dict)


class EvaluationSpec(Contract):
    """Repeated stratified k-fold or temporal holdout over orders (deepmg-style protocol).

    Each campaign seed is one repetition: it shuffles the folds and seeds the job.
    """

    split: Literal["kfold", "temporal_holdout"]
    n_folds: int = Field(default=10, ge=2, le=20)
    test_size: float = Field(default=0.2, gt=0, lt=1)
    budget_fraction: float = Field(default=0.25, ge=0.05, le=0.5)
    stratify: Literal["dominant_category"] = "dominant_category"
    # "population": rescale subset order times to the full order arrival rate, so a
    # 1/k test fold is not simulated at 1/k of the load. None keeps sampled timestamps.
    order_rate: Literal["population"] | None = None

    @model_serializer(mode="wrap")
    def omit_absent_order_rate(self, handler):
        data = handler(self)
        if data.get("order_rate") is None:
            data.pop("order_rate", None)
        return data

    @property
    def folds(self) -> int:
        return self.n_folds if self.split == "kfold" else 1


class ExperimentSpec(Contract):
    id: str = Field(pattern=r"^E\d{2}$")
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
            "joint_evaluations_to_best",
            "train_objective",
            "test_objective",
            "test_mean_distance_m",
            "test_mean_wait_s",
            "generalization_gap",
        ]
    ] = Field(default=["wall_s", "mean_distance_m", "mean_wait_s"], min_length=1)
    acceptance: str = Field(min_length=5)
    statistical_method: Literal["descriptive_paired_exploratory"] = "descriptive_paired_exploratory"


def planned_jobs(spec: "CampaignSpec") -> int:
    folds = spec.evaluation.folds if spec.evaluation else 1
    return sum(
        len(e.datasets) * len(e.treatments) * len(spec.seeds) * spec.repetitions * folds
        for e in spec.experiments
    )


class CampaignSpec(Contract):
    schema_version: Literal["1.0", "1.1"] = "1.0"
    name: str = Field(min_length=1, max_length=120)
    data_origin: Literal["SYNTHETIC"] = "SYNTHETIC"
    datasets: list[DatasetSpec] = Field(min_length=1, max_length=20)
    experiments: list[ExperimentSpec] = Field(min_length=1, max_length=10)
    seeds: list[int] = Field(default=[11, 23, 37], min_length=1, max_length=100)
    repetitions: int = Field(default=1, ge=1, le=10)
    # Float defaults: unvalidated int defaults would hash differently after a JSON round trip.
    job_time_limit_s: float = Field(default=15.0, gt=0, le=900)
    memory_limit_mb: int = Field(default=1024, ge=128, le=8192)
    max_wall_s: float = Field(default=600.0, gt=0, le=14400)
    max_jobs: int = Field(default=128, ge=1, le=1000)
    max_retries: int = Field(default=1, ge=0, le=2)
    workers: Literal[1] = 1
    cache_policy: Literal["isolated", "reuse"] = "isolated"
    evaluation: EvaluationSpec | None = None

    @model_serializer(mode="wrap")
    def omit_absent_evaluation(self, handler):
        # Version 1.0 manifests keep their pre-existing canonical form and hash.
        data = handler(self)
        if data.get("evaluation") is None:
            data.pop("evaluation", None)
        return data

    @model_validator(mode="after")
    def references(self) -> Self:
        if self.evaluation is not None and self.schema_version != "1.1":
            raise ValueError("Held-out evaluation requires campaign schema_version 1.1")
        if planned_jobs(self) > 1000:
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
