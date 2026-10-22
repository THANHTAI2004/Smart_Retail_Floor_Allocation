"""Failure-preserving descriptive statistics and seed-paired exploratory comparisons."""

import math
import statistics
from collections import defaultdict

from scipy.stats import t, ttest_rel

METRICS = (
    "t1_objective",
    "wall_s",
    "peak_child_rss_bytes",
    "sampled_child_cpu_s",
    "mean_distance_m",
    "mean_wait_s",
    "t2_objective",
    "t3_objective",
    "joint_objective",
    "joint_evaluations",
    "joint_iterations_to_best",
    "holdout_objective",
)


def describe(values):
    n = len(values)
    if not n:
        return {"n": 0, "mean": None, "median": None, "sd": None, "ci95": None}
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if n > 1 else None
    half = float(t.ppf(0.975, n - 1)) * sd / math.sqrt(n) if sd is not None else None
    return {
        "n": n,
        "mean": mean,
        "median": statistics.median(values),
        "sd": sd,
        "ci95": [mean - half, mean + half] if half is not None else None,
        "minimum": min(values),
        "maximum": max(values),
    }


def analyze(rows, selected_metrics: dict[str, list[str]] | None = None):
    groups = defaultdict(list)
    for row in rows:
        groups[row["experiment"], row["dataset"], row["treatment"]].append(row)
    summary = []
    for (experiment, dataset, treatment), records in sorted(groups.items()):
        successes = sum(r["status"] == "SUCCEEDED" for r in records)
        n, p = len(records), successes / len(records)
        z = 1.959963984540054
        center, half = (
            (p + z * z / (2 * n)) / (1 + z * z / n),
            z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n),
        )
        summary.append(
            {
                "experiment": experiment,
                "dataset": dataset,
                "treatment": treatment,
                "total": n,
                "succeeded": successes,
                "failed_or_incomplete": n - successes,
                "completion_rate": p,
                "solution_feasible_count": sum(
                    r.get("solution_feasible", r["status"] == "SUCCEEDED") for r in records
                ),
                "solution_feasibility_rate": sum(
                    r.get("solution_feasible", r["status"] == "SUCCEEDED") for r in records
                )
                / n,
                "completion_rate_wilson95": [center - half, center + half],
                "metrics": {
                    metric: describe(
                        [r[metric] for r in records if isinstance(r.get(metric), (int, float))]
                    )
                    for metric in METRICS
                },
            }
        )
    comparisons = []
    for experiment, dataset in sorted({(r["experiment"], r["dataset"]) for r in rows}):
        arms = sorted(
            {
                r["treatment"]
                for r in rows
                if r["experiment"] == experiment and r["dataset"] == dataset
            }
        )
        if len(arms) < 2:
            continue
        baseline = "baseline" if "baseline" in arms else arms[0]
        for treatment in arms:
            if treatment == baseline:
                continue
            for metric in METRICS:
                if selected_metrics is not None and metric not in selected_metrics.get(
                    experiment, []
                ):
                    continue
                seed_values: dict[str, dict[int, list[float]]] = {
                    arm: defaultdict(list) for arm in (baseline, treatment)
                }
                for row in rows:
                    if (
                        row["experiment"] == experiment
                        and row["dataset"] == dataset
                        and row["treatment"] in seed_values
                        and row["status"] == "SUCCEEDED"
                        and isinstance(row.get(metric), (int, float))
                    ):
                        seed_values[row["treatment"]][row["seed"]].append(row[metric])
                seeds = sorted(seed_values[baseline].keys() & seed_values[treatment].keys())
                a = [statistics.mean(seed_values[baseline][seed]) for seed in seeds]
                b = [statistics.mean(seed_values[treatment][seed]) for seed in seeds]
                differences = [y - x for x, y in zip(a, b)]
                record = {
                    "experiment": experiment,
                    "dataset": dataset,
                    "baseline": baseline,
                    "treatment": treatment,
                    "metric": metric,
                    "seeds": seeds,
                    "difference": describe(differences),
                    "paired_effect_dz": None,
                    "exploratory_p": None,
                    "holm_p": None,
                }
                if len(seeds) >= 3 and statistics.stdev(differences) > 1e-10:
                    record["exploratory_p"] = float(ttest_rel(b, a).pvalue)
                    record["paired_effect_dz"] = statistics.mean(differences) / statistics.stdev(
                        differences
                    )
                else:
                    record["limitation"] = (
                        "Insufficient independent seeds or constant differences; no test inference"
                    )
                comparisons.append(record)
    tested = sorted(
        (r for r in comparisons if r["exploratory_p"] is not None), key=lambda r: r["exploratory_p"]
    )
    adjusted = 0.0
    for i, record in enumerate(tested):
        adjusted = max(adjusted, min(1, record["exploratory_p"] * (len(tested) - i)))
        record["holm_p"] = adjusted
    return {
        "selected_metrics": selected_metrics,
        "summary": summary,
        "comparisons": comparisons,
        "assumptions": [
            "Exploratory Student-t intervals and paired tests; no population-level efficacy claim",
            "Repeated identical seeds are averaged before pairing, not counted as independent replications",
            "Failure rates include all attempted jobs; solution metrics only exist for valid results",
            "Completion rate is not a proof of feasibility/infeasibility for unsolved cases",
            "Holm adjustment covers every reported nondegenerate paired metric comparison",
        ],
    }
