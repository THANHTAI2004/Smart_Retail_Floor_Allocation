import copy
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
def tiny():
    return generate(DatasetSpec(id="tiny", scale="tiny", facings=6))[0]


def ids(section):
    return {o["id"] for o in section["orders"]}


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


def test_temporal_holdout_tests_on_latest_orders(tiny):
    spec = EvaluationSpec(split="temporal_holdout", test_size=0.25)
    plan = split_orders(tiny, spec, 11)
    (fold,) = plan["folds"]
    stamps = {o["id"]: o["placed_at"] for o in tiny["orders"]["orders"]}
    assert len(fold["test"]) == math.ceil(len(stamps) * 0.25)
    assert max(stamps[i] for i in fold["train"]) <= min(stamps[i] for i in fold["test"])
    assert plan["folds"] == split_orders(tiny, spec, 99)["folds"]


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


def test_apply_split_rejects_orders_changed_by_overrides(tiny):
    plan = split_orders(tiny, KFOLD, 11)
    changed = copy.deepcopy(tiny)
    changed["orders"]["orders"][0]["due_s"] = 1
    with pytest.raises(ValueError, match="changed the orders"):
        apply_split(changed, plan, 0, KFOLD)


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


def test_engine_errors_survive_simpy_reraise_and_pickling():
    import pickle

    import simpy

    from smart_retail.domain.models import EngineError

    env = simpy.Environment()

    def journey():
        yield env.timeout(1)
        raise EngineError("TIMEOUT", "T4 simulation time limit")

    env.process(journey())
    with pytest.raises(EngineError) as raised:
        env.run()
    assert raised.value.code == "TIMEOUT" and str(raised.value) == "T4 simulation time limit"
    copy_ = pickle.loads(pickle.dumps(raised.value))
    assert (copy_.code, str(copy_)) == ("TIMEOUT", "T4 simulation time limit")


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


def test_worker_wall_budget_leaves_finalization_grace():
    from smart_retail.workers.runner import wall_budget

    assert wall_budget(20) == 35
    assert wall_budget(300) == 330
    assert wall_budget(900) == 990
    assert OptimizationInput(time_limit_s=900).time_limit_s == 900
    with pytest.raises(ValidationError):
        OptimizationInput(time_limit_s=1801)


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


def test_campaign_evaluation_contract_and_job_ceiling():
    with pytest.raises(ValidationError, match="schema_version 1.1"):
        CampaignSpec.model_validate({**campaign(seeds=[1]), "schema_version": "1.0"})
    with pytest.raises(ValidationError, match="1,000 jobs"):
        CampaignSpec.model_validate(campaign(seeds=list(range(1, 21))))
    spec = CampaignSpec.model_validate(campaign(seeds=[1, 2]))
    assert planned_jobs(spec) == 3 * 2 * 2 * 10


def test_partition_keeps_each_dataset_seed_unit_in_one_part():
    parts = partition(campaign(), max_jobs=250)
    assert all(planned_jobs(p) <= 250 and p.max_jobs == planned_jobs(p) for p in parts)
    assert sum(planned_jobs(p) for p in parts) == 3 * 2 * 10 * 10
    units = [(d.id, seed) for p in parts for d in p.datasets for seed in p.seeds]
    assert len(units) == len(set(units)) == 30
    with pytest.raises(ValueError, match="one seed"):
        partition(campaign(), max_jobs=10)


def test_corrected_resampled_test_is_more_conservative_than_naive():
    differences = [0.1, 0.12, 0.08, 0.11, 0.09, 0.13, 0.1, 0.07, 0.12, 0.1]
    corrected = nadeau_bengio_p(differences, test_to_train=1 / 9)
    naive = nadeau_bengio_p(differences, test_to_train=0)
    assert naive < corrected < 1
    assert nadeau_bengio_p([1, 1, 1], 0.1) is None
    assert vargha_delaney_a12([2, 3], [1, 1]) == 1 and vargha_delaney_a12([1], [1]) == 0.5


def test_friedman_nemenyi_ranks_and_critical_difference():
    blocks = [[1.0, 2.0, 3.0]] * 6
    result = friedman_nemenyi(blocks, ["a", "b", "c"], "dataset_means")
    assert result["average_ranks"] == {"a": 1.0, "b": 2.0, "c": 3.0}
    assert result["nemenyi_cd_0_05"] == pytest.approx(2.343 * math.sqrt(12 / 36), rel=1e-3)
    assert ["a", "c"] in result["nemenyi_different"]
    assert "limitation" in friedman_nemenyi([[1.0, 2.0]], ["a", "b"], "units")


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
