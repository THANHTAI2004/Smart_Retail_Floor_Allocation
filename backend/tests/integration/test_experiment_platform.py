import copy
import json
import time

import pytest
from pydantic import ValidationError

from smart_retail.application.experiments.campaign import run
from smart_retail.application.experiments.cli import compare
from smart_retail.application.experiments.generators import generate
from smart_retail.application.experiments.reports import report
from smart_retail.application.experiments.storage import read, verify_integrity
from smart_retail.application.workflow import _candidate
from smart_retail.contracts.experiments import CampaignSpec, DatasetSpec
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError
from smart_retail.infrastructure.stage_cache import StageCache
from smart_retail.workers.resources import sample as sample_resources


def spec():
    return CampaignSpec.model_validate(
        {
            "name": "pipeline regression",
            "seeds": [11, 23],
            "datasets": [{"id": "tiny", "scale": "tiny"}],
            "experiments": [
                {
                    "id": "E01",
                    "question": "Does independent geometry replay accept every witness?",
                    "hypothesis": "All accepted witnesses have zero violations",
                    "datasets": ["tiny"],
                    "acceptance": "Zero independently replayed violations",
                    "treatments": [
                        {
                            "id": "baseline",
                            "overrides": {"optimization": {"stop_after_stage": "T1"}},
                        }
                    ],
                }
            ],
        }
    )


@pytest.mark.parametrize("scale", ["tiny", "small", "medium", "large"])
@pytest.mark.parametrize("scenario", ["feasible", "infeasible", "high_load", "volatile", "uneven"])
def test_generators_are_deterministic_valid_and_labeled(scale, scenario):
    request = DatasetSpec(id=scale, scale=scale, scenario=scenario)
    a, ma = generate(request)
    b, mb = generate(request)
    assert a == b and ma == mb
    assert ma["data_origin"] == "SYNTHETIC"
    assert all(
        value["schema_version"] == "1.1" and value["data_origin"] == "SYNTHETIC"
        for value in a.values()
    )
    to_domain(a)


def test_resume_reports_checksums_and_full_campaign_replay(tmp_path):
    configuration = spec()
    output = tmp_path / "campaign"
    first = run(configuration, output, max_new_jobs=1)
    assert first["status"] == "PAUSED_PARTIAL" and first["completed"] == 1
    record = next((output / "records").glob("*.json"))
    original = record.read_bytes()
    second = run(configuration, output, resume=True)
    assert second["status"] == "COMPLETED" and second["completed"] == 2
    assert record.read_bytes() == original
    assert verify_integrity(output)["status"] == "PASS"
    records = [read(p) for p in (output / "records").glob("*.json")]
    assert all(
        r["validation"]["status"] == "PASS" and r["peak_child_rss_bytes"] > 0 for r in records
    )
    replay = tmp_path / "replay"
    run(configuration, replay)
    comparisons = compare(output, replay)["rows"]
    assert all(r["byte_identical_result"] and r["numerically_equivalent"] for r in comparisons)
    result = report(output, tmp_path / "report")
    assert result["records"] == 2 and result["figures"] >= 2
    for filename in (
        "summary.md",
        "results.csv",
        "results.json",
        "comparisons.csv",
        "statistics.json",
        "failures.csv",
        "manifest.json",
    ):
        assert (tmp_path / "report" / filename).is_file()
    with pytest.raises(FileExistsError):
        report(output, tmp_path / "report")
    record.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        verify_integrity(output)


def test_repeated_kfold_campaign_records_folds_and_pools_reports(tmp_path):
    arms = {
        "baseline": {"algorithm": "greedy", "slotting_algorithm": "first_fit"},
        "milp": {"algorithm": "milp", "slotting_algorithm": "milp"},
        "milp_multistart": {"algorithm": "milp", "candidate_count": 2},
    }
    configuration = CampaignSpec.model_validate(
        {
            "schema_version": "1.1",
            "name": "kfold regression",
            "seeds": [11],
            "datasets": [{"id": "tiny", "scale": "tiny", "facings": 6}],
            "experiments": [
                {
                    "id": "E16",
                    "question": "Do selected plans keep their objective on held-out orders?",
                    "hypothesis": "Every held-out replay passes independent validation",
                    "datasets": ["tiny"],
                    "acceptance": "Zero violations on training and held-out replays",
                    "treatments": [
                        {"id": arm, "overrides": {"optimization": overrides}}
                        for arm, overrides in arms.items()
                    ],
                    "metrics": ["test_objective", "train_objective", "generalization_gap"],
                }
            ],
            "evaluation": {"split": "kfold", "n_folds": 3},
        }
    )
    output = tmp_path / "campaign"
    assert run(configuration, output)["status"] == "COMPLETED"
    plan = read(output / "datasets" / "tiny" / "splits" / "11.json")
    assert [f["fold"] for f in plan["folds"]] == [0, 1, 2]
    records = [read(p) for p in (output / "records").glob("*.json")]
    assert len(records) == 9
    assert {(r["treatment"], r["cv_fold"]) for r in records} == {
        (arm, fold) for arm in arms for fold in range(3)
    }
    assert all(
        r["status"] == "SUCCEEDED"
        and r["evaluation_status"] == "COMPLETED"
        and r["train_orders"] + r["test_orders"] == 20
        and r["validation"]["status"] == "PASS"
        for r in records
    )
    replay = tmp_path / "replay"
    run(configuration, replay)
    assert all(r["byte_identical_result"] for r in compare(output, replay)["rows"])
    report(output, tmp_path / "report")
    for filename in ("fold_results.csv", "run_means.csv", "status_matrix.csv", "rankings.csv"):
        assert (tmp_path / "report" / filename).is_file()
    arm = tmp_path / "report" / "results" / "E16_tiny_milp_k3_r1_t15s"
    for suffix in (
        "file_sum_ok.txt",
        "file_eachfold.txt",
        "file_mean_test_objective.txt",
        "file_mean_test_distance.txt",
        "config.json",
    ):
        assert (arm / f"E16_tiny_milp_k3_r1_t15s_{suffix}").is_file()
    eachfold = (arm / "E16_tiny_milp_k3_r1_t15s_file_eachfold.txt").read_text(encoding="utf-8")
    assert len(eachfold.splitlines()) == 1 + 3
    repeat = CampaignSpec.model_validate(read(arm / "E16_tiny_milp_k3_r1_t15s_config.json"))
    keys = {r["job_key"] for r in records if r["treatment"] == "milp"}
    single = run(repeat, tmp_path / "repeat-arm")
    assert single["completed"] == 3
    assert {read(p)["job_key"] for p in (tmp_path / "repeat-arm" / "records").glob("*.json")} == keys
    statistics = read(tmp_path / "report" / "statistics.json")
    assert {c["paired_units"] for c in statistics["comparisons"]} == {3}
    assert all(c["cross_validated"] for c in statistics["comparisons"])
    with pytest.raises(ValueError, match="more than one campaign"):
        report([output, replay], tmp_path / "pooled")


def test_persistent_cache_invalidation_and_tampering(sample, tmp_path):
    cache = StageCache(tmp_path / "cache")
    sample["optimization"]["stop_after_stage"] = "T3"
    original = copy.deepcopy(sample)
    first = _candidate(sample, deadline=time.monotonic() + 10, cache=cache)
    second = _candidate(sample, deadline=time.monotonic() + 10, cache=cache)
    assert all(value["hit"] for value in second["stage_cache"].values())
    assert sample == original
    sample["products"]["items"][0]["demand"] += 1
    third = _candidate(sample, deadline=time.monotonic() + 10, cache=cache)
    assert third["stage_cache"]["T1"]["hit"] and third["stage_cache"]["T2"]["hit"]
    assert not third["stage_cache"]["T3"]["hit"]
    path = cache.root / f"{first['stage_cache']['T1']['key']}.json"
    broken = read(path)
    broken["payload"]["objective"] = 999
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(EngineError) as error:
        _candidate(sample, deadline=time.monotonic() + 10, cache=cache)
    assert error.value.code == "CACHE_CORRUPT"


def test_campaign_contract_rejects_invalid_refs_and_parallel_workers():
    data = spec().model_dump()
    data["workers"] = 2
    with pytest.raises(ValidationError):
        CampaignSpec.model_validate(data)
    data["workers"] = 1
    data["experiments"][0]["datasets"] = ["missing"]
    with pytest.raises(ValidationError):
        CampaignSpec.model_validate(data)


def test_resource_sampler_measures_current_process():
    import os

    result = sample_resources(os.getpid())
    assert result["rss_bytes"] > 0 and result["peak_rss_bytes"] >= result["rss_bytes"]


def test_process_creation_failures_have_bounded_retry_and_terminal_receipts(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from smart_retail.workers import runner

    def process(*args, **kwargs):
        def fail():
            raise OSError("Injected process creation failure")

        return SimpleNamespace(start=fail)

    monkeypatch.setattr(runner.mp, "get_context", lambda _: SimpleNamespace(Process=process))
    configuration = spec().model_copy(update={"seeds": [11], "max_retries": 1})
    output = tmp_path / "retry"
    state = run(configuration, output)
    assert state["completed"] == 1
    [record] = [read(p) for p in (output / "records").glob("*.json")]
    assert record["status"] == "FAILED" and record["error"]["code"] == "WORKER_CRASH"
    assert len(record["attempts"]) == 2
    assert len(list((output / "artifacts").glob("*/receipt.json"))) == 2


def test_imported_dataset_requires_hash_and_synthetic_origin(sample, tmp_path, monkeypatch):
    import hashlib

    from smart_retail.application.experiments import generators

    monkeypatch.setattr(generators, "DATASET_ROOT", tmp_path)
    path = tmp_path / "custom.json"
    path.write_text(json.dumps(sample), encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    data, manifest = generate(
        DatasetSpec(id="custom", input_path=str(path), input_file_sha256=digest)
    )
    assert manifest["sha256"] and data == sample
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        generate(DatasetSpec(id="custom", input_path=str(path), input_file_sha256=digest))


def test_oversized_cartesian_plan_rejected_before_materialization():
    configuration = spec().model_dump()
    configuration["seeds"] = list(range(100))
    configuration["repetitions"] = 10
    configuration["experiments"][0]["treatments"] *= 2
    configuration["experiments"][0]["treatments"][1]["id"] = "second"
    with pytest.raises(ValidationError, match="1,000"):
        CampaignSpec.model_validate(configuration)
