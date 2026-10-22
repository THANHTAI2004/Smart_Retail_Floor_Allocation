"""Standalone research tables and Matplotlib figures from recorded outcomes."""

import csv
import hashlib
import json
from pathlib import Path

from smart_retail.application.experiments.analysis import analyze
from smart_retail.application.experiments.joint_reports import export as export_joint
from smart_retail.application.experiments.storage import read, verify_integrity, write
from smart_retail.infrastructure.filesystem import normalize_fs_path


def table(path, rows):
    path = normalize_fs_path(path)
    columns = sorted({key for row in rows for key in row}) or ["no_records"]
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                    for k, v in row.items()
                }
            )


def report(root: Path, output: Path):
    root, output = normalize_fs_path(root), normalize_fs_path(output)
    integrity = verify_integrity(root)
    rows = [read(path) for path in sorted((root / "records").glob("*.json"))]
    if not rows:
        raise ValueError("Campaign has no recorded outcomes")
    output.mkdir(parents=True, exist_ok=False)
    configuration = read(root / "configuration.json")
    statistics = analyze(rows, {e["id"]: e["metrics"] for e in configuration["experiments"]})
    write(output / "results.json", rows, immutable=True)
    write(output / "statistics.json", statistics, immutable=True)
    table(output / "results.csv", rows)
    table(output / "comparisons.csv", statistics["comparisons"])
    table(output / "failures.csv", [r for r in rows if r["status"] != "SUCCEEDED"])
    table(output / "summary.csv", statistics["summary"])
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures = output / "figures"
    figures.mkdir()
    labels = [f"{r['experiment']}/{r['dataset']}/{r['treatment']}" for r in statistics["summary"]]
    plt.rcParams.update({"font.size": 9, "figure.dpi": 140})
    for metric, unit in (
        ("wall_s", "Wall time (s, includes worker startup)"),
        ("mean_distance_m", "Mean journey distance (m)"),
        ("mean_wait_s", "Mean journey wait (s)"),
        ("peak_child_rss_bytes", "Peak child working set (bytes, OS sampled)"),
    ):
        values = [entry["metrics"][metric]["mean"] for entry in statistics["summary"]]
        bars = [(label, value) for label, value in zip(labels, values) if value is not None]
        if not bars:
            continue
        fig, ax = plt.subplots(figsize=(10, max(3, len(bars) * 0.23)))
        ax.barh([x[0] for x in bars], [x[1] for x in bars])
        ax.set_xlabel(unit)
        ax.set_title("Synthetic campaign: descriptive means; failures retained separately")
        fig.tight_layout()
        fig.savefig(figures / f"{metric}.png")
        fig.savefig(figures / f"{metric}.svg")
        plt.close(fig)
    valid = [
        r for r in rows if r.get("mean_distance_m") is not None and r.get("mean_wait_s") is not None
    ]
    if valid:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter(
            [r["mean_distance_m"] for r in valid], [r["mean_wait_s"] for r in valid], alpha=0.65
        )
        ax.set(
            xlabel="Mean distance (m)",
            ylabel="Mean wait (s)",
            title="Observed outcomes across datasets; not a global Pareto frontier",
        )
        fig.tight_layout()
        fig.savefig(figures / "outcomes.png")
        fig.savefig(figures / "outcomes.svg")
        plt.close(fig)
    checkpoint = read(root / "checkpoint.json")
    export_joint(root, output, rows, table)
    body = [
        "# Synthetic experiment report",
        "",
        f"Campaign: {read(root / 'configuration.json')['name']}",
        f"Status: {checkpoint['status']}; attempted {len(rows)} / planned {checkpoint['planned']}; not executed {checkpoint['not_executed']}.",
        "",
        "| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in statistics["summary"]:
        body.append(
            f"| {row['experiment']} | {row['dataset']} | {row['treatment']} | {row['succeeded']}/{row['total']} | {row['metrics']['wall_s']['mean']} | {row['metrics']['mean_distance_m']['mean']} |"
        )
    body.extend(
        [
            "",
            "## Assumptions and limitations",
            *[f"- {v}" for v in statistics["assumptions"]],
            "- SYNTHETIC only; no real-world validation. Resource-limited/unexecuted jobs are not PASS.",
            "- Solver optimality is scoped to each encoded model. Candidate selection is not global optimality.",
            "- Runtime and RSS are OS/process measurements on this machine; no cross-machine speed claim.",
        ]
    )
    (output / "summary.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    hashes = {
        p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in output.rglob("*")
        if p.is_file()
    }
    write(
        output / "manifest.json",
        {
            "campaign": str(root.resolve()),
            "identity": read(root / "identity.json"),
            "configuration": read(root / "configuration.json"),
            "datasets": [
                read(path) for path in sorted((root / "datasets").glob("*/manifest.json"))
            ],
            "validation": integrity,
            "files": hashes,
        },
        immutable=True,
    )
    return {
        "output": str(output),
        "records": len(rows),
        "figures": len(list(figures.glob("*.png"))),
    }
