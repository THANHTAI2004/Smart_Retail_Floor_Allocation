import hashlib
import importlib.metadata
import platform
from pathlib import Path


def runtime_identity() -> dict:
    source = hashlib.sha256()
    root = Path(__file__).resolve().parents[1]
    for path in sorted(root.rglob("*.py")):
        source.update(path.relative_to(root).as_posix().encode())
        source.update(path.read_bytes())
    return {
        "source_sha256": source.hexdigest(),
        "python": platform.python_version(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "shapely", "simpy", "networkx", "pydantic", "SQLAlchemy")
        },
    }
