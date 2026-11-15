# Vai trò: Kiểm thử seed theo instance, surrogate, restart và baseline di truyền V5.
# Các assertion mô tả hành vi mong đợi; kết quả chỉ được xác nhận sau khi chạy test.
"""paper-v5 search controls: contract, instance-scoped search seed, surrogate and genetic mode."""

import copy
import time
from dataclasses import replace
from fractions import Fraction
from itertools import permutations

import pytest

from smart_retail.application.experiments.generators import generate, merge
from smart_retail.application.feedback import (
    coordinator,
    genetic,
    neighborhood,
    restarts,
    surrogate,
)
from smart_retail.application.feedback.diagnostics import analyze
from smart_retail.application.feedback.evaluator import evaluate, exact_score
from smart_retail.application.feedback.genetic import evolve
from smart_retail.application.feedback.neighborhood import actions, relabel, t1_edits, t1_pool
from smart_retail.application.feedback.restarts import DUPLICATE_LIMIT, search_seed
from smart_retail.application.stage_workflow import canonical_hash
from smart_retail.application.workflow import execute
from smart_retail.contracts.experiments import DatasetSpec
from smart_retail.contracts.feedback import V5_CONTROLS, JointConfig
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError
from smart_retail.engines.t1_layout.geometry import violations

JOINT = {
    "objective": {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]},
    "scenario_seeds": [0, 101],
    "scenario_seed_policy": "job_seed_offsets",
}


@pytest.fixture(scope="module")
# Hàm tiny: xử lý bước tiny trong phạm vi module hiện tại.
def tiny():
    return generate(DatasetSpec(id="tiny", scale="tiny", facings=6))[0]


@pytest.fixture(scope="module")
# Hàm initial: xử lý bước initial trong phạm vi module hiện tại.
def initial(tiny):
    """Sequential plan of the generated tiny instance and its T4 feedback."""
    config = JointConfig(**JOINT, mode="feedback")
    sections = merge(
        copy.deepcopy(tiny), {"optimization": {"joint": config.model_dump(mode="json")}}
    )
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


@pytest.fixture(scope="module")
# Hàm small_initial: xử lý bước small initial trong phạm vi module hiện tại.
def small_initial():
    """Sequential plan of the generated small instance (12 shelves) and its T4 feedback."""
    base = generate(DatasetSpec(id="small", scale="small", facings=4))[0]
    config = JointConfig(**JOINT, mode="feedback")
    sections = merge(
        copy.deepcopy(base), {"optimization": {"joint": config.model_dump(mode="json")}}
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
    return sections, state, analyze(state, sections)


# Hàm test_absent_v5_controls_keep_the_paper_v4_canonical_form: kiểm tra kịch bản absent v5 controls keep the paper v4 canonical form bằng các assertion trong thân hàm.
def test_absent_v5_controls_keep_the_paper_v4_canonical_form():
    dumped = JointConfig(**JOINT, mode="feedback").model_dump(mode="json")
    assert not set(V5_CONTROLS) & set(dumped)
    full = JointConfig(**JOINT, mode="genetic", surrogate="walk_heat", population=4)
    dumped = full.model_dump(mode="json")
    assert dumped["surrogate"] == "walk_heat" and dumped["population"] == 4
    assert dumped["mode"] == "genetic" and "compound_moves" not in dumped


# Hàm test_restart_controls_are_validated: kiểm tra kịch bản restart controls are validated bằng các assertion trong thân hàm.
def test_restart_controls_are_validated():
    with pytest.raises(ValueError):
        JointConfig(**JOINT, restart_evaluations=3)
    with pytest.raises(ValueError):
        JointConfig(**JOINT, restart_evaluations=5, restart_samples=4)
    ok = JointConfig(**JOINT, restart_samples=8, restart_evaluations=3)
    assert ok.restart_samples == 8 and ok.restart_evaluations == 3


# Hàm test_search_seed_scope: kiểm tra kịch bản search seed scope bằng các assertion trong thân hàm.
def test_search_seed_scope(tiny):
    sections = copy.deepcopy(tiny)
    assert search_seed(sections, 1, None) == 1 == search_seed(sections, 1, "job")
    scoped = search_seed(sections, 1, "instance")
    other = generate(DatasetSpec(id="tiny", scale="tiny", facings=6, seed=102))[0]
    assert scoped != search_seed(other, 1, "instance")
    assert scoped == search_seed(copy.deepcopy(sections), 1, "instance")
    assert scoped != search_seed(sections, 2, "instance")
    tuned = merge(copy.deepcopy(sections), {"optimization": {"joint": {"mode": "random_search"}}})
    assert scoped == search_seed(tuned, 1, "instance")


HEAT = {"C0": 9, "C1": 1, "C2": 4}


# Hàm reject_layout: xử lý bước reject layout trong phạm vi module hiện tại.
def reject_layout(monkeypatch, code, poses=None):
    """Make `surrogate.navigation` raise `code` for the layout with these poses (None: any)."""
    real = surrogate.navigation

    # Hàm fake: xử lý bước fake trong phạm vi module hiện tại.
    def fake(floor, shelves, *args, **kwargs):
        if poses is None or all([s.x, s.y, s.rotation] == poses[s.id] for s in shelves):
            raise EngineError(code, "injected")
        return real(floor, shelves, *args, **kwargs)

    monkeypatch.setattr(surrogate, "navigation", fake)


# Hàm test_surrogate_value_is_the_optimal_one_to_one_pairing: kiểm tra kịch bản surrogate value is the optimal one to one pairing bằng các assertion trong thân hàm.
def test_surrogate_value_is_the_optimal_one_to_one_pairing(initial):
    sections, state, _ = initial
    d = surrogate.distances(sections, state["decisions"]["poses"])
    assert d is not None and set(d) == {"S0", "S1", "S2", "S3"}
    assert all(v >= 0 for v in d.values()) and len(set(d.values())) > 1
    totals = [
        sum(HEAT[c] * d[s] for c, s in zip(HEAT, shelves, strict=True))
        for shelves in permutations(d, len(HEAT))
    ]
    assert surrogate.value(sections, d, HEAT) == pytest.approx(min(totals), abs=1e-9)
    assert max(totals) > min(totals)


# Hàm test_surrogate_distance_is_the_nearest_pickup_over_all_faces: kiểm tra kịch bản surrogate distance is the nearest pickup over all faces bằng các assertion trong thân hàm.
def test_surrogate_distance_is_the_nearest_pickup_over_all_faces(initial):
    sections, state, _ = initial
    poses = state["decisions"]["poses"]
    one = surrogate.distances(sections, poses)
    double = copy.deepcopy(sections)
    double["shelves"]["items"][0]["faces"] = 2
    two = surrogate.distances(double, poses)
    assert one is not None and two is not None
    assert two["S0"] < one["S0"]
    assert {k: v for k, v in two.items() if k != "S0"} == {
        k: v for k, v in one.items() if k != "S0"
    }


# Hàm test_surrogate_respects_fixed_category_shelves: kiểm tra kịch bản surrogate respects fixed category shelves bằng các assertion trong thân hàm.
def test_surrogate_respects_fixed_category_shelves(initial):
    sections, state, _ = initial
    d = surrogate.distances(sections, state["decisions"]["poses"])
    assert d is not None and d["S3"] > min(d.values())
    free = surrogate.value(sections, d, HEAT)
    fixed = copy.deepcopy(sections)
    fixed["categories"]["items"][0]["fixed_shelf_id"] = "S3"
    # The free categories are still paired with the whole shelf list, S3 included.
    nearest = sorted(d.values())
    expected = HEAT["C0"] * d["S3"] + HEAT["C2"] * nearest[0] + HEAT["C1"] * nearest[1]
    assert surrogate.value(fixed, d, HEAT) == pytest.approx(expected, abs=1e-9)
    assert expected != pytest.approx(free)


# Hàm test_surrogate_repeats_the_shelf_list_when_categories_outnumber_shelves: kiểm tra kịch bản surrogate repeats the shelf list when categories outnumber shelves bằng các assertion trong thân hàm.
def test_surrogate_repeats_the_shelf_list_when_categories_outnumber_shelves(initial):
    sections, _, _ = initial
    d = {"S0": 1.0, "S1": 2.0}
    expected = 9 * 1.0 + 4 * 2.0 + 1 * 1.0
    assert surrogate.value(sections, d, HEAT) == pytest.approx(expected, abs=1e-9)


# Hàm test_surrogate_heat_weighting: kiểm tra kịch bản surrogate heat weighting bằng các assertion trong thân hàm.
def test_surrogate_heat_weighting(initial):
    sections, _, feedback = initial
    categories = {p["sku"]: p["category_id"] for p in sections["products"]["items"]}
    assert surrogate.heat(feedback, sections, False) == {"C0": 1.0, "C1": 1.0, "C2": 1.0}
    weighted = surrogate.heat(feedback, sections, True)
    for cid in ("C0", "C1", "C2"):
        picked = sum(q for sku, q in feedback["sku_pick_counts"].items() if categories[sku] == cid)
        assert weighted[cid] == 1 + picked
    assert max(weighted.values()) > 1


# Hàm test_surrogate_rank_drops_invalid_topology: kiểm tra kịch bản surrogate rank drops invalid topology bằng các assertion trong thân hàm.
def test_surrogate_rank_drops_invalid_topology(initial, monkeypatch):
    sections, state, feedback = initial
    config = JointConfig(**JOINT, layers=["T1"], max_actions=1000)
    candidates = actions(state, feedback, sections, config)[:12]
    heat = surrogate.heat(feedback, sections, True)
    ranked = surrogate.rank(candidates, sections, heat)
    assert len(ranked) > 3
    values = [a["surrogate"] for a in ranked]
    assert values == sorted(values) and "surrogate" not in candidates[0]
    dropped = ranked[len(ranked) // 2]
    reject_layout(monkeypatch, "UNREACHABLE", dropped["decisions"]["poses"])
    kept = surrogate.rank(candidates, sections, heat)
    assert [a["decisions"] for a in kept] == [
        a["decisions"] for a in ranked if a["decisions"] is not dropped["decisions"]
    ]
    assert [a["surrogate"] for a in kept] == [
        a["surrogate"] for a in ranked if a["decisions"] is not dropped["decisions"]
    ]
    reject_layout(monkeypatch, "DISCONNECTED_AISLES")
    assert surrogate.rank(candidates, sections, heat) == []


# Hàm test_surrogate_rank_breaks_ties_by_the_decision_hash: kiểm tra kịch bản surrogate rank breaks ties by the decision hash bằng các assertion trong thân hàm.
def test_surrogate_rank_breaks_ties_by_the_decision_hash(initial):
    sections, state, feedback = initial
    poses = state["decisions"]["poses"]
    twins = [
        {"layer": "T1", "type": "T1_MOVE", "decisions": {"poses": poses, "tag": tag}}
        for tag in ("a", "b", "c")
    ]
    heat = surrogate.heat(feedback, sections, True)
    expected = sorted(twins, key=lambda a: canonical_hash(a["decisions"]))
    for order in (twins, twins[::-1], twins[1:] + twins[:1]):
        ranked = surrogate.rank(order, sections, heat)
        assert [a["decisions"] for a in ranked] == [a["decisions"] for a in expected]
        assert len({a["surrogate"] for a in ranked}) == 1


@pytest.mark.parametrize("code", ["UNREACHABLE", "DISCONNECTED_AISLES", "PROBLEM_LIMIT"])
# Hàm test_surrogate_distances_are_none_for_an_invalid_layout: kiểm tra kịch bản surrogate distances are none for an invalid layout bằng các assertion trong thân hàm.
def test_surrogate_distances_are_none_for_an_invalid_layout(initial, monkeypatch, code):
    sections, state, _ = initial
    reject_layout(monkeypatch, code)
    assert surrogate.distances(sections, state["decisions"]["poses"]) is None


@pytest.mark.parametrize("code", ["TIMEOUT", "CANCELLED"])
# Hàm test_surrogate_distances_propagate_timeout_and_cancellation: kiểm tra kịch bản surrogate distances propagate timeout and cancellation bằng các assertion trong thân hàm.
def test_surrogate_distances_propagate_timeout_and_cancellation(initial, monkeypatch, code):
    sections, state, feedback = initial
    reject_layout(monkeypatch, code)
    with pytest.raises(EngineError) as raised:
        surrogate.distances(sections, state["decisions"]["poses"])
    assert raised.value.code == code
    with pytest.raises(EngineError):
        surrogate.rank(
            [{"decisions": {"poses": state["decisions"]["poses"]}}],
            sections,
            surrogate.heat(feedback, sections, False),
        )


# Hàm pool_order: xử lý bước pool order trong phạm vi module hiện tại.
def pool_order(pool):
    return [canonical_hash(a["decisions"]) for a in pool]


# Hàm test_pool_samples_every_shelf_and_is_deterministic: kiểm tra kịch bản pool samples every shelf and is deterministic bằng các assertion trong thân hàm.
def test_pool_samples_every_shelf_and_is_deterministic(small_initial):
    sections, state, feedback = small_initial
    config = JointConfig(**JOINT, surrogate_pool=96)
    pool = t1_pool(state, feedback, sections, config, 1)
    assert 0 < len(pool) <= 96
    assert {a["layer"] for a in pool} == {"T1"}
    assert len({s for a in pool for s in a["changed"]}) >= 8
    assert t1_pool(state, feedback, sections, config, 1) == pool
    other = t1_pool(state, feedback, sections, config, 2)
    assert other != pool and pool_order(other) != pool_order(pool)
    data = to_domain(sections)
    for action in pool:
        p = action["decisions"]["poses"]
        layout = tuple(
            replace(s, x=p[s.id][0], y=p[s.id][1], rotation=p[s.id][2]) for s in data.shelves
        )
        assert not violations(data.floorplan, layout)
        assert p != state["decisions"]["poses"]
        assert not {"assignment", "placements"} & set(action["decisions"])
        assert action["evidence"] == feedback["diagnostic_evidence"]
    assert len(set(pool_order(pool))) == len(pool)


# Hàm test_pool_size_follows_surrogate_pool: kiểm tra kịch bản pool size follows surrogate pool bằng các assertion trong thân hàm.
def test_pool_size_follows_surrogate_pool(small_initial):
    sections, state, feedback = small_initial
    for size in (5, 40):
        config = JointConfig(**JOINT, surrogate_pool=size)
        assert len(t1_pool(state, feedback, sections, config, 3)) == size
    default = JointConfig(**JOINT, surrogate="walk")
    assert len(t1_pool(state, feedback, sections, default, 3)) <= 96


# Hàm test_pool_ranked_by_surrogate: kiểm tra kịch bản pool ranked by surrogate bằng các assertion trong thân hàm.
def test_pool_ranked_by_surrogate(small_initial):
    sections, state, feedback = small_initial
    config = JointConfig(
        **JOINT, layers=["T1"], max_actions=1000, surrogate="walk_heat", surrogate_pool=32
    )
    queue = actions(state, feedback, sections, config, pool_seed=1)
    values = [a["surrogate"] for a in queue]
    assert len(values) > 3 and values == sorted(values) and len(set(values)) > 1
    assert pool_order(queue) == pool_order(t1_pool(state, feedback, sections, config, 1))


# Hàm test_compound_moves_change_several_shelves: kiểm tra kịch bản compound moves change several shelves bằng các assertion trong thân hàm.
def test_compound_moves_change_several_shelves(small_initial):
    sections, state, feedback = small_initial
    before = state["decisions"]["poses"]
    config = JointConfig(**JOINT, surrogate_pool=4, compound_moves=8)
    pool = t1_pool(state, feedback, sections, config, 1)
    compound = [a for a in pool if a["type"] == "T1_COMPOUND"]
    assert compound and len(compound) <= 8
    for action in compound:
        poses = action["decisions"]["poses"]
        assert action["layer"] == "T1" and len(action["changed"]) >= 2
        assert {k for k in before if poses[k] != before[k]} <= set(action["changed"])
        assert not {"assignment", "placements"} & set(action["decisions"])
        assert action["decisions"]["routing_policy"] == state["decisions"]["routing_policy"]
        assert poses != before
    assert len(set(pool_order(pool))) == len(pool)
    plain = config.model_copy(update={"compound_moves": None})
    assert len(t1_pool(state, feedback, sections, plain, 1)) == 4


# Hàm test_pool_without_valid_topology_keeps_t2_actions: kiểm tra kịch bản pool without valid topology keeps t2 actions bằng các assertion trong thân hàm.
def test_pool_without_valid_topology_keeps_t2_actions(small_initial, monkeypatch):
    sections, state, feedback = small_initial
    config = JointConfig(**JOINT, max_actions=1000, surrogate="walk_heat", surrogate_pool=8)
    v4 = config.model_copy(update={"surrogate": None, "surrogate_pool": None})
    baseline = actions(state, feedback, sections, v4)
    monkeypatch.setattr(surrogate, "distances", lambda *args, **kwargs: None)
    queue = actions(state, feedback, sections, config, pool_seed=1)
    assert not [a for a in queue if a["layer"] == "T1"]
    for layer in ("T2", "T3"):
        assert [a for a in queue if a["layer"] == layer] == [
            a for a in baseline if a["layer"] == layer
        ]
    assert any(a["layer"] == "T2" for a in queue)


# Hàm test_v4_neighborhood_unchanged_without_pool: kiểm tra kịch bản v4 neighborhood unchanged without pool bằng các assertion trong thân hàm.
def test_v4_neighborhood_unchanged_without_pool(small_initial):
    sections, state, feedback = small_initial
    config = JointConfig(**JOINT, max_actions=1000, t1_steps=[1, 3], geometry_prefilter=True)
    plain = actions(state, feedback, sections, config)
    assert actions(state, feedback, sections, config, pool_seed=5) == plain
    assert actions(state, feedback, sections, config, pool_seed=5, deadline=0.0) == plain
    pooled = config.model_copy(update={"surrogate_pool": 16})
    assert actions(state, feedback, sections, pooled) == plain
    assert actions(state, feedback, sections, pooled, pool_seed=5) != plain


# feedback_v4 (scripts/build_paper_v4_configs.py) plus the paper-v5 warm start and pool.
V5 = {
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
    "surrogate_pool": 24,
    "restart_samples": 8,
    "restart_evaluations": 3,
}


# Hàm run: thực hiện luồng chạy với trạng thái và ngân sách được quản lý trong thân hàm.
def run(base, **joint):
    sections = merge(
        copy.deepcopy(base),
        {"optimization": {"joint": {**JOINT, **joint}, "seed": 5, "time_limit_s": 300}},
    )
    return execute(copy.deepcopy(sections)), sections


# Hàm warm_start: xử lý bước warm start trong phạm vi module hiện tại.
def warm_start(joint):
    return [e for e in joint["trace"] if e.get("action") == "SURROGATE_RESTART"]


@pytest.fixture(scope="module")
# Hàm v5_run: xử lý bước v5 run trong phạm vi module hiện tại.
def v5_run(tiny):
    return run(tiny, **V5, max_evaluations=6)


# Hàm test_restart_phase_spends_declared_evaluations: kiểm tra kịch bản restart phase spends declared evaluations bằng các assertion trong thân hàm.
def test_restart_phase_spends_declared_evaluations(v5_run):
    result, _ = v5_run
    joint = result["joint"]
    phase = warm_start(joint)
    assert len(phase) == 3 and {e["status"] for e in phase} <= {"EVALUATING", "FAILED"}
    assert joint["restart_evaluations"] == 3 and joint["evaluations"] == 6
    scored = [e for e in phase if e["status"] == "EVALUATING"]
    assert scored and all(e["layer"] == "T1" and e["changed"] for e in scored)
    values = [e["surrogate"] for e in scored]
    assert values == sorted(values)
    curve = [Fraction(*c["score_fraction"]) for c in joint["incumbent_curve"]]
    assert all(a > b for a, b in zip(curve, curve[1:]))
    assert joint["best"]["score"] <= joint["initial_score"]
    # The descent starts from the best of the initial plan and the warm-start candidates.
    trace = joint["trace"]
    initial_id = next(e["candidate_id"] for e in trace if e.get("iteration") == 0)
    leader = min(scored, key=lambda e: e["after"])
    start = leader["candidate_id"] if leader["after"] < joint["initial_score"] else initial_id
    first = next(e for e in trace if e["status"] == "IMPROVING" and "feedback" in e)
    assert first["event"] > phase[-1]["event"] and first["candidate_id"] == start


# Hàm test_feedback_v5_is_deterministic: kiểm tra kịch bản feedback v5 is deterministic bằng các assertion trong thân hàm.
def test_feedback_v5_is_deterministic(v5_run):
    result, sections = v5_run
    joint = result["joint"]
    again = execute(copy.deepcopy(sections))["joint"]
    assert again["best"]["score_fraction"] == joint["best"]["score_fraction"]
    ids = [e["candidate_id"] for e in joint["trace"] if "candidate_id" in e]
    assert [e["candidate_id"] for e in again["trace"] if "candidate_id" in e] == ids


# Hàm test_restart_phase_skips_locked_layouts: kiểm tra kịch bản restart phase skips locked layouts bằng các assertion trong thân hàm.
def test_restart_phase_skips_locked_layouts(tiny):
    locked = copy.deepcopy(tiny)
    for shelf in locked["shelves"]["items"]:
        shelf["locked"] = True
    joint = run(locked, **V5, max_evaluations=4)[0]["joint"]
    assert [(e["status"], e["reason"]) for e in warm_start(joint)] == [
        ("FAILED", "RESTART_UNAVAILABLE")
    ]
    assert joint["restart_evaluations"] == 0
    assert joint["best"] is not None and joint["evaluations"] >= 1


# Hàm test_v5_search_time_limit: kiểm tra kịch bản v5 search time limit bằng các assertion trong thân hàm.
def test_v5_search_time_limit(tiny):
    joint = run(tiny, **V5, max_evaluations=10000, search_time_s=0.5)[0]["joint"]
    assert joint["status"] == "SEARCH_TIME_LIMIT"
    assert joint["best"] is not None and joint["evaluations"] >= 1


@pytest.mark.parametrize("phase", [True, False])
# Hàm test_surrogate_timeout_stops_the_search_with_a_result: kiểm tra kịch bản surrogate timeout stops the search with a result bằng các assertion trong thân hàm.
def test_surrogate_timeout_stops_the_search_with_a_result(tiny, monkeypatch, phase):
    # Hàm late: xử lý bước late trong phạm vi module hiện tại.
    def late(*args, **kwargs):
        raise EngineError("TIMEOUT", "injected")

    monkeypatch.setattr(surrogate, "rank", late)
    config = V5 if phase else {k: v for k, v in V5.items() if not k.startswith("restart_")}
    joint = run(tiny, **config, max_evaluations=6, search_time_s=300)[0]["joint"]
    assert joint["status"] == "SEARCH_TIME_LIMIT" and joint["evaluations"] == 1
    assert joint["best"] is not None
    assert joint.get("restart_evaluations") == (0 if phase else None)
    assert not [e for e in joint["trace"] if e.get("action")]


# Hàm test_instance_seed_scope_changes_random_search_stream: kiểm tra kịch bản instance seed scope changes random search stream bằng các assertion trong thân hàm.
def test_instance_seed_scope_changes_random_search_stream(tiny):
    other = generate(DatasetSpec(id="tiny", scale="tiny", facings=6, seed=102))[0]

    # Hàm walks: xử lý bước walks trong phạm vi module hiện tại.
    def walks(base, **scope):
        result = run(base, mode="random_search", max_evaluations=4, **scope)[0]
        changed = [
            e["changed"]
            for e in result["joint"]["trace"]
            if e.get("action") == "MULTISTART_RESTART" and e["status"] == "EVALUATING"
        ]
        poses = [
            [(s["id"], s["x"], s["y"], s["rotation"]) for s in c["stages"]["T1"]["shelves"]]
            for c in result["integrated"]["candidates"]
        ]
        assert len(changed) == 3
        return changed, poses

    assert walks(tiny) == walks(other)
    scoped = walks(tiny, search_seed_scope="instance")
    elsewhere = walks(other, search_seed_scope="instance")
    assert scoped[0] != elsewhere[0] and scoped[1][1:] != elsewhere[1][1:]
    assert scoped[1][0] == elsewhere[1][0]


# Hàm layout_violations: xử lý bước layout violations trong phạm vi module hiện tại.
def layout_violations(sections, candidate):
    data = to_domain(sections)
    poses = {s["id"]: s for s in candidate["stages"]["T1"]["shelves"]}
    layout = tuple(
        replace(s, x=poses[s.id]["x"], y=poses[s.id]["y"], rotation=poses[s.id]["rotation"])
        for s in data.shelves
    )
    return violations(data.floorplan, layout)


# Hàm ga: xử lý bước ga trong phạm vi module hiện tại.
def ga(trace, action):
    """Events of a genetic phase that spent budget (skipped proposals cost nothing)."""
    skipped = ("DUPLICATE", "RESTART_UNAVAILABLE")
    return [e for e in trace if e.get("action") == action and e.get("reason") not in skipped]


# Hàm test_genetic_respects_budget_and_is_deterministic: kiểm tra kịch bản genetic respects budget and is deterministic bằng các assertion trong thân hàm.
def test_genetic_respects_budget_and_is_deterministic(tiny):
    result, sections = run(tiny, mode="genetic", max_evaluations=8, population=4)
    joint = result["joint"]
    assert result["integrated"]["algorithm"] == "joint-genetic" and joint["mode"] == "genetic"
    assert joint["evaluations"] == 8 and joint["status"] == "EVALUATION_LIMIT"
    trace = joint["trace"]
    init, offspring = ga(trace, "GA_INIT"), ga(trace, "GA_OFFSPRING")
    assert len(init) == 3 and offspring
    assert len(init) + len(offspring) + 1 == joint["evaluations"]
    known = {next(e["candidate_id"] for e in trace if e.get("iteration") == 0)}
    for event in init + offspring:
        assert event["layer"] == "T1" and {"status", "variant"} <= set(event)
        if event["status"] == "EVALUATING":
            assert event["changed"]
            if event["action"] == "GA_OFFSPRING":
                assert len(event["parent_ids"]) == 2 and set(event["parent_ids"]) <= known
            known.add(event["candidate_id"])
    assert joint["best"]["score"] <= joint["initial_score"]
    again = execute(copy.deepcopy(sections))["joint"]
    assert again["best"]["score_fraction"] == joint["best"]["score_fraction"]
    ids = [e["candidate_id"] for e in trace if "candidate_id" in e]
    assert [e["candidate_id"] for e in again["trace"] if "candidate_id" in e] == ids
    for candidate in result["integrated"]["candidates"]:
        assert not layout_violations(sections, candidate)


# Hàm test_genetic_population_larger_than_budget: kiểm tra kịch bản genetic population larger than budget bằng các assertion trong thân hàm.
def test_genetic_population_larger_than_budget(tiny):
    joint = run(tiny, mode="genetic", max_evaluations=4, population=8)[0]["joint"]
    assert joint["evaluations"] == 4 and joint["status"] == "EVALUATION_LIMIT"
    assert len(ga(joint["trace"], "GA_INIT")) == 3
    assert not ga(joint["trace"], "GA_OFFSPRING")


# Hàm test_genetic_emits_no_descent_events: kiểm tra kịch bản genetic emits no descent events bằng các assertion trong thân hàm.
def test_genetic_emits_no_descent_events(tiny):
    joint = run(tiny, mode="genetic", max_evaluations=8, population=4)[0]["joint"]
    assert not [e for e in joint["trace"] if e["status"] == "IMPROVING"]
    assert not {e.get("action") for e in joint["trace"]} & {"T1_MOVE", "T1_ROTATE", "T1_SWAP"}
    assert not [e for e in joint["trace"] if "iteration" in e and e["iteration"] > 0]


# Hàm test_genetic_follows_the_instance_seed_scope: kiểm tra kịch bản genetic follows the instance seed scope bằng các assertion trong thân hàm.
def test_genetic_follows_the_instance_seed_scope(tiny):
    other = generate(DatasetSpec(id="tiny", scale="tiny", facings=6, seed=102))[0]

    # Hàm stream: xử lý bước stream trong phạm vi module hiện tại.
    def stream(base, **scope):
        result = run(base, mode="genetic", max_evaluations=4, population=4, **scope)[0]
        changed = [e["changed"] for e in ga(result["joint"]["trace"], "GA_INIT")]
        assert len(changed) == 3
        return changed

    assert stream(tiny) == stream(other)
    assert stream(tiny, search_seed_scope="instance") != stream(
        other, search_seed_scope="instance"
    )


# Hàm drive: xử lý bước drive trong phạm vi module hiện tại.
def drive(initial, score=None, behave=None, seed=1, max_step=3, start=500, **joint):
    """Run `evolve` on the initial plan with a fake evaluator (no simulation).

    `score(call, decision)` gives the numerator over 1000 of an evaluated decision (default:
    a hash of it); `behave(call)` may raise an EngineError; `start` is the initial plan's
    numerator. `call` counts evaluations including the initial plan, as the budget does.
    """
    sections, state, _ = initial
    state = {**state, "score": start / 1000, "score_fraction": [start, 1000]}
    config = JointConfig(**JOINT, mode="genetic", **joint)
    calls, seen, archive, trace = [1], {state["id"]}, [state], []

    # Hàm assess: xử lý bước assess trong phạm vi module hiện tại.
    def assess(decision, variant=0, reference=None):
        calls[0] += 1
        if behave:
            behave(calls[0])
        key = canonical_hash(decision)
        value = score(calls[0], decision) if score else int(key[:6], 16) % 997 + 1
        candidate = {
            "id": key,
            "decisions": decision,
            "score": value / 1000,
            "score_fraction": [value, 1000],
        }
        archive.append(candidate)
        return candidate

    # Hàm exhausted: xử lý bước exhausted trong phạm vi module hiện tại.
    def exhausted():
        return calls[0] >= config.max_evaluations

    best, termination = evolve(
        state, sections, config, seed, assess, seen, archive, trace.append, exhausted, max_step
    )
    assert exact_score(best) == min(exact_score(s) for s in archive)
    return best, termination, trace, calls[0]


# Hàm failures: xử lý bước failures trong phạm vi module hiện tại.
def failures(trace):
    return [e for e in ga(trace, "GA_INIT") + ga(trace, "GA_OFFSPRING") if e["status"] == "FAILED"]


# Hàm injected: xử lý bước injected trong phạm vi module hiện tại.
def injected(code, at):
    # Hàm behave: xử lý bước behave trong phạm vi module hiện tại.
    def behave(call):
        if call == at:
            raise EngineError(code, "injected")

    return behave


# Hàm test_genetic_population_defaults_to_eight: kiểm tra kịch bản genetic population defaults to eight bằng các assertion trong thân hàm.
def test_genetic_population_defaults_to_eight(initial):
    _, termination, trace, calls = drive(initial, max_evaluations=5)
    assert (termination, calls) == ("EVALUATION_LIMIT", 5)
    assert len(ga(trace, "GA_INIT")) == 4 and not ga(trace, "GA_OFFSPRING")
    _, termination, trace, calls = drive(initial, max_evaluations=12)
    assert (termination, calls) == ("EVALUATION_LIMIT", 12)
    assert len(ga(trace, "GA_INIT")) == 7 and len(ga(trace, "GA_OFFSPRING")) == 4


# Hàm test_genetic_streams_follow_the_search_seed_and_controls: kiểm tra kịch bản genetic streams follow the search seed and controls bằng các assertion trong thân hàm.
def test_genetic_streams_follow_the_search_seed_and_controls(initial, monkeypatch):
    calls = []
    real = genetic.restart

    # Hàm spy: xử lý bước spy trong phạm vi module hiện tại.
    def spy(state, sections, seed, variant, **kwargs):
        calls.append((seed, variant, kwargs))
        return real(state, sections, seed, variant, **kwargs)

    monkeypatch.setattr(genetic, "restart", spy)
    drive(initial, seed=7, max_step=2, max_evaluations=9, population=3, mutation_edits=4)
    init = [c for c in calls if "edits" not in c[2]]
    mutations = [c for c in calls if "edits" in c[2]]
    assert [c[:2] for c in init[:2]] == [(7, 1), (7, 2)]
    assert mutations and [c[1] for c in mutations[:3]] == [1, 2, 3]
    assert {c[0] for c in mutations} == {7 + 104729}
    assert all(c[2]["edits"] == 4 and c[2]["max_step"] == 2 for c in mutations)
    assert all(c[2]["max_step"] == 2 for c in init)
    calls.clear()
    drive(initial, max_evaluations=6, population=3)
    assert {c[2]["edits"] for c in calls if "edits" in c[2]} == {2}


# Hàm test_genetic_is_deterministic_without_simulation: kiểm tra kịch bản genetic is deterministic without simulation bằng các assertion trong thân hàm.
def test_genetic_is_deterministic_without_simulation(initial):
    first = drive(initial, max_evaluations=20, population=4)
    again = drive(initial, max_evaluations=20, population=4)
    assert first[0]["id"] == again[0]["id"] and first[2] == again[2]
    assert drive(initial, seed=2, max_evaluations=20, population=4)[2] != first[2]


@pytest.mark.parametrize(("start", "members", "children"), [(500, 100, 900), (300, 300, 300)])
# Hàm test_genetic_children_that_are_not_better_never_replace_members: kiểm tra kịch bản genetic children that are not better never replace members bằng các assertion trong thân hàm.
def test_genetic_children_that_are_not_better_never_replace_members(
    initial, start, members, children
):
    # Tính giá trị mục tiêu của quyết định theo định nghĩa và các thành phần đã khai báo.
    def score(call, decision):
        return members if call <= 4 else children

    best, termination, trace, _ = drive(
        initial, score=score, start=start, max_evaluations=24, population=4, mutation_edits=1
    )
    init = {e["candidate_id"] for e in ga(trace, "GA_INIT") if e["status"] == "EVALUATING"}
    offspring = [e for e in ga(trace, "GA_OFFSPRING") if e["status"] == "EVALUATING"]
    assert termination == "EVALUATION_LIMIT" and len(offspring) > 5
    founders = init | {initial[1]["id"]}
    assert all(set(e["parent_ids"]) <= founders for e in offspring)
    assert best["score_fraction"] == [min(start, members), 1000]


# Hàm test_genetic_better_children_replace_the_worst_member: kiểm tra kịch bản genetic better children replace the worst member bằng các assertion trong thân hàm.
def test_genetic_better_children_replace_the_worst_member(initial):
    # Tính giá trị mục tiêu của quyết định theo định nghĩa và các thành phần đã khai báo.
    def score(call, decision):
        return 400 - call if call <= 4 else 300 - call

    best, _, trace, _ = drive(initial, score=score, max_evaluations=40, population=4)
    offspring = [e for e in ga(trace, "GA_OFFSPRING") if e["status"] == "EVALUATING"]
    assert len(offspring) > 10
    ids = {e["candidate_id"] for e in offspring}
    assert any(set(e["parent_ids"]) & ids for e in offspring)
    assert best["id"] == offspring[-1]["candidate_id"]


# Hàm test_genetic_tournament_favours_the_better_and_the_worst_is_dropped: kiểm tra kịch bản genetic tournament favours the better and the worst is dropped bằng các assertion trong thân hàm.
def test_genetic_tournament_favours_the_better_and_the_worst_is_dropped(initial):
    # Tính giá trị mục tiêu của quyết định theo định nghĩa và các thành phần đã khai báo.
    def score(call, decision):
        return {2: 400, 3: 300, 4: 200}.get(call, 150)

    _, _, trace, _ = drive(initial, score=score, start=50, max_evaluations=30, population=4)
    worst = next(e for e in ga(trace, "GA_INIT") if e["status"] == "EVALUATING")["candidate_id"]
    offspring = [e for e in ga(trace, "GA_OFFSPRING") if e["status"] == "EVALUATING"]
    assert len(offspring) > 10
    # The initial plan leads, so it keeps winning tournaments; the worst member leaves first.
    assert any(initial[1]["id"] in e["parent_ids"] for e in offspring[3:])
    assert worst not in {p for e in offspring[1:] for p in e["parent_ids"]}
    children = {e["candidate_id"] for e in offspring}
    assert any(set(e["parent_ids"]) & children for e in offspring)


# Hàm test_genetic_falls_back_to_a_parent_when_no_crossover_is_valid: kiểm tra kịch bản genetic falls back to a parent when no crossover is valid bằng các assertion trong thân hàm.
def test_genetic_falls_back_to_a_parent_when_no_crossover_is_valid(initial, monkeypatch):
    tries, mutated, plans = [], [], [initial[1]["decisions"]["poses"]]
    monkeypatch.setattr(genetic, "geometry_valid", lambda domain, poses: tries.append(1) or False)
    real = genetic.restart

    # Hàm spy: xử lý bước spy trong phạm vi module hiện tại.
    def spy(plan, *args, **kwargs):
        result = real(plan, *args, **kwargs)
        if "edits" in kwargs:
            mutated.append(plan["decisions"]["poses"])
        if result[0] is not None:
            plans.append(result[0]["poses"])
        return result

    monkeypatch.setattr(genetic, "restart", spy)
    drive(initial, max_evaluations=8, population=3)
    assert mutated and len(tries) == genetic.CROSSOVER_TRIES * len(mutated)
    assert all(poses in plans for poses in mutated)


@pytest.mark.parametrize("at", [3, 6])
# Hàm test_genetic_continues_after_a_failed_evaluation: kiểm tra kịch bản genetic continues after a failed evaluation bằng các assertion trong thân hàm.
def test_genetic_continues_after_a_failed_evaluation(initial, at):
    _, termination, trace, calls = drive(
        initial, behave=injected("UNREACHABLE", at), max_evaluations=10, population=4
    )
    failed = failures(trace)
    assert (termination, calls) == ("EVALUATION_LIMIT", 10)
    assert len(failed) == 1 and failed[0]["reason"] == "UNREACHABLE" and "variant" in failed[0]
    assert failed[0]["action"] == ("GA_INIT" if at < 5 else "GA_OFFSPRING")


@pytest.mark.parametrize("code", ["TIMEOUT", "CANCELLED"])
@pytest.mark.parametrize("at", [3, 6])
# Hàm test_genetic_stops_on_timeout_and_cancellation: kiểm tra kịch bản genetic stops on timeout and cancellation bằng các assertion trong thân hàm.
def test_genetic_stops_on_timeout_and_cancellation(initial, code, at):
    best, termination, trace, calls = drive(
        initial, behave=injected(code, at), max_evaluations=10, population=4
    )
    assert (termination, calls) == (code, at) and best is not None
    assert not failures(trace)


@pytest.mark.parametrize("code", ["CACHE_CORRUPT", "SOURCE_DRIFT"])
@pytest.mark.parametrize("at", [3, 6])
# Hàm test_genetic_reraises_integrity_errors: kiểm tra kịch bản genetic reraises integrity errors bằng các assertion trong thân hàm.
def test_genetic_reraises_integrity_errors(initial, code, at):
    with pytest.raises(EngineError) as raised:
        drive(initial, behave=injected(code, at), max_evaluations=10, population=4)
    assert raised.value.code == code


# Hàm test_genetic_stops_after_consecutive_duplicate_restarts: kiểm tra kịch bản genetic stops after consecutive duplicate restarts bằng các assertion trong thân hàm.
def test_genetic_stops_after_consecutive_duplicate_restarts(initial, monkeypatch):
    sections, state, _ = initial
    fixed = restarts.restart(state, sections, 1, 1)
    monkeypatch.setattr(genetic, "restart", lambda *args, **kwargs: fixed)
    _, termination, trace, calls = drive(initial, max_evaluations=100, population=3)
    assert (termination, calls) == ("NEIGHBORHOOD_EXHAUSTED", 2)
    duplicates = [e for e in trace if e.get("reason") == "DUPLICATE"]
    assert len(duplicates) == DUPLICATE_LIMIT and {e["action"] for e in duplicates} == {"GA_INIT"}


# Hàm test_genetic_treats_the_initial_layout_as_evaluated: kiểm tra kịch bản genetic treats the initial layout as evaluated bằng các assertion trong thân hàm.
def test_genetic_treats_the_initial_layout_as_evaluated(initial, monkeypatch):
    state = initial[1]
    back = ({k: state["decisions"][k] for k in ("poses", "routing_policy")}, ["S0"])
    real = genetic.restart

    # Hàm walk: xử lý bước walk trong phạm vi module hiện tại.
    def walk(*args, **kwargs):
        return back if "edits" in kwargs else real(*args, **kwargs)

    monkeypatch.setattr(genetic, "restart", walk)
    _, termination, trace, calls = drive(initial, max_evaluations=100, population=3)
    assert (termination, calls) == ("NEIGHBORHOOD_EXHAUSTED", 3)
    assert not ga(trace, "GA_OFFSPRING")


# Hàm test_genetic_stops_when_no_shelf_can_move: kiểm tra kịch bản genetic stops when no shelf can move bằng các assertion trong thân hàm.
def test_genetic_stops_when_no_shelf_can_move(initial, monkeypatch):
    monkeypatch.setattr(genetic, "restart", lambda *args, **kwargs: (None, []))
    best, termination, trace, calls = drive(initial, max_evaluations=100, population=3)
    assert (termination, calls) == ("NEIGHBORHOOD_EXHAUSTED", 1) and best["id"]
    unavailable = [e for e in trace if e.get("reason") == "RESTART_UNAVAILABLE"]
    assert len(unavailable) == DUPLICATE_LIMIT


# Hàm test_genetic_offspring_phase_exhausts_on_duplicates: kiểm tra kịch bản genetic offspring phase exhausts on duplicates bằng các assertion trong thân hàm.
def test_genetic_offspring_phase_exhausts_on_duplicates(initial, monkeypatch):
    sections, state, _ = initial
    answers = iter([restarts.restart(state, sections, 1, 1)])
    # One init member, then no mutation: offspring are plain crossovers of the two plans.
    monkeypatch.setattr(genetic, "restart", lambda *args, **kwargs: next(answers, (None, [])))
    _, termination, trace, calls = drive(initial, max_evaluations=100, population=2)
    assert termination == "NEIGHBORHOOD_EXHAUSTED" and calls < 100
    duplicates = [e for e in trace if e.get("reason") == "DUPLICATE"]
    assert len(duplicates) >= DUPLICATE_LIMIT
    assert {e["action"] for e in duplicates} == {"GA_OFFSPRING"}


# Hàm swaps: xử lý bước swaps trong phạm vi module hiện tại.
def swaps(queue):
    return [tuple(a["changed"]) for a in queue if a["type"] == "T1_SWAP"]


# Hàm test_identical_shelf_swaps_are_dropped_only_when_requested: kiểm tra kịch bản identical shelf swaps are dropped only when requested bằng các assertion trong thân hàm.
def test_identical_shelf_swaps_are_dropped_only_when_requested(initial):
    sections, state, feedback = initial
    config = JointConfig(**JOINT, max_actions=1000)
    plain = actions(state, feedback, sections, config)
    off = config.model_copy(update={"drop_identical_swaps": False})
    assert actions(state, feedback, sections, off) == plain and len(swaps(plain)) == 6
    on = config.model_copy(update={"drop_identical_swaps": True})
    # The four generated shelves are physically identical: every swap only relabels two.
    assert actions(state, feedback, sections, on) == [a for a in plain if a["type"] != "T1_SWAP"]
    edits = [(kind, changed) for kind, _, changed in t1_edits(state, feedback, sections, on)]
    assert edits == [
        (kind, changed)
        for kind, _, changed in t1_edits(state, feedback, sections, config)
        if kind != "T1_SWAP"
    ]
    varied = copy.deepcopy(sections)
    varied["shelves"]["items"][0]["faces"] = 2
    assert swaps(actions(state, feedback, varied, on)) == [("S0", "S1"), ("S0", "S2"), ("S0", "S3")]


# Hàm test_swaps_of_a_fixed_category_shelf_are_kept: kiểm tra kịch bản swaps of a fixed category shelf are kept bằng các assertion trong thân hàm.
def test_swaps_of_a_fixed_category_shelf_are_kept(initial):
    sections, state, feedback = initial
    fixed = copy.deepcopy(sections)
    fixed["categories"]["items"][0]["fixed_shelf_id"] = "S2"
    config = JointConfig(**JOINT, max_actions=1000, drop_identical_swaps=True)
    assert swaps(actions(state, feedback, fixed, config)) == [("S0", "S2"), ("S1", "S2"), ("S2", "S3")]


# Hàm test_relabel_detects_permutations_of_identical_shelves: kiểm tra kịch bản relabel detects permutations of identical shelves bằng các assertion trong thân hàm.
def test_relabel_detects_permutations_of_identical_shelves(initial):
    sections, state, _ = initial
    poses = state["decisions"]["poses"]
    cycled = {**poses, "S0": poses["S1"], "S1": poses["S2"], "S2": poses["S0"]}
    assert relabel(sections, poses, cycled) and relabel(sections, poses, poses)
    x, y, angle = poses["S0"]
    assert not relabel(sections, poses, {**cycled, "S3": [x, y, 90 - angle]})
    varied = copy.deepcopy(sections)
    varied["shelves"]["items"][1]["faces"] = 2
    assert not relabel(varied, poses, cycled)
    fixed = copy.deepcopy(sections)
    fixed["categories"]["items"][0]["fixed_shelf_id"] = "S2"
    assert not relabel(fixed, poses, cycled)
    assert relabel(fixed, poses, {**poses, "S0": poses["S1"], "S1": poses["S0"]})


# Hàm test_pool_drops_compound_walks_that_only_relabel: kiểm tra kịch bản pool drops compound walks that only relabel bằng các assertion trong thân hàm.
def test_pool_drops_compound_walks_that_only_relabel(small_initial, monkeypatch):
    sections, state, feedback = small_initial
    poses = state["decisions"]["poses"]
    policy = state["decisions"]["routing_policy"]
    relabelled = {**poses, "S0": poses["S1"], "S1": poses["S0"], "S2": poses["S3"], "S3": poses["S2"]}
    turned = {**poses, **{sid: [*poses[sid][:2], 90 - poses[sid][2]] for sid in ("S0", "S1")}}
    walks = {
        1: ({"poses": relabelled, "routing_policy": policy}, ["S0", "S1", "S2", "S3"]),
        2: ({"poses": turned, "routing_policy": policy}, ["S0", "S1"]),
    }
    monkeypatch.setattr(
        neighborhood, "restart", lambda state, sections, seed, variant, **kw: walks[variant]
    )

    # Hàm compound: xử lý bước compound trong phạm vi module hiện tại.
    def compound(config, chosen=sections):
        pool = t1_pool(state, feedback, chosen, config, 1)
        return [a["decisions"]["poses"] for a in pool if a["type"] == "T1_COMPOUND"]

    config = JointConfig(**JOINT, surrogate_pool=4, compound_moves=2)
    assert sorted(map(canonical_hash, compound(config))) == sorted(
        map(canonical_hash, [relabelled, turned])
    )
    on = config.model_copy(update={"drop_identical_swaps": True})
    assert compound(on) == [turned]
    fixed = copy.deepcopy(sections)
    fixed["categories"]["items"][0]["fixed_shelf_id"] = "S1"
    assert len(compound(on, fixed)) == 2


ANNEALING_V5 = {"mode": "annealing", "drop_identical_swaps": True, "t3_scope": "objective"}


# Hàm test_annealing_neighbourhood_without_relabels_or_neutral_t3_edits: kiểm tra kịch bản annealing neighbourhood without relabels or neutral t3 edits bằng các assertion trong thân hàm.
def test_annealing_neighbourhood_without_relabels_or_neutral_t3_edits(initial, tiny):
    sections, state, feedback = initial
    # As in coordinator.anneal: the whole neighbourhood, untruncated.
    wide = JointConfig(**JOINT, mode="annealing").model_copy(update={"max_actions": 10**9})
    assert {"T1_SWAP", "T3_LEVEL", "T3_POSITION"} <= {
        a["type"] for a in actions(state, feedback, sections, wide)
    }
    strong = wide.model_copy(update={"drop_identical_swaps": True, "t3_scope": "objective"})
    kinds = {a["type"] for a in actions(state, feedback, sections, strong)}
    assert {"T1_MOVE", "T1_ROTATE", "T2_REASSIGN"} <= kinds
    assert not kinds & {"T1_SWAP", "T3_LEVEL", "T3_POSITION", "T3_ORIENTATION"}
    joint = run(tiny, **ANNEALING_V5, max_evaluations=12)[0]["joint"]
    proposed = [e["action"] for e in joint["trace"] if e.get("action")]
    assert joint["evaluations"] == 12 and len(proposed) == 11
    assert not set(proposed) & {"T1_SWAP", "T3_LEVEL", "T3_POSITION", "T3_ORIENTATION"}


# Hàm test_warm_start_walks_are_the_random_search_walks: kiểm tra kịch bản warm start walks are the random search walks bằng các assertion trong thân hàm.
def test_warm_start_walks_are_the_random_search_walks(tiny, v5_run):
    """Common random numbers: the warm start draws random_search's (seed, variant) walks."""
    result, _ = v5_run
    phase = [e for e in warm_start(result["joint"]) if e["status"] == "EVALUATING"]
    searched = run(tiny, mode="random_search", max_evaluations=9)[0]
    walks = {
        e["variant"]: e["changed"]
        for e in searched["joint"]["trace"]
        if e.get("action") == "MULTISTART_RESTART" and e["status"] == "EVALUATING"
    }
    assert phase and sorted(walks) == list(range(1, 9))
    assert all(walks[e["variant"]] == e["changed"] for e in phase)

    # Hàm layouts: xử lý bước layouts trong phạm vi module hiện tại.
    def layouts(candidates):
        return [
            sorted((s["id"], s["x"], s["y"], s["rotation"]) for s in c["stages"]["T1"]["shelves"])
            for c in candidates
        ]

    # Warm-start candidates follow the initial plan in the archive, in evaluation order.
    evaluated = layouts(result["integrated"]["candidates"][1 : 1 + len(phase)])
    assert all(layout in layouts(searched["integrated"]["candidates"][1:]) for layout in evaluated)


# Hàm test_warm_start_without_surrogate_keeps_generation_order: kiểm tra kịch bản warm start without surrogate keeps generation order bằng các assertion trong thân hàm.
def test_warm_start_without_surrogate_keeps_generation_order(tiny):
    unranked = {k: v for k, v in V5.items() if k != "surrogate"}
    phase = warm_start(run(tiny, **unranked, max_evaluations=6)[0]["joint"])
    assert [e["variant"] for e in phase] == [1, 2, 3]
    assert not [e for e in phase if "surrogate" in e]


@pytest.mark.parametrize("pooled", [True, False])
# Hàm test_spent_budget_skips_only_the_pooled_ranking: kiểm tra kịch bản spent budget skips only the pooled ranking bằng các assertion trong thân hàm.
def test_spent_budget_skips_only_the_pooled_ranking(tiny, monkeypatch, pooled):
    calls = []
    real = coordinator.actions

    # Hàm spy: xử lý bước spy trong phạm vi module hiện tại.
    def spy(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(coordinator, "actions", spy)
    config = V5 if pooled else {k: v for k, v in V5.items() if not k.startswith("surrogate")}
    # One initial evaluation plus three warm-start walks spend the whole budget.
    joint = run(tiny, **config, max_evaluations=4)[0]["joint"]
    assert joint["evaluations"] == 4 and len(warm_start(joint)) == 3
    assert joint["status"] == "EVALUATION_LIMIT"
    descent = [e for e in joint["trace"] if e["status"] == "IMPROVING" and "feedback" in e]
    # The unpooled (paper-v4) descent still builds its action list once, as before.
    assert (len(calls), len(descent)) == ((0, 0) if pooled else (1, 1))


# Hàm test_warm_start_walk_generation_stops_at_the_search_deadline: kiểm tra kịch bản warm start walk generation stops at the search deadline bằng các assertion trong thân hàm.
def test_warm_start_walk_generation_stops_at_the_search_deadline(tiny, monkeypatch):
    offset, variants = [0.0], []
    real_time, real_restart = coordinator.time, coordinator.restart

    class Clock:
        @staticmethod
        # Hàm monotonic: xử lý bước monotonic trong phạm vi module hiện tại.
        def monotonic():
            return real_time.monotonic() + offset[0]

    # Hàm walk: xử lý bước walk trong phạm vi module hiện tại.
    def walk(state, sections, seed, variant, **kwargs):
        variants.append(variant)
        if variant == 2:
            offset[0] = 150.0
        return real_restart(state, sections, seed, variant, **kwargs)

    monkeypatch.setattr(coordinator, "time", Clock)
    monkeypatch.setattr(coordinator, "restart", walk)
    joint = run(tiny, **V5, max_evaluations=6, search_time_s=100)[0]["joint"]
    assert variants == [1, 2]
    assert joint["status"] == "SEARCH_TIME_LIMIT" and joint["restart_evaluations"] == 0
    assert joint["evaluations"] == 1 and not warm_start(joint)


# feedback_v4 as in scripts/build_paper_v4_configs.py: no paper-v5 control.
V4_ONLY = {k: v for k, v in V5.items() if k not in V5_CONTROLS}
# sha256 of the trace (telemetry removed) of the paper-v4 path on the generated tiny instance,
# 6 evaluations. Measured 2026-11-03 on Windows / Python 3.12: equal for HEAD 0b58d04 (before
# the paper-v5 work) and for this tree.
V4_TRACE_SHA256 = "d2d53935cbd9286ffd9d933adee8e910fec6479f068bd7186a0c163449458d22"


# Hàm test_paper_v4_trace_is_unchanged: kiểm tra kịch bản paper v4 trace is unchanged bằng các assertion trong thân hàm.
def test_paper_v4_trace_is_unchanged(tiny):
    joint = run(tiny, **V4_ONLY, max_evaluations=6)[0]["joint"]
    trace = [{k: v for k, v in e.items() if k != "telemetry"} for e in joint["trace"]]
    assert canonical_hash(trace) == V4_TRACE_SHA256
