"""Standalone research tables and Matplotlib figures from recorded outcomes."""

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from smart_retail.application.experiments.analysis import analyze
from smart_retail.application.experiments.deepmg_export import export as export_deepmg
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


def run_means(rows, metrics: dict[str, list[str]]):
    """Per-repetition means over folds, the deepmg ``*_mean_*`` analogue."""
    groups = defaultdict(list)
    for row in rows:
        key = (row["experiment"], row["dataset"], row["treatment"], row["seed"], row["repetition"])
        groups[key].append(row)
    result = []
    for (experiment, dataset, treatment, seed, repetition), records in sorted(groups.items()):
        entry = {
            "experiment": experiment,
            "dataset": dataset,
            "treatment": treatment,
            "seed": seed,
            "repetition": repetition,
            "folds_attempted": len(records),
            "folds_succeeded": sum(r["status"] == "SUCCEEDED" for r in records),
        }
        for metric in metrics.get(experiment, []):
            values = [r[metric] for r in records if isinstance(r.get(metric), (int, float))]
            entry[metric] = sum(values) / len(values) if values else None
        result.append(entry)
    return result


def status_matrix(rows):
    """Outcome counts per arm, the analogue of a confusion matrix for solver statuses."""
    counts = Counter(
        (r["experiment"], r["dataset"], r["treatment"], r["status"], r.get("evaluation_status"))
        for r in rows
    )
    return [
        {
            "experiment": e,
            "dataset": d,
            "treatment": t,
            "status": s,
            "evaluation_status": v,
            "count": n,
        }
        for (e, d, t, s, v), n in sorted(counts.items(), key=str)
    ]


def report(root: Path | list[Path], output: Path):
    roots = [normalize_fs_path(r) for r in (root if isinstance(root, list) else [root])]
    output = normalize_fs_path(output)
    integrity = [verify_integrity(r) for r in roots]
    identities = [read(r / "identity.json")["runtime"] for r in roots]
    if any(identity != identities[0] for identity in identities):
        raise ValueError("Campaigns differ in source/dependency identity; do not pool them")
    per_root = {r: [read(path) for path in sorted((r / "records").glob("*.json"))] for r in roots}
    rows = [row for r in roots for row in per_root[r]]
    if not rows:
        raise ValueError("Campaign has no recorded outcomes")
    if len({row["job_key"] for row in rows}) != len(rows):
        raise ValueError("The same job appears in more than one campaign")
    output.mkdir(parents=True, exist_ok=False)
    configurations = [read(r / "configuration.json") for r in roots]
    selected: dict[str, list[str]] = {}
    for configuration in configurations:
        for e in configuration["experiments"]:
            selected[e["id"]] = sorted(set(selected.get(e["id"], [])) | set(e["metrics"]))
    scales = {d["id"]: d["scale"] for c in configurations for d in c.get("datasets", [])}
    statistics = analyze(rows, selected, scales)
    write(output / "results.json", rows, immutable=True)
    write(output / "statistics.json", statistics, immutable=True)
    table(output / "results.csv", rows)
    table(output / "comparisons.csv", statistics["comparisons"])
    table(output / "instance_comparisons.csv", statistics["instance_comparisons"])
    table(output / "rankings.csv", statistics["rankings"])
    table(output / "failures.csv", [r for r in rows if r["status"] != "SUCCEEDED"])
    table(output / "summary.csv", statistics["summary"])
    table(output / "status_matrix.csv", status_matrix(rows))
    table(output / "run_means.csv", run_means(rows, selected))
    if any("cv_fold" in r for r in rows):
        table(output / "fold_results.csv", [r for r in rows if "cv_fold" in r])
    arms = export_deepmg(roots, output, rows, configurations)
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
    export_joint([(r, per_root[r]) for r in roots], output, table)
    body = ["# Synthetic experiment report", ""]
    for r, configuration in zip(roots, configurations):
        checkpoint = read(r / "checkpoint.json")
        body.extend(
            [
                f"Campaign: {configuration['name']}",
                f"Status: {checkpoint['status']}; attempted {len(per_root[r])} / planned {checkpoint['planned']}; not executed {checkpoint['not_executed']}.",
            ]
        )
        if configuration.get("evaluation"):
            spec = configuration["evaluation"]
            body.append(
                f"Held-out protocol: {spec['split']}, folds per repetition {spec['n_folds'] if spec['split'] == 'kfold' else 1}, repetitions = seeds {configuration['seeds']}."
            )
    body.extend(
        [
            "",
            "| Experiment | Dataset | Treatment | Succeeded / attempted | Mean wall s | Mean route m |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
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
    single = len(roots) == 1
    entries = [
        {
            "campaign": str(r.resolve()),
            "identity": read(r / "identity.json"),
            "configuration": configuration,
            "datasets": [read(path) for path in sorted((r / "datasets").glob("*/manifest.json"))],
            "validation": check,
        }
        for r, configuration, check in zip(roots, configurations, integrity)
    ]
    write(
        output / "manifest.json",
        {**entries[0], "files": hashes} if single else {"campaigns": entries, "files": hashes},
        immutable=True,
    )
    return {
        "output": str(output),
        "records": len(rows),
        "figures": len(list(figures.glob("*.png"))),
        "arms_complete": sum(a["complete"] for a in arms),
        "arms": len(arms),
    }
