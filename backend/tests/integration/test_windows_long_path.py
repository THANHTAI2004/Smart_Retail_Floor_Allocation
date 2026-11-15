# Vai trò: Kiểm thử I/O Unicode, đường dẫn dài, spawn và công bố cache đồng thời.
# Các assertion mô tả hành vi mong đợi; kết quả chỉ được xác nhận sau khi chạy test.
"""Actual deep Unicode I/O and spawn, without changing Windows system policy."""

import multiprocessing as mp
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from smart_retail.application.experiments.storage import read, write
from smart_retail.domain.models import EngineError
from smart_retail.infrastructure.filesystem import (
    logical_fs_path,
    normalize_fs_path,
    windows_extended_path,
)
from smart_retail.infrastructure.stage_cache import StageCache


# Hàm deep_root: xử lý bước deep root trong phạm vi module hiện tại.
def deep_root(tmp_path):
    root = normalize_fs_path(tmp_path)
    while len(str(root)) < 330:
        root /= "thu-muc-ti\u1ebfng-Vi\u1ec7t-" + "nested" * 5
    return logical_fs_path(root)


# Hàm spawn_writer: xử lý bước spawn writer trong phạm vi module hiện tại.
def spawn_writer(root):
    cache = StageCache(Path(root))
    cache["a" * 64] = {"message": "D\u1eef li\u1ec7u b\u1ea5t bi\u1ebfn", "count": 7}
    write(Path(root) / "subprocess.json", {"done": True}, immutable=True)


@pytest.mark.parametrize("long", [False, True])
# Hàm test_cache_short_long_unicode_repeated_and_no_temp: kiểm tra kịch bản cache short long unicode repeated and no temp bằng các assertion trong thân hàm.
def test_cache_short_long_unicode_repeated_and_no_temp(tmp_path, long):
    root = deep_root(tmp_path) if long else tmp_path / "ng\u1eafn"
    cache = StageCache(root)
    key = "a" * 64
    if long:
        assert len(str(logical_fs_path(cache.root / f"{key}.json"))) > 260
    for _ in range(3):
        cache[key] = {"value": "\u0110\u01a1n h\u00e0ng", "number": 12}
        assert key in cache and cache[key]["value"] == "\u0110\u01a1n h\u00e0ng"
    cache[key] = {"different": True}
    assert cache[key]["number"] == 12
    assert not list(cache.root.glob("*.tmp"))
    write(root / "immutable.json", {"ok": True}, immutable=True)
    with pytest.raises(FileExistsError):
        write(root / "immutable.json", {"ok": False}, immutable=True)
    assert read(root / "immutable.json") == {"ok": True}
    write(root / "checkpoint.json", {"step": 1})
    write(root / "checkpoint.json", {"step": 2})
    assert read(root / "checkpoint.json") == {"step": 2}
    assert not list(cache.root.glob("*.tmp"))


# Hàm test_cache_corruption_and_concurrent_publication: kiểm tra kịch bản cache corruption and concurrent publication bằng các assertion trong thân hàm.
def test_cache_corruption_and_concurrent_publication(tmp_path):
    cache = StageCache(deep_root(tmp_path))
    key = "b" * 64
    with ThreadPoolExecutor(max_workers=12) as executor:
        list(executor.map(lambda n: cache.__setitem__(key, {"winner": n}), range(32)))
    first = cache[key]
    assert first["winner"] in range(32)
    assert not list(cache.root.glob("*.tmp"))
    path = cache.root / f"{key}.json"
    text = path.read_text()
    path.write_text(text.replace('"winner":', '"altered":'))
    with pytest.raises(EngineError, match="checksum"):
        cache[key]


# Hàm test_spawned_subprocess_writes_deep_cache: kiểm tra kịch bản spawned subprocess writes deep cache bằng các assertion trong thân hàm.
def test_spawned_subprocess_writes_deep_cache(tmp_path):
    root = deep_root(tmp_path)
    process = mp.get_context("spawn").Process(target=spawn_writer, args=(str(root),))
    process.start()
    process.join(30)
    if process.is_alive():
        process.terminate()
        process.join()
        pytest.fail("Spawned filesystem writer exceeded timeout")
    assert process.exitcode == 0
    assert StageCache(root)["a" * 64]["count"] == 7
    assert read(root / "subprocess.json") == {"done": True}


# Hàm test_failed_link_never_overwrites_or_leaks_temporary: kiểm tra kịch bản failed link never overwrites or leaks temporary bằng các assertion trong thân hàm.
def test_failed_link_never_overwrites_or_leaks_temporary(tmp_path, monkeypatch):
    cache = StageCache(deep_root(tmp_path))

    # Hàm unsupported: xử lý bước unsupported trong phạm vi module hiện tại.
    def unsupported(*args):
        raise OSError("hard links unavailable")

    monkeypatch.setattr(os, "link", unsupported)
    with pytest.raises(OSError, match="unavailable"):
        cache["c" * 64] = {"value": 1}
    assert "c" * 64 not in cache
    assert not list(cache.root.glob("*.tmp"))


# Hàm test_windows_drive_unc_conversion_and_posix_identity: kiểm tra kịch bản windows drive unc conversion and posix identity bằng các assertion trong thân hàm.
def test_windows_drive_unc_conversion_and_posix_identity(tmp_path):
    assert windows_extended_path(r"C:\folder\..\data") == "\\\\?\\C:\\data"
    assert windows_extended_path(r"\\server\share\folder") == "\\\\?\\UNC\\server\\share\\folder"
    extended = "\\\\?\\C:\\data"
    assert windows_extended_path(extended) == extended
    for invalid in ["relative", "C:relative", r"\\.\PhysicalDrive0", "\\\\?\\relative"]:
        with pytest.raises(ValueError):
            windows_extended_path(invalid)
    assert normalize_fs_path(logical_fs_path(tmp_path)) == normalize_fs_path(tmp_path.resolve())
    if os.name != "nt":
        assert not str(normalize_fs_path(tmp_path)).startswith("\\\\?\\")
