"""Real full-suite long/short contrast followed by three independent HTTP repeats."""

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from smart_retail.infrastructure.filesystem import logical_fs_path, normalize_fs_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--temp-root", type=Path, default=Path("var"))
    args = parser.parse_args()
    output = normalize_fs_path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    cases = [("full-long", ["backend/tests"], True), ("full-short", ["backend/tests"], False)]
    http = ["backend/tests/integration/test_joint_research_http.py::test_joint_http_worker_certificate_report_and_safe_artifact",
            "backend/tests/integration/test_research_http.py::test_research_http_runs_real_child_and_exports_audited_report"]
    cases += [(f"http-repeat-{i}", http, True) for i in range(1, 4)]
    for label, tests, long in cases:
        base = args.temp_root.resolve() / ("lp-" + uuid4().hex[:10])
        if long:
            while len(str(base)) < 315:
                base /= "duong-dan-ki\u1ec3m-th\u1eed-" + "nested" * 5
        # Pytest itself needs an extended base before creating its own fixtures;
        # application tests additionally supply plain >260-character paths.
        base = normalize_fs_path(base)
        base.parent.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-m", "pytest", *tests, "-q", "--tb=short",
                   "--basetemp", str(base), "--junitxml", str(output / f"{label}.xml")]
        began = datetime.now(UTC).isoformat()
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=600)
        (output / f"{label}.stdout.log").write_text(result.stdout, encoding="utf-8")
        (output / f"{label}.stderr.log").write_text(result.stderr, encoding="utf-8")
        rows.append({"name": label, "command": command, "started_utc": began,
                     "ended_utc": datetime.now(UTC).isoformat(), "exit_code": result.returncode,
                     "logical_base_length": len(str(logical_fs_path(base))),
                     "status": "PASS" if result.returncode == 0 else "FAIL"})
        print(label, rows[-1]["status"], "base length", rows[-1]["logical_base_length"], flush=True)
    receipt = {"status": "PASS" if all(r["exit_code"] == 0 for r in rows) else "FAIL",
               "platform": sys.platform, "checks": rows,
               "unc_live": "NOT_APPLICABLE" if not os.getenv("SMART_RETAIL_TEST_UNC_ROOT") else "NOT_RUN"}
    (output / "verification.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
