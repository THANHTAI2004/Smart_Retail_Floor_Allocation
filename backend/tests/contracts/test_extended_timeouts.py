import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from smart_retail.contracts.experiments import CampaignSpec
from smart_retail.contracts.inputs import OptimizationInput, to_domain
from smart_retail.workers.runner import wall_budget


def test_extended_campaign_budget_and_schema_roundtrip(sample):
    root = Path(__file__).resolve().parents[3]
    data = json.loads((root / "experiments/configs/paper-v3/paper-x2-medium-part01.json").read_text())
    data.update(job_time_limit_s=1800, max_wall_s=28800, memory_limit_mb=None)
    spec = CampaignSpec.model_validate(data)
    assert CampaignSpec.model_validate_json(spec.model_dump_json()) == spec
    sample["optimization"]["time_limit_s"] = 1800
    assert to_domain(sample).config.time_limit_s == 1800
    assert wall_budget(1800) == 1980


@pytest.mark.parametrize("key,value", [("job_time_limit_s", 3601), ("max_wall_s", 28801)])
def test_extended_campaign_still_has_bounded_limits(key, value):
    root = Path(__file__).resolve().parents[3]
    data = json.loads((root / "experiments/configs/paper-v3/paper-x1-trap.json").read_text())
    data[key] = value
    with pytest.raises(ValidationError):
        CampaignSpec.model_validate(data)


def test_optimization_rejects_above_extended_limit():
    with pytest.raises(ValidationError):
        OptimizationInput(time_limit_s=3601)
