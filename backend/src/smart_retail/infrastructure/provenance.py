import hashlib
import importlib.metadata
import platform
from pathlib import Path

from scipy.optimize._highspy import _core


def runtime_identity() -> dict:
    source = hashlib.sha256()
    root = Path(__file__).resolve().parents[1]
    for path in sorted(root.rglob("*.py")):
        source.update(path.relative_to(root).as_posix().encode())
        source.update(path.read_bytes())
    return {
        "source_sha256": source.hexdigest(),
        "python": platform.python_version(),
        "solver": {
            "name": "HiGHS",
            "version": f"{_core.HIGHS_VERSION_MAJOR}.{_core.HIGHS_VERSION_MINOR}.{_core.HIGHS_VERSION_PATCH}",
        },
        "model_versions": {
            "input_contract": "1.1",
            "t1": "grid-local-search-1.1",
            "t2": "allocation-affinity-milp-1.1",
            "t3": "facing-strip-milp-1.2-first-fit-repair",
            "t4": "picker-grid-queue-1.1",
            "workflow": "bounded-candidates-1.1",
            "joint": "finite-saa-feedback-1",
        },
        "packages": {
            distribution.metadata["Name"].lower(): distribution.version
            for distribution in sorted(
                importlib.metadata.distributions(), key=lambda d: d.metadata["Name"].lower()
            )
        },
    }
