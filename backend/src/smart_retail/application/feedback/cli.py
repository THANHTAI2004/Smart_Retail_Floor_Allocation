"""Independent certificate replay from an immutable worker input and exported proof."""

import argparse
import json
import time
from pathlib import Path

from smart_retail.application.feedback.coordinator import identity, resolved_config, validate_space
from smart_retail.application.feedback.evaluator import evaluate
from smart_retail.engines.joint_exact.verifier import verify
from smart_retail.infrastructure.provenance import runtime_identity


def main():
    parser = argparse.ArgumentParser(description="Independently verify a finite-model certificate")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--time-limit", type=float, default=120)
    args = parser.parse_args()
    if not 0 < args.time_limit <= 300:
        parser.error("time-limit must be in (0,300] seconds")
    if args.output.exists():
        raise FileExistsError(args.output)
    sections = json.loads(args.input.read_text(encoding="utf-8"))
    if sections.get("_runtime") and sections["_runtime"] != runtime_identity():
        raise ValueError("SOURCE_DRIFT: use the recorded compatible source/dependency environment")
    config = resolved_config(sections)
    validate_space(config, sections)
    certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
    deadline = time.monotonic() + args.time_limit
    result = verify(
        certificate,
        lambda d: evaluate(
            sections, config, d, deadline, lambda: False, lambda _: None, {}, lambda *args: None
        ),
        identity=identity(sections, config),
        deadline=deadline,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(result)
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
