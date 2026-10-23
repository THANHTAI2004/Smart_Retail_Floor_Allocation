"""Sequential, isolated system verification with immutable per-command evidence."""

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from smart_retail.contracts.experiments import CampaignSpec
from smart_retail.infrastructure.provenance import runtime_identity

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, default=Path("var/system-audit-current.json"))
    args = parser.parse_args()
    audit = json.loads(args.state.read_text(encoding="utf-8"))
    output = Path(audit["root"])
    commands = output / "commands"
    commands.mkdir(exist_ok=False)
    env = dict(os.environ)
    env.update(
        SMART_RETAIL_TEST_DB_PREFIX=audit["database_prefix"],
        SMART_RETAIL_CAMPAIGN_DB_PREFIX=audit["database_prefix"],
        SMART_RETAIL_COMPOSE_DB_PREFIX=audit["database_prefix"],
        SMART_RETAIL_COMPOSE_JOINT_SMOKE="1",
        SMART_RETAIL_AUDIT_OUTPUT=str(output / "full-regression"),
        PYTHONIOENCODING="utf-8",
    )
    rows = []

    def run(name, command, timeout=1200):
        began = datetime.now(UTC).isoformat()
        result = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        (commands / f"{name}.stdout.log").write_text(result.stdout, encoding="utf-8")
        (commands / f"{name}.stderr.log").write_text(result.stderr, encoding="utf-8")
        rows.append(
            {
                "name": name,
                "command": command,
                "started_utc": began,
                "ended_utc": datetime.now(UTC).isoformat(),
                "exit_code": result.returncode,
                "status": "PASS" if result.returncode == 0 else "FAIL",
            }
        )
        (commands / "journal.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(name, rows[-1]["status"], flush=True)
        if result.returncode:
            raise RuntimeError("Audit command failed: " + name)

    python = sys.executable
    run("ruff", [python, "-m", "ruff", "check", "backend"])
    run(
        "mypy",
        [
            python,
            "-m",
            "mypy",
            "--config-file",
            "backend/pyproject.toml",
            "backend/src/smart_retail",
        ],
    )
    run("pip-check", [python, "-m", "pip", "check"])
    run(
        "eslint",
        ["powershell", "-NoProfile", "-Command", "npm --prefix frontend run lint"],
    )
    run("vitest", ["powershell", "-NoProfile", "-Command", "npm --prefix frontend test"])
    run(
        "frontend-build",
        ["powershell", "-NoProfile", "-Command", "npm --prefix frontend run build"],
    )
    run(
        "npm-audit",
        ["powershell", "-NoProfile", "-Command", "npm --prefix frontend audit --json"],
    )
    run(
        "architecture",
        [
            python,
            "scripts/verify_architecture.py",
            "--output",
            str(output / "architecture.json"),
        ],
    )
    run(
        "windows-long-path",
        [
            python,
            "scripts/verify_windows_long_path.py",
            "--output",
            str(output / "long-path"),
            "--temp-root",
            str(output / "tmp"),
        ],
    )
    # Each configuration is schema-validated; config presence is not execution proof.
    specs = []
    for file in sorted((ROOT / "experiments/configs").glob("*.json")):
        spec = CampaignSpec.model_validate_json(file.read_text(encoding="utf-8"))
        specs.append(
            {
                "file": str(file.relative_to(ROOT)),
                "experiments": [e.id for e in spec.experiments],
                "validated": True,
            }
        )
    (output / "configuration-inventory.json").write_text(json.dumps(specs, indent=2))
    for kind, config in [
        ("pilot", "pilot.json"),
        ("joint", "joint_certification.json"),
    ]:
        raw = json.loads((ROOT / "experiments/configs" / config).read_text(encoding="utf-8"))
        raw["seeds"] = [11, 23]
        path = output / (kind + "-config.json")
        path.write_text(json.dumps(raw, indent=2))
        campaign = output / (kind + "-campaign")
        command = [python, "-m", "smart_retail.application.experiments.cli"]
        if kind == "pilot":
            run(
                "pilot-pause",
                [
                    *command,
                    "run",
                    "--config",
                    str(path),
                    "--output",
                    str(campaign),
                    "--max-new-jobs",
                    "3",
                ],
            )
            checkpoint = json.loads((campaign / "checkpoint.json").read_text())
            assert checkpoint["status"] == "PAUSED_PARTIAL" and checkpoint["completed"] == 3
            (output / "pilot-pause-proof.json").write_text(json.dumps(checkpoint, indent=2))
            run(
                "pilot-resume",
                [*command, "resume", "--config", str(path), "--output", str(campaign)],
            )
        else:
            run(
                "joint-run",
                [*command, "run", "--config", str(path), "--output", str(campaign)],
            )
        replay = output / (kind + "-replay")
        run(
            kind + "-replay",
            [*command, "replay", str(campaign), "--output", str(replay)],
        )
        run(
            kind + "-compare",
            [
                *command,
                "compare",
                str(campaign),
                str(replay),
                "--output",
                str(output / (kind + "-comparison.json")),
            ],
        )
        comparison = json.loads((output / (kind + "-comparison.json")).read_text(encoding="utf-8"))
        assert comparison["rows"]
        for row in comparison["rows"]:
            assert row["present_in_both"] and row["same_status"] and row["same_input_hash"]
            if row.get("numerically_equivalent") is not None:
                assert row["byte_identical_result"] and row["numerically_equivalent"]
            else:
                assert row["same_failure_code"]
        run(
            kind + "-report",
            [
                *command,
                "analyze",
                str(campaign),
                "--output",
                str(output / (kind + "-report")),
            ],
        )
    run(
        "compose",
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "scripts/verify_mongodb_compose.ps1",
            "-Output",
            str(output / "compose"),
        ],
    )
    run(
        "e2e",
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "scripts/verify_e2e.ps1",
            "-OutputRoot",
            str(output / "e2e-final"),
            "-DatabasePrefix",
            audit["database_prefix"],
        ],
    )
    (output / "verification.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "runtime": runtime_identity(),
                "audit_id": audit["audit_id"],
                "commands": rows,
                "atlas": "OUT_OF_SCOPE",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
