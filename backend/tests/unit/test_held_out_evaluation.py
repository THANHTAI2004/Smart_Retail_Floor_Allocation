# Vai trò: Kiểm thử chia tập, tránh rò rỉ dữ liệu, chấm holdout và suy luận thống kê ghép cặp.
# Các assertion mô tả hành vi mong đợi; kết quả chỉ được xác nhận sau khi chạy test.
import copy
import json
import math

import pytest
from pydantic import ValidationError

from smart_retail.application.evaluation import estimate_demand
from smart_retail.application.experiments.analysis import (
    analyze,
    friedman_nemenyi,
    nadeau_bengio_p,
    vargha_delaney_a12,
)
from smart_retail.application.experiments.generators import generate, merge
from smart_retail.application.experiments.partition import partition
from smart_retail.application.experiments.splits import apply_split, split_orders
from smart_retail.application.workflow import canonical_hash, execute
from smart_retail.contracts.experiments import (
    CampaignSpec,
    DatasetSpec,
    EvaluationSpec,
    planned_jobs,
)
from smart_retail.contracts.inputs import OptimizationInput, to_domain, validate_references

KFOLD = EvaluationSpec(split="kfold", n_folds=5)


@pytest.fixture(scope="module")
# Hàm tiny: xử lý bước tiny trong phạm vi module hiện tại.
def tiny():
    return generate(DatasetSpec(id="tiny", scale="tiny", facings=6))[0]


# Hàm ids: xử lý bước ids trong phạm vi module hiện tại.
def ids(section):
    return {o["id"] for o in section["orders"]}


# Hàm test_kfold_partition_is_deterministic_disjoint_exhaustive_and_balanced: kiểm tra kịch bản kfold partition is deterministic disjoint exhaustive and balanced bằng các assertion trong thân hàm.
def test_kfold_partition_is_deterministic_disjoint_exhaustive_and_balanced(tiny):
    plan = split_orders(tiny, KFOLD, 11)
    assert plan == split_orders(tiny, KFOLD, 11)
    assert plan["sha256"] == canonical_hash({k: v for k, v in plan.items() if k != "sha256"})
    everyone = ids(tiny["orders"])
    tests = [set(f["test"]) for f in plan["folds"]]
    assert set().union(*tests) == everyone and sum(map(len, tests)) == len(everyone)
    assert max(map(len, tests)) - min(map(len, tests)) <= 1
    for fold in plan["folds"]:
        assert set(fold["train"]) | set(fold["test"]) == everyone
        assert not set(fold["train"]) & set(fold["test"])
    assert sum(plan["strata_sizes"].values()) == len(everyone)
    assert split_orders(tiny, KFOLD, 23)["folds"] != plan["folds"]


# Hàm test_temporal_holdout_tests_on_latest_orders: kiểm tra kịch bản temporal holdout tests on latest orders bằng các assertion trong thân hàm.
def test_temporal_holdout_tests_on_latest_orders(tiny):
    spec = EvaluationSpec(split="temporal_holdout", test_size=0.25)
    plan = split_orders(tiny, spec, 11)
    (fold,) = plan["folds"]
    stamps = {o["id"]: o["placed_at"] for o in tiny["orders"]["orders"]}
    assert len(fold["test"]) == math.ceil(len(stamps) * 0.25)
    assert max(stamps[i] for i in fold["train"]) <= min(stamps[i] for i in fold["test"])
    assert plan["folds"] == split_orders(tiny, spec, 99)["folds"]


# Hàm test_too_many_folds_rejected: kiểm tra kịch bản too many folds rejected bằng các assertion trong thân hàm.
def test_too_many_folds_rejected(tiny):
    small = copy.deepcopy(tiny)
    small["orders"]["orders"] = small["orders"]["orders"][:3]
    kept = ids(small["orders"])
    small["orders"]["order_lines"] = [
        x for x in small["orders"]["order_lines"] if x["order_id"] in kept
    ]
    with pytest.raises(ValueError, match="at least as many orders"):
        split_orders(small, KFOLD, 11)
    with pytest.raises(ValueError, match="one training and one test"):
        split_orders(small, EvaluationSpec(split="temporal_holdout", test_size=0.99), 11)


# Hàm test_demand_is_estimated_from_the_subset_only: kiểm tra kịch bản demand is estimated from the subset only bằng các assertion trong thân hàm.
def test_demand_is_estimated_from_the_subset_only(tiny):
    orders = copy.deepcopy(tiny["orders"])
    orders["orders"] = orders["orders"][:4]
    kept = ids(orders)
    orders["order_lines"] = [x for x in orders["order_lines"] if x["order_id"] in kept]
    data = estimate_demand(tiny, orders, population_orders=20)
    units = {}
    for line in orders["order_lines"]:
        units[line["sku"]] = units.get(line["sku"], 0) + line["quantity"]
    for product in data["products"]["items"]:
        assert product["demand"] == pytest.approx(units.get(product["sku"], 0) * 20 / 4)
    for category in data["categories"]["items"]:
        expected = sum(
            p["demand"] for p in data["products"]["items"] if p["category_id"] == category["id"]
        )
        assert category["demand"] == pytest.approx(expected)
    assert ids(data["orders"]) == kept
    to_domain(data)


# Hàm test_held_out_orders_never_reach_the_domain_or_engines: kiểm tra kịch bản held out orders never reach the domain or engines bằng các assertion trong thân hàm.
def test_held_out_orders_never_reach_the_domain_or_engines(tiny):
    plan = split_orders(tiny, KFOLD, 11)
    job = apply_split(tiny, plan, 0, KFOLD)
    held_out = ids(job["optimization"]["evaluation"]["orders"])
    assert held_out == set(plan["folds"][0]["test"])
    dataset = to_domain(job)
    assert {o.id for o in dataset.orders} == set(plan["folds"][0]["train"])
    assert not hasattr(dataset.config, "evaluation")
    overlapping = copy.deepcopy(job)
    first_training_order = job["orders"]["orders"][0]["id"]
    overlapping["optimization"]["evaluation"]["orders"]["orders"][0]["id"] = first_training_order
    assert "Held-out orders overlap training orders" in validate_references(overlapping)


# Hàm test_apply_split_rejects_orders_changed_by_overrides: kiểm tra kịch bản apply split rejects orders changed by overrides bằng các assertion trong thân hàm.
def test_apply_split_rejects_orders_changed_by_overrides(tiny):
    plan = split_orders(tiny, KFOLD, 11)
    changed = copy.deepcopy(tiny)
    changed["orders"]["orders"][0]["due_s"] = 1
    with pytest.raises(ValueError, match="changed the orders"):
        apply_split(changed, plan, 0, KFOLD)


# Hàm test_execute_optimizes_on_training_orders_and_scores_held_out_orders: kiểm tra kịch bản execute optimizes on training orders and scores held out orders bằng các assertion trong thân hàm.
def test_execute_optimizes_on_training_orders_and_scores_held_out_orders(tiny):
    plan = split_orders(tiny, KFOLD, 11)
    job = apply_split(tiny, plan, 1, KFOLD)
    job["optimization"].update(seed=11, time_limit_s=20)
    result = execute(job)
    assert result["input_sha256"] == canonical_hash(job)
    journeys = result["stages"]["T4"]["metrics"]["journeys"]
    pickers = {j["id"] for j in journeys if j["kind"] == "picker"}
    assert pickers <= set(plan["folds"][1]["train"])
    evaluation = result["evaluation"]
    assert evaluation["status"] == "COMPLETED" and evaluation["validation"] == "PASS"
    assert (evaluation["train_orders"], evaluation["test_orders"]) == (16, 4)
    assert evaluation["generalization_gap"] == pytest.approx(
        evaluation["objective"] - evaluation["train_objective"]
    )
    selected = result["integrated"]["candidates"][result["integrated"]["selected_candidate"]]
    assert evaluation["train_objective"] == selected["score"]
    assert execute(copy.deepcopy(job))["evaluation"]["objective"] == evaluation["objective"]


# Hàm test_joint_mode_scores_selected_decisions_on_held_out_orders: kiểm tra kịch bản joint mode scores selected decisions on held out orders bằng các assertion trong thân hàm.
def test_joint_mode_scores_selected_decisions_on_held_out_orders(tiny):
    joint = {
        "objective": {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]},
        "scenario_seeds": [0, 101],
        "scenario_seed_policy": "job_seed_offsets",
        "max_iterations": 1,
        "max_evaluations": 6,
        "max_actions": 4,
        "mode": "feedback",
    }
    data = merge(copy.deepcopy(tiny), {"optimization": {"joint": joint}})
    job = apply_split(data, split_orders(data, KFOLD, 11), 0, KFOLD)
    job["optimization"].update(seed=11, time_limit_s=30)
    result = execute(job)
    evaluation = result["evaluation"]
    assert evaluation["status"] == "COMPLETED"
    assert evaluation["train_objective"] == result["joint"]["best"]["score"]
    assert math.isfinite(evaluation["objective"])


# Hàm test_engine_errors_survive_simpy_reraise_and_pickling: kiểm tra kịch bản engine errors survive simpy reraise and pickling bằng các assertion trong thân hàm.
def test_engine_errors_survive_simpy_reraise_and_pickling():
    import pickle

    import simpy

    from smart_retail.domain.models import EngineError

    env = simpy.Environment()

    # Hàm journey: xử lý bước journey trong phạm vi module hiện tại.
    def journey():
        yield env.timeout(1)
        raise EngineError("TIMEOUT", "T4 simulation time limit")

    env.process(journey())
    with pytest.raises(EngineError) as raised:
        env.run()
    assert raised.value.code == "TIMEOUT" and str(raised.value) == "T4 simulation time limit"
    copy_ = pickle.loads(pickle.dumps(raised.value))
    assert (copy_.code, str(copy_)) == ("TIMEOUT", "T4 simulation time limit")


# Hàm test_held_out_budget_exhaustion_is_recorded_not_failed: kiểm tra kịch bản held out budget exhaustion is recorded not failed bằng các assertion trong thân hàm.
def test_held_out_budget_exhaustion_is_recorded_not_failed(tiny):
    plan = split_orders(tiny, KFOLD, 11)
    job = apply_split(tiny, plan, 0, KFOLD)
    job["optimization"].update(seed=11, time_limit_s=20)
    from smart_retail.application.evaluation import evaluate_held_out

    result = execute(copy.deepcopy(job))
    evaluation = evaluate_held_out(
        job, result, 0.0, lambda: False, lambda _: None, {}, lambda *args: None
    )
    assert evaluation["status"] == "NOT_EXECUTED_BUDGET"


# Hàm test_worker_wall_budget_leaves_finalization_grace: kiểm tra kịch bản worker wall budget leaves finalization grace bằng các assertion trong thân hàm.
def test_worker_wall_budget_leaves_finalization_grace():
    from smart_retail.workers.runner import wall_budget

    assert wall_budget(20) == 35
    assert wall_budget(300) == 330
    assert wall_budget(900) == 990
    assert wall_budget(3600) == 3960
    # paper-v4: medium budget 40 and large equal-wall-time blocks need jobs above 900 s.
    assert OptimizationInput(time_limit_s=3600).time_limit_s == 3600
    with pytest.raises(ValidationError):
        OptimizationInput(time_limit_s=3601)


# Hàm test_inputs_without_evaluation_keep_their_canonical_form: kiểm tra kịch bản inputs without evaluation keep their canonical form bằng các assertion trong thân hàm.
def test_inputs_without_evaluation_keep_their_canonical_form():
    assert "evaluation" not in OptimizationInput().model_dump(mode="json")
    spec = CampaignSpec.model_validate(
        {
            "name": "x",
            "datasets": [{"id": "tiny"}],
            "experiments": [
                {
                    "id": "E01",
                    "question": "Question?",
                    "hypothesis": "Hypothesis",
                    "datasets": ["tiny"],
                    "treatments": [{"id": "baseline"}],
                    "acceptance": "Accept",
                }
            ],
        }
    )
    assert "evaluation" not in spec.model_dump(mode="json")
    assert planned_jobs(spec) == 3


# Hàm campaign: xử lý bước campaign trong phạm vi module hiện tại.
def campaign(**extra):
    return {
        "schema_version": "1.1",
        "name": "cv",
        "datasets": [{"id": f"d{i}"} for i in range(3)],
        "experiments": [
            {
                "id": "E16",
                "question": "Question?",
                "hypothesis": "Hypothesis",
                "datasets": ["d0", "d1", "d2"],
                "treatments": [{"id": "baseline"}, {"id": "treatment"}],
                "acceptance": "Accept",
            }
        ],
        "seeds": list(range(1, 11)),
        "evaluation": {"split": "kfold", "n_folds": 10},
        **extra,
    }


# Hàm test_campaign_evaluation_contract_and_job_ceiling: kiểm tra kịch bản campaign evaluation contract and job ceiling bằng các assertion trong thân hàm.
def test_campaign_evaluation_contract_and_job_ceiling():
    with pytest.raises(ValidationError, match="schema_version 1.1"):
        CampaignSpec.model_validate({**campaign(seeds=[1]), "schema_version": "1.0"})
    with pytest.raises(ValidationError, match="1,000 jobs"):
        CampaignSpec.model_validate(campaign(seeds=list(range(1, 21))))
    spec = CampaignSpec.model_validate(campaign(seeds=[1, 2]))
    assert planned_jobs(spec) == 3 * 2 * 2 * 10


# Hàm test_partition_keeps_each_dataset_seed_unit_in_one_part: kiểm tra kịch bản partition keeps each dataset seed unit in one part bằng các assertion trong thân hàm.
def test_partition_keeps_each_dataset_seed_unit_in_one_part():
    parts = partition(campaign(), max_jobs=250)
    assert all(planned_jobs(p) <= 250 and p.max_jobs == planned_jobs(p) for p in parts)
    assert sum(planned_jobs(p) for p in parts) == 3 * 2 * 10 * 10
    units = [(d.id, seed) for p in parts for d in p.datasets for seed in p.seeds]
    assert len(units) == len(set(units)) == 30
    with pytest.raises(ValueError, match="one seed"):
        partition(campaign(), max_jobs=10)


# Hàm test_corrected_resampled_test_is_more_conservative_than_naive: kiểm tra kịch bản corrected resampled test is more conservative than naive bằng các assertion trong thân hàm.
def test_corrected_resampled_test_is_more_conservative_than_naive():
    differences = [0.1, 0.12, 0.08, 0.11, 0.09, 0.13, 0.1, 0.07, 0.12, 0.1]
    corrected = nadeau_bengio_p(differences, test_to_train=1 / 9)
    naive = nadeau_bengio_p(differences, test_to_train=0)
    assert naive < corrected < 1
    assert nadeau_bengio_p([1, 1, 1], 0.1) is None
    assert vargha_delaney_a12([2, 3], [1, 1]) == 1 and vargha_delaney_a12([1], [1]) == 0.5


# Hàm test_friedman_nemenyi_ranks_and_critical_difference: kiểm tra kịch bản friedman nemenyi ranks and critical difference bằng các assertion trong thân hàm.
def test_friedman_nemenyi_ranks_and_critical_difference():
    blocks = [[1.0, 2.0, 3.0]] * 6
    result = friedman_nemenyi(blocks, ["a", "b", "c"], "dataset_means")
    assert result["average_ranks"] == {"a": 1.0, "b": 2.0, "c": 3.0}
    assert result["nemenyi_cd_0_05"] == pytest.approx(2.343 * math.sqrt(12 / 36), rel=1e-3)
    assert ["a", "c"] in result["nemenyi_different"]
    assert "limitation" in friedman_nemenyi([[1.0, 2.0]], ["a", "b"], "units")


# Hàm test_arms_with_different_objective_definitions_are_not_tested: kiểm tra kịch bản arms with different objective definitions are not tested bằng các assertion trong thân hàm.
def test_arms_with_different_objective_definitions_are_not_tested():
    rows = [
        {
            "experiment": "E16",
            "dataset": "d",
            "treatment": arm,
            "seed": seed,
            "cv_fold": 0,
            "repetition": 0,
            "status": "SUCCEEDED",
            "objective_definition": definition,
            "test_objective": seed + (arm == "treatment"),
            "test_mean_distance_m": seed + 2 * (arm == "treatment") + 0.1 * seed**2,
        }
        for seed in range(1, 6)
        for arm, definition in (("baseline", "integrated-v1"), ("treatment", "joint:abc"))
    ]
    result = analyze(rows, {"E16": ["test_objective", "test_mean_distance_m"]})
    by_metric = {c["metric"]: c for c in result["comparisons"]}
    assert by_metric["test_objective"]["exploratory_p"] is None
    assert "not comparable" in by_metric["test_objective"]["limitation"]
    assert by_metric["test_mean_distance_m"]["wilcoxon_p"] is not None


# Hàm test_folds_are_distinct_pairing_units_with_corrected_inference: kiểm tra kịch bản folds are distinct pairing units with corrected inference bằng các assertion trong thân hàm.
def test_folds_are_distinct_pairing_units_with_corrected_inference():
    rows = []
    for seed in (1, 2):
        for fold in range(5):
            for arm, delta in (("baseline", 0.0), ("treatment", 1.0 + 0.1 * fold)):
                rows.append(
                    {
                        "experiment": "E16",
                        "dataset": "d",
                        "treatment": arm,
                        "seed": seed,
                        "cv_fold": fold,
                        "repetition": 0,
                        "status": "SUCCEEDED",
                        "train_orders": 16,
                        "test_orders": 4,
                        "test_objective": 10 + delta + seed,
                    }
                )
    result = analyze(rows, {"E16": ["test_objective"]})
    (comparison,) = result["comparisons"]
    assert comparison["paired_units"] == 10 and comparison["cross_validated"]
    assert comparison["test_to_train_orders"] == 0.25
    assert comparison["nadeau_bengio_p"] > comparison["exploratory_p"]
    assert comparison["holm_nadeau_bengio_p"] == comparison["nadeau_bengio_p"]
    assert comparison["a12_treatment_greater"] > 0.5
    assert comparison["wilcoxon_p"] is not None


# Hàm test_load_calibration_fields_keep_old_canonical_form_and_drive_generator: kiểm tra kịch bản load calibration fields keep old canonical form and drive generator bằng các assertion trong thân hàm.
def test_load_calibration_fields_keep_old_canonical_form_and_drive_generator():
    from smart_retail.application.experiments.splits import arrival_rate

    plain = DatasetSpec(id="tiny", scale="tiny", facings=6)
    assert {"orders", "order_interval_s", "picker_count"}.isdisjoint(plain.model_dump())
    assert "order_rate" not in KFOLD.model_dump()
    assert generate(plain)[0] == generate(DatasetSpec(**plain.model_dump()))[0]
    spec = plain.model_copy(update={"orders": 150, "order_interval_s": 12.5, "picker_count": 3})
    data = generate(spec)[0]
    assert len(data["orders"]["orders"]) == 150
    assert data["demand"]["picker_count"] == 3
    assert 1 / arrival_rate(data["orders"]["orders"]) == pytest.approx(12.5, rel=0.25)
    # Same products as the uncalibrated instance; only order times and counts change.
    assert data["products"] == generate(plain)[0]["products"]


# Hàm test_population_order_rate_keeps_fold_load_equal_to_full_load: kiểm tra kịch bản population order rate keeps fold load equal to full load bằng các assertion trong thân hàm.
def test_population_order_rate_keeps_fold_load_equal_to_full_load():
    from smart_retail.application.experiments.splits import arrival_rate

    data = generate(
        DatasetSpec(id="tiny", scale="tiny", facings=6, orders=150, order_interval_s=12.5)
    )[0]
    population = arrival_rate(data["orders"]["orders"])
    spec = EvaluationSpec(split="kfold", n_folds=5, order_rate="population")
    plan = split_orders(data, spec, 11)
    job = apply_split(data, plan, 0, spec)
    test_orders = job["optimization"]["evaluation"]["orders"]["orders"]
    assert len(test_orders) == 30
    assert arrival_rate(test_orders) == pytest.approx(population)
    assert arrival_rate(job["orders"]["orders"]) == pytest.approx(population)
    sampled = apply_split(data, plan, 0, KFOLD.model_copy(update={"n_folds": 5}))
    assert arrival_rate(sampled["optimization"]["evaluation"]["orders"]["orders"]) < population / 3


# Hàm test_calibration_reaches_target_picker_utilization: kiểm tra kịch bản calibration reaches target picker utilization bằng các assertion trong thân hàm.
def test_calibration_reaches_target_picker_utilization():
    from smart_retail.application.experiments.calibration import calibrate

    overrides = {"optimization": {"algorithm": "milp", "slotting_algorithm": "milp"}}
    spec, evidence = calibrate(
        DatasetSpec(id="tiny", scale="tiny", facings=6, orders=150), overrides, target=0.7
    )
    assert evidence["within_tolerance"]
    assert abs(evidence["achieved_utilization"] - 0.7) <= 0.05
    assert spec.order_interval_s == evidence["order_interval_s"] and spec.picker_count == 2
    again, _ = calibrate(
        DatasetSpec(id="tiny", scale="tiny", facings=6, orders=150), overrides, target=0.7
    )
    assert again == spec


# Hàm test_instance_level_comparison_uses_seq_milp_reference_and_scales: kiểm tra kịch bản instance level comparison uses seq milp reference and scales bằng các assertion trong thân hàm.
def test_instance_level_comparison_uses_seq_milp_reference_and_scales():
    from smart_retail.application.experiments.analysis import instance_comparisons

    rows = []
    for index, dataset in enumerate(["tiny_a", "tiny_b", "tiny_c", "small_a", "small_b"]):
        for arm, value in (("baseline", 2.0), ("seq_milp", 1.0), ("feedback", 0.8 - index * 0.01)):
            for seed in (1, 2):
                for fold in (0, 1):
                    rows.append(
                        {
                            "experiment": "E30",
                            "dataset": dataset,
                            "treatment": arm,
                            "seed": seed,
                            "cv_fold": fold,
                            "status": "SUCCEEDED",
                            "test_objective": value + 0.001 * fold,
                        }
                    )
    scales = {d: d.split("_")[0] for d in {r["dataset"] for r in rows}}
    records = instance_comparisons(rows, lambda _: ["test_objective"], scales)
    feedback = {r["scale"]: r for r in records if r["treatment"] == "feedback"}
    assert set(feedback) == {"tiny", "small", "all"}
    assert all(r["reference"] == "seq_milp" for r in records)
    assert feedback["all"]["instances"] == 5 and feedback["all"]["treatment_lower"] == 5
    # Exact test with 5 instances cannot go below 2 / 2**5.
    assert feedback["all"]["wilcoxon_exact_p"] == pytest.approx(0.0625)
    assert feedback["all"]["smallest_attainable_p"] == pytest.approx(0.0625)
    assert feedback["tiny"]["relative_change_of_means"] == pytest.approx(-0.2 - 0.01 / 1.0005, rel=0.05)
    assert all(r["holm_wilcoxon_exact_p"] >= r["wilcoxon_exact_p"] for r in records)
    # Secondary metrics and per-scale rows do not enter the pre-declared primary (pooled) family.
    timed = [{**r, "wall_s": 10 * r["test_objective"]} for r in rows]
    wider = instance_comparisons(timed, lambda _: ["test_objective", "wall_s"], scales)
    assert {r["metric"] for r in wider} == {"test_objective", "wall_s"}
    for r in wider:
        if r["metric"] == "test_objective" and r["scale"] == "all":
            assert (
                r["wilcoxon_exact_p"]
                <= r["holm_primary_wilcoxon_exact_p"]
                <= r["holm_wilcoxon_exact_p"]
            )
        else:
            assert r["holm_primary_wilcoxon_exact_p"] is None
    assert any(
        r["holm_primary_wilcoxon_exact_p"] < r["holm_wilcoxon_exact_p"]
        for r in wider
        if r["metric"] == "test_objective" and r["scale"] == "all"
    )


# Hàm test_instance_comparison_adds_exact_reference_for_union_gap: kiểm tra kịch bản instance comparison adds exact reference for union gap bằng các assertion trong thân hàm.
def test_instance_comparison_adds_exact_reference_for_union_gap():
    from smart_retail.application.experiments.analysis import instance_comparisons

    rows = [
        {
            "experiment": "E41",
            "dataset": f"tiny_{index}",
            "treatment": arm,
            "seed": seed,
            "status": "SUCCEEDED",
            "joint_objective": value - 0.001 * index,
        }
        for index in range(6)
        for seed in (1, 2)
        for arm, value in (("seq_milp", 1.0), ("feedback", 0.8), ("exact", 0.75))
    ]
    records = instance_comparisons(rows, lambda _: ["joint_objective"])
    gaps = {(r["reference"], r["treatment"]): r for r in records}
    assert set(gaps) == {
        ("seq_milp", "feedback"),
        ("seq_milp", "exact"),
        ("exact", "feedback"),
        ("exact", "seq_milp"),
    }
    gap = gaps["exact", "feedback"]
    assert gap["instances"] == 6 and gap["treatment_lower"] == 0
    assert gap["relative_change_of_means"] > 0


# Gain of each arm over seq_milp (objective 100) on six instances. The differences vary in sign
# and size so the exact p-values and their Holm corrections differ between comparisons.
GAINS = {
    dataset: {"seq_milp": 0, "random_search": random, "feedback_v5": feedback}
    for dataset, random, feedback in (
        ("tiny_a", 10, 41),
        ("tiny_b", 20, 33),
        ("tiny_c", 30, 52),
        ("small_a", 5, 29),
        ("small_b", 15, -8),
        ("small_c", 25, 46),
    )
}
SCALES = {dataset: dataset.split("_")[0] for dataset in GAINS}
RANDOM, FEEDBACK = ("seq_milp", "random_search"), ("seq_milp", "feedback_v5")
DIRECT = ("random_search", "feedback_v5")
# Exact two-sided signed-rank p by hand: n differences of one sign give 2 / 2**n; one difference
# of the other sign with rank w gives 2 * #(rank subsets with sum <= w) / 2**n.
EXPECTED_P = {
    RANDOM: {"tiny": 0.25, "small": 0.25, "all": 2 / 64},
    FEEDBACK: {"tiny": 0.25, "small": 0.5, "all": 4 / 64},
    DIRECT: {"tiny": 0.25, "small": 0.75, "all": 14 / 64},
}


# Hàm gain_rows: xử lý bước gain rows trong phạm vi module hiện tại.
def gain_rows(gains, experiment="E50"):
    """Rows from {dataset: {arm: gain}}; wall_s is a secondary metric with the same ordering."""
    return [
        {
            "experiment": experiment,
            "dataset": dataset,
            "treatment": arm,
            "seed": 1,
            "status": "SUCCEEDED",
            "joint_objective": 100.0 - gain,
            "wall_s": 10.0 - gain / 10,
        }
        for dataset, by_arm in gains.items()
        for arm, gain in by_arm.items()
    ]


# Hàm keyed: xử lý bước keyed trong phạm vi module hiện tại.
def keyed(records):
    return {(r["metric"], r["reference"], r["treatment"], r["scale"]): r for r in records}


METRICS = ["joint_objective", "wall_s"]


# Hàm test_predeclared_primary_family_is_the_pooled_group_of_primary_metrics: kiểm tra kịch bản predeclared primary family is the pooled group of primary metrics bằng các assertion trong thân hàm.
def test_predeclared_primary_family_is_the_pooled_group_of_primary_metrics():
    from smart_retail.application.experiments.analysis import instance_comparisons

    records = instance_comparisons(gain_rows(GAINS), lambda _: METRICS, SCALES)
    rows = keyed(records)
    assert {r["scale"] for r in records} == {"tiny", "small", "all"}
    for (reference, treatment), by_scale in EXPECTED_P.items():
        for scale, p in by_scale.items():
            row = rows["joint_objective", reference, treatment, scale]
            assert row["wilcoxon_exact_p"] == pytest.approx(p)
    pooled = {
        k: r["holm_primary_wilcoxon_exact_p"]
        for k, r in rows.items()
        if r["holm_primary_wilcoxon_exact_p"] is not None
    }
    # Holm over the pooled p-values 2/64, 4/64, 14/64 (multipliers 3, 2, 1); nothing else counts.
    assert pooled == pytest.approx(
        {
            ("joint_objective", *RANDOM, "all"): 6 / 64,
            ("joint_objective", *FEEDBACK, "all"): 8 / 64,
            ("joint_objective", *DIRECT, "all"): 14 / 64,
        }
    )
    # The full-table column keeps every metric and scale: 18 tests, smallest p 2/64.
    assert rows["joint_objective", *RANDOM, "all"]["holm_wilcoxon_exact_p"] == pytest.approx(0.5625)
    assert all(r["holm_wilcoxon_exact_p"] is not None for r in records)


# Hàm test_scale_holm_corrects_primary_metrics_within_each_scale: kiểm tra kịch bản scale holm corrects primary metrics within each scale bằng các assertion trong thân hàm.
def test_scale_holm_corrects_primary_metrics_within_each_scale():
    from smart_retail.application.experiments.analysis import instance_comparisons

    rows = keyed(instance_comparisons(gain_rows(GAINS), lambda _: METRICS, SCALES))
    # tiny: 0.25 x3 -> 0.75 each. small: 0.25, 0.5, 0.75 -> 0.75, 1.0, 1.0. all: as the family.
    expected = {
        "tiny": {RANDOM: 0.75, FEEDBACK: 0.75, DIRECT: 0.75},
        "small": {RANDOM: 0.75, FEEDBACK: 1.0, DIRECT: 1.0},
        "all": {RANDOM: 6 / 64, FEEDBACK: 8 / 64, DIRECT: 14 / 64},
    }
    for scale, by_pair in expected.items():
        for (reference, treatment), value in by_pair.items():
            row = rows["joint_objective", reference, treatment, scale]
            assert row["holm_scale_wilcoxon_exact_p"] == pytest.approx(value)
            assert (
                rows["wall_s", reference, treatment, scale]["holm_scale_wilcoxon_exact_p"] is None
            )


@pytest.mark.parametrize("scales", [{dataset: "tiny" for dataset in GAINS}, None])
# Hàm test_single_scale_experiment_keeps_its_primary_family: kiểm tra kịch bản single scale experiment keeps its primary family bằng các assertion trong thân hàm.
def test_single_scale_experiment_keeps_its_primary_family(scales):
    from smart_retail.application.experiments.analysis import instance_comparisons

    records = instance_comparisons(gain_rows(GAINS), lambda _: METRICS, scales)
    assert {r["scale"] for r in records} == {"tiny" if scales else "unknown"}
    expected = {RANDOM: 6 / 64, FEEDBACK: 8 / 64, DIRECT: 14 / 64}
    for column in ("holm_primary_wilcoxon_exact_p", "holm_scale_wilcoxon_exact_p"):
        found = {
            (r["reference"], r["treatment"]): r[column]
            for r in records
            if r["metric"] == "joint_objective"
        }
        assert found == pytest.approx(expected)
        assert all(r[column] is None for r in records if r["metric"] == "wall_s")


# Hàm test_primary_family_pools_the_primary_rows_across_experiments: kiểm tra kịch bản primary family pools the primary rows across experiments bằng các assertion trong thân hàm.
def test_primary_family_pools_the_primary_rows_across_experiments():
    from smart_retail.application.experiments.analysis import instance_comparisons

    solo = {f"solo_{i}": {"seq_milp": 0, "feedback_v5": 10 + i} for i in range(6)}
    rows = gain_rows(GAINS) + gain_rows(solo, "E51")
    scales = {**SCALES, **{dataset: "tiny" for dataset in solo}}
    records = instance_comparisons(rows, lambda _: ["joint_objective"], scales)
    found = {(r["experiment"], r["scale"], r["reference"], r["treatment"]): r for r in records}
    assert {r["scale"] for r in records if r["experiment"] == "E51"} == {"tiny"}
    # E50 contributes its three pooled rows (2/64, 4/64, 14/64), E51 its only row (2/64).
    expected = {
        ("E50", "all", *RANDOM): 8 / 64,
        ("E50", "all", *FEEDBACK): 8 / 64,
        ("E50", "all", *DIRECT): 14 / 64,
        ("E51", "tiny", *FEEDBACK): 8 / 64,
    }
    column = "holm_primary_wilcoxon_exact_p"
    assert {k: r[column] for k, r in found.items() if r[column] is not None} == pytest.approx(
        expected
    )
    # Per-scale Holm never mixes experiments: the lone E51 row is its own group.
    assert found["E51", "tiny", *FEEDBACK]["holm_scale_wilcoxon_exact_p"] == pytest.approx(2 / 64)
    assert found["E50", "tiny", *RANDOM]["holm_scale_wilcoxon_exact_p"] == pytest.approx(0.75)


@pytest.mark.parametrize("sequential", ["seq_milp", "baseline"])
# Hàm test_random_search_is_a_second_instance_reference: kiểm tra kịch bản random search is a second instance reference bằng các assertion trong thân hàm.
def test_random_search_is_a_second_instance_reference(sequential):
    from smart_retail.application.experiments.analysis import instance_comparisons

    gains = {
        dataset: {(sequential if arm == "seq_milp" else arm): gain for arm, gain in by_arm.items()}
        for dataset, by_arm in GAINS.items()
    }
    pairs = {
        (r["reference"], r["treatment"])
        for r in instance_comparisons(gain_rows(gains), lambda _: ["joint_objective"], SCALES)
    }
    # No (random_search -> sequential) row: it would mirror (sequential -> random_search).
    assert pairs == {
        (sequential, "random_search"),
        (sequential, "feedback_v5"),
        ("random_search", "feedback_v5"),
    }
    alone = {d: {k: v for k, v in by_arm.items() if k != "seq_milp"} for d, by_arm in GAINS.items()}
    records = instance_comparisons(gain_rows(alone), lambda _: ["joint_objective"])
    assert [(r["reference"], r["treatment"]) for r in records] == [DIRECT]


# Hàm test_random_search_does_not_mirror_the_exact_reference_rows: kiểm tra kịch bản random search does not mirror the exact reference rows bằng các assertion trong thân hàm.
def test_random_search_does_not_mirror_the_exact_reference_rows():
    from smart_retail.application.experiments.analysis import instance_comparisons

    gains = {d: {**by_arm, "exact": 60} for d, by_arm in GAINS.items()}
    records = instance_comparisons(gain_rows(gains), lambda _: ["joint_objective"], SCALES)
    assert {(r["reference"], r["treatment"]) for r in records} == {
        ("seq_milp", "exact"),
        ("seq_milp", "random_search"),
        ("seq_milp", "feedback_v5"),
        ("exact", "seq_milp"),
        ("exact", "random_search"),
        ("exact", "feedback_v5"),
        ("random_search", "feedback_v5"),
    }


# Hàm test_feedback_v5_is_a_reference_of_its_ablation_arms: kiểm tra kịch bản feedback v5 is a reference of its ablation arms bằng các assertion trong thân hàm.
def test_feedback_v5_is_a_reference_of_its_ablation_arms():
    from smart_retail.application.experiments.analysis import instance_comparisons

    # W2-like: eight small instances; v5_no_surrogate loses everywhere, v5_no_heat ties on four.
    gains = {
        f"small_{i}": {
            "seq_milp": 0,
            "feedback_v5": 20 + i,
            "v5_no_surrogate": 10 + i,
            "v5_no_heat": 20 + i - i % 2,
        }
        for i in range(8)
    }
    scales = {dataset: "small" for dataset in gains}
    records = instance_comparisons(gain_rows(gains), lambda _: ["joint_objective"], scales)
    # feedback_v5 meets the ablation arms only: no mirrored (feedback_v5 -> seq_milp) row.
    assert [(r["reference"], r["treatment"]) for r in records] == [
        ("seq_milp", "feedback_v5"),
        ("seq_milp", "v5_no_heat"),
        ("seq_milp", "v5_no_surrogate"),
        ("feedback_v5", "v5_no_heat"),
        ("feedback_v5", "v5_no_surrogate"),
    ]
    rows = keyed(records)
    lost = rows["joint_objective", "feedback_v5", "v5_no_surrogate", "small"]
    assert lost["instances"] == 8 and lost["treatment_lower"] == 0
    assert lost["relative_change_of_means"] > 0 and lost["wilcoxon_exact_p"] == pytest.approx(2 / 256)
    tied = rows["joint_objective", "feedback_v5", "v5_no_heat", "small"]
    assert tied["ties"] == 4 and tied["wilcoxon_exact_p"] == pytest.approx(2 / 16)
    # One scale: all five rows form the primary family; four p = 2/256 -> 5 x 2/256 after Holm.
    assert lost["holm_primary_wilcoxon_exact_p"] == pytest.approx(10 / 256)
    assert tied["holm_primary_wilcoxon_exact_p"] == pytest.approx(2 / 16)
    # Without v5_no_* arms (W1) feedback_v5 is no reference.
    plain = instance_comparisons(gain_rows(GAINS), lambda _: ["joint_objective"], SCALES)
    assert "feedback_v5" not in {r["reference"] for r in plain}


# Hàm test_feedback_v5_reference_keeps_the_random_search_row: kiểm tra kịch bản feedback v5 reference keeps the random search row bằng các assertion trong thân hàm.
def test_feedback_v5_reference_keeps_the_random_search_row():
    from smart_retail.application.experiments.analysis import instance_comparisons

    gains = {d: {**by_arm, "v5_no_heat": by_arm["feedback_v5"] - 3} for d, by_arm in GAINS.items()}
    pairs = {
        (r["reference"], r["treatment"])
        for r in instance_comparisons(gain_rows(gains), lambda _: ["joint_objective"], SCALES)
    }
    # Each pair of references appears once, in the direction of the earlier reference.
    assert pairs == {
        ("seq_milp", "random_search"),
        ("seq_milp", "feedback_v5"),
        ("seq_milp", "v5_no_heat"),
        ("random_search", "feedback_v5"),
        ("random_search", "v5_no_heat"),
        ("feedback_v5", "v5_no_heat"),
    }


# Hàm write_manifests: ghi manifests theo quy tắc trong thân hàm.
def write_manifests(root, *manifests):
    for manifest in manifests:
        folder = root / "datasets" / manifest["dataset_id"]
        folder.mkdir(parents=True)
        (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


# Hàm test_dataset_scales_from_manifests: kiểm tra kịch bản dataset scales from manifests bằng các assertion trong thân hàm.
def test_dataset_scales_from_manifests(tmp_path):
    from smart_retail.application.experiments.reports import dataset_scales

    first, second = tmp_path / "one", tmp_path / "two"
    write_manifests(
        first,
        {"dataset_id": "a", "spec": {"scale": "small"}},
        {"dataset_id": "b", "generator": "imported-seven-section-bundle"},
    )
    write_manifests(second, {"dataset_id": "c", "spec": {"scale": "tiny"}})
    assert dataset_scales([first]) == {"a": "small"}
    assert dataset_scales([first, second]) == {"a": "small", "c": "tiny"}


# Hàm test_dataset_scales_reject_one_dataset_with_two_scales: kiểm tra kịch bản dataset scales reject one dataset with two scales bằng các assertion trong thân hàm.
def test_dataset_scales_reject_one_dataset_with_two_scales(tmp_path):
    from smart_retail.application.experiments.reports import dataset_scales

    first, second, third = tmp_path / "one", tmp_path / "two", tmp_path / "three"
    write_manifests(first, {"dataset_id": "a", "spec": {"scale": "small"}})
    write_manifests(second, {"dataset_id": "a", "spec": {"scale": "tiny"}})
    write_manifests(third, {"dataset_id": "a", "spec": {"scale": "small"}})
    with pytest.raises(ValueError, match="different scales"):
        dataset_scales([first, second])
    assert dataset_scales([first, third]) == {"a": "small"}


# Hàm campaign_root: xử lý bước campaign root trong phạm vi module hiện tại.
def campaign_root(root, job_key, scale):
    files = {
        "identity.json": {"runtime": {}},
        "configuration.json": {"experiments": [{"id": "E50", "metrics": ["joint_objective"]}]},
        f"records/{job_key}.json": {"job_key": job_key, "experiment": "E50"},
    }
    for name, content in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(json.dumps(content), encoding="utf-8")
    write_manifests(root, {"dataset_id": "a", "spec": {"scale": scale}})
    return root


# Hàm test_report_passes_dataset_scales_to_the_analysis: kiểm tra kịch bản report passes dataset scales to the analysis bằng các assertion trong thân hàm.
def test_report_passes_dataset_scales_to_the_analysis(tmp_path, monkeypatch):
    from smart_retail.application.experiments import reports

    seen = {}

    # Hàm capture: xử lý bước capture trong phạm vi module hiện tại.
    def capture(rows, selected, scales):
        seen.update(selected=selected, scales=scales)
        raise StopIteration

    monkeypatch.setattr(reports, "verify_integrity", lambda _: {})
    monkeypatch.setattr(reports, "analyze", capture)
    root = campaign_root(tmp_path / "campaign", "k1", "small")
    with pytest.raises(StopIteration):
        reports.report(root, tmp_path / "out")
    assert seen == {"selected": {"E50": ["joint_objective"]}, "scales": {"a": "small"}}


# Hàm test_report_refuses_conflicting_scales_before_creating_the_output: kiểm tra kịch bản report refuses conflicting scales before creating the output bằng các assertion trong thân hàm.
def test_report_refuses_conflicting_scales_before_creating_the_output(tmp_path, monkeypatch):
    from smart_retail.application.experiments import reports

    monkeypatch.setattr(reports, "verify_integrity", lambda _: {})
    roots = [
        campaign_root(tmp_path / "one", "k1", "small"),
        campaign_root(tmp_path / "two", "k2", "tiny"),
    ]
    with pytest.raises(ValueError, match="different scales"):
        reports.report(roots, tmp_path / "out")
    assert not (tmp_path / "out").exists()
