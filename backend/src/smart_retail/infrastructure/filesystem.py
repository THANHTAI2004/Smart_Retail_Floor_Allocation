"""Normalize owned artifact roots once so every derived operation uses native paths."""

import ntpath
import os
from pathlib import Path


def windows_extended_path(value: str) -> str:
    """Pure Windows conversion for absolute drive/UNC paths, never device paths."""
    if value.startswith("\\\\?\\"):
        plain = "\\\\" + value[8:] if value.startswith("\\\\?\\UNC\\") else value[4:]
        return windows_extended_path(plain)
    if value.startswith("\\\\.\\"):
        raise ValueError("Device paths are not artifact paths")
    value = ntpath.normpath(value)
    drive, tail = ntpath.splitdrive(value)
    if drive.startswith("\\\\") and tail.startswith("\\"):
        if len(drive[2:].split("\\")) != 2:
            raise ValueError("UNC server and share required")
        return "\\\\?\\UNC\\" + value[2:]
    if len(drive) == 2 and drive[1] == ":" and tail.startswith("\\"):
        return "\\\\?\\" + value
    raise ValueError("Absolute drive or UNC path required")


def normalize_fs_path(path: Path | str) -> Path:
    # abspath does not probe existence and works before nested directories exist.
    absolute = os.path.abspath(os.fspath(path))
    return Path(windows_extended_path(absolute) if os.name == "nt" else absolute)


def logical_fs_path(path: Path | str) -> Path:
    """Stable logical identity for paths persisted before extended-path support."""
    value = str(normalize_fs_path(path))
    if os.name == "nt":
        if value.startswith("\\\\?\\UNC\\"):
            value = "\\\\" + value[8:]
        elif value.startswith("\\\\?\\"):
            value = value[4:]
    return Path(value)


def publish_immutable_file(temporary: Path, target: Path) -> bool:
    """Hard-link publication is atomic/no-overwrite; unsupported filesystems fail."""
    try:
        os.link(normalize_fs_path(temporary), normalize_fs_path(target))
        return True
    except FileExistsError:
        return False
