"""paper-v4 search controls: neighborhood shape, prefilter, T3 scope, allocation and ILS."""

import copy
import time
from dataclasses import replace
from itertools import zip_longest

import pytest

from smart_retail.application.experiments.generators import generate, merge
from smart_retail.application.feedback.diagnostics import analyze
from smart_retail.application.feedback.evaluator import evaluate
from smart_retail.application.feedback.neighborhood import actions, interleave
from smart_retail.application.feedback.restarts import restart
from smart_retail.application.workflow import execute
from smart_retail.contracts.experiments import DatasetSpec
from smart_retail.contracts.feedback import V4_CONTROLS, JointConfig
from smart_retail.contracts.inputs import to_domain
from smart_retail.engines.t1_layout.geometry import violations

JOINT = {
    "objective": {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]},
    "scenario_seeds": [0, 101],
    "scenario_seed_policy": "job_seed_offsets",
}


@pytest.fixture(scope="module")
def tiny():
    return generate(DatasetSpec(id="tiny", scale="tiny", facings=6))[0]


@pytest.fixture(scope="module")
def initial(tiny):
    """Sequential plan of the generated tiny instance and its T4 feedback."""
    config = JointConfig(**JOINT, mode="feedback")
    sections = merge(copy.deepcopy(tiny), {"optimization": {"joint": config.model_dump(mode="json")}})
    state = evaluate(
        sections,
        config,
        None,
        time.monotonic() + 60,
        lambda: False,
        lambda _: None,
        {},
        lambda *args: None,
    )
    return sections, state, analyze(state, sections)


def test_absent_controls_keep_the_paper_v3_canonical_form():
    dumped = JointConfig(**JOINT, mode="feedback").model_dump(mode="json")
    assert not set(V4_CONTROLS) & set(dumped)
    full = JointConfig(**JOINT, t1_steps=[1, 3], kicks=2, t3_scope="objective").model_dump(mode="json")
    assert full["t1_steps"] == [1, 3] and full["kicks"] == 2 and "kick_edits" not in full
    for bad in ([1, 1], [0], [11]):
        with pytest.raises(ValueError):
            JointConfig(t1_steps=bad)


def test_interleave_defaults_to_round_robin_and_weights_are_deterministic():
    queues = {"T1": ["a1", "a2", "a3", "a4"], "T2": ["b1", "b2"], "T3": ["c1"]}
    fair = [x for group in zip_longest(*queues.values()) for x in group if x]
    assert interleave(queues) == fair
    weighted = interleave(queues, {"T1": 0.9, "T2": 0.1, "T3": 0.1})
    assert sorted(weighted) == sorted(fair)
    assert weighted[:3] == ["a1", "a2", "a3"]
    assert weighted == interleave(queues, {"T1": 0.9, "T2": 0.1, "T3": 0.1})
    # Equal weights reproduce the fair order.
    assert interleave(queues, dict.fromkeys(queues, 0.5)) == fair


def test_unit_steps_reproduce_the_paper_v3_neighborhood(initial):
    sections, state, feedback = initial
    base = JointConfig(**JOINT, max_actions=1000)
    explicit = base.model_copy(update={"t1_steps": [1], "t3_scope": "all", "geometry_prefilter": False})
    assert actions(state, feedback, sections, base) == actions(state, feedback, sections, explicit)


def test_multi_step_moves_and_geometry_prefilter(initial):
    sections, state, feedback = initial
    grid = sections["floorplan"]["grid_m"]
    config = JointConfig(**JOINT, layers=["T1"], max_actions=1000, t1_steps=[1, 3])
    long = actions(state, feedback, sections, config)
    poses = state["decisions"]["poses"]
    shifts = {
        round(
            max(
                abs(a["decisions"]["poses"][sid][0] - poses[sid][0]),
                abs(a["decisions"]["poses"][sid][1] - poses[sid][1]),
            )
            / grid
        )
        for a in long
        if a["type"] == "T1_MOVE"
        for sid in a["changed"]
    }
    assert shifts == {1, 3}
    filtered = actions(
        state, feedback, sections, config.model_copy(update={"geometry_prefilter": True})
    )
    assert filtered and len(filtered) < len(long)
    data = to_domain(sections)
    for action in filtered:
        p = action["decisions"]["poses"]
        layout = tuple(
            replace(s, x=p[s.id][0], y=p[s.id][1], rotation=p[s.id][2]) for s in data.shelves
        )
        assert not violations(data.floorplan, layout)
    # The prefilter only removes edits; surviving edits keep their order.
    keys = [str(a["decisions"]["poses"]) for a in long]
    positions = [keys.index(str(a["decisions"]["poses"])) for a in filtered]
    assert positions == sorted(positions)


def test_objective_t3_scope_keeps_only_score_relevant_edits(initial):
    sections, state, feedback = initial
    config = JointConfig(**JOINT, layers=["T3"], max_actions=1000)
    full = actions(state, feedback, sections, config)
    scoped = actions(
        state, feedback, sections, config.model_copy(update={"t3_scope": "objective"})
    )
    assert {a["type"] for a in scoped} <= {"T3_FACE", "T3_SWAP", "T3_FACINGS"}
    assert len(scoped) < len(full)
    rows = state["decisions"]["placements"]
    for action in scoped:
        if action["type"] == "T3_SWAP":
            a, b = (next(r for r in rows if r["sku"] == sku) for sku in action["changed"])
            assert a["face"] != b["face"]


def test_restart_step_and_edit_count_are_bounded(initial):
    sections, state, _ = initial
    grid = sections["floorplan"]["grid_m"]
    before = state["decisions"]["poses"]
    for variant in range(1, 6):
        decision, changed = restart(state, sections, 3, variant, max_step=1, edits=1)
        assert decision is not None and 1 <= len(changed) <= 2
        after = decision["poses"]
        assert {k for k in before if after[k] != before[k]} <= set(changed)
        if len(changed) == 1 and after[changed[0]][2] == before[changed[0]][2]:
            sid = changed[0]
            shift = max(abs(after[sid][0] - before[sid][0]), abs(after[sid][1] - before[sid][1]))
            assert shift <= grid + 1e-9


def run(tiny, **joint):
    sections = merge(
        copy.deepcopy(tiny),
        {"optimization": {"joint": {**JOINT, **joint}, "seed": 5, "time_limit_s": 300}},
    )
    return execute(copy.deepcopy(sections)), sections


def test_iterated_local_search_kicks_after_local_convergence(tiny):
    result, sections = run(
        tiny,
        mode="feedback",
        layers=["T1"],
        max_iterations=100,
        max_actions=2,
        max_evaluations=10,
        patience=1,
        policy="first_improvement",
        kicks=3,
        kick_edits=2,
        geometry_prefilter=True,
        t1_steps=[1, 2],
    )
    joint = result["joint"]
    kicks = [e for e in joint["trace"] if e.get("action") == "ILS_KICK"]
    assert kicks and len(kicks) <= 3
    assert any(e["reason"] == "PERTURBATION" for e in kicks)
    assert joint["evaluations"] <= 10
    scores = [c["score"] for c in result["integrated"]["candidates"]]
    assert joint["best"]["score"] == min(scores)
    assert joint["status"] in ("EVALUATION_LIMIT", "CONVERGED_LOCAL")
    again = execute(copy.deepcopy(sections))["joint"]
    assert again["best"]["decisions"] == joint["best"]["decisions"]
    assert [e.get("variant") for e in again["trace"] if e.get("action") == "ILS_KICK"] == [
        e.get("variant") for e in kicks
    ]


def test_adaptive_layer_allocation_reports_smoothed_weights(tiny):
    result, _ = run(
        tiny,
        mode="feedback",
        max_iterations=100,
        max_actions=6,
        max_evaluations=8,
        patience=20,
        policy="first_improvement",
        layer_allocation="adaptive",
        t3_scope="objective",
    )
    weights = [e["layer_weights"] for e in result["joint"]["trace"] if "layer_weights" in e]
    assert weights and weights[0] == {"T1": 0.5, "T2": 0.5, "T3": 0.5}
    assert all(0 < w < 1 for entry in weights for w in entry.values())
    assert result["joint"]["evaluations"] == 8


def test_screening_and_search_time_contracts():
    with pytest.raises(ValueError):
        JointConfig(scenario_seeds=[1, 2], screen_seeds=2)
    with pytest.raises(ValueError):
        JointConfig(scenario_seeds=[1, 2], screen_margin=0.1)
    with pytest.raises(ValueError):
        JointConfig(mode="exact", scenario_seeds=[1, 2], screen_seeds=1, finite_space={})
    ok = JointConfig(scenario_seeds=[1, 2], screen_seeds=1, screen_margin=0.05, search_time_s=60)
    assert ok.model_dump(mode="json")["screen_seeds"] == 1


def test_two_fidelity_screening_counts_seed_simulations(tiny):
    result, sections = run(
        tiny,
        mode="feedback",
        layers=["T1"],
        max_iterations=100,
        max_actions=24,
        max_evaluations=4,
        patience=20,
        policy="first_improvement",
        geometry_prefilter=True,
        screen_seeds=1,
        screen_margin=0.0,
    )
    joint = result["joint"]
    screened = [e for e in joint["trace"] if e.get("reason") == "SCREENED_OUT"]
    assert joint["screened_out"] == len(screened) > 0
    # Each screened-out candidate costs half an evaluation (1 of 2 scenario seeds); the
    # last promoted candidate may exceed the budget by at most that remainder.
    assert joint["evaluations"] > 4
    assert 4 <= joint["budget_spent"] <= 4.5
    assert all(e["status"] == "SCREENED_OUT" for e in screened)
    assert joint["incumbent_curve"][-1]["budget_spent"] <= joint["budget_spent"]
    assert joint["best"]["score"] == min(c["score"] for c in result["integrated"]["candidates"])
    again = execute(copy.deepcopy(sections))["joint"]
    assert again["best"]["decisions"] == joint["best"]["decisions"]


def test_search_time_limit_stops_search_but_keeps_a_result(tiny):
    result, _ = run(
        tiny,
        mode="random_search",
        max_evaluations=10000,
        search_time_s=0.5,
    )
    joint = result["joint"]
    assert joint["status"] == "SEARCH_TIME_LIMIT"
    assert joint["search_time_s"] == 0.5
    assert joint["best"] is not None and joint["evaluations"] >= 1


def test_promotion_reuses_the_screened_seed_simulation(initial):
    sections, state, _ = initial
    config = JointConfig(**JOINT)
    seeds = [11, 12]
    config = config.model_copy(update={"scenario_seeds": seeds})
    cache: dict = {}

    def call(chosen, context=None):
        return evaluate(
            sections,
            config,
            state["decisions"],
            time.monotonic() + 60,
            lambda: False,
            lambda _: None,
            cache,
            lambda *args: None,
            seeds=chosen,
            context_seeds=context,
        )

    screened = call(seeds[:1], seeds)
    full = call(None)
    assert full["scenarios"][0]["stage_cache"]["T4"]["hit"] is True
    assert full["scenarios"][1]["stage_cache"]["T4"]["hit"] is False
    assert screened["scenarios"][0]["stage_cache"]["T4"]["key"] == full["scenarios"][0]["stage_cache"]["T4"]["key"]
