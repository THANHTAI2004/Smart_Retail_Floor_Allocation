"""Content-addressed JSON stage cache with checksum validation and no pickle."""

import json
import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from uuid import uuid4

from smart_retail.application.workflow import canonical_hash
from smart_retail.domain.models import (
    EngineError,
    LayoutSolution,
    Planogram,
    Shelf,
    ShelfLevel,
    SimulationResult,
)


class StageCache(dict):
    def __init__(self, root: Path):
        super().__init__()
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def __contains__(self, key):
        return (self.root / f"{key}.json").exists()

    def __getitem__(self, key):
        envelope = json.loads((self.root / f"{key}.json").read_text(encoding="utf-8"))
        if envelope["key"] != key or canonical_hash(envelope["payload"]) != envelope["sha256"]:
            raise EngineError("CACHE_CORRUPT", f"Stage cache checksum mismatch {key}")
        payload, kind = envelope["payload"], envelope["kind"]
        if kind == "LayoutSolution":
            shelves = tuple(
                Shelf(**{**s, "levels": tuple(ShelfLevel(**level) for level in s["levels"])})
                for s in payload["shelves"]
            )
            return LayoutSolution(**{**payload, "shelves": shelves})
        if kind == "Planogram":
            return Planogram(**{**payload, "placements": tuple(payload["placements"])})
        if kind == "SimulationResult":
            return SimulationResult(**{**payload, "assumptions": tuple(payload["assumptions"])})
        if kind != "dict":
            raise EngineError("CACHE_CORRUPT", "Unknown cached type")
        return payload

    def __setitem__(self, key, value):
        payload = asdict(value) if is_dataclass(value) and not isinstance(value, type) else value
        envelope = {
            "key": key,
            "kind": type(value).__name__,
            "payload": payload,
            "sha256": canonical_hash(payload),
        }
        path = self.root / f"{key}.json"
        if path.exists():
            return
        temporary = self.root / f".{uuid4()}.tmp"
        temporary.write_text(json.dumps(envelope, allow_nan=False), encoding="utf-8")
        # Publish by hard link: an already published immutable value is never replaced.
        try:

            def native_path(value: Path) -> str:
                absolute = str(value.resolve())
                if os.name != "nt" or absolute.startswith("\\\\?\\"):
                    return absolute
                return (
                    "\\\\?\\UNC\\" + absolute[2:]
                    if absolute.startswith("\\\\")
                    else "\\\\?\\" + absolute
                )

            os.link(native_path(temporary), native_path(path))
        except FileExistsError:
            pass
        finally:
            temporary.unlink()
