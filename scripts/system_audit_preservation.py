"""Read-only preservation/replay assertions after a completed isolated system audit."""

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from smart_retail.application.workflow import canonical_hash
from smart_retail.infrastructure.database import connect
from smart_retail.infrastructure.provenance import runtime_identity


def main():
    root = Path(__file__).resolve().parents[1]
    audit = json.loads((root / "var/system-audit-current.json").read_text(encoding="utf-8"))
    output = Path(audit["root"])
    destination = output / "preservation.json"
    if destination.exists():
        raise FileExistsError(destination)
    began = datetime.now(UTC).isoformat()
    store, _ = connect()
    assert store.database.name == "smart_retail"
    values = {
        name: list(store.database[name].find().sort("_id", 1))
        for name in ("projects", "optimization_runs")
    }
    business = canonical_hash(values)
    assert business == audit["primary_business_sha256"]
    counts = {name: len(rows) for name, rows in values.items()}
    assert counts == audit["primary_counts"]
    store.dispose()

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root).decode("utf-8").strip()

    head = git("rev-parse", "HEAD")
    index = Path(git("rev-parse", "--git-path", "index"))
    if not index.is_absolute():
        index = root / index
    index_sha = hashlib.sha256(index.read_bytes()).hexdigest()
    assert head == audit["git_head"] and index_sha == audit["git_index_sha256"]
    backup_root = Path.home() / "Documents/SmartRetailBackups"
    artifacts = json.loads(
        (backup_root / "20261022-mongodb-01/artifact-manifest.json").read_text(encoding="utf-8")
    )
    for relative, digest in artifacts.items():
        assert (
            hashlib.sha256((root / "var/artifacts" / relative).read_bytes()).hexdigest() == digest
        ), relative
    research_manifest = backup_root / "20261022-release-research-1792650862/manifest.json"
    research = json.loads(research_manifest.read_text(encoding="utf-8"))
    size = 0
    for relative, digest in research.items():
        path = root / "experiments/results" / relative
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest, relative
        size += len(data)
    old = json.loads(
        (root / "docs/migration/mongodb-migration-report.json").read_text(encoding="utf-8")
    )
    assert (
        hashlib.sha256(Path(old["source_backup"]).read_bytes()).hexdigest() == old["source_sha256"]
    )
    comparisons = {}
    for kind in ("pilot", "joint"):
        rows = json.loads((output / f"{kind}-comparison.json").read_text(encoding="utf-8"))["rows"]
        assert len(rows) == (38 if kind == "pilot" else 10)
        for row in rows:
            assert row["present_in_both"] and row["same_input_hash"] and row["same_status"]
            if row["numerically_equivalent"] is not None:
                assert row["byte_identical_result"] and row["numerically_equivalent"]
            else:
                assert row["same_failure_code"]
        comparisons[kind] = {"rows": len(rows), "all_scientific_comparisons_pass": True}
    verification = json.loads((output / "verification.json").read_text(encoding="utf-8"))
    identity = runtime_identity()
    assert verification["status"] == "PASS" and identity == verification["runtime"]
    patch = subprocess.check_output(["git", "diff", "--binary"], cwd=root)
    (output / "audited-tracked.patch").write_bytes(patch)
    changed = git("ls-files", "-m", "--others", "--exclude-standard").splitlines()
    files = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in changed
        if (root / name).is_file()
    }
    destination.write_text(
        json.dumps(
            {
                "status": "PASS",
                "started_utc": began,
                "ended_utc": datetime.now(UTC).isoformat(),
                "command": [".venv/Scripts/python.exe", "scripts/system_audit_preservation.py"],
                "primary_database": "smart_retail",
                "primary_counts": counts,
                "primary_business_sha256": business,
                "matches_initial_business_sha": True,
                "original_artifact_files": len(artifacts),
                "original_artifact_checksums_match": True,
                "historical_research_files": len(research),
                "historical_research_bytes": size,
                "historical_research_manifest": str(research_manifest),
                "all_historical_research_checksums_match": True,
                "external_legacy_backup_sha256": old["source_sha256"],
                "external_legacy_backup_matches": True,
                "git_head": head,
                "git_index_sha256": index_sha,
                "git_index_unchanged": True,
                "changed_file_sha256": files,
                "tracked_patch_sha256": hashlib.sha256(patch).hexdigest(),
                "runtime": identity,
                "comparisons": comparisons,
                "exit_code": 0,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        "Preservation PASS:", counts, len(artifacts), "artifacts,", len(research), "research files"
    )


if __name__ == "__main__":
    main()
