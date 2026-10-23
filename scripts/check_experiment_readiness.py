"""Evaluate the published local synthetic readiness gates against actual evidence."""

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from smart_retail.application.experiments.storage import read, verify_integrity
from smart_retail.contracts.inputs import SECTIONS
from smart_retail.infrastructure.provenance import runtime_identity

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verification = read(args.evidence / "verification.json")
    checks = {c["name"]: c["exit_code"] == 0 for c in verification["checks"]}
    suite = ET.parse(args.evidence / "pytest.xml").getroot().find("testsuite")
    tests = {case.attrib["name"] for case in suite.findall("testcase") if case.find("failure") is None and case.find("error") is None}
    all_tests_ok = int(suite.attrib["failures"]) == int(suite.attrib["errors"]) == 0
    rows = [read(p) for p in (args.campaign / "records").glob("*.json")]
    manifest = read(args.report / "manifest.json")
    compared = read(args.comparison)["rows"]
    identity = read(args.campaign / "identity.json")["runtime"]
    gates = []
    def gate(identifier, condition, evidence, limitation=""):
        gates.append({"gate": identifier, "status": "PASS" if condition else "FAIL", "evidence": evidence, "limitation": limitation})
    gate("ER01", checks.get("ruff") and checks.get("mypy") and checks.get("architecture"), "Fresh Ruff/mypy/import audit; modular backend and React shell/pages/hooks")
    schema_ok = all(read(ROOT / f"datasets/schemas/{key}.schema.json") == cls.model_json_schema() for key, cls in SECTIONS.items())
    gate("ER02", schema_ok and any(t.startswith("test_lossless_csv_including_nested_values") for t in tests) and "test_version_migration_is_non_destructive_and_explicit" in tests, "Versioned 1.1 contracts, CSV/JSON, immutable migration and reference/units tests")
    def experiments(identifier):
        chosen = [r for r in rows if r["experiment"] == identifier]
        return chosen and all(r["status"] == "SUCCEEDED" and r["validation"]["status"] == "PASS" for r in chosen)
    gate("ER03", experiments("E01") and "test_local_search_improves_feasible_layout" in tests and "test_full_walkable_topology_rejects_disconnected_components" in tests, "E01 witnesses plus geometry/topology/local-search reference regressions")
    gate("ER04", experiments("E02") and "test_soft_affinity_milp_matches_independent_enumeration" in tests and "test_t2_matches_independent_enumeration" in tests, "Greedy/MILP E02 and independently enumerated allocation/affinity objectives")
    gate("ER05", experiments("E03") and "test_mip_matches_independent_exhaustive_stock_enumeration" in tests and "test_mip_facing_range_and_shelf_compatibility" in tests, "First-fit/MIP E03; independent physical replay, exact optimum and facing/compatibility tests")
    gate("ER06", experiments("E04") and "test_exact_routing_matches_permutation_oracle" in tests and "test_customer_exit_and_required_aisle_replay" in tests, "Nearest/return/exact E04, route/quantity/time replay and finite picker/period/exit regressions")
    gate("ER07", experiments("E05") and "test_persistent_cache_invalidation_and_tampering" in tests and "test_process_creation_failures_have_bounded_retry_and_terminal_receipts" in tests, "Bounded integrated candidates, stage artifacts, content cache, dependency rerun, cancellation and bounded retry")
    sizes = {read(p)["counts"]["shelves"] for p in (args.campaign / "datasets").glob("*/manifest.json")}
    gate("ER08", {4, 12, 36, 80} <= sizes and any(t.startswith("test_generators_are_deterministic_valid_and_labeled") for t in tests), "Tiny/Small/Medium/Large manifest fingerprints and all five scenario generators")
    gate("ER09", "test_resume_reports_checksums_and_full_campaign_replay" in tests and read(args.campaign / "checkpoint.json")["status"] == "COMPLETED", "Real durable worker campaign, resume without rewriting completed jobs, process fault/retry receipts")
    gate("ER10", (args.report / "statistics.json").is_file() and "test_failed_jobs_retained_and_duplicate_seeds_not_independent" in tests and "test_degenerate_pairs_get_no_hypothesis_test" in tests, "Mean/median/SD/CI, selected-metric seed pairing, effect sizes/Holm where valid, failure retention", "Exploratory synthetic analysis, not population efficacy certification")
    hashes_ok = verify_integrity(args.campaign)["status"] == verify_integrity(args.pilot)["status"] == "PASS"
    comparison_ok = compared and all(r.get("same_input_hash") and r.get("byte_identical_result") and r.get("numerically_equivalent") for r in compared)
    gate("ER11", hashes_ok and comparison_ok and identity == runtime_identity() and verification["runtime"] == identity, "Clean Python environment replay; exact result hashes distinguished from numeric tolerance; current source/dependency identity")
    gate("ER12", all_tests_ok and all(checks.get(c) for c in ("pytest", "eslint", "vitest", "frontend-build", "e2e", "pip-check", "npm-audit")), f"Fresh automated release checks: {suite.attrib['tests']} backend cases plus Vitest/E2E")
    required = ("summary.md", "results.csv", "results.json", "comparisons.csv", "statistics.json", "failures.csv", "manifest.json")
    report_hashes = all((args.report / name).is_file() for name in required)
    report_hashes = report_hashes and all(hashlib.sha256((args.report / name).read_bytes()).hexdigest() == value for name, value in manifest["files"].items())
    gate("ER13", report_hashes and bool(list((args.report / "figures").glob("*.png"))) and bool(list((args.report / "figures").glob("*.svg"))), "Verified CSV/JSON/Markdown/report manifest and Matplotlib PNG/SVG from actual rows")
    docs = ("EXPERIMENT_READINESS.md", "EXPERIMENT_READINESS_MATRIX.md", "HOW_TO_RUN_EXPERIMENTS.md")
    gate("ER14", all((ROOT / "docs/research" / name).is_file() for name in docs) and (ROOT / "docs/architecture/CURRENT_STATE.md").is_file() and (ROOT / "docs/architecture/DEPENDENCY_MAP.md").is_file(), "Published model scope, limits, protocol, installation/replay/report commands, current state and dependency map")
    browser = read(args.evidence / "browser/results.json")
    gate("ER15", experiments("E01") and experiments("E02") and experiments("E03") and experiments("E04") and experiments("E05") and browser["stats"].get("unexpected", 1) == 0 and checks.get("e2e"), "CLI pilot/main plus actual dashboard campaign/download/figure/replay and input CSV browser demonstration")
    status = "EXPERIMENT_READY_SYNTHETIC" if all(g["status"] == "PASS" for g in gates) else "EXPERIMENT_READINESS_INCOMPLETE"
    result = {"status": status, "scope": "Declared controlled local Windows/MongoDB synthetic experiments; not production or real-world validation", "gates": gates,
              "runtime": identity, "tolerances": {"absolute": 1e-8, "relative": 1e-9}, "claims_excluded": ["REAL_WORLD_VALIDATED", "Container deployment runtime verified", "Large full T1-T4 scalability established", "Global integrated optimality"]}
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(status)
    for g in gates:
        print(g["gate"], g["status"])
    if status != "EXPERIMENT_READY_SYNTHETIC":
        sys.exit(1)


if __name__ == "__main__":
    main()
