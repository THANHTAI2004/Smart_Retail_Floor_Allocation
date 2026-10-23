"""Split an over-limit campaign design into paired-comparison-preserving parts.

The atomic unit is one dataset with a chunk of seeds: every treatment and fold of
that unit stays in the same part, so paired comparisons never cross campaigns.
"""

from smart_retail.contracts.experiments import CampaignSpec, planned_jobs

HARD_LIMIT = 1000


def jobs_per_seed(spec: CampaignSpec, dataset_id: str) -> int:
    folds = spec.evaluation.folds if spec.evaluation else 1
    return sum(
        len(e.treatments) * spec.repetitions * folds
        for e in spec.experiments
        if dataset_id in e.datasets
    )


def partition(spec: dict, max_jobs: int = HARD_LIMIT) -> list[CampaignSpec]:
    if not 1 <= max_jobs <= HARD_LIMIT:
        raise ValueError(f"max_jobs must be within 1..{HARD_LIMIT}")
    # Validate everything except the job ceiling that this function resolves.
    seeds = spec.get("seeds", [11, 23, 37])
    probe = CampaignSpec.model_validate({**spec, "seeds": seeds[:1]})
    units: list[tuple[list[str], list[int]]] = []
    whole: list[tuple[str, int]] = []
    for dataset in probe.datasets:
        per_seed = jobs_per_seed(probe, dataset.id)
        if per_seed == 0:
            continue
        if per_seed > max_jobs:
            raise ValueError(f"Dataset {dataset.id} needs {per_seed} jobs for one seed")
        if per_seed * len(seeds) <= max_jobs:
            whole.append((dataset.id, per_seed * len(seeds)))
        else:
            size = max_jobs // per_seed
            units.extend(([dataset.id], seeds[i : i + size]) for i in range(0, len(seeds), size))
    group: list[str] = []
    load = 0
    for dataset_id, jobs in whole:
        if group and load + jobs > max_jobs:
            units.append((group, seeds))
            group, load = [], 0
        group.append(dataset_id)
        load += jobs
    if group:
        units.append((group, seeds))
    parts = []
    for index, (datasets, chunk) in enumerate(units, start=1):
        experiments = [
            {**e, "datasets": [d for d in e["datasets"] if d in datasets]}
            for e in spec["experiments"]
            if any(d in datasets for d in e["datasets"])
        ]
        part = CampaignSpec.model_validate(
            {
                **spec,
                "name": f"{spec['name']}-part{index:02d}",
                "datasets": [d for d in spec["datasets"] if d["id"] in datasets],
                "experiments": experiments,
                "seeds": chunk,
            }
        )
        part = part.model_copy(update={"max_jobs": planned_jobs(part)})
        parts.append(part)
    return parts
