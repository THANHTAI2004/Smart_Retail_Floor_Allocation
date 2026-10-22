import math

from experiments.analyze_campaign import paired
from experiments.run_campaign import summarize


def test_single_observation_does_not_invent_uncertainty():
    summary = summarize([{"experiment": "E", "treatment": "A", "status": "SUCCEEDED", "wall_s": 2}])
    assert summary[0]["metrics"]["wall_s"] == {"n": 1, "mean": 2, "sample_sd": None, "ci95": None}


def test_statistics_preserve_failures_and_constant_paired_differences():
    rows = []
    for seed in range(5):
        for arm, delta in (("baseline", 0), ("treatment", -1)):
            rows.append({"experiment": "E", "treatment": arm, "status": "SUCCEEDED", "seed": seed,
                         "mean_distance_m": 10 + seed + delta, "mean_wait_s": 0, "wall_s": seed + 1})
    comparison = paired(rows)[0]
    assert comparison["n"] == 5
    assert comparison["mean_treatment_minus_baseline"] == -1
    assert comparison["ci95"] == [-1, -1]
    assert comparison["exploratory_p"] is None
    assert comparison["holm_p"] is None
    for row in rows:
        if row["treatment"] == "treatment":
            row["status"] = "FAILED"
    assert paired(rows)[0]["n"] == 0
    assert paired(rows)[0]["ci95"] is None
    assert summarize(rows)[1]["succeeded"] == 0


def test_nonconstant_paired_ci_and_holm_are_finite():
    rows = []
    for seed in range(5):
        for arm, delta in (("baseline", 0), ("treatment", seed + 1)):
            rows.append({"experiment": "E", "treatment": arm, "status": "SUCCEEDED", "seed": seed,
                         "mean_distance_m": 10 + delta, "mean_wait_s": delta, "wall_s": 1 + delta})
    comparison = paired(rows)
    for result in comparison:
        assert result["mean_treatment_minus_baseline"] == 3
        assert all(math.isfinite(x) for x in result["ci95"])
        assert 0 <= result["exploratory_p"] <= result["holm_p"] <= 1
