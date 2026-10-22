"""Child-process resource sampling using OS APIs, not supervisor memory proxies."""

import os
from pathlib import Path


def is_alive(pid: int) -> bool:
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        try:
            status = wintypes.DWORD()
            return bool(
                kernel.GetExitCodeProcess(handle, ctypes.byref(status)) and status.value == 259
            )
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def sample(pid: int) -> dict:
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                *[
                    (n, ctypes.c_size_t)
                    for n in (
                        "PeakWorkingSetSize",
                        "WorkingSetSize",
                        "QuotaPeakPagedPoolUsage",
                        "QuotaPagedPoolUsage",
                        "QuotaPeakNonPagedPoolUsage",
                        "QuotaNonPagedPoolUsage",
                        "PagefileUsage",
                        "PeakPagefileUsage",
                    )
                ],
            ]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x410, False, pid)
        if not handle:
            return {"rss_bytes": None, "peak_rss_bytes": None, "cpu_s": None}
        try:
            values = Counters()
            values.cb = ctypes.sizeof(values)
            psapi = ctypes.WinDLL("psapi")
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
            ok = psapi.GetProcessMemoryInfo(handle, ctypes.byref(values), values.cb)
            stamps = [ctypes.c_ulonglong() for _ in range(4)]
            kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.c_void_p] * 4)]
            timed = kernel.GetProcessTimes(handle, *(ctypes.byref(v) for v in stamps))
            return {
                "rss_bytes": int(values.WorkingSetSize) if ok else None,
                "peak_rss_bytes": int(values.PeakWorkingSetSize) if ok else None,
                "cpu_s": (stamps[2].value + stamps[3].value) / 1e7 if timed else None,
            }
        finally:
            kernel.CloseHandle(handle)
    try:
        lines = Path(f"/proc/{pid}/status").read_text().splitlines()
        fields = {line.split(":")[0]: line.split(":")[1].strip() for line in lines}
        stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return {
            "rss_bytes": int(fields["VmRSS"].split()[0]) * 1024,
            "peak_rss_bytes": int(fields["VmHWM"].split()[0]) * 1024,
            "cpu_s": (int(stat[11]) + int(stat[12])) / getattr(os, "sysconf")("SC_CLK_TCK"),
        }
    except (OSError, KeyError):
        return {"rss_bytes": None, "peak_rss_bytes": None, "cpu_s": None}
