"""Real engine oracles, adversarial proofs, rollback and dependency boundaries."""

import copy
import json
import time
from pathlib import Path

import pytest

from smart_retail.application.feedback.coordinator import identity
from smart_retail.application.feedback.diagnostics import analyze
from smart_retail.application.feedback.evaluator import evaluate, exact_score
from smart_retail.application.feedback.neighborhood import actions
from smart_retail.application.workflow import execute
from smart_retail.contracts.feedback import JointConfig
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError
from smart_retail.engines.joint_exact.solver import digest, solve
from smart_retail.engines.joint_exact.verifier import verify

ROOT = Path(__file__).resolve().parents[3]


def problem(name="local-trap", **settings):
    sections = json.loads((ROOT / f"datasets/joint/{name}.json").read_text())
    space = json.loads((ROOT / f"datasets/joint/{name}-space.json").read_text())
    config = JointConfig(finite_space=space, **settings)
    sections["optimization"]["joint"] = config.model_dump(mode="json")
    return sections, config


def evaluator(sections, config, cache=None):
    return lambda d: evaluate(
        sections,
        config,
        d,
        time.monotonic() + 30,
        lambda: False,
        lambda _: None,
        cache if cache is not None else {},
        lambda *args: None,
    )


@pytest.fixture(scope="module")
def trap_exact():
    sections, config = problem(mode="exact")
    return sections, config, execute(sections)


def test_local_trap_is_distinct_from_global_certificate(trap_exact):
    sections, _, exact = trap_exact
    feedback = copy.deepcopy(sections)
    feedback["optimization"]["joint"].update(mode="feedback", layers=["T3"])
    before = copy.deepcopy(feedback)
    local = execute(feedback)
    assert feedback == before
    assert local["joint"]["status"] == "CONVERGED_LOCAL"
    assert local["joint"]["best"]["score"] > exact["joint"]["best"]["score"]
    assert not local["integrated"]["global_optimality_proven"]
    assert exact["integrated"]["global_optimality_proven"]
    cert = exact["joint"]["certificate"]
    assert cert["evaluated_states"] == cert["total_states"] == 4
    assert exact["joint"]["verification"]["status"] == "PASS"
    # Hand-designed trap: both SKU on the face toward entrance is the global solution.
    assert {r["face"] for r in cert["incumbent"]["placements"]} == {1}
    assert cert["absolute_gap"] == 0


@pytest.mark.parametrize(
    "attack", ["seal", "objective", "bounds", "relative", "solution", "leaves", "space", "input"]
)
def test_certificate_tampering_even_with_resealed_payload_is_rejected(trap_exact, attack):
    sections, config, result = trap_exact
    cert = copy.deepcopy(result["joint"]["certificate"])
    if attack == "objective":
        cert["upper_bound_fraction"] = [0, 1]
    elif attack == "bounds":
        cert["lower_bound_fraction"] = [0, 1]
    elif attack == "relative":
        cert["relative_gap"] = 0.5
    elif attack == "solution":
        cert["incumbent"]["poses"]["S1"] = [0, 0, 0]
    elif attack == "leaves":
        cert["leaves"].pop()
        cert["evaluated_states"] -= 1
    elif attack == "space":
        cert["finite_space"]["poses"]["S1"] = [[1, 1, 0]]
    elif attack == "input":
        cert["identity"]["problem_id"] = "wrong"
    if attack != "seal":
        cert["artifact_sha256"] = digest({k: v for k, v in cert.items() if k != "artifact_sha256"})
    else:
        cert["artifact_sha256"] = "0" * 64
    checked = verify(cert, evaluator(sections, config), identity=identity(sections, config))
    assert checked["status"] == "PROOF_VERIFICATION_FAILED"


def test_partial_search_has_valid_zero_lower_bound_and_no_optimality(trap_exact):
    sections, config, result = trap_exact
    best, cert, _ = solve(
        config.finite_space,
        evaluator(sections, config),
        identity=identity(sections, config),
        deadline=time.monotonic() + 20,
        max_evaluations=1,
    )
    assert best and cert["status"] == "BOUNDED_GAP" and not cert["complete"]
    assert cert["lower_bound_fraction"] == [0, 1]
    assert cert["absolute_gap"] >= 0
    assert (
        verify(cert, evaluator(sections, config), identity=identity(sections, config))["status"]
        == "PASS"
    )
    _, timed, _ = solve(
        config.finite_space,
        evaluator(sections, config),
        identity=identity(sections, config),
        deadline=0,
    )
    assert timed["status"] == "TIMEOUT" and timed["evaluated_states"] == 0


def test_one_state_ties_and_proven_infeasibility(trap_exact):
    sections, config, result = trap_exact
    space = copy.deepcopy(config.finite_space)
    for sku in space["placements"]:
        space["placements"][sku] = space["placements"][sku][:1]
    one = copy.deepcopy(sections)
    one["optimization"]["joint"]["finite_space"] = space
    assert execute(one)["joint"]["certificate"]["total_states"] == 1
    # Same travel/wait for alternative horizontal offsets: distinct co-optimal states.
    row = copy.deepcopy(space["placements"]["P2"][0])
    row["x_m"] = 0.6
    space["placements"]["P2"].append(row)
    tied = execute(one)["joint"]["certificate"]
    assert len({tuple(record["score_fraction"]) for record in tied["leaves"]}) == 1
    for rows in space["placements"].values():
        for row in rows:
            row["x_m"] = 100
    infeasible = execute(one)
    assert infeasible["joint"]["certificate"]["status"] == "INFEASIBLE_PROVEN"
    assert infeasible["joint"]["verification"]["status"] == "PASS"
    assert infeasible["joint"]["best"] is None


def test_feedback_real_layer_actions_and_dependency_cache():
    sections, config = problem("two-shelves", mode="feedback", max_actions=100)
    cache = {}
    call = evaluator(sections, config, cache)
    initial = call(None)
    feedback = analyze(initial, sections)
    proposals = actions(initial, feedback, sections, config)
    assert feedback["hot_shelves"] and feedback["sku_pick_counts"]["P1"] > 0
    assert "no corridor" in feedback["diagnostic_evidence"]["scope"]
    changed = {}
    for layer in ["T1", "T2", "T3", "T4"]:
        if layer == "T4":
            decision = copy.deepcopy(initial["decisions"])
            decision["routing_policy"] = "return"
            candidate = call(decision)
        else:
            for action in proposals:
                if action["layer"] != layer:
                    continue
                try:
                    candidate = call(action["decisions"])
                except EngineError:
                    continue
                if candidate["id"] != initial["id"]:
                    break
            else:
                pytest.fail(f"No valid actual decision edit in {layer}")
        changed[layer] = candidate
    base = initial["result"]["stage_cache"]
    for layer, indices in [
        ("T1", ["T1", "T2", "T3", "T4"]),
        ("T2", ["T2", "T3", "T4"]),
        ("T3", ["T3", "T4"]),
        ("T4", ["T4"]),
    ]:
        candidate = changed[layer]
        for stage in ["T1", "T2", "T3", "T4"]:
            key = candidate["result"]["stage_cache"][stage]["key"]
            assert (key != base[stage]["key"]) == (stage in indices)
        assert candidate["validation"] == "PASS"
    assert sections["demand"] == problem("two-shelves")[0]["demand"]
    # Locked shelf S2 is never proposed for a T1 change.
    assert all("S2" not in a["changed"] for a in proposals if a["layer"] == "T1")


def test_invalid_proposal_cannot_mutate_incumbent_or_change_weights():
    sections, config = problem(mode="feedback")
    call = evaluator(sections, config)
    state = call(None)
    old = copy.deepcopy(state)
    bad = copy.deepcopy(state["decisions"])
    bad["poses"]["S1"] = [0, 0, 0]
    with pytest.raises(EngineError, match="Locked"):
        call(bad)
    assert state == old
    assert exact_score(state) >= 0
    with pytest.raises(ValueError):
        JointConfig(objective={"weights": [-1, 0, 0, 0]})
    with pytest.raises(ValueError):
        JointConfig(scenario_seeds=[11], holdout_seeds=[11])


def test_joint_limits_hybrid_holdout_and_strict_descent():
    sections, config = problem(
        "two-shelves", mode="feedback", max_iterations=3, max_evaluations=20, holdout_seeds=[97]
    )
    result = execute(sections)
    joint = result["joint"]
    assert joint["evaluations"] <= 20
    assert joint["best"]["score"] <= joint["initial_score"]
    assert joint["holdout"]["scenario_seeds"] == [97]
    for entry in joint["trace"]:
        if entry.get("accepted"):
            assert entry["after"] < entry["before"] - config.tolerance
    sections, config = problem(mode="hybrid", max_evaluations=30)
    hybrid = execute(sections)
    assert hybrid["joint"]["proof_status"] == "GLOBAL_OPTIMAL_CERTIFIED"
    with pytest.raises(EngineError):
        execute(sections, cancelled=lambda: True)


def test_independent_manual_four_state_exhaustive_reference(trap_exact):
    sections, config, result = trap_exact
    # Explicit four-state reference, not solver iteration or its completeness data.
    call = evaluator(sections, config)
    values = []
    for face1, face2 in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        decision = {
            "poses": {"S1": [2, 3, 0]},
            "assignment": {"A": "S1"},
            "routing_policy": "nearest",
            "placements": [
                copy.deepcopy(config.finite_space["placements"]["P1"][face1]),
                copy.deepcopy(config.finite_space["placements"]["P2"][face2]),
            ],
        }
        values.append(exact_score(call(decision)))
    # A one-face edit is a plateau, which strict descent correctly rejects.
    assert values[-1] == min(values) < values[0] <= min(values[1:3])
    assert exact_score(result["joint"]["best"]) == min(values)


def test_joint_contract_domain_is_serialized_immutably():
    sections, _ = problem(mode="feedback")
    domain = to_domain(sections)
    assert isinstance(domain.config.joint, str)
    before = domain.config.joint
    sections["optimization"]["joint"]["max_iterations"] = 99
    assert domain.config.joint == before


def test_snapshot_frozen_payload_is_independent_of_mutable_readers():
    from dataclasses import FrozenInstanceError

    from smart_retail.application.feedback.state import FeedbackSnapshot

    original = {"decisions": {"poses": {"S1": [2, 3, 0]}}, "hit": True}
    state = FeedbackSnapshot.capture(original)
    original["decisions"]["poses"]["S1"][0] = 99
    reader = state.read()
    reader["decisions"]["poses"]["S1"][0] = 88
    assert state.read()["decisions"]["poses"]["S1"][0] == 2
    with pytest.raises(FrozenInstanceError):
        state.sha256 = "changed"


def test_t3_initial_failure_can_trigger_actual_t2_feasibility_repair():
    sections, config = problem("two-shelves", mode="feedback", max_iterations=0, max_evaluations=20)
    for product in sections["products"]["items"]:
        product["width_m"] = 1.2
    for shelf in sections["shelves"]["items"]:
        shelf["faces"] = 1
    result = execute(sections)
    assert result["joint"]["best"]
    assert any(
        e.get("action") == "REPAIR_T2" and e.get("accepted") for e in result["joint"]["trace"]
    )
    assert len(set(result["stages"]["T2"]["assignment"].values())) == 2


def test_cancel_between_iterations_retains_verified_best_snapshot():
    sections, config = problem(
        "two-shelves", mode="feedback", max_iterations=10, max_evaluations=100
    )
    stop = [False]

    def observe(stage, key, inputs, value, hit, elapsed):
        if stage == "JOINT_EVENT" and value.get("status") == "IMPROVING" and "feedback" in value:
            stop[0] = True

    result = execute(sections, cancelled=lambda: stop[0], observer=observe)
    assert result["joint"]["status"] == "CANCELLED"
    assert result["joint"]["best"]["score"] == result["joint"]["initial_score"]
    assert not result["integrated"]["global_optimality_proven"]


def test_corrupted_domain_rows_are_invalid_model_not_infeasibility():
    from smart_retail.contracts.optimality import FiniteSpace

    sections, config = problem(mode="exact")
    bad = copy.deepcopy(config.finite_space)
    bad["placements"]["P1"][0]["facings"] = 1.5
    with pytest.raises(ValueError):
        FiniteSpace.model_validate(bad)
    bad = copy.deepcopy(config.finite_space)
    bad["poses"].pop("S1")
    sections["optimization"]["joint"]["finite_space"] = bad
    with pytest.raises(EngineError, match="exactly every"):
        execute(sections)


def test_multistart_restarts_differ_on_generated_fixed_layout():
    from smart_retail.application.experiments.generators import generate, merge
    from smart_retail.contracts.experiments import DatasetSpec

    tiny = generate(DatasetSpec(id="tiny", scale="tiny", facings=6))[0]
    assert tiny["shelves"]["layout_mode"] == "fixed"
    joint = {
        "objective": {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]},
        "scenario_seeds": [0, 101],
        "scenario_seed_policy": "job_seed_offsets",
        "max_evaluations": 10,
        "mode": "multistart",
    }
    sections = merge(
        copy.deepcopy(tiny),
        {"optimization": {"joint": joint, "candidate_count": 3, "seed": 7, "time_limit_s": 60}},
    )
    result = execute(copy.deepcopy(sections))
    candidates = result["integrated"]["candidates"]
    poses = [
        tuple(sorted((s["id"], s["x"], s["y"], s["rotation"]) for s in c["stages"]["T1"]["shelves"]))
        for c in candidates
    ]
    assert len(candidates) == 3
    # Variant 0 is the sequential plan; restarts must explore other shelf layouts.
    assert len(set(poses)) == 3
    selected = result["integrated"]["selected_candidate"]
    assert candidates[selected]["score"] == min(c["score"] for c in candidates)
    restarts = [e for e in result["joint"]["trace"] if e.get("action") == "MULTISTART_RESTART"]
    assert len(restarts) == 2
    again = execute(copy.deepcopy(sections))
    assert again["joint"]["best"]["decisions"] == result["joint"]["best"]["decisions"]


@pytest.mark.parametrize("mode", ["random_search", "annealing", "feedback"])
def test_equal_evaluation_budget_modes_spend_budget_and_report_anytime_curve(mode):
    from smart_retail.application.experiments.generators import generate, merge
    from smart_retail.contracts.experiments import DatasetSpec

    tiny = generate(DatasetSpec(id="tiny", scale="tiny", facings=6))[0]
    joint = {
        "objective": {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]},
        "scenario_seeds": [0, 101],
        "scenario_seed_policy": "job_seed_offsets",
        "max_iterations": 100,
        "max_actions": 6,
        "max_evaluations": 8,
        "patience": 20,
        "mode": mode,
    }
    sections = merge(
        copy.deepcopy(tiny), {"optimization": {"joint": joint, "seed": 5, "time_limit_s": 120}}
    )
    result = execute(copy.deepcopy(sections))
    joint_result = result["joint"]
    assert joint_result["evaluations"] == 8
    assert joint_result["status"] == "EVALUATION_LIMIT"
    curve = joint_result["incumbent_curve"]
    assert curve[0]["evaluation"] == 1
    assert all(a["score"] > b["score"] for a, b in zip(curve, curve[1:]))
    assert curve[-1]["score"] == joint_result["best"]["score"]
    assert joint_result["evaluations_to_best"] == curve[-1]["evaluation"]
    scores = [c["score"] for c in result["integrated"]["candidates"]]
    assert joint_result["best"]["score"] == min(scores)
    if mode == "annealing":
        assert any(e.get("reason") == "METROPOLIS" for e in joint_result["trace"])
    again = execute(copy.deepcopy(sections))["joint"]
    assert again["best"]["decisions"] == joint_result["best"]["decisions"]


def test_union_space_contains_heuristic_solutions_and_certifies_recombination():
    from smart_retail.application.experiments.finite_spaces import union_space
    from smart_retail.application.experiments.generators import generate, merge
    from smart_retail.application.feedback.coordinator import member
    from smart_retail.contracts.experiments import DatasetSpec
    from smart_retail.contracts.optimality import FiniteSpace

    tiny = generate(DatasetSpec(id="tiny", scale="tiny", facings=6))[0]
    base = {
        "objective": {"weights": [1, 0.2, 0.1, 0.1], "scales": [100, 100, 1, 1]},
        "scenario_seeds": [0, 101],
        "scenario_seed_policy": "job_seed_offsets",
        "max_evaluations": 12,
        "max_iterations": 100,
        "max_actions": 6,
        "policy": "first_improvement",
    }

    def run(**joint):
        sections = merge(
            copy.deepcopy(tiny),
            {"optimization": {"joint": {**base, **joint}, "seed": 3, "time_limit_s": 120}},
        )
        return execute(sections)["joint"]

    sources = [run(mode="sequential"), run(mode="feedback"), run(mode="annealing")]
    decisions = [s["best"]["decisions"] for s in sources]
    space, info = union_space(decisions)
    assert info["states"] == info["layouts"] * info["allocations"] * len(space["routing_policies"])
    assert union_space(decisions + decisions)[0] == space
    model = FiniteSpace.model_validate(space)
    assert all(member(d, model) for d in decisions)
    exact = run(mode="exact", finite_space=space, max_evaluations=info["states"])
    assert exact["proof_status"] == "GLOBAL_OPTIMAL_CERTIFIED"
    assert exact["verification"]["status"] == "PASS"
    assert exact["certificate"]["total_states"] == info["states"]
    assert all(exact["best"]["score"] <= s["best"]["score"] + 1e-12 for s in sources)
    # Spaces without bundles keep the pre-existing canonical form.
    legacy = json.loads((ROOT / "datasets/joint/local-trap-space.json").read_text())
    assert "layouts" not in FiniteSpace.model_validate(legacy).model_dump(mode="json")
