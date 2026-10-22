"""Immutable evidence files and atomic replaceable campaign checkpoints."""

import hashlib
import json
import time
from pathlib import Path
from uuid import uuid4


def read(path: Path):
    for attempt in range(25):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except PermissionError:
            if attempt == 24:
                raise
            time.sleep(0.01)


def write(path: Path, value, *, immutable: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, indent=2) + "\n"
    if immutable:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
    else:
        temporary = path.with_name(f".{uuid4()}.tmp")
        temporary.write_text(text, encoding="utf-8")
        for attempt in range(50):
            try:
                temporary.replace(path)
                break
            except PermissionError:
                if attempt == 49:
                    raise
                time.sleep(0.01)


def fingerprint(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*.json"))
        if ".stage-cache" not in path.parts
        and path.name not in ("integrity.json", "checkpoint.json")
    }


def verify_integrity(root: Path):
    saved = read(root / "integrity.json")
    for relative, expected in saved.items():
        path = (root / relative).resolve()
        if (
            not path.is_relative_to(root.resolve())
            or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected
        ):
            raise ValueError(f"Artifact checksum mismatch: {relative}")
    return {"status": "PASS", "files": len(saved)}
