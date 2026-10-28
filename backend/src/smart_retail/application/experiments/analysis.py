"""Failure-preserving descriptive statistics and seed/fold-paired comparisons.

Pairing unit: (seed, cv_fold); repetitions of one unit are averaged first. Folds of
one repetition share training orders, so repeated k-fold tests use the
Nadeau-Bengio corrected variance instead of treating folds as independent.
"""

import math
import random
import statistics
from collections import defaultdict

from scipy.stats import friedmanchisquare, rankdata, studentized_range, t, ttest_rel, wilcoxon

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
    "joint_evaluations_to_best",
    "holdout_objective",
    "train_objective",
    "test_objective",
    "test_mean_distance_m",
    "test_mean_wait_s",
    "generalization_gap",
)
OBJECTIVE_METRICS = {"train_objective", "test_objective", "generalization_gap"}
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20261023
TOLERANCE = 1e-10
# Instance-level reference: the strongest sequential pipeline when present.
REFERENCE_ARMS = ("seq_milp", "baseline")
# Primary Holm family of instance_comparisons (held-out objective, else training objective).
PRIMARY_METRICS = ("test_objective", "joint_objective")


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


def vargha_delaney_a12(treatment, baseline):
    """P(treatment > baseline) + 0.5 P(tie); 0.5 means no stochastic difference."""
    if not treatment or not baseline:
        return None
    greater = sum((x > y) + 0.5 * (x == y) for x in treatment for y in baseline)
    return greater / (len(treatment) * len(baseline))


def bootstrap_median_ci(differences, resamples=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED):
    if len(differences) < 2:
        return None
    rng = random.Random(seed)
    medians = sorted(
        statistics.median(rng.choices(differences, k=len(differences))) for _ in range(resamples)
    )
    return [medians[int(0.025 * resamples)], medians[int(0.975 * resamples) - 1]]


def wilcoxon_p(differences):
    if sum(abs(d) > TOLERANCE for d in differences) < 2:
        return None
    return float(wilcoxon(differences, zero_method="wilcox").pvalue)


def nadeau_bengio_p(differences, test_to_train):
    """Corrected resampled t-test (Nadeau & Bengio, 2003) for repeated k-fold units."""
    n = len(differences)
    if n < 3 or test_to_train is None:
        return None
    variance = statistics.variance(differences)
    if variance <= TOLERANCE:
        return None
    statistic = statistics.mean(differences) / math.sqrt((1 / n + test_to_train) * variance)
    return float(2 * t.sf(abs(statistic), n - 1))


def holm(records, key, target):
    tested = sorted((r for r in records if r[key] is not None), key=lambda r: r[key])
    adjusted = 0.0
    for i, record in enumerate(tested):
        adjusted = max(adjusted, min(1, record[key] * (len(tested) - i)))
        record[target] = adjusted


def unit_values(rows, experiment, dataset, metric):
    """{treatment: {(seed, cv_fold): mean over repetitions}} for successful jobs."""
    values: dict[str, dict[tuple, list[float]]] = defaultdict(lambda: defaultdict(list))
    ratios: list[float] = []
    for row in rows:
        if (
            row["experiment"] == experiment
            and row["dataset"] == dataset
            and row["status"] == "SUCCEEDED"
            and isinstance(row.get(metric), (int, float))
        ):
            values[row["treatment"]][row["seed"], row.get("cv_fold")].append(row[metric])
            if row.get("test_orders") and row.get("train_orders"):
                ratios.append(row["test_orders"] / row["train_orders"])
    means = {
        arm: {u: statistics.mean(v) for u, v in units.items()} for arm, units in values.items()
    }
    return means, (statistics.mean(ratios) if ratios else None)


def mixed_objectives(rows, experiment, arms, metric) -> bool:
    """True when arms were scored by different objective definitions."""
    if metric not in OBJECTIVE_METRICS:
        return False
    definitions = {
        r.get("objective_definition")
        for r in rows
        if r["experiment"] == experiment and r["treatment"] in arms and r["status"] == "SUCCEEDED"
    }
    return len(definitions) > 1


def friedman_nemenyi(blocks: list[list[float]], arms: list[str], level: str) -> dict:
    """Average ranks (1 = smallest value), Friedman test and Nemenyi critical difference."""
    k, n = len(arms), len(blocks)
    record: dict = {"level": level, "treatments": arms, "blocks": n}
    if k < 3 or n < 2:
        return {**record, "limitation": "Friedman needs >=3 treatments and >=2 complete blocks"}
    ranks = [rankdata(block) for block in blocks]
    average = [float(sum(r[i] for r in ranks) / n) for i in range(k)]
    columns = [[block[i] for block in blocks] for i in range(k)]
    degenerate = all(max(b) - min(b) <= TOLERANCE for b in blocks)
    q = float(studentized_range.ppf(0.95, k, math.inf)) / math.sqrt(2)
    cd = q * math.sqrt(k * (k + 1) / (6 * n))
    record.update(
        average_ranks=dict(zip(arms, average)),
        friedman_p=None if degenerate else float(friedmanchisquare(*columns).pvalue),
        nemenyi_cd_0_05=cd,
        nemenyi_different=[
            [arms[i], arms[j]]
            for i in range(k)
            for j in range(i + 1, k)
            if abs(average[i] - average[j]) > cd
        ],
    )
    if n < 5:
        record["limitation"] = "Fewer than five blocks; ranking test has little power"
    return record


def exact_wilcoxon_p(differences):
    """Two-sided exact signed-rank p over nonzero differences; None if all are zero."""
    nonzero = [d for d in differences if abs(d) > TOLERANCE]
    if not nonzero:
        return None
    return float(wilcoxon(nonzero, method="exact").pvalue)


def instance_comparisons(rows, metrics_of, scales: dict[str, str] | None = None):
    """Instance-level inference: each instance contributes one paired mean per arm.

    Per instance, arm values are averaged over the (seed, cv_fold) units shared with the
    reference arm (seq_milp, else baseline). When an ``exact`` arm exists (X1), every arm
    is also compared with it: the gap to the certified optimum of the declared space.
    Folds and seeds of one instance are not independent, so the instance is the unit of
    the exact Wilcoxon test. Results are reported per scale and pooled; Holm runs over
    the whole table.
    """
    scales = scales or {}
    records = []
    for experiment in sorted({r["experiment"] for r in rows}):
        arms = sorted({r["treatment"] for r in rows if r["experiment"] == experiment})
        references = [a for a in REFERENCE_ARMS if a in arms][:1]
        # X1: the certified optimum of the declared space is a second reference (the gap).
        if "exact" in arms:
            references.append("exact")
        datasets = sorted({r["dataset"] for r in rows if r["experiment"] == experiment})
        for reference, metric in (
            (reference, metric) for reference in references for metric in metrics_of(experiment)
        ):
            pairs: dict[str, dict[str, tuple[float, float]]] = defaultdict(dict)
            for dataset in datasets:
                values, _ = unit_values(rows, experiment, dataset, metric)
                base = values.get(reference, {})
                for arm in arms:
                    common = base.keys() & values.get(arm, {}).keys()
                    if arm != reference and common:
                        pairs[arm][dataset] = (
                            statistics.mean(base[u] for u in common),
                            statistics.mean(values[arm][u] for u in common),
                        )
            for arm, by_dataset in sorted(pairs.items()):
                if mixed_objectives(rows, experiment, (reference, arm), metric):
                    continue
                groups: dict[str, list[str]] = defaultdict(list)
                for dataset in by_dataset:
                    groups[scales.get(dataset, "unknown")].append(dataset)
                if len(groups) > 1:
                    groups["all"] = list(by_dataset)
                for scale, members in sorted(groups.items()):
                    a = [by_dataset[d][0] for d in members]
                    b = [by_dataset[d][1] for d in members]
                    differences = [y - x for x, y in zip(a, b)]
                    relative = [(y - x) / x for x, y in zip(a, b) if abs(x) > TOLERANCE]
                    records.append(
                        {
                            "experiment": experiment,
                            "metric": metric,
                            "scale": scale,
                            "reference": reference,
                            "treatment": arm,
                            "instances": len(members),
                            "treatment_lower": sum(d < -TOLERANCE for d in differences),
                            "ties": sum(abs(d) <= TOLERANCE for d in differences),
                            "reference_mean": statistics.mean(a),
                            "treatment_mean": statistics.mean(b),
                            "relative_change_of_means": (statistics.mean(b) - statistics.mean(a))
                            / statistics.mean(a)
                            if abs(statistics.mean(a)) > TOLERANCE
                            else None,
                            "relative_change_per_instance": describe(relative),
                            "wilcoxon_exact_p": exact_wilcoxon_p(differences),
                            "smallest_attainable_p": 2 / 2 ** len(members),
                            "holm_wilcoxon_exact_p": None,
                            "holm_primary_wilcoxon_exact_p": None,
                        }
                    )
    holm(records, "wilcoxon_exact_p", "holm_wilcoxon_exact_p")
    # Pre-declared primary family: objective metrics only (wall time, memory and component
    # metrics stay in the full-table family and are reported as secondary).
    primary = [r for r in records if r["metric"] in PRIMARY_METRICS]
    holm(primary, "wilcoxon_exact_p", "holm_primary_wilcoxon_exact_p")
    return records


def analyze(
    rows,
    selected_metrics: dict[str, list[str]] | None = None,
    scales: dict[str, str] | None = None,
):
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

    def chosen(experiment):
        return [
            m
            for m in METRICS
            if selected_metrics is None or m in selected_metrics.get(experiment, [])
        ]

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
        for metric in chosen(experiment):
            values, ratio = unit_values(rows, experiment, dataset, metric)
            cross_validated = any(u[1] is not None for arm in values.values() for u in arm)
            for treatment in arms:
                if treatment == baseline:
                    continue
                units = sorted(
                    values.get(baseline, {}).keys() & values.get(treatment, {}).keys(),
                    key=lambda u: (u[0], -1 if u[1] is None else u[1]),
                )
                a = [values[baseline][u] for u in units]
                b = [values[treatment][u] for u in units]
                differences = [y - x for x, y in zip(a, b)]
                record = {
                    "experiment": experiment,
                    "dataset": dataset,
                    "baseline": baseline,
                    "treatment": treatment,
                    "metric": metric,
                    "seeds": sorted({u[0] for u in units}),
                    "paired_units": len(units),
                    "cross_validated": cross_validated,
                    "difference": describe(differences),
                    "median_difference_bootstrap_ci95": bootstrap_median_ci(differences),
                    "a12_treatment_greater": vargha_delaney_a12(b, a),
                    "paired_effect_dz": None,
                    "exploratory_p": None,
                    "holm_p": None,
                    "wilcoxon_p": wilcoxon_p(differences),
                    "holm_wilcoxon_p": None,
                    "nadeau_bengio_p": nadeau_bengio_p(differences, ratio)
                    if cross_validated
                    else None,
                    "holm_nadeau_bengio_p": None,
                    "test_to_train_orders": ratio,
                }
                if mixed_objectives(rows, experiment, (baseline, treatment), metric):
                    record.update(
                        wilcoxon_p=None,
                        nadeau_bengio_p=None,
                        limitation="Arms use different objective definitions; values are not comparable",
                    )
                elif len(units) >= 3 and statistics.stdev(differences) > TOLERANCE:
                    record["exploratory_p"] = float(ttest_rel(b, a).pvalue)
                    record["paired_effect_dz"] = statistics.mean(differences) / statistics.stdev(
                        differences
                    )
                else:
                    record["limitation"] = (
                        "Insufficient independent units or constant differences; no t-test inference"
                    )
                comparisons.append(record)
    holm(comparisons, "exploratory_p", "holm_p")
    holm(comparisons, "wilcoxon_p", "holm_wilcoxon_p")
    holm(comparisons, "nadeau_bengio_p", "holm_nadeau_bengio_p")

    rankings = []
    for experiment in sorted({r["experiment"] for r in rows}):
        datasets = sorted({r["dataset"] for r in rows if r["experiment"] == experiment})
        arms = sorted({r["treatment"] for r in rows if r["experiment"] == experiment})
        if len(arms) < 3:
            continue
        for metric in chosen(experiment):
            if mixed_objectives(rows, experiment, arms, metric):
                rankings.append(
                    {
                        "experiment": experiment,
                        "metric": metric,
                        "limitation": "Arms use different objective definitions; no ranking",
                    }
                )
                continue
            per_dataset = {d: unit_values(rows, experiment, d, metric)[0] for d in datasets}
            unit_blocks: list[list[float]] = []
            dataset_blocks: list[list[float]] = []
            for d, values in per_dataset.items():
                if not all(arm in values for arm in arms):
                    continue
                common = set.intersection(*(set(values[arm]) for arm in arms))
                unit_blocks.extend(
                    [values[arm][u] for arm in arms] for u in sorted(common, key=str)
                )
                dataset_blocks.append([statistics.mean(values[arm].values()) for arm in arms])
            for level, blocks in (("dataset_means", dataset_blocks), ("units", unit_blocks)):
                rankings.append(
                    {
                        "experiment": experiment,
                        "metric": metric,
                        **friedman_nemenyi(blocks, arms, level),
                    }
                )
    return {
        "selected_metrics": selected_metrics,
        "summary": summary,
        "comparisons": comparisons,
        "instance_comparisons": instance_comparisons(rows, chosen, scales),
        "rankings": rankings,
        "assumptions": [
            "Exploratory paired tests; no population-level efficacy claim",
            "Pairing unit is (seed, cv_fold); repeated identical units are averaged, not counted as independent",
            "Repeated k-fold units share training orders: use nadeau_bengio_p, not the naive t-test, for cross-validated comparisons",
            "Wilcoxon signed-rank drops zero differences; A12 = P(treatment > baseline) + 0.5 P(tie)",
            f"Median-difference CI: percentile bootstrap, {BOOTSTRAP_RESAMPLES} resamples, seed {BOOTSTRAP_SEED}",
            "Friedman/Nemenyi rank 1 = smallest value; dataset_means blocks are the inferential level, units blocks are exploratory",
            "Failure rates include all attempted jobs; solution metrics only exist for valid results",
            "Completion rate is not a proof of feasibility/infeasibility for unsolved cases",
            "Holm adjustment is applied separately to each reported test family",
            "instance_comparisons: the instance is the inferential unit (mean over shared seed/fold units), reference arm seq_milp else baseline, exact two-sided Wilcoxon, reported per scale and pooled",
        ],
    }
