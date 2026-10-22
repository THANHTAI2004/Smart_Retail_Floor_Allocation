import json
from pathlib import Path

import pytest

from smart_retail.workers.runner import read_progress


def test_progress_read_survives_transient_windows_sharing_violation(tmp_path, monkeypatch):
    path = tmp_path / "progress.json"
    path.write_text('{"stage": "T3"}', encoding="utf-8")
    original = Path.read_text
    calls = 0

    def read(self, *args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise PermissionError("Windows sharing violation")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)
    assert read_progress(path) is None
    assert read_progress(path) == "T3"
    assert read_progress(tmp_path / "missing.json") is None


def test_progress_read_does_not_hide_corrupt_artifact(tmp_path):
    path = tmp_path / "progress.json"
    path.write_text("invalid", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        read_progress(path)
