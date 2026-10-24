"""Collect fresh release checks into a new, reviewable evidence directory."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    python = str(ROOT / ".venv/Scripts/python.exe")
    temporary = ROOT / "var" / f"pytest-release-{uuid4().hex[:12]}"
    checks = [
        ("pytest", [python, "-m", "pytest", "backend/tests", "-q", "--basetemp", str(temporary), "--junitxml", str(output / "pytest.xml")]),
        ("ruff", [python, "-m", "ruff", "check", "backend"]),
        ("mypy", [python, "-m", "mypy", "--config-file", "backend/pyproject.toml", "backend/src/smart_retail"]),
        ("pip-check", [python, "-m", "pip", "check"]),
        ("eslint", ["powershell", "-NoProfile", "-Command", "npm --prefix frontend run lint"]),
        ("vitest", ["powershell", "-NoProfile", "-Command", "npm --prefix frontend test"]),
        ("frontend-build", ["powershell", "-NoProfile", "-Command", "npm --prefix frontend run build"]),
        ("npm-audit", ["powershell", "-NoProfile", "-Command", "npm --prefix frontend audit --json"]),
        ("architecture", [python, "scripts/verify_architecture.py", "--output", str(output / "architecture.json")]),
        ("e2e", ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/verify_e2e.ps1"]),
    ]
    results = []
    for name, command in checks:
        began = datetime.now(UTC).isoformat()
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        (output / f"{name}.stdout.log").write_text(process.stdout, encoding="utf-8")
        (output / f"{name}.stderr.log").write_text(process.stderr, encoding="utf-8")
        results.append({"name": name, "command": command, "exit_code": process.returncode,
                        "started_utc": began, "ended_utc": datetime.now(UTC).isoformat()})
        print(name, "PASS" if process.returncode == 0 else "FAIL", flush=True)
        if name == "e2e" and process.returncode == 0:
            found = re.search(r"E2E evidence: ([^\r\n]+)", process.stdout)
            if found:
                source = Path(found.group(1).strip())
                shutil.copytree(source / "browser", output / "browser")
                shutil.copy2(source / "health.json", output / "isolated-health.json")
    from smart_retail.infrastructure.provenance import runtime_identity
    receipt = {"checks": results, "runtime": runtime_identity(),
               "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "git_index_sha256": hashlib.sha256((ROOT / ".git/index").read_bytes()).hexdigest(),
               "scope": "Local Windows/MongoDB synthetic platform; not container deployment or field validation",
               "files": {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file()}}
    (output / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if any(r["exit_code"] != 0 for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
