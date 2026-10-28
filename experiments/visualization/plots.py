"""Export actual scalability, sensitivity and finite-candidate Pareto figures.

Run from repository root; a new output directory and source-bound manifest are required.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from smart_retail.application.experiments.analysis import describe
from smart_retail.application.experiments.storage import read, verify_integrity, write


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify_integrity(args.campaign)
    args.output.mkdir(parents=True, exist_ok=False)
    rows = [read(path) for path in (args.campaign / "records").glob("*.json")]
    figure_data = []
    def save(fig, name):
        fig.tight_layout()
        fig.savefig(args.output / f"{name}.png", dpi=160)
        fig.savefig(args.output / f"{name}.svg")
        plt.close(fig)
    scales = []
    for dataset in sorted({row["dataset"] for row in rows if row["experiment"] == "E08"}):
        group = [r for r in rows if r["experiment"] == "E08" and r["dataset"] == dataset]
        shelves = read(args.campaign / "datasets" / dataset / "manifest.json")["counts"]["shelves"]
        scales.append((shelves, dataset, describe([r["wall_s"] for r in group]), describe([r["peak_child_rss_bytes"]/1048576 for r in group if r["peak_child_rss_bytes"] is not None])))
    if scales:
        scales.sort()
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for axis, index, unit in ((axes[0], 2, "Wall time (s, includes process creation)"), (axes[1], 3, "Observed child peak working set (MiB)")):
            values = [g[index] for g in scales]
            axis.errorbar([g[0] for g in scales], [v["mean"] for v in values], yerr=[(v["ci95"][1]-v["ci95"][0])/2 if v["ci95"] else 0 for v in values], marker="o", capsize=4)
            axis.set(xlabel="Shelf count; declared T1 instances", ylabel=unit)
        fig.suptitle("T1 scalability only; descriptive seed intervals on this machine")
        save(fig, "scalability")
        figure_data.extend({"figure": "scalability", "dataset": g[1], "shelves": g[0], "wall": g[2], "rss_mib": g[3]} for g in scales)
    groups = sorted({(r["dataset"], r["treatment"]) for r in rows if r["experiment"] == "E06"})
    if groups:
        summaries = []
        for dataset, treatment in groups:
            values = [r["mean_wait_s"] for r in rows if r["experiment"] == "E06" and r["dataset"] == dataset and r["treatment"] == treatment and r.get("mean_wait_s") is not None]
            summaries.append(describe(values))
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.bar([f"{d}/{t}" for d, t in groups], [v["mean"] for v in summaries], yerr=[(v["ci95"][1]-v["ci95"][0])/2 if v["ci95"] else 0 for v in summaries], capsize=4)
        ax.set(ylabel="Mean journey wait (s)", title="Coupled arrival/picker sensitivity; effects are not separately identified")
        ax.tick_params(axis="x", labelrotation=15)
        save(fig, "sensitivity")
        figure_data.extend({"figure": "sensitivity", "dataset": d, "treatment": t, "summary": v} for (d, t), v in zip(groups, summaries))
    representative = next((r for r in rows if r["experiment"] == "E05" and r["treatment"] == "multistart" and r["seed"] == min(v["seed"] for v in rows)), None)
    if representative:
        result = read(args.campaign / "artifacts" / representative["run_id"] / "result.json")
        candidates = [c for c in result["integrated"]["candidates"] if c["status"] == "FEASIBLE"]
        front = [c for c in candidates if not any(all(a <= b for a, b in zip(other["components"], c["components"])) and any(a < b for a, b in zip(other["components"], c["components"])) for other in candidates)]
        if {c["candidate"] for c in front} != set(result["integrated"]["pareto_candidates"]):
            raise ValueError("Independent finite Pareto replay mismatch")
        fig, ax = plt.subplots(figsize=(8, 4))
        scatter = ax.scatter([c["components"][0] for c in candidates], [c["components"][1] for c in candidates], c=[c["components"][2] for c in candidates], cmap="viridis", s=85)
        ax.scatter([c["components"][0] for c in front], [c["components"][1] for c in front], facecolors="none", edgecolors="red", s=160, label="Nondominated within this finite run")
        for candidate in candidates:
            ax.annotate(str(candidate["candidate"]), candidate["components"][:2], xytext=(5, 5), textcoords="offset points")
        fig.colorbar(scatter, ax=ax, label="Normalized stock shortfall (third objective)")
        ax.set(xlabel="Normalized mean travel", ylabel="Normalized mean wait", title="E05 finite candidate frontier; no global Pareto claim")
        ax.legend(fontsize=8)
        save(fig, "pareto-candidates")
        figure_data.append({"figure": "pareto", "run_id": representative["run_id"], "dataset": representative["dataset"], "seed": representative["seed"], "candidates": candidates, "finite_frontier": [c["candidate"] for c in front]})
    write(args.output / "plot-data.json", figure_data, immutable=True)
    with (args.output / "plot-data.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, ["figure", "data_json"])
        writer.writeheader()
        writer.writerows({"figure": row["figure"], "data_json": json.dumps(row)} for row in figure_data)
    write(args.output / "manifest.json", {"campaign_identity": read(args.campaign / "identity.json"),
                                         "plot_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                         "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.iterdir() if p.is_file()}}, immutable=True)
    print(f"Published {len(list(args.output.glob('*.png')))} actual-data figures")


if __name__ == "__main__":
    main()
