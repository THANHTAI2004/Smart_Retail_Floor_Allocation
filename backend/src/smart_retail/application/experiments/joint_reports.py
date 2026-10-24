"""Additional proof and convergence artifacts extracted only from recorded worker results."""

from pathlib import Path

from smart_retail.application.experiments.storage import read, write


def export(roots: list[Path], output: Path, per_root: dict[Path, list], table):
    traces = []
    comparisons = []
    examples = {}
    for root, record in ((root, record) for root in roots for record in per_root[root]):
        if "proof_status" not in record:
            continue
        result = read(root / "artifacts" / record["run_id"] / "result.json")
        joint = result["joint"]
        comparisons.append({k: v for k, v in record.items() if not isinstance(v, (dict, list))})
        for event in joint["trace"]:
            traces.append(
                {
                    "job_key": record["job_key"],
                    "experiment": record["experiment"],
                    "treatment": record["treatment"],
                    "seed": record["seed"],
                    **event,
                }
            )
        if joint.get("certificate"):
            directory = output / "certificates"
            directory.mkdir(exist_ok=True)
            write(directory / f"{record['job_key']}.json", joint["certificate"], immutable=True)
        key = (record["experiment"], record["dataset"], record["treatment"])
        if key not in examples:
            examples[key] = (record, joint)
    if not comparisons:
        return
    table(output / "joint-comparison.csv", comparisons)
    table(output / "joint-trace.csv", traces)
    write(
        output / "joint-examples.json",
        [{"record": r, "joint": j} for r, j in examples.values()],
        immutable=True,
    )
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    for (experiment, dataset, treatment), (record, joint) in examples.items():
        if joint["initial_score"] is None:
            continue
        values = [joint["initial_score"]] + [
            e["best_score"] for e in joint["trace"] if "best_score" in e
        ]
        ax.plot(
            range(len(values)),
            values,
            marker=".",
            label=f"{experiment}/{dataset}/{treatment}/seed={record['seed']}",
        )
    ax.set_xlabel("Completed feedback iteration (one representative seed per arm)")
    ax.set_ylabel("Fixed normalized joint objective")
    ax.set_title("Recorded convergence; absence of improvement is retained")
    ax.legend(fontsize=6, loc="best")
    fig.tight_layout()
    for suffix in ("png", "svg"):
        fig.savefig(output / "figures" / f"joint-convergence.{suffix}")
    plt.close(fig)
