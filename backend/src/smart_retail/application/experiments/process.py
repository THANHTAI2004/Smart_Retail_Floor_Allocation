"""Background campaign supervisor, invoked without a shell by HTTP."""

import argparse
from pathlib import Path

from smart_retail.application.experiments.campaign import run
from smart_retail.application.experiments.reports import report
from smart_retail.application.experiments.storage import read, write
from smart_retail.contracts.experiments import CampaignSpec


def main():
    parser = argparse.ArgumentParser()
    for name in ("config", "output", "reports", "status"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    try:
        result = run(
            CampaignSpec.model_validate(read(args.config)), args.output, resume=args.resume
        )
        if result["completed"]:
            report(args.output, args.reports)
        write(
            args.status,
            {
                "status": result["status"],
                "report": str(args.reports) if result["completed"] else None,
            },
        )
    except Exception as exc:
        write(args.status, {"status": "FAILED", "error": f"{type(exc).__name__}: {exc}"})
        raise


if __name__ == "__main__":
    main()
