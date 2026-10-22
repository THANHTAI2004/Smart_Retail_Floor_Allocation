import math

from smart_retail.application.experiments.analysis import analyze, describe


def test_singleton_and_empty_samples_do_not_invent_intervals():
    assert describe([])["ci95"] is None
    assert describe([3])["sd"] is None
    assert describe([1, 3])["median"] == 2


def test_failed_jobs_retained_and_duplicate_seeds_not_independent():
    rows = []
    for seed in (1, 2, 3):
        for treatment, delta in (("baseline", 0), ("treatment", seed)):
            for repetition in (0, 1):
                rows.append(
                    {
                        "experiment": "E04",
                        "dataset": "tiny",
                        "treatment": treatment,
                        "seed": seed,
                        "repetition": repetition,
                        "status": "SUCCEEDED",
                        "wall_s": 1 + seed + delta,
                        "mean_distance_m": 10 + delta,
                    }
                )
    rows.append(
        {
            "experiment": "E04",
            "dataset": "tiny",
            "treatment": "treatment",
            "seed": 9,
            "repetition": 0,
            "status": "TIMED_OUT",
            "wall_s": 20,
        }
    )
    result = analyze(rows)
    summary = next(g for g in result["summary"] if g["treatment"] == "treatment")
    assert summary["total"] == 7 and summary["succeeded"] == 6
    assert summary["completion_rate"] == 6 / 7
    assert summary["metrics"]["wall_s"]["n"] == 7
    assert summary["metrics"]["mean_distance_m"]["n"] == 6
    comparisons = [c for c in result["comparisons"] if c["metric"] == "mean_distance_m"]
    assert comparisons[0]["difference"]["n"] == 3
    assert comparisons[0]["difference"]["mean"] == 2
    assert math.isfinite(comparisons[0]["paired_effect_dz"])
    assert 0 <= comparisons[0]["exploratory_p"] <= comparisons[0]["holm_p"] <= 1


def test_degenerate_pairs_get_no_hypothesis_test():
    rows = [
        {
            "experiment": "E",
            "dataset": "D",
            "treatment": arm,
            "seed": seed,
            "status": "SUCCEEDED",
            "wall_s": 1,
            "mean_distance_m": 10 + delta,
        }
        for seed in range(5)
        for arm, delta in (("baseline", 0), ("treatment", -1))
    ]
    comparison = next(c for c in analyze(rows)["comparisons"] if c["metric"] == "mean_distance_m")
    assert comparison["difference"]["ci95"] == [-1, -1]
    assert comparison["exploratory_p"] is None
    assert comparison["holm_p"] is None
