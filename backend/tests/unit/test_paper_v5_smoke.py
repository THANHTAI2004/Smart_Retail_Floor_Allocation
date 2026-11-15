# Vai trò: Kiểm thử pipeline thực trên các họ mặt bằng và hai chế độ tìm kiếm V5.
# Các assertion mô tả hành vi mong đợi; kết quả chỉ được xác nhận sau khi chạy test.
"""paper-v5 smoke: every layout family simulates end to end and both new search modes finish."""

import copy
import math
import time

import pytest

from smart_retail.application.experiments.generators import generate, merge
from smart_retail.application.feedback.evaluator import evaluate
from smart_retail.application.workflow import execute
from smart_retail.contracts.experiments import DatasetSpec
from smart_retail.contracts.feedback import JointConfig

JOINT = {
    "objective": {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]},
    "scenario_seeds": [0, 101],
    "scenario_seed_policy": "job_seed_offsets",
}
FAMILIES = ("grid", "corner_entrance", "wide", "columns")
# Scale -> paper-v5 instance (first seed, facings, orders, order interval, pickers).
SCALES = {
    "tiny": (8001, 6, 150, 12.58, 2),
    "small": (8101, 4, 300, 16.85, 2),
    "medium": (8201, 3, 500, 23.37, 2),
}
# First paper-v5 medium instance seed of each family checked on medium (W1: two per family).
MEDIUM_SEEDS = {"wide": 8205, "columns": 8207}
# feedback_v5 as in scripts/build_paper_v5_configs.py with a two-evaluation warm start.
FEEDBACK_V5 = {
    "mode": "feedback",
    "max_iterations": 100,
    "max_actions": 24,
    "policy": "first_improvement",
    "t1_steps": [1, 2, 3],
    "geometry_prefilter": True,
    "t3_scope": "objective",
    "layer_allocation": "adaptive",
    "kicks": 10,
    "kick_edits": 3,
    "patience": 2,
    "surrogate": "walk_heat",
    "surrogate_pool": 96,
    "compound_moves": 32,
    "restart_samples": 128,
    "restart_evaluations": 2,
    "search_seed_scope": "instance",
    "drop_identical_swaps": True,
}


# Hàm instance: xử lý bước instance trong phạm vi module hiện tại.
def instance(scale, family, seed=None):
    first, facings, orders, interval, pickers = SCALES[scale]
    seed = first if seed is None else seed
    spec = DatasetSpec(
        id=f"{scale}_{family}",
        scale=scale,
        seed=seed,
        facings=facings,
        orders=orders,
        order_interval_s=interval,
        picker_count=pickers,
        layout_family=family,
    )
    return generate(spec)[0]


# Hàm simulate: xử lý bước simulate trong phạm vi module hiện tại.
def simulate(sections):
    config = JointConfig(**JOINT, mode="sequential")
    sections = merge(
        copy.deepcopy(sections), {"optimization": {"joint": config.model_dump(mode="json")}}
    )
    state = evaluate(
        sections,
        config,
        None,
        time.monotonic() + 600,
        lambda: False,
        lambda _: None,
        {},
        lambda *args: None,
    )
    # "PASS": the independent verify() inside evaluate() did not raise for any scenario.
    assert math.isfinite(state["score"]) and state["validation"] == "PASS"


@pytest.mark.parametrize("scale", ["tiny", "small"])
@pytest.mark.parametrize("family", FAMILIES)
# Hàm test_sequential_plan_simulates_end_to_end: kiểm tra kịch bản sequential plan simulates end to end bằng các assertion trong thân hàm.
def test_sequential_plan_simulates_end_to_end(scale, family):
    simulate(instance(scale, family))


@pytest.mark.parametrize("family", MEDIUM_SEEDS)
# Hàm test_sequential_plan_simulates_on_medium: kiểm tra kịch bản sequential plan simulates on medium bằng các assertion trong thân hàm.
def test_sequential_plan_simulates_on_medium(family):
    simulate(instance("medium", family, MEDIUM_SEEDS[family]))


# Hàm run: thực hiện luồng chạy với trạng thái và ngân sách được quản lý trong thân hàm.
def run(joint):
    sections = merge(
        copy.deepcopy(instance("tiny", "columns")),
        {"optimization": {"joint": {**JOINT, **joint}, "seed": 5, "time_limit_s": 300}},
    )
    return execute(sections)["joint"]


# Hàm test_feedback_v5_finishes_on_the_columns_family: kiểm tra kịch bản feedback v5 finishes on the columns family bằng các assertion trong thân hàm.
def test_feedback_v5_finishes_on_the_columns_family():
    joint = run({**FEEDBACK_V5, "max_evaluations": 4})
    assert joint["best"] is not None and math.isfinite(joint["best"]["score"])
    assert 1 < joint["evaluations"] <= 4 and joint["best"]["score"] <= joint["initial_score"]
    assert joint["restart_evaluations"] >= 1


# Hàm test_genetic_finishes_on_the_columns_family: kiểm tra kịch bản genetic finishes on the columns family bằng các assertion trong thân hàm.
def test_genetic_finishes_on_the_columns_family():
    joint = run({"mode": "genetic", "population": 3, "max_evaluations": 4})
    assert joint["mode"] == "genetic"
    actions = {e.get("action") for e in joint["trace"]}
    assert {"GA_INIT", "GA_OFFSPRING"} <= actions
    assert joint["best"] is not None and math.isfinite(joint["best"]["score"])
    assert 1 < joint["evaluations"] <= 4 and joint["best"]["score"] <= joint["initial_score"]
