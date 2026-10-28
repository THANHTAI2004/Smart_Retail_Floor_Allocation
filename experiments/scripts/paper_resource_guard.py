"""OS measurements and conservative, latched admission control for paper campaigns."""

import ctypes
import time


class MemoryStatus(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
        (name, ctypes.c_ulonglong)
        for name in (
            "total",
            "available",
            "page_total",
            "page_available",
            "virtual_total",
            "virtual_available",
            "extended",
        )
    ]


class Sampler:
    def __init__(self):
        self.previous = None

    def sample(self):
        memory = MemoryStatus()
        memory.length = ctypes.sizeof(memory)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
            raise OSError("Cannot measure physical memory")
        idle, kernel, user = (ctypes.c_ulonglong() for _ in range(3))
        if not ctypes.windll.kernel32.GetSystemTimes(
            ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
        ):
            raise OSError("Cannot measure system CPU")
        current = (idle.value, kernel.value + user.value)
        cpu = None
        if self.previous:
            elapsed = current[1] - self.previous[1]
            if elapsed > 0:
                cpu = 100 * (1 - (current[0] - self.previous[0]) / elapsed)
        self.previous = current
        return {
            "ram_percent": memory.load,
            "available_bytes": memory.available,
            "cpu_percent": cpu,
        }


def resource_failure(record, cpu_percent):
    if record.get("status") == "SUCCEEDED":
        return False
    error = record.get("error") or {}
    message = str(error.get("message", "")).lower()
    memory = any(
        token in message
        for token in (
            "memoryerror",
            "out of memory",
            "bad_alloc",
            "unable to allocate",
            "not enough memory",
            "paging file is too small",
        )
    )
    return (
        memory
        or error.get("code") in {"WORKER_CRASH", "WORKER_LOST", "RESOURCE_LIMIT"}
        or (error.get("code") in {"TIMEOUT", "TIMED_OUT"} and (cpu_percent or 0) >= 90)
    )


class Guard:
    def __init__(self):
        self.memory_since = None
        self.cpu_since = None

    def reason(self, sample, failure=False, timestamp=None):
        timestamp = time.monotonic() if timestamp is None else timestamp
        memory_high = (
            sample["ram_percent"] >= 90 or sample["available_bytes"] < 2 * 1024**3
        )
        cpu_high = (sample["cpu_percent"] or 0) >= 95
        self.memory_since = (
            (timestamp if self.memory_since is None else self.memory_since)
            if memory_high
            else None
        )
        self.cpu_since = (
            (timestamp if self.cpu_since is None else self.cpu_since)
            if cpu_high
            else None
        )
        if failure:
            return "NEW_RESOURCE_FAILURE_OR_WORKER_CRASH"
        if self.memory_since is not None and timestamp - self.memory_since >= 15:
            return "RAM_PRESSURE_15S"
        if self.cpu_since is not None and timestamp - self.cpu_since >= 120:
            return "CPU_SATURATION_120S"
        return None
