import copy
import json
from pathlib import Path

from smart_retail.application.experiments.campaign import run
from smart_retail.contracts.experiments import CampaignSpec


def test_real_worker_retains_failed_search_and_proven_infeasibility_without_success(tmp_path):
    root = Path(__file__).resolve().parents[3]
    spec = json.loads((root / "experiments/configs/joint_certification.json").read_text())
    base = next(t for t in spec["experiments"][0]["treatments"] if t["id"] == "exact")
    arms = []
    for name, budget in [("partial", 1), ("infeasible", 10)]:
        arm = copy.deepcopy(base)
        arm["id"] = name
        joint = arm["overrides"]["optimization"]["joint"]
        joint["max_evaluations"] = budget
        for rows in joint["finite_space"]["placements"].values():
            for row in rows:
                row["x_m"] = 100
        arms.append(arm)
    spec["experiments"][0]["treatments"] = arms
    spec["seeds"] = [11]
    out = tmp_path / "campaign"
    run(CampaignSpec.model_validate(spec), out)
    rows = {
        r["treatment"]: r
        for r in [json.loads(p.read_text()) for p in (out / "records").glob("*.json")]
    }
    assert rows["partial"]["status"] == "FAILED"
    assert rows["partial"]["error"]["code"] == "SEARCH_EXHAUSTED"
    assert rows["partial"]["validation"]["status"] == "NO_SOLUTION"
    assert rows["infeasible"]["status"] == "INFEASIBLE"
    assert rows["infeasible"]["proof_status"] == "INFEASIBLE_PROVEN"
    assert rows["infeasible"]["certificate_verification"] == "PASS"
    assert all(not row["solution_feasible"] for row in rows.values())
    for row in rows.values():
        result = json.loads((out / "artifacts" / row["run_id"] / "result.json").read_text())
        assert result["joint"]["certificate"] and result["joint"]["best"] is None
    assert json.loads((out / "checkpoint.json").read_text())["completed"] == 2
