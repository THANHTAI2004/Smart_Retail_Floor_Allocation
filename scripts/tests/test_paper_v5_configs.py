import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_paper_v5_configs as v5  # noqa: E402
from build_paper_configs import HOLDOUT  # noqa: E402
from build_paper_v4_configs import FEEDBACK, V4, V4_SCALES  # noqa: E402

from smart_retail.contracts.experiments import CampaignSpec, planned_jobs  # noqa: E402
from smart_retail.contracts.feedback import JointConfig  # noqa: E402

FAMILIES = ("grid", "corner_entrance", "wide", "columns")
V5_FIELDS = ("surrogate", "surrogate_pool", "compound_moves", "restart_samples", "restart_evaluations", "search_seed_scope", "population", "mutation_edits", "drop_identical_swaps")
W1_ARMS = ["seq_milp", "random_search", "annealing", "genetic", "feedback_v4", "feedback_v5"]
W2_ARMS = ["seq_milp", "feedback_v5", "v5_no_surrogate", "v5_no_compound", "v5_no_restart", "v5_no_heat"]


@pytest.fixture(scope="module")
def designs():
    return {spec["name"]: (block, spec) for block, spec in v5.build()}


def joint(treatment):
    return treatment["overrides"]["optimization"]["joint"]


def arms_of(spec):
    (experiment,) = spec["experiments"]
    return {t["id"]: joint(t) for t in experiment["treatments"]}


def jobs(spec):
    return sum(planned_jobs(part) for part in v5.finalize(spec))


def test_campaign_names_blocks_and_totals(designs):
    # Insertion order is the index order: W1 medium first (least known job times), then small, tiny.
    assert [(name, block) for name, (block, _) in designs.items()] == [
        ("paper-v5-w1-medium", "W1"),
        ("paper-v5-w1-small", "W1"),
        ("paper-v5-w1-tiny", "W1"),
        ("paper-v5-w2-ablation", "W2"),
    ]
    totals = {name: jobs(spec) for name, (_, spec) in designs.items()}
    assert totals == {
        "paper-v5-w1-tiny": 360,
        "paper-v5-w1-small": 360,
        "paper-v5-w1-medium": 144,
        "paper-v5-w2-ablation": 144,
    }
    assert sum(jobs(spec) for block, spec in designs.values() if block == "W1") == 864
    assert sum(totals.values()) == 1008


def test_finalized_parts_are_valid_and_named_uniquely(designs):
    names = []
    for _, spec in designs.values():
        parts = v5.finalize(spec)
        assert parts
        for part in parts:
            assert part.max_jobs == planned_jobs(part)
            assert part.evaluation is not None and part.evaluation.split == "temporal_holdout"
            CampaignSpec.model_validate_json(part.model_dump_json())
            names.append(part.name)
    assert len(names) == len(set(names))


def test_every_treatment_validates_as_joint_config(designs):
    for _, spec in designs.values():
        CampaignSpec.model_validate(spec)
        for experiment in spec["experiments"]:
            for treatment in experiment["treatments"]:
                JointConfig.model_validate(joint(treatment))


def test_datasets_cover_four_families_on_fresh_seeds(designs):
    expected = {
        "paper-v5-w1-tiny": ("tiny", 3, 8001),
        "paper-v5-w1-small": ("small", 3, 8101),
        "paper-v5-w1-medium": ("medium", 2, 8201),
        "paper-v5-w2-ablation": ("small", 2, 8301),
    }
    for name, (scale, per_family, first) in expected.items():
        items = designs[name][1]["datasets"]
        assert len(items) == per_family * len(FAMILIES)
        assert all(d["scale"] == scale and d["layout_family"] in FAMILIES for d in items)
        assert [d["seed"] for d in items] == list(range(first, first + len(items)))
        for index, family in enumerate(FAMILIES):
            block = items[index * per_family:(index + 1) * per_family]
            assert [d["layout_family"] for d in block] == [family] * per_family
        assert len({d["id"] for d in items}) == len(items)
        for d in items:
            facings = V4_SCALES[scale][0]
            assert d["id"] == f"{scale}_f{facings}_{d['layout_family']}_s{d['seed']}"
            assert d["facings"] == facings and d["orders"] == V4_SCALES[scale][1]
            assert d["order_interval_s"] > 0 and d["picker_count"] >= 1
    seeds = [d["seed"] for _, spec in designs.values() for d in spec["datasets"]]
    assert min(seeds) >= 8001 and len(seeds) == len(set(seeds))


def test_experiments_reference_their_datasets(designs):
    for name, (_, spec) in designs.items():
        (experiment,) = spec["experiments"]
        assert experiment["id"] == ("E62" if name.endswith("ablation") else "E61")
        assert experiment["datasets"] == [d["id"] for d in spec["datasets"]]
        assert experiment["question"]


def test_search_seeds_protocol_and_job_caps(designs):
    seeds = {name: spec["seeds"] for name, (_, spec) in designs.items()}
    assert seeds == {
        "paper-v5-w1-tiny": [1, 2, 3, 4, 5],
        "paper-v5-w1-small": [1, 2, 3, 4, 5],
        "paper-v5-w1-medium": [1, 2, 3],
        "paper-v5-w2-ablation": [1, 2, 3],
    }
    caps = {"tiny": 300.0, "small": 600.0, "medium": 3600.0}
    for name, scale in (("tiny", "tiny"), ("small", "small"), ("medium", "medium")):
        assert designs[f"paper-v5-w1-{name}"][1]["job_time_limit_s"] == caps[scale]
    assert designs["paper-v5-w2-ablation"][1]["job_time_limit_s"] == 600.0
    for _, spec in designs.values():
        assert spec["evaluation"] == HOLDOUT


def test_arms_per_experiment_and_budgets(designs):
    for name, (_, spec) in designs.items():
        expected = W2_ARMS if name.endswith("ablation") else W1_ARMS
        arms = arms_of(spec)
        assert list(arms) == expected
        scale = "small" if name.endswith("ablation") else name.rsplit("-", 1)[1]
        assert {a["max_evaluations"] for a in arms.values()} == {V4_SCALES[scale][2]}


def test_w1_arm_settings(designs):
    for scale, restart in (("tiny", 10), ("small", 8), ("medium", 10)):
        arms = arms_of(designs[f"paper-v5-w1-{scale}"][1])
        assert arms["seq_milp"]["mode"] == "sequential"
        assert arms["genetic"]["mode"] == "genetic"
        assert (arms["genetic"]["population"], arms["genetic"]["mutation_edits"]) == (8, 2)
        assert arms["random_search"]["mode"] == "random_search"
        assert arms["annealing"]["mode"] == "annealing"
        # Annealing differs from paper-v4: no identical-shelf swaps, objective T3 scope only.
        assert arms["annealing"]["drop_identical_swaps"] is True
        assert arms["annealing"]["t3_scope"] == "objective"
        assert not [key for key in V4 if key != "t3_scope" and key in arms["annealing"]]
        assert not [key for key in V5_FIELDS if key not in ("search_seed_scope", "drop_identical_swaps") and key in arms["annealing"]]
        for unchanged in ("random_search", "genetic", "feedback_v4"):
            assert "drop_identical_swaps" not in arms[unchanged]
        assert "t3_scope" not in arms["random_search"] and "t3_scope" not in arms["genetic"]
        assert arms["feedback_v5"]["drop_identical_swaps"] is True
        for key, value in {**FEEDBACK, **V4}.items():
            assert arms["feedback_v4"][key] == value
            assert arms["feedback_v5"][key] == value
        assert not [key for key in V5_FIELDS if key != "search_seed_scope" and key in arms["feedback_v4"]]
        assert arms["feedback_v5"]["surrogate"] == "walk_heat"
        assert arms["feedback_v5"]["surrogate_pool"] == 96
        assert arms["feedback_v5"]["compound_moves"] == 32
        assert arms["feedback_v5"]["restart_samples"] == 128
        assert arms["feedback_v5"]["restart_evaluations"] == restart
        for stochastic in ("random_search", "annealing", "genetic", "feedback_v4", "feedback_v5"):
            assert arms[stochastic]["search_seed_scope"] == "instance"


def test_no_seq_milp_arm_carries_v5_fields(designs):
    for _, spec in designs.values():
        reference = arms_of(spec)["seq_milp"]
        assert reference["mode"] == "sequential"
        assert not [key for key in V5_FIELDS if key in reference]


def test_w2_ablation_arms_remove_exactly_one_component(designs):
    arms = arms_of(designs["paper-v5-w2-ablation"][1])
    full = arms["feedback_v5"]
    assert full["restart_evaluations"] == 8 and full["surrogate"] == "walk_heat"
    assert "surrogate" not in arms["v5_no_surrogate"]
    assert arms["v5_no_surrogate"]["surrogate_pool"] == 96
    assert "compound_moves" not in arms["v5_no_compound"]
    assert "restart_samples" not in arms["v5_no_restart"] and "restart_evaluations" not in arms["v5_no_restart"]
    assert arms["v5_no_heat"]["surrogate"] == "walk"
    removed = {
        "v5_no_surrogate": {"surrogate"},
        "v5_no_compound": {"compound_moves"},
        "v5_no_restart": {"restart_samples", "restart_evaluations"},
    }
    for identifier, keys in removed.items():
        assert {key: value for key, value in full.items() if key not in keys} == arms[identifier]
    assert {key: value for key, value in full.items() if key != "surrogate"} == {
        key: value for key, value in arms["v5_no_heat"].items() if key != "surrogate"
    }
    for identifier in W2_ARMS[2:]:
        assert arms[identifier]["search_seed_scope"] == "instance"
        assert arms[identifier]["drop_identical_swaps"] is True


@pytest.mark.skipif(not v5.OUT.exists(), reason="paper-v5 configs not generated")
def test_generated_configs_match_the_builder():
    parts = [(block, part) for block, spec in v5.build() for part in v5.finalize(spec)]
    index = json.loads((v5.OUT / "index.json").read_text(encoding="utf-8"))
    assert [(row["block"], row["config"], row["jobs"]) for row in index] == [
        (block, f"{part.name}.json", planned_jobs(part)) for block, part in parts
    ]
    for _, part in parts:
        saved = (v5.OUT / f"{part.name}.json").read_text(encoding="utf-8")
        assert saved == json.dumps(part.model_dump(mode="json"), indent=2) + "\n"
    assert sorted(p.name for p in v5.OUT.iterdir()) == sorted([row["config"] for row in index] + ["index.json"])
    w1 = [row["config"] for row in index if row["block"] == "W1"]
    scales = [name.split("-")[3] for name in w1]
    assert scales == sorted(scales, key=["medium", "small", "tiny"].index) and scales[0] == "medium"
    assert sum(row["jobs"] for row in index) == 1008
