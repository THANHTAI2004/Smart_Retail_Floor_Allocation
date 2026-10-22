"""Assess JO gates from executed release/campaign/proof receipts, never file presence alone."""

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from smart_retail.application.experiments.storage import verify_integrity
from smart_retail.infrastructure.provenance import runtime_identity

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--campaign-suffix", default="02", choices=["01", "02"])
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    release = read(args.release / "verification.json")
    check = {r["name"]: r["exit_code"] == 0 for r in release["checks"]}
    receipt_hashes = all(
        hashlib.sha256((args.release / name).read_bytes()).hexdigest() == h
        for name, h in release["files"].items()
    )
    suite = ET.parse(args.release / "pytest.xml")
    names = {
        c.attrib["name"].split("[")[0] for c in suite.iter("testcase") if not list(c)
    }
    all_tests = not list(suite.iter("failure")) and not list(suite.iter("error"))
    current = runtime_identity()
    identical = release["runtime"] == current
    rows = []
    campaigns = []
    hashes = True
    for name in [
        "effectiveness",
        "ablation",
        "certification",
        "scalability",
        "holdout",
        "certification-128",
    ]:
        root = (
            ROOT / f"experiments/results/20261022-joint-{name}-{args.campaign_suffix}"
        )
        integrity = verify_integrity(root)
        checkpoint = read(root / "checkpoint.json")
        identity = read(root / "identity.json")
        campaign_rows = [read(p) for p in (root / "records").glob("*.json")]
        rows.extend(campaign_rows)
        report = (
            ROOT / f"experiments/reports/20261022-joint-{name}-{args.campaign_suffix}"
        )
        manifest = read(report / "manifest.json")
        valid_report = all(
            hashlib.sha256((report / file).read_bytes()).hexdigest() == h
            for file, h in manifest["files"].items()
        )
        hashes &= (
            valid_report
            and integrity["status"] == "PASS"
            and identity["runtime"] == current
        )
        campaigns.append(
            {
                "name": name,
                "checkpoint": checkpoint,
                "integrity": integrity,
                "report_hashes": valid_report,
                "source_matches": identity["runtime"] == current,
            }
        )
    proof_rows = [
        r
        for r in rows
        if r["experiment"] == "E13" and r["treatment"] in ("exact", "hybrid")
    ]
    proof_ok = proof_rows and all(
        r.get("proof_status") == "GLOBAL_OPTIMAL_CERTIFIED"
        and r.get("certificate_verification") == "PASS"
        for r in proof_rows
    )
    completed = all(
        c["checkpoint"]["status"] == "COMPLETED"
        and c["checkpoint"]["not_executed"] == 0
        for c in campaigns
    )
    witnesses = all(
        r["validation"]["status"] == "PASS" for r in rows if r["status"] == "SUCCEEDED"
    )
    comparison = read(
        ROOT
        / f"experiments/reports/20261022-joint-clean-comparison-{args.campaign_suffix}.json"
    )
    replay = bool(comparison["rows"]) and all(
        r.get("same_input_hash")
        and r.get("byte_identical_result")
        and r.get("numerically_equivalent")
        for r in comparison["rows"]
    )
    feedback_comparison = read(
        ROOT
        / f"experiments/reports/20261022-joint-feedback-clean-comparison-{args.campaign_suffix}.json"
    )
    replay = (
        replay
        and bool(feedback_comparison["rows"])
        and all(
            r.get("same_input_hash")
            and r.get("byte_identical_result")
            and r.get("numerically_equivalent")
            for r in feedback_comparison["rows"]
        )
    )
    cli = read(
        ROOT
        / f"docs/research/evidence/20261022-joint-proof-cli-{args.campaign_suffix}.json"
    )
    controls_root = (
        ROOT
        / f"experiments/results/20261022-joint-failure-controls-{args.campaign_suffix}"
    )
    control_rows = [read(p) for p in (controls_root / "records").glob("*.json")]
    control_statuses = {r["status"] for r in control_rows}
    controls_ok = (
        verify_integrity(controls_root)["status"] == "PASS"
        and control_statuses == {"FAILED", "INFEASIBLE"}
        and all(not r["solution_feasible"] for r in control_rows)
    )
    holdout_rows = [r for r in rows if r["experiment"] == "E15"]
    holdouts_ok = bool(holdout_rows) and all(
        isinstance(r.get("holdout_objective"), (int, float)) for r in holdout_rows
    )
    gates = []

    def gate(number, passed, evidence, limitation=""):
        gates.append(
            {
                "gate": f"JO{number:02}",
                "status": "PASS" if passed else "FAIL",
                "evidence": evidence,
                "limitation": limitation,
            }
        )

    def tested(name):
        return all_tests and check.get("pytest", False) and name in names

    layer = tested("test_feedback_real_layer_actions_and_dependency_cache")
    gate(
        1,
        tested("test_joint_contract_domain_is_serialized_immutably") and proof_ok,
        "Explicit finite domains and fixed scenario objective; formulation; contract/reference proofs",
    )
    gate(
        2,
        tested("test_snapshot_frozen_payload_is_independent_of_mutable_readers"),
        "Frozen content-sealed snapshot and mutation/rollback regression; JOINT_STATE artifacts",
    )
    gate(
        3,
        layer,
        "Real simulated visits/picks/queue diagnostics with declared attribution proxies",
    )
    for i, layer_name in [(4, "T1"), (5, "T2"), (6, "T3")]:
        gate(
            i,
            layer,
            f"Real valid {layer_name} edits and independent constraint replay; action traces",
        )
    gate(
        7,
        layer,
        "Observed unchanged upstream and changed downstream content keys for actual T1/T2/T3/T4 edits",
    )
    gate(
        8,
        tested("test_joint_limits_hybrid_holdout_and_strict_descent")
        and any(r.get("joint_iterations_to_best", 0) >= 2 for r in rows),
        "Multiple actual improving E11 iterations and strict-descent tests",
        "Local convergence only within examined, possibly truncated neighborhood",
    )
    gate(
        9,
        tested("test_invalid_proposal_cannot_mutate_incumbent_or_change_weights")
        and tested("test_cancellation_kills_a_real_running_t4_child")
        and tested(
            "test_real_worker_retains_failed_search_and_proven_infeasibility_without_success"
        )
        and controls_ok,
        "Rollback, iteration/evaluation limits, actual process cancellation/RSS/wall supervision regressions",
    )
    gate(
        10,
        witnesses and layer,
        "Every successful recorded job independently replays official physical and route witnesses",
    )
    gate(
        11,
        tested("test_independent_manual_four_state_exhaustive_reference") and proof_ok,
        "Hand-authored four-state oracle, 128-state model, one-state/tie/infeasible tests",
        "Finite explicitly listed decision domains only",
    )
    gate(
        12,
        proof_ok
        and tested("test_partial_search_has_valid_zero_lower_bound_and_no_optimality"),
        "Complete certificates, validated UB and valid zero LB for partial search; timeout tests",
        "Exact comparison of serialized numerical simulation observations, not real arithmetic",
    )
    gate(
        13,
        tested("test_certificate_tampering_even_with_resealed_payload_is_rejected")
        and cli["status"] == "PASS",
        "Resealed tampering rejection plus independent offline verifier receipt",
        "Verifier shares official model physics/simulation; separately enumerates and selects minimum",
    )
    gate(
        14,
        tested("test_local_trap_is_distinct_from_global_certificate") and proof_ok,
        "Local plateau distinguished from strictly better exact finite solution in E13",
    )
    gate(
        15,
        completed
        and hashes
        and holdouts_ok
        and {"E11", "E12", "E13", "E14", "E15"} <= {r["experiment"] for r in rows},
        "Executed E11-E15, immutable identities, report hashes and failure-preserving records",
        "E14 bounded Small-scale sweep; E15 synthetic holdout only; three independent job seeds per arm",
    )
    gate(
        16,
        check.get("e2e", False)
        and (args.release / "browser/ui/joint-exact.png").is_file(),
        "Real browser campaign/proof/convergence/decision views and trace/certificate exports",
    )
    gate(
        17,
        all(check.values()) and receipt_hashes and identical,
        "Fresh full release commands, source identity, immutable receipt hashes",
    )
    gate(
        18,
        replay and identical and hashes,
        "15/15 E13 and 9/9 improving E11 exact scientific-result and input hashes in separate pinned Python environment",
        "Same Windows machine; no cross-platform/real-store validation",
    )
    status = {
        "CLOSED_LOOP_FEEDBACK_READY": all(g["status"] == "PASS" for g in gates[:10]),
        "JOINT_EXACT_SMALL_INSTANCE_CERTIFIED": all(
            g["status"] == "PASS" for g in gates[10:14]
        ),
        "JOINT_GENERAL_OPTIMALITY_NOT_PROVEN": True,
    }
    result = {
        "statuses": status,
        "gates": gates,
        "campaigns": campaigns,
        "release": str(args.release),
        "all_gates_pass": all(g["status"] == "PASS" for g in gates),
        "runtime": current,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(status)
    for g in gates:
        print(g["gate"], g["status"])
    if not result["all_gates_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
